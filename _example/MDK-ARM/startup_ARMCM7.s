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

                ALIGN

                AREA    |.text|, CODE, READONLY

                IMPORT  __main

                EXPORT  Reset_Handler [WEAK]
Reset_Handler   PROC
                LDR     R0, =SystemInit
                BLX     R0
                LDR     R0, =__main
                BX      R0
                ENDP

                ALIGN

                EXPORT  NMI_Handler [WEAK]
NMI_Handler     PROC
                B       .
                ENDP

                EXPORT  HardFault_Handler [WEAK]
HardFault_Handler PROC
                B       .
                ENDP

                EXPORT  MemManage_Handler [WEAK]
MemManage_Handler PROC
                B       .
                ENDP

                EXPORT  BusFault_Handler [WEAK]
BusFault_Handler PROC
                B       .
                ENDP

                EXPORT  UsageFault_Handler [WEAK]
UsageFault_Handler PROC
                B       .
                ENDP

                EXPORT  SVC_Handler [WEAK]
SVC_Handler     PROC
                B       .
                ENDP

                EXPORT  DebugMon_Handler [WEAK]
DebugMon_Handler PROC
                B       .
                ENDP

                EXPORT  PendSV_Handler [WEAK]
PendSV_Handler  PROC
                B       .
                ENDP

                EXPORT  SysTick_Handler [WEAK]
SysTick_Handler PROC
                B       .
                ENDP

                EXPORT  SystemInit [WEAK]
SystemInit      PROC
                BX      LR
                ENDP

                ALIGN

                END