# DLog — A Low-Footprint Logging Solution for Embedded Systems

中文说明[在此](README.md)。

DLog separates log text from log data: all log text is collected into a standalone link-time region (consuming no runtime flash), while at runtime each log entry stores only a 32-bit log header plus its arguments, which the accompanying Python toolchain later restores offline into readable text. The core uses no dynamic memory and has no RTOS dependency—just one `.c` and two `.h` files—making it easy to port.

## Features

- **Storage cost decoupled from text length**: each log entry stores a fixed 32-bit header + an argument area (32 bits per argument), and the log text never enters the log stream—no matter how long a message is, its storage cost stays essentially the same.
- **No runtime flash consumed**: all log text is linked into a standalone region that can sit outside flash (the examples place it at `0x10000000`); it is never needed at runtime.
- **Storage-medium agnostic**: how logs are persisted is decided by a user-registered callback—a RAM ring buffer, on-chip Flash, EEPROM, or streaming over UART/RTT all work.
- **4 log levels, adjustable at runtime**: Error / Warn / Info / Debug; all levels are printed by default.
- **Optional timestamps**: provided by a user-registered timestamp callback.

## Directory Layout

```
DictionaryLog/
├── Inc/                dlog.h (public API), dlog_internal.h (internal definitions)
├── Src/                Core implementation dlog.c
├── Tools/              Offline parsing scripts elf2logstr.py / bin2txt.py, plus pyelftools.zip
└── _example/           Examples for three toolchains (sharing one main.c)
    ├── ARM-GNU/        arm-none-eabi-gcc: Makefile / build.cmd / example.ld
    ├── EWARM/          IAR project: example.eww / example.icf
    ├── MDK-ARM/        Keil project: example.uvprojx / example.sct
    ├── Tools/          Log-parsing entry scripts for the examples (EWARM.py / MDK-ARM.py)
    └── main.c          Example main program
```

## Quick Start

### 1. Initialization

```c
#include "dlog.h"

/* Timestamp callback: returns the current timestamp; pass NULL at init if not needed */
static uint32_t GetTick(void)
{
    return HAL_GetTick();                        /* Implement per platform */
}

/* Storage callback: how logs are persisted is entirely up to the user */
static void DLogStore(DLOG_HEAD_T *head, uint8_t *body, size_t size)
{
    head->SN = gSN++;                            /* SN increment and concurrency control are this callback's job */
    LogBufWrite((uint8_t *)head, sizeof(*head)); /* head/body point to scratch space; copy them before returning */
    LogBufWrite(body, size);
}

DLogInit(GetTick, DLogStore);                    /* Init fails when store is NULL */
```

### 2. Printing Logs

```c
DLogPrintfError("System init failed, code=%d", 1001);
DLogPrintfWarn("Temperature over threshold: %d > %d", 85, 70);
DLogPrintfInfo("Device started, version=%d.%d.%d", 1, 2, 3);
DLogPrintfInfo("No args log");

DLogSetLevel(DLOG_LEVEL_WARN);                   /* Adjust the level at runtime (default DEBUG: print everything) */
```

### 3. Configuring the Linker Script

Reserve a dedicated region for the log text in your linker script (the `logstr` section); the configuration for the three toolchains is covered in [Linker Script Configuration for the Three Toolchains](#linker-script-configuration-for-the-three-toolchains) below.

### 4. Offline Parsing

After building the ELF/AXF and running the firmware to produce the binary log file (`dlog.bin` in the examples), restore it in one step with the scripts under `_example/Tools/`:

```bash
cd _example/Tools
python EWARM.py        # IAR example
python MDK-ARM.py      # Keil example
python ARM-GNU.py      # Arm GNU example
```

Each script performs two steps automatically: it first extracts the string region from the ELF to build `logstr.json`, then uses it to decode `dlog.bin` into `log.txt`:

```
[sn:000][Error][0]:System init failed, code=1001
[sn:001][Warn ][1]:Temperature over threshold: 85 > 70
[sn:002][Info ][2]:Device started, version=1.2.3
```

Each script is bound to the build-output paths of its toolchain. The IAR / Keil linkers merge and rename custom sections in the ELF, so those two scripts locate the string region by link address, whereas the Arm GNU script locates it by section name `.logstr` and verifies that the section's link address matches `LOGSTR_BASE` in the script.

Parsing depends on [pyelftools](https://github.com/eliben/pyelftools): `pip install pyelftools`, or use the bundled copy in `Tools/pyelftools.zip`.

## Key Configuration: Three Addresses That Must Stay in Sync

`DLOG_FORMAT_START_ADDRESS` (source code), the string-region start address (linker script), and `LOGSTR_BASE` (parsing script) jointly determine whether logs can be restored correctly—**whenever you change any one of them, you must check the other two as well**:

| Item | Where it lives | Example value | Purpose |
|---|---|---|---|
| String-region start address | Linker script (icf / sct / ld) | `0x10000000` | Link address of the log text |
| `LOGSTR_BASE` | `_example/Tools/*.py` | `0x10000000` | Address used to locate/verify the string region in the ELF |
| `DLOG_FORMAT_START_ADDRESS` | `Inc/dlog.h` | `0` (default) | Address basis for computing log keys |

The rules:

1. **`LOGSTR_BASE` must exactly equal the region start address in the linker script.**
   The IAR / Keil linkers merge and rename custom sections in the ELF (e.g. `P3 ro`), so looking them up by name is unreliable; the parsing scripts for these two toolchains therefore locate the string region by address—if the address does not match, it cannot be found. The Arm GNU parsing script locates the region by section name `.logstr`, but it still verifies the section's link address against `LOGSTR_BASE` and refuses to parse on mismatch.

2. **`DLOG_FORMAT_START_ADDRESS` has two legal choices (pick one):**
   - If the region start address is **aligned to 512KB (0x80000)**, keep the default `0` (the examples' approach: `0x10000000` is 256MB, which is naturally 512KB-aligned);
   - For an arbitrary region start address, you must define it to a value **exactly equal** to the region start address (edit `dlog.h` directly, or override it via the compiler option `-DDLOG_FORMAT_START_ADDRESS=0x…`).

3. **The string region must not exceed 512KB in total**: the key index space caps out at 512KB of text, so allocating a larger region buys nothing.

The typical symptom of a mismatch among the three: the parser prints `There is no such logstr!`. In addition, the ELF/AXF used for parsing must come from **the same build** as the firmware that produced the logs—once the text dictionary changes, old logs can no longer be restored.

## Linker Script Configuration for the Three Toolchains

All three examples use the same string region: starting at `0x10000000`, 512KB in size, outside the normal flash. The region plays no part at runtime—it exists only in the ELF/AXF for the parsing scripts to extract. Section placement on the source side (IAR's `@ "logstr"`, Keil/GNU's `__attribute__((section(...)))`) is already handled automatically by `dlog_internal.h`; users only need to configure the linker script.

### IAR (EWARM) — example.icf

Override the default icf in the project options (Options → Linker → Config; already done in the examples). Add the following to the icf:

```
/*-logstr-*/
define symbol __LOGSTR_start__ = 0x10000000;
define symbol __LOGSTR_end__   = 0x1007FFFF;
/*-logstr-*/
define region LOGSTR_region = mem:[from __LOGSTR_start__ to __LOGSTR_end__];

/*-logstr-*/
place in LOGSTR_region { readonly section logstr };
```

Notes:

- The string-region address must lie within `0x00000000 ~ 0x1FFFFFFF` (an IAR address-range mapping limitation); the examples' `0x10000000` satisfies this.
- The IAR linker renames custom sections in the ELF (e.g. `P3 ro`), so the parsing script locates the string region by address rather than by section name; `__LOGSTR_start__` must therefore match `LOGSTR_BASE` in the parsing script.

### Keil MDK — example.sct

Point μVision's Options → Linker at the scatter file (`.\Objects\example.sct` in the examples). Add a separate load region, outside the existing ones, to collect the `logstr` section:

```
LR_LOGSTR 0x10000000 0x00080000  {
  Logstr_Section 0x10000000 0x00080000  {
    .ANY (logstr)
  }
}
```

Notes:

- The start address of `LR_LOGSTR` must match `LOGSTR_BASE` in the parsing script.
- The Keil linker may likewise rename sections, so parsing also goes by address.
- When debugging with the μVision software simulator, this address range is not in the default memory map and must be mapped explicitly in the Debug initialization file (`debug_sim.ini` in the examples): `MAP 0x10000000, 0x1007FFFF READ WRITE`.

### Arm GNU — example.ld

Define the region in `MEMORY` and collect the section in `SECTIONS`:

```
MEMORY
{
    /* ... FLASH / RAM ... */
    LOGSTR (r)  : ORIGIN = 0x10000000, LENGTH = 512K
}

SECTIONS
{
    /* DLog string region: not used at runtime, present only for the parsing scripts to extract. */
    .logstr ORIGIN(LOGSTR) :
    {
        . = ALIGN(4);
        __logstr_start = .;
        KEEP(*(.logstr))
        . = ALIGN(4);
        __logstr_end = .;
    } > LOGSTR
}
```

Notes:

- GCC section names carry a dot: the sources emit `.logstr`, and the linker script collects it with `*(.logstr)`.
- `KEEP` is indispensable—without it, `--gc-sections` would strip the entire unreferenced string region.
- The parsing script locates the string region by section name `.logstr` and verifies the section's link address against `LOGSTR_BASE` in the script, so neither the section name nor the ORIGIN of `LOGSTR` may be changed carelessly.

## Examples

All three examples share `_example/main.c` and demonstrate initialization, printing at every level, and runtime level filtering. They run on each IDE's software simulator and use semihosting to write the logs into `dlog.bin` on the host, which is then parsed into `log.txt` by the matching script under `_example/Tools/`.

| Toolchain | Project entry | How to build | Parsing script |
|---|---|---|---|
| IAR EWARM | `_example/EWARM/example.eww` | Open in IDE, build, download & run | `python EWARM.py` |
| Keil MDK | `_example/MDK-ARM/example.uvprojx` | Open in IDE, build, simulate | `python MDK-ARM.py` |
| Arm GNU | `_example/ARM-GNU/` | `make` (POSIX shell) or `build.cmd` (Windows cmd) | `python ARM-GNU.py` |

Building requires `arm-none-eabi-gcc` on the PATH (`build.cmd` checks the PATH and then the default install locations); if it is not on the PATH, pass it via `make TOOLCHAIN_BINDIR="…/bin/"`.

## Limitations

- At most **7 arguments** per log entry (`DLOG_ARGS_MAX`).
- Arguments are always stored as **32-bit values**; wider values are truncated automatically, and floating-point arguments are not supported.
- Stick to integer/character format specifiers: `%d %i %u %o %x %X %c` (the parsing script restores signed/unsigned according to the specifier).
- The log sequence number SN is 8-bit (wrapping 0–255) and is incremented by the storage callback.
- If the string region's address or range changes, be sure to update all three configuration points in sync (see [Key Configuration](#key-configuration-three-addresses-that-must-stay-in-sync) above).

## License

AGPL-3.0, see [LICENSE](LICENSE).
