/**
  ******************************************************************************
  * @file    startup_ARMCM4.S
  * @brief   CMSIS Cortex-M4 Core Device Startup File for GNU Assembler
  ******************************************************************************
**/

    .syntax unified
    .cpu cortex-m4
    .fpu fpv4-sp-d16
    .thumb

    .global  Reset_Handler
    .weak    NMI_Handler
    .weak    HardFault_Handler
    .weak    MemManage_Handler
    .weak    BusFault_Handler
    .weak    UsageFault_Handler
    .weak    SVC_Handler
    .weak    DebugMon_Handler
    .weak    PendSV_Handler
    .weak    SysTick_Handler
    .weak    Default_Handler

    .equ     Stack_Size, 0x00004000
    .equ     Heap_Size,  0x00002000

    .section .stack, "aw", %nobits
    .align  3
    .global __StackTop
    .global __StackLimit
__StackLimit:
    .space  Stack_Size
__StackTop:

    .section .heap, "aw", %nobits
    .align  3
    .global __HeapBase
    .global __HeapLimit
__HeapBase:
    .space  Heap_Size
__HeapLimit:

    .section .isr_vector, "a", %progbits
    .align  2
    .global __Vectors
    .global __Vectors_End
    .global __Vectors_Size
__Vectors:
    .long   __StackTop
    .long   Reset_Handler
    .long   NMI_Handler
    .long   HardFault_Handler
    .long   MemManage_Handler
    .long   BusFault_Handler
    .long   UsageFault_Handler
    .long   0
    .long   0
    .long   0
    .long   0
    .long   SVC_Handler
    .long   DebugMon_Handler
    .long   0
    .long   PendSV_Handler
    .long   SysTick_Handler
__Vectors_End:
    .equ    __Vectors_Size, __Vectors_End - __Vectors

    .section .text
    .align  2
    .thumb_func
    .weak   Default_Handler
Default_Handler:
    b       .

    .thumb_func
    .global Reset_Handler
    .type   Reset_Handler, %function
Reset_Handler:
    bl      SystemInit
    bl      main
    b       .

    .thumb_func
    .weak   SystemInit
    .type   SystemInit, %function
SystemInit:
    ldr     r0, =0xE000ED88
    ldr     r1, [r0]
    orr     r1, r1, #0x00F00000
    str     r1, [r0]
    dsb
    isb
    bx      lr

    .thumb_func
    .weak   NMI_Handler
    .type   NMI_Handler, %function
NMI_Handler:
    b       .

    .thumb_func
    .weak   HardFault_Handler
    .type   HardFault_Handler, %function
HardFault_Handler:
    b       .

    .thumb_func
    .weak   MemManage_Handler
    .type   MemManage_Handler, %function
MemManage_Handler:
    b       .

    .thumb_func
    .weak   BusFault_Handler
    .type   BusFault_Handler, %function
BusFault_Handler:
    b       .

    .thumb_func
    .weak   UsageFault_Handler
    .type   UsageFault_Handler, %function
UsageFault_Handler:
    b       .

    .thumb_func
    .weak   SVC_Handler
    .type   SVC_Handler, %function
SVC_Handler:
    b       .

    .thumb_func
    .weak   DebugMon_Handler
    .type   DebugMon_Handler, %function
DebugMon_Handler:
    b       .

    .thumb_func
    .weak   PendSV_Handler
    .type   PendSV_Handler, %function
PendSV_Handler:
    b       .

    .thumb_func
    .weak   SysTick_Handler
    .type   SysTick_Handler, %function
SysTick_Handler:
    b       .

    .end