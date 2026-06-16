
extern unsigned int _stack_top;
extern unsigned int _etext;
extern unsigned int _data;
extern unsigned int _edata;
extern unsigned int _bss;
extern unsigned int _ebss;

void Reset_Handler(void);
void Default_Handler(void) { while(1); }
int main(void);
extern void SystemInit(void);

// Declaración de manejadores de interrupción débilmente enlazados al Default_Handler
void NMI_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void HardFault_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void MemManage_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void BusFault_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void UsageFault_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void SVC_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void DebugMon_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void PendSV_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));
void SysTick_Handler(void) __attribute__ ((weak, alias ("Default_Handler")));

// LPC17xx Specific Handlers
void WDT_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void TIMER0_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void TIMER1_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void TIMER2_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void TIMER3_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void UART0_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void UART1_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void UART2_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void UART3_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void PWM1_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void I2C0_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void I2C1_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void I2C2_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void SPI_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void SSP0_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void SSP1_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void PLL0_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void RTC_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void EINT0_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void EINT1_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void EINT2_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void EINT3_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void ADC_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void BOD_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void USB_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void CAN_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void DMA_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void I2S_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void ENET_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void RIT_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void MCPWM_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void QEI_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void PLL1_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void USBActivity_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));
void CANActivity_IRQHandler(void) __attribute__ ((weak, alias ("Default_Handler")));

// Tabla de vectores (Cortex-M3)
__attribute__((section(".vectors")))
void (*const vectors[])(void) = {
    (void (*)(void))&_stack_top, // 0: Stack pointer
    Reset_Handler,               // 1: Reset
    NMI_Handler,                 // 2: NMI
    HardFault_Handler,           // 3: HardFault
    MemManage_Handler,           // 4: MemManage
    BusFault_Handler,            // 5: BusFault
    UsageFault_Handler,          // 6: UsageFault
    (void (*)(void))0,           // 7: Checksum
    0,                           // 8: Reserved
    0,                           // 9: Reserved
    0,                           // 10: Reserved
    SVC_Handler,                 // 11: SVCall
    DebugMon_Handler,            // 12: Debug Monitor
    0,                           // 13: Reserved
    PendSV_Handler,              // 14: PendSV
    SysTick_Handler,             // 15: SysTick
    
    // External Interrupts
    WDT_IRQHandler,              // 16: Watchdog Timer
    TIMER0_IRQHandler,           // 17: Timer0
    TIMER1_IRQHandler,           // 18: Timer1
    TIMER2_IRQHandler,           // 19: Timer2
    TIMER3_IRQHandler,           // 20: Timer3
    UART0_IRQHandler,            // 21: UART0
    UART1_IRQHandler,            // 22: UART1
    UART2_IRQHandler,            // 23: UART2
    UART3_IRQHandler,            // 24: UART3
    PWM1_IRQHandler,             // 25: PWM1
    I2C0_IRQHandler,             // 26: I2C0
    I2C1_IRQHandler,             // 27: I2C1
    I2C2_IRQHandler,             // 28: I2C2
    SPI_IRQHandler,              // 29: SPI
    SSP0_IRQHandler,             // 30: SSP0
    SSP1_IRQHandler,             // 31: SSP1
    PLL0_IRQHandler,             // 32: PLL0 Lock (Main PLL)
    RTC_IRQHandler,              // 33: Real Time Clock
    EINT0_IRQHandler,            // 34: External Interrupt 0
    EINT1_IRQHandler,            // 35: External Interrupt 1
    EINT2_IRQHandler,            // 36: External Interrupt 2
    EINT3_IRQHandler,            // 37: External Interrupt 3
    ADC_IRQHandler,              // 38: A/D Converter
    BOD_IRQHandler,              // 39: Brown-Out Detect
    USB_IRQHandler,              // 40: USB
    CAN_IRQHandler,              // 41: CAN
    DMA_IRQHandler,              // 42: General Purpose DMA
    I2S_IRQHandler,              // 43: I2S
    ENET_IRQHandler,             // 44: Ethernet
    RIT_IRQHandler,              // 45: Repetitive Interrupt Timer
    MCPWM_IRQHandler,            // 46: Motor Control PWM
    QEI_IRQHandler,              // 47: Quadrature Encoder Interface
    PLL1_IRQHandler,             // 48: PLL1 Lock (USB PLL)
    USBActivity_IRQHandler,      // 49: USB Activity interrupt to wakeup
    CANActivity_IRQHandler       // 50: CAN Activity interrupt to wakeup
};

void Reset_Handler(void) {
    unsigned int *src = &_etext;
    unsigned int *dest = &_data;

    while(dest < &_edata) {
        *dest++ = *src++;
    }

    dest = &_bss;
    while(dest < &_ebss) {
        *dest++ = 0;
    }

    SystemInit();
    main();
    while(1);
}
