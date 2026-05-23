#include "LPC17xx.h"
#include "lpc17xx_gpio.h"

extern uint32_t SystemCoreClock;

void configGPIO();
void configSysTick();

int main(void) {

  configGPIO();
  configSysTick();

  while (1) {
  }

  return 0;
}

void configGPIO() {
  // Led
  GPIO_SetDir(0, (1 << 22), 1);
}

void configSysTick() {
  // Calculo 10ms
  uint32_t tick10ms = (SystemCoreClock * 0.01);

  // Verificacion
  if (SysTick_Config(tick10ms)) {
    while (1)
      ;
  }
}

void SysTick_Handler() {
  static int contador10ms = 0;
  contador10ms++;

  if (contador10ms >= 50) {
    LPC_GPIO0->FIOPIN ^= (1 << 0);

    // Reinicio el contador
    contador10ms = 0;
  }
}