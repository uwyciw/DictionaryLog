# DLog —— 面向嵌入式系统的低空间占用日志方案

English Readme is [here](README-EN.md).

DLog 将日志文本与日志数据分离：日志文本集中存放在一个独立的链接区域（不占用运行
flash），运行时每条日志只存储一个 32bit 日志头和参数区，再由配套的 Python 工具链
离线还原为可读文本。内核无动态内存、无 RTOS 依赖，仅一个 `.c` 加两个 `.h`，便于移植。

## 特色

- **空间开销与文本长度解耦**：每条日志固定存储 32bit 日志头 + 参数区（每参数 32bit），
  日志文本不进入日志流——文本再长的日志，存储开销也几乎不变；
- **不占用运行 flash**：全部日志文本链接到一个独立区域，可放在 flash 之外（例程放在
  `0x10000000`），运行时完全不需要它；
- **存储介质无关**：日志如何落地由用户注册的回调决定，RAM 环形缓冲、片内 Flash、
  EEPROM、串口/RTT 上报均可；
- **4 级日志、运行时调级**：Error / Warn / Info / Debug，默认全部打印；
- **可选时间戳**：由用户注册的时间戳回调提供。

## 目录结构

```
DictionaryLog/
├── Inc/                dlog.h（对外 API）、dlog_internal.h（内部定义）
├── Src/                内核实现 dlog.c
├── Tools/              离线解析脚本 elf2logstr.py / bin2txt.py，及 pyelftools.zip
└── _example/           三套工具链例程（共用同一份 main.c）
    ├── ARM-GNU/        arm-none-eabi-gcc：Makefile / build.cmd / example.ld
    ├── EWARM/          IAR 工程：example.eww / example.icf
    ├── MDK-ARM/        Keil 工程：example.uvprojx / example.sct
    ├── Tools/          例程的日志解析入口脚本（EWARM.py / MDK-ARM.py）
    └── main.c          例程主程序
```

## 快速上手

### 1. 初始化

```c
#include "dlog.h"

/* 时间戳回调：返回当前时间戳；不需要时间戳，初始化时直接传 NULL */
static uint32_t GetTick(void)
{
    return HAL_GetTick();                        /* 按平台实现 */
}

/* 存储回调：日志落地方式完全由用户决定 */
static void DLogStore(DLOG_HEAD_T *head, uint8_t *body, size_t size)
{
    head->SN = gSN++;                            /* SN 的自增与并发控制由本回调负责 */
    LogBufWrite((uint8_t *)head, sizeof(*head)); /* head/body 均为临时空间，须在返回前拷贝 */
    LogBufWrite(body, size);
}

DLogInit(GetTick, DLogStore);                    /* store 传 NULL 时初始化失败 */
```

### 2. 打印日志

```c
DLogPrintfError("System init failed, code=%d", 1001);
DLogPrintfWarn("Temperature over threshold: %d > %d", 85, 70);
DLogPrintfInfo("Device started, version=%d.%d.%d", 1, 2, 3);
DLogPrintfInfo("No args log");

DLogSetLevel(DLOG_LEVEL_WARN);                   /* 运行时调整级别（默认 DEBUG，全打印） */
```

### 3. 配置链接脚本

在链接脚本中为日志文本开辟一个独立区域（`logstr` 段），三个工具链的配置见下文
[三大工具链的链接脚本配置](#三大工具链的链接脚本配置)。

### 4. 离线解析

编译得到 ELF/AXF，固件运行产生日志二进制文件（例程为 `dlog.bin`）后，用
`_example/Tools/` 下的脚本一步还原：

```bash
cd _example/Tools
python EWARM.py        # IAR 例程
python MDK-ARM.py      # Keil 例程
python ARM-GNU.py      # Arm GNU 例程
```

脚本自动完成两步：先从 ELF 提取字符域生成 `logstr.json`，再依据它把 `dlog.bin`
解析成 `log.txt`：

```
[sn:000][Error][0]:System init failed, code=1001
[sn:001][Warn ][1]:Temperature over threshold: 85 > 70
[sn:002][Info ][2]:Device started, version=1.2.3
```

三个脚本分别与对应工具链的构建产物路径绑定；IAR / Keil 的链接器会在 ELF 中合并
重命名自定义段，故这两个脚本按链接地址定位字符域，而 Arm GNU 的脚本按段名
`.logstr` 定位，并校验段的链接地址与脚本中的 `LOGSTR_BASE` 一致。

解析依赖 [pyelftools](https://github.com/eliben/pyelftools)：`pip install pyelftools`，
或使用 `Tools/pyelftools.zip` 中附带的副本。

## 关键配置：三处地址必须保持一致

`DLOG_FORMAT_START_ADDRESS`（源码）、字符域区域起始地址（链接脚本）、`LOGSTR_BASE`
（解析脚本）三者共同决定了日志能否被正确还原，**修改任何一处都必须同步检查另外两处**：

| 配置项 | 所在位置 | 例程取值 | 作用 |
|---|---|---|---|
| 字符域区域起始地址 | 链接脚本（icf / sct / ld） | `0x10000000` | 日志文本的链接地址 |
| `LOGSTR_BASE` | `_example/Tools/*.py` | `0x10000000` | 在 ELF 中定位/校验字符域的链接地址 |
| `DLOG_FORMAT_START_ADDRESS` | `Inc/dlog.h` | `0`（默认） | 计算日志 Key 值的地址基准 |

规则如下：

1. **`LOGSTR_BASE` 必须与链接脚本中的区域起始地址完全相等。**
   IAR / Keil 链接器会把自定义段在 ELF 中合并重命名（如 `P3 ro`），按段名查找不可靠，
   这两个工具链的解析脚本因此按地址查找字符域，地址对不上就找不到；Arm GNU 的解析
   脚本虽按段名 `.logstr` 查找，但会校验段的链接地址与 `LOGSTR_BASE` 一致，不一致
   同样拒绝解析。

2. **`DLOG_FORMAT_START_ADDRESS` 有两种合法取法（二选一）：**
   - 区域起始地址按 **512KB（0x80000）对齐**时，保持默认值 `0` 即可（例程做法：
     `0x10000000` 为 256MB，天然满足 512KB 对齐）；
   - 区域起始地址为任意值时，必须把它定义为与区域起始地址**完全相同**的数值
     （可直接改 `dlog.h`，也可通过编译选项 `-DDLOG_FORMAT_START_ADDRESS=0x…` 覆盖）。

3. **字符域总大小不得超过 512KB**：Key 的索引空间上限为 512KB 文本，区域给大了
   也没有意义。

三处不一致的典型症状：解析输出 `There is no such logstr!`。另外，解析用的
ELF/AXF 必须与产生日志的固件是**同一次构建**的产物，文本字典变了旧的日志就还原不出来了。

## 三大工具链的链接脚本配置

三个例程的字符域区域统一为：起始 `0x10000000`、大小 512KB、位于常规 flash 之外。
该区域不参与运行，仅存在于 ELF/AXF 中供解析脚本提取。源码侧的段名定位
（IAR 的 `@ "logstr"`、Keil/GNU 的 `__attribute__((section(...)))`）已由
`dlog_internal.h` 自动处理，用户只需配置链接脚本。

### IAR（EWARM）—— example.icf

工程选项中需覆盖默认 icf（Options → Linker → Config，例程已配置）。在 icf 中新增：

```
/*-logstr-*/
define symbol __LOGSTR_start__ = 0x10000000;
define symbol __LOGSTR_end__   = 0x1007FFFF;
/*-logstr-*/
define region LOGSTR_region = mem:[from __LOGSTR_start__ to __LOGSTR_end__];

/*-logstr-*/
place in LOGSTR_region { readonly section logstr };
```

注意事项：

- 字符域区域地址需位于 `0x00000000 ~ 0x1FFFFFFF` 之间（IAR 的地址区间映射限制），
  例程的 `0x10000000` 满足要求；
- IAR 链接器会在 ELF 中重命名自定义段（如 `P3 ro`），解析脚本因此按地址而非段名
  查找字符域，故 `__LOGSTR_start__` 必须与解析脚本中的 `LOGSTR_BASE` 一致。

### Keil MDK —— example.sct

在 μVision 的 Options → Linker 中指定 scatter 文件（例程为 `.\Objects\example.sct`）。
在原有加载域之外，新增一个独立加载域收集 `logstr` 段：

```
LR_LOGSTR 0x10000000 0x00080000  {
  Logstr_Section 0x10000000 0x00080000  {
    .ANY (logstr)
  }
}
```

注意事项：

- `LR_LOGSTR` 的起始地址必须与解析脚本中的 `LOGSTR_BASE` 一致；
- Keil 链接器同样可能重命名段，解析也按地址查找；
- 若使用 μVision 软件仿真调试，该地址区间不在默认存储映射内，需在 Debug 初始化
  文件中显式映射（例程 `debug_sim.ini`）：`MAP 0x10000000, 0x1007FFFF READ WRITE`。

### Arm GNU —— example.ld

在 `MEMORY` 中定义区域，并在 `SECTIONS` 中收集段：

```
MEMORY
{
    /* ... FLASH / RAM ... */
    LOGSTR (r)  : ORIGIN = 0x10000000, LENGTH = 512K
}

SECTIONS
{
    /* DLog 字符域：不参与运行，仅供解析脚本提取。 */
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

注意事项：

- GCC 侧段名带点：源码生成 `.logstr`，链接脚本用 `*(.logstr)` 对应收集；
- `KEEP` 必不可少，否则 `--gc-sections` 会把无引用的字符域全部裁掉；
- 解析脚本按段名 `.logstr` 定位字符域，并校验段的链接地址与脚本中的 `LOGSTR_BASE`
  一致，因此段名与 `LOGSTR` 的 ORIGIN 都不能随意改动。

## 例程

三套例程共用 `_example/main.c`，演示初始化、各级别打印、调级过滤；基于各 IDE 的
软件仿真运行，借助 semihosting 把日志写入宿主机的 `dlog.bin`，再用 `_example/Tools/`
下对应脚本解析成 `log.txt`。

| 工具链 | 工程入口 | 构建方式 | 解析脚本 |
|---|---|---|---|
| IAR EWARM | `_example/EWARM/example.eww` | IDE 打开、构建、下载运行 | `python EWARM.py` |
| Keil MDK | `_example/MDK-ARM/example.uvprojx` | IDE 打开、构建、仿真运行 | `python MDK-ARM.py` |
| Arm GNU | `_example/ARM-GNU/` | `make`（POSIX shell）或 `build.cmd`（Windows cmd） | `python ARM-GNU.py` |

构建需要 `arm-none-eabi-gcc` 在 PATH 中（`build.cmd` 会依次检查 PATH 和默认安装路径）；
若不在 PATH，可 `make TOOLCHAIN_BINDIR="…/bin/"` 指定。

## 使用限制

- 每条日志最多 **7 个参数**（`DLOG_ARGS_MAX`）；
- 参数一律按 **32bit 数值**存储，超出位数自动截断，不支持浮点参数；
- 格式符建议使用整型/字符：`%d %i %u %o %x %X %c`（解析脚本按格式符还原有/无符号）；
- 日志序号 SN 为 8bit（0~255 循环），由存储回调负责自增；
- 字符域区域地址或范围变更时，务必同步三处配置（见上文[关键配置](#关键配置三处地址必须保持一致)）。

## License

AGPL-3.0，见 [LICENSE](LICENSE)。
