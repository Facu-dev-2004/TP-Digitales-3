# Sistema de Efectos de Audio
## Descripción General
El proyecto consiste en el diseño e implementación de un modificador de voz utilizando el microcontrolador LPC1769. El sistema será capaz de capturar una señal de voz analógica mediante un micrófono, digitalizarla, almacenarla temporalmente en la memoria interna y aplicarle distintos filtros o efectos digitales (eco, distorsión tipo radio, pitch shift). Finalmente, la señal procesada será transmitida hacia una computadora vía UART para su reproducción. Toda la interfaz de usuario será gestionada a través de una pantalla LCD y un teclado matricial.

## Objetivos Funcionales
* **Interfaz de Usuario:** Un menú interactivo mostrado en una pantalla LCD que indique el estado del sistema ("Esperando", "Grabando...", "Procesando").
* **Selección de Efectos:** Mediante un teclado matricial (dividido en grupos categóricos A, B, C, D), el usuario podrá elegir entre múltiples efectos pre-programados.
* **Adquisición de Datos:** Grabación de un fragmento de voz de duración predefinida utilizando el módulo ADC, activada por un pulsador.
* **Procesamiento de Audio:** Aplicación de algoritmos matemáticos sobre el arreglo de datos en memoria para alterar las características de la voz.
* **Transmisión (Salida):** Envío de los datos procesados hacia una PC mediante el protocolo UART para ser escuchados a través de los altavoces de la computadora (mediante un script de recepción).

## Hardware y Perifericos a Utilizar
* **Módulo ADC + Timer + GPDMA:** Para capturar el audio a una frecuencia de muestreo exacta (ej. 8 kHz) y guardarlo en la memoria SRAM sin bloquear la CPU.
* **Circuito Acondicionador de Audio:** Un preamplificador analógico para adaptar la débil señal del micrófono a los niveles de tensión leíbles por el ADC (0 a 3.3V).
* **GPIO y Teclado Matricial 4x4:** Para la navegación por los menús de efectos.
* **Pantalla LCD (I2C o GPIO):** Para la visualización de la interfaz.
* **Módulo UART:** Para enviar la ráfaga de datos modificados a la computadora.
