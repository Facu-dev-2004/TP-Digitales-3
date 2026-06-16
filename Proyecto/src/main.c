#include "LPC17xx.h"
#include "lpc17xx_adc.h"
#include "lpc17xx_pinsel.h"
#include "lpc17xx_exti.h"
#include "lpc17xx_uart.h"
#include "lpc17xx_systick.h"

#define ADC_RATE    8000 //freq muestreo
#define LISTSIZE    12000 //muestras por grabacion

#define SEG_MASK        0x7F

#define DIG0_BIT        (1 << 4)
#define DIG1_BIT        (1 << 5)
#define DIG2_BIT        (1 << 12)

#define SEG_O    0x3F
#define SEG_F    0x71
#define SEG_r    0x50
#define SEG_E    0x79
#define SEG_C    0x39

static const uint8_t MSG_OFF[3] = { SEG_O, SEG_F, SEG_F }; //off
static const uint8_t MSG_REC[3] = { SEG_r, SEG_E, SEG_C }; //recording

volatile uint8_t SEG_MSG[3] = { SEG_O, SEG_F, SEG_F };

void configADC(void);
void configGPIO(void);
void configSEG(void);
void configEINT0(void);
void configNVIC(void);
void configUART(void);
void cleanListADC(void);
void buttonDebounce(void);
void sendSamplesUART(void);
void seg_show(const uint8_t *msg);

volatile uint16_t listADC[LISTSIZE] = {0};  //audio
volatile uint32_t samples_count = 0;

uint8_t          RECORDING = 0;
volatile uint8_t FINISHED  = 0;


int main(void)
{
    configGPIO();
    configSEG();
    configEINT0();
    configADC();
    configUART();
    configNVIC();

    SYSTICK_InternalInit(5);
    SYSTICK_IntCmd(ENABLE);
    SYSTICK_Cmd(ENABLE);

    seg_show(MSG_OFF);

    while (1)
    {
        if (FINISHED) //si termina de grabar
        {
            FINISHED = 0; //bajo flag
            sendSamplesUART(); //mando la grab al uart
        }
    }
    return 0;
}


void cleanListADC(void)
{
    for (uint32_t i = 0; i < LISTSIZE; i++) listADC[i] = 0;
}

void buttonDebounce(void)
{
    for (volatile uint32_t i = 0; i < 50000; i++) {}
}


void seg_show(const uint8_t *msg)
{
    SEG_MSG[0] = msg[2];
    SEG_MSG[1] = msg[1];
    SEG_MSG[2] = msg[0];
}


void configGPIO(void)
{
    PINSEL_CFG_T pinCFG;

        //0.23 como adc0.0
    pinCFG.port      = PORT_0;
    pinCFG.pin       = PIN_23;
    pinCFG.func      = PINSEL_FUNC_01;
    pinCFG.mode      = PINSEL_TRISTATE;
    pinCFG.openDrain = DISABLE;
    PINSEL_ConfigPin(&pinCFG);
        //2.10 como eint0
    pinCFG.port      = PORT_2;
    pinCFG.pin       = PIN_10;
    pinCFG.func      = PINSEL_FUNC_01;
    pinCFG.mode      = PINSEL_PULLDOWN;
    pinCFG.openDrain = DISABLE;
    PINSEL_ConfigPin(&pinCFG);
        //0.10 cfg tx uart2
    pinCFG.port      = PORT_0;
    pinCFG.pin       = PIN_10;
    pinCFG.func      = PINSEL_FUNC_01;
    pinCFG.mode      = PINSEL_PULLUP;
    pinCFG.openDrain = DISABLE;
    PINSEL_ConfigPin(&pinCFG);
        //0.11 cfg rx uart2
    pinCFG.pin = PIN_11;
    PINSEL_ConfigPin(&pinCFG);

    LPC_GPIO0->FIODIR |= (1 << 22);
    LPC_GPIO3->FIODIR |= (1 << 25);
    LPC_GPIO3->FIODIR |= (1 << 26);

    LPC_GPIO0->FIOSET = (1 << 22);
    LPC_GPIO3->FIOSET = (1 << 25) | (1 << 26);
}

void configSEG(void) //configuracion de displays como salida y los enable
{
    PINSEL_CFG_T pinCFG;

    pinCFG.port      = PORT_2;
    pinCFG.func      = PINSEL_FUNC_00;
    pinCFG.mode      = PINSEL_PULLDOWN;
    pinCFG.openDrain = DISABLE;

    pinCFG.pin = PIN_0;  PINSEL_ConfigPin(&pinCFG);
    pinCFG.pin = PIN_1;  PINSEL_ConfigPin(&pinCFG);
    pinCFG.pin = PIN_2;  PINSEL_ConfigPin(&pinCFG);
    pinCFG.pin = PIN_3;  PINSEL_ConfigPin(&pinCFG);
    pinCFG.pin = PIN_4;  PINSEL_ConfigPin(&pinCFG);
    pinCFG.pin = PIN_5;  PINSEL_ConfigPin(&pinCFG);
    pinCFG.pin = PIN_6;  PINSEL_ConfigPin(&pinCFG);

    pinCFG.port = PORT_0;
    pinCFG.pin  = PIN_4;  PINSEL_ConfigPin(&pinCFG);
    pinCFG.pin  = PIN_5;  PINSEL_ConfigPin(&pinCFG);

    pinCFG.port = PORT_2;
    pinCFG.pin  = PIN_12; PINSEL_ConfigPin(&pinCFG);

    LPC_GPIO2->FIODIR |= SEG_MASK | DIG2_BIT;
    LPC_GPIO0->FIODIR |= DIG0_BIT | DIG1_BIT;

    LPC_GPIO2->FIOCLR  = SEG_MASK | DIG2_BIT;
    LPC_GPIO0->FIOCLR  = DIG0_BIT | DIG1_BIT;
}

void configADC(void)  // adc0.0 en 0.23 burst mode a 8000hz
{
    ADC_Init(ADC_RATE);
    ADC_ChannelEnable(ADC_CHANNEL_0);
    ADC_BurstEnable();
    ADC_IntEnable(ADC_INT_CH0);
    ADC_StartCmd(ADC_START_CONTINUOUS);
}

void configEINT0(void)
{
    EXTI_CFG_T exti;

    exti.line     = EXTI_EINT0;
    exti.mode     = EXTI_EDGE_SENSITIVE;
    exti.polarity = EXTI_RISING_EDGE;

    EXTI_Init();
    EXTI_Config(&exti);
}

void configNVIC(void)
{
    EXTI_ClearFlag(EXTI_EINT0);
    NVIC_ClearPendingIRQ(EINT0_IRQn);
    NVIC_EnableIRQ(EINT0_IRQn);
}

void configUART(void)
{
    UART_CFG_T UARTConfigStruct;

    UARTConfigStruct.baudRate = 115200;
    UARTConfigStruct.dataBits = UART_DBITS_8;
    UARTConfigStruct.stopBits = UART_STOPBIT_1;
    UARTConfigStruct.parity   = UART_PARITY_NONE;

    UART_Init(LPC_UART2, &UARTConfigStruct);

    LPC_UART2->FCR = UART_FCR_FIFO_EN
                   | UART_FCR_RX_RS
                   | UART_FCR_TX_RS
                   | UART_FCR_TRG_LEV0;

    LPC_UART2->TER = UART_TER_TXEN;
    LPC_UART2->IER = 0;
}


void SysTick_Handler(void)
{
    static uint8_t digit = 0;

    LPC_GPIO0->FIOCLR = DIG0_BIT | DIG1_BIT;
    LPC_GPIO2->FIOCLR = DIG2_BIT;

    LPC_GPIO2->FIOCLR = SEG_MASK;
    LPC_GPIO2->FIOSET = SEG_MSG[digit] & SEG_MASK;

    switch (digit)
    {
        case 0: LPC_GPIO0->FIOSET = DIG0_BIT; break;
        case 1: LPC_GPIO0->FIOSET = DIG1_BIT; break;
        case 2: LPC_GPIO2->FIOSET = DIG2_BIT; break;
    }

    digit = (digit + 1) % 3;
}

void ADC_IRQHandler(void)
{
    if (RECORDING)
    {
        if (samples_count < LISTSIZE)
        {
            LPC_GPIO3->FIOCLR = (1 << 26);

            listADC[samples_count] = (uint16_t)((LPC_ADC->ADDR0 >> 4) & 0x0FFF);
            samples_count++;
        }

        if (samples_count >= LISTSIZE)
        {
            LPC_GPIO0->FIOSET = (1 << 22);
            LPC_GPIO3->FIOSET = (1 << 25) | (1 << 26);

            RECORDING = 0;
            FINISHED  = 1;

            seg_show(MSG_OFF);

            NVIC_DisableIRQ(ADC_IRQn);
        }
    }

    (void)LPC_ADC->ADGDR;
}

void EINT0_IRQHandler(void)
{
    EXTI_ClearFlag(EXTI_EINT0);
    NVIC_ClearPendingIRQ(EINT0_IRQn);

    buttonDebounce();

    RECORDING     = 0;
    FINISHED      = 0;
    samples_count = 0;
    cleanListADC();

    RECORDING = 1;
    seg_show(MSG_REC);

    NVIC_EnableIRQ(ADC_IRQn);
}

void sendSamplesUART(void)
{
    uint8_t buf[2];

    for (uint32_t i = 0; i < LISTSIZE; i++)
    {
        uint16_t sample = (listADC[i] >> 6) & 0x03FF;

        buf[0] = (uint8_t)((sample >> 8) & 0x03);  // ver p q sirve
        buf[1] = (uint8_t)( sample & 0xFF);

        UART_Send(LPC_UART2, buf, 2, BLOCKING);
    }

    samples_count = 0;
    NVIC_EnableIRQ(ADC_IRQn);
}