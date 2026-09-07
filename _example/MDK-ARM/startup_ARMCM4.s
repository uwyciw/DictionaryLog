;*******************************************************************************
;* @file     startup_ARMCM4.s
;* @brief    CMSIS Cortex-M4 Core Device Startup File
;*******************************************************************************

                PRESERVE8
                THUMB

Stack_Size      EQU     0x00004000
Heap_Size       EQU     0x00002000

                AREA    STACK, DATA, NOINIT, READWRITE, ALIGN=3
Stack_Mem       SPACE   Stack_Size
                EXPORT  __initial_sp
__initial_sp

                AREA    HEAP, DATA, NOINIT, READWRITE, ALIGN=3
                EXPORT  __heap_base
__heap_base
Heap_Mem        SPACE   Heap_Size
                EXPORT  __heap_limit
__heap_limit

                AREA    RESET, DATA, READONLY, ALIGN=3
                EXPORT  __Vectors
                EXPORT  __Vectors_End
                EXPORT  __Vectors_Size
__Vectors       DCD     __initial_sp
                DCD     Reset_Handler
                DCD     NMI_Handler
                DCD     HardFault_Handler
                DCD     MemManage_Handler
                DCD     BusFault_Handler
                DCD     UsageFault_Handler
                DCD     0
                DCD     0
                DCD     0
                DCD     0
                DCD     SVC_Handler
                DCD     DebugMon_Handler
                DCD     0
                DCD     PendSV_Handler
                DCD     SysTick_Handler
__Vectors_End

__Vectors_Size  EQU     __Vectors_End - __Vectors

                AREA    |.text|, CODE, READONLY

                IMPORT  __main

Reset_Handler   PROC
                EXPORT  Reset_Handler [WEAK]
                LDR     R0, =SystemInit
                BLX     R0
                LDR     R0, =__main
                BX      R0
                ENDP

NMI_Handler     PROC
                EXPORT  NMI_Handler [WEAK]
                B       .
                ENDP
HardFault_Handler PROC
                EXPORT  HardFault_Handler [WEAK]
                B       .
                ENDP
MemManage_Handler PROC
                EXPORT  MemManage_Handler [WEAK]
                B       .
                ENDP
BusFault_Handler PROC
                EXPORT  BusFault_Handler [WEAK]
                B       .
                ENDP
UsageFault_Handler PROC
                EXPORT  UsageFault_Handler [WEAK]
                B       .
                ENDP
SVC_Handler     PROC
                EXPORT  SVC_Handler [WEAK]
                B       .
                ENDP
DebugMon_Handler PROC
                EXPORT  DebugMon_Handler [WEAK]
                B       .
                ENDP
PendSV_Handler  PROC
                EXPORT  PendSV_Handler [WEAK]
                B       .
                ENDP
SysTick_Handler PROC
                EXPORT  SysTick_Handler [WEAK]
                B       .
                ENDP

                ALIGN

SystemInit      PROC
                EXPORT  SystemInit [WEAK]
                LDR     R0, =0xE000ED88
                LDR     R1, [R0]
                ORR     R1, R1, #0x00F00000
                STR     R1, [R0]
                DSB
                ISB
                BX      LR
                ENDP

                ALIGN

                END