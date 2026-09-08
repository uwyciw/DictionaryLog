PREFIX  = arm-none-eabi-
CC      = $(PREFIX)gcc
AS      = $(PREFIX)gcc
LD      = $(PREFIX)gcc
OBJCOPY = $(PREFIX)objcopy
SIZE    = $(PREFIX)size

CPU     = -mcpu=cortex-m4
FPU     = -mfpu=fpv4-sp-d16 -mfloat-abi=hard
ARCH    = -mthumb $(CPU) $(FPU)

DEFS    = -D__GNUC__

INC     = -I../../Inc

CFLAGS  = $(ARCH) $(DEFS) $(INC) -Wall -Wextra -Wno-unused-parameter -O2 -g -ffunction-sections -fdata-sections -fno-common -fmessage-length=0

ASFLAGS = $(ARCH) $(DEFS) -Wall -g

LDFLAGS = $(ARCH) -Wl,--gc-sections -T example.ld -Wl,-Map=example.map --specs=nosys.specs

C_SRCS  = ../../Src/dlog.c ../main.c
A_SRCS  = startup_ARMCM4.S

C_OBJS  = $(patsubst %.c,%.o,$(C_SRCS))
A_OBJS  = $(patsubst %.S,%.o,$(A_SRCS))
OBJS    = $(A_OBJS) $(C_OBJS)

TARGET  = example

.PHONY: all clean

all: $(TARGET).elf
	$(SIZE) $(TARGET).elf

$(TARGET).elf: $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	$(AS) $(ASFLAGS) -c -o $@ $<

clean:
	$(RM) $(OBJS) $(TARGET).elf $(TARGET).map