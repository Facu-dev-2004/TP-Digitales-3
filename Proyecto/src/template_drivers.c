/**
 * @file template_drivers.c
 * @brief Plantilla genérica con los Includes y funciones base para el LPC1769.
 * 
 * Este archivo sirve como referencia para saber qué librerías incluir y cómo
 * inicializar los periféricos más comunes.
 */

/* --- Includes Básicos del Sistema --- */
#include "LPC17xx.h"
#include "lpc17xx_libcfg.h" // Configuración de drivers (DEBE estar en src)

/* --- Includes de Drivers (Añadir según se necesiten) --- */
#include "lpc17xx_gpio.h"   // Para manejo de pines
#include "lpc17xx_pinsel.h" // Para configurar funciones de pines
#include "lpc17xx_timer.h"  // Para temporizadores
#include "lpc17xx_uart.h"   // Para comunicación serie
#include "lpc17xx_adc.h"    // Para conversión analógica-digital
#include "lpc17xx_dac.h"    // Para salida analógica
#include "lpc17xx_systick.h"// Para el temporizador del sistema

/* --- Variables Globales --- */
extern uint32_t SystemCoreClock; // Reloj del sistema (necesario para cálculos)

/* --- Prototipos de Funciones de Ejemplo --- */
void setup_GPIO(void);
void setup_UART(void);
void setup_Timer(void);

/**
 * @brief Ejemplo de configuración de GPIO
 */
void setup_GPIO(void) {
    // Configurar P0.22 como salida (Led en la placa)
    GPIO_SetDir(0, (1 << 22), 1);
    
    // Encender Led
    GPIO_SetValue(0, (1 << 22));
}

/**
 * @brief Ejemplo de configuración de UART0 (115200 baudios)
 */
void setup_UART(void) {
    UART_CFG_Type UARTConfigStruct;
    UART_FIFO_CFG_Type UARTFIFOConfigStruct;
    PINSEL_CFG_Type PinCfg;

    // Configuración de pines P0.2 y P0.3 para UART0
    PinCfg.Funcnum = 1;
    PinCfg.OpenDrain = 0;
    PinCfg.Pinmode = 0;
    PinCfg.Pinnum = 2;
    PinCfg.Portnum = 0;
    PINSEL_ConfigPin(&PinCfg);
    PinCfg.Pinnum = 3;
    PINSEL_ConfigPin(&PinCfg);

    // Inicializar UART con valores por defecto
    UART_ConfigStructInit(&UARTConfigStruct);
    UART_Init(LPC_UART0, &UARTConfigStruct);

    // Inicializar FIFO
    UART_FIFOConfigStructInit(&UARTFIFOConfigStruct);
    UART_FIFOConfig(LPC_UART0, &UARTFIFOConfigStruct);

    // Habilitar transmisión
    UART_TxCmd(LPC_UART0, ENABLE);
}

/**
 * @brief Ejemplo de configuración de Timer0 (Match a 1 seg)
 */
void setup_Timer(void) {
    TIM_TIMERCFG_Type TIM_ConfigStruct;
    TIM_MATCHCFG_Type TIM_MatchConfigStruct;

    // Configuración inicial del Timer
    TIM_ConfigStruct.PrescaleOption = TIM_PRESCALE_USVAL;
    TIM_ConfigStruct.PrescaleValue = 100;
    TIM_Init(LPC_TIMER0, TIM_TIMER_MODE, &TIM_ConfigStruct);

    // Configuración del Match (1 segundo)
    TIM_MatchConfigStruct.MatchChannel = 0;
    TIM_MatchConfigStruct.IntOnMatch = ENABLE;
    TIM_MatchConfigStruct.ResetOnMatch = ENABLE;
    TIM_MatchConfigStruct.StopOnMatch = DISABLE;
    TIM_MatchConfigStruct.ExtMatchOutputType = TIM_EXTMATCH_NOTHING;
    TIM_MatchConfigStruct.MatchValue = 10000;
    TIM_ConfigMatch(LPC_TIMER0, &TIM_MatchConfigStruct);

    // Iniciar Timer
    TIM_Cmd(LPC_TIMER0, ENABLE);
}
