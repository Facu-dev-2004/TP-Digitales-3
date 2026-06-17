# Sistema de Efectos de Audio

## Descripción General
El proyecto consiste en el diseño e implementación de un grabador y modificador de voz utilizando el microcontrolador LPC1769. El sistema captura una señal de voz analógica mediante un micrófono **MAX9814**, la digitaliza con el módulo ADC, la almacena temporalmente en la memoria SRAM interna y la transmite vía **UART** hacia una computadora. Allí, un script en **Python** se encarga de reproducir el audio y aplicarle distintos efectos de sonido. El estado del sistema (en espera o grabando) se indica mediante **3 displays de 7 segmentos**.

## Funcionamiento

* **Indicación de Estado:** 3 displays de 7 segmentos, multiplexados por software (refrescados desde el handler de `SysTick`), muestran `OFF` cuando el sistema está inactivo y `REC` mientras se está grabando.
* **Inicio de Grabación:** Un pulsador conectado a la entrada de interrupción externa **EINT0** (configurada por flanco ascendente) dispara el inicio de la grabación. Al presionarlo se reinicia el buffer de muestras, se activa la bandera `RECORDING` y se habilita la interrupción del ADC.
* **Adquisición de Datos:** El módulo ADC se configura en modo *burst* a una frecuencia de muestreo de **8 kHz**, generando una interrupción por cada muestra convertida (`ADC_IRQHandler`). Cada muestra de 12 bits se guarda en un arreglo en SRAM (`listADC`) hasta completar **12000 muestras** (~1.5 segundos de audio).
* **Fin de Grabación:** Al completarse el buffer, se desactiva la interrupción del ADC, se actualiza el display a `OFF` y se levanta la bandera `FINISHED`, que el `main()` detecta en su loop principal para iniciar el envío de datos.
* **Transmisión (Salida):** Las muestras capturadas (recortadas de 12 a 10 bits para mejor calidad de audio) se envían por **UART2** a 115200 baudios, en paquetes de 2 bytes por muestra, hacia la PC.


## Hardware y Periféricos Utilizados

* **Micrófono MAX9814:** Módulo con amplificador de ganancia automática (AGC) que adapta la señal de audio captada a niveles compatibles con el ADC (0 a 3.3V). Su salida analógica se conecta al pin **P0.23 (AD0.0)**.
* **Módulo ADC:** Configurado en modo *burst continuo* a 8 kHz, con interrupción habilitada en el canal 0, para digitalizar la señal del micrófono sin intervención de DMA.
* **Pulsador + EINT0:** Botón físico conectado a la entrada de interrupción externa 0, utilizado para iniciar manualmente cada grabación.
* **3 Displays de 7 Segmentos:** Multiplexados mediante GPIO y refrescados periódicamente por interrupción de SysTick, muestran el mensaje `OFF` (en espera) o `REC` (grabando).
* **Módulo UART (UART2):** Configurado a 115200 baudios, 8 bits de datos, sin paridad y 1 bit de parada, utilizado para enviar la ráfaga de muestras capturadas hacia la PC.
* **Script de Recepción en Python:** Corriendo en la computadora, recibe los datos por el puerto serie, los reconstruye, aplica los efectos de audio seleccionados y reproduce el resultado por los parlantes.

## Parámetros de Captura
  * **DURACION:** LISTSIZE / ADC_RATE = 12000 / 8000 = 1.5 segundos
| Parámetro | Valor |
|---|---|
| Frecuencia de muestreo | 8 kHz |
| Resolución de captura (ADC) | 12 bits |
| Resolución transmitida (UART) | 10 bits |
| Cantidad de muestras por grabación | 12000 |
| Duración aproximada de grabación | ~1.5 s |
| Baud rate UART | 115200 |
