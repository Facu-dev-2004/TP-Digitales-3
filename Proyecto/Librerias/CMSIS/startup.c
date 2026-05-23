
extern unsigned int _stack_top;
extern unsigned int _etext;
extern unsigned int _data;
extern unsigned int _edata;
extern unsigned int _bss;
extern unsigned int _ebss;

void Reset_Handler(void);
void Default_Handler(void) { while(1); }
int main(void);

// Tabla de vectores (Cortex-M3)
__attribute__((section(".vectors")))
void (*const vectors[])(void) = {
    (void (*)(void))&_stack_top, // 0: Stack pointer
    Reset_Handler,               // 1: Reset
    Default_Handler,             // 2: NMI
    Default_Handler,             // 3: HardFault
    Default_Handler,             // 4: MemManage
    Default_Handler,             // 5: BusFault
    Default_Handler,             // 6: UsageFault
    (void (*)(void))0            // 7: Checksum (LinkServer lo rellena)
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

    main();
    while(1);
}
