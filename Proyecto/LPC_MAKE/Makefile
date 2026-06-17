# Rutas al compilador y herramientas. 
# Si usas MCUXpresso en Windows y no están en el PATH, reemplaza por la ruta completa.
# Ejemplo: CC = C:/nxp/MCUXpressoIDE.../tools/bin/arm-none-eabi-gcc
CC = C:/PROGRA~2/ARMGNU~1/14EFD8~1.2RE/bin/arm-none-eabi-gcc.exe
OBJCOPY = C:/PROGRA~2/ARMGNU~1/14EFD8~1.2RE/bin/arm-none-eabi-objcopy.exe
CHECKSUM = powershell.exe -ExecutionPolicy Bypass -File lpc_checksum.ps1
LINKSERVER = C:/nxp/LinkServer_26.5.59/LinkServer.exe

# Directorios relativos a este Makefile (en LPC_MAKE/)
PROJ_ROOT = ..
LIB_DIR = $(PROJ_ROOT)/Librerias
DRIVERS_DIR = $(LIB_DIR)/Drivers
CMSIS_DIR = $(LIB_DIR)/CMSIS
SRC_DIR = $(PROJ_ROOT)/src

# Archivo fuente por defecto
SRC ?= $(SRC_DIR)/main.c

# --- Configuración de Drivers y CMSIS ---
INCLUDES = -I$(DRIVERS_DIR)/inc -I$(CMSIS_DIR) -I$(SRC_DIR)
DRIVER_SRC = $(wildcard $(DRIVERS_DIR)/src/*.c)
CMSIS_SRC = $(CMSIS_DIR)/startup.c $(CMSIS_DIR)/system_LPC17xx.c $(CMSIS_DIR)/core_cm3.c
# --------------------------------

CFLAGS = -mcpu=cortex-m3 -mthumb -O0 -g3 -fmessage-length=0 -fno-builtin -ffunction-sections -fdata-sections -fno-common $(INCLUDES)
LDFLAGS = -T $(PROJ_ROOT)/LPC_MAKE/LPC1769.ld -nostartfiles -Wl,--gc-sections

all: main.axf main.bin

main.axf: $(SRC) $(CMSIS_SRC) $(DRIVER_SRC)
	$(CC) $(CFLAGS) $(LDFLAGS) $^ -o main.axf

main.bin: main.axf
	$(OBJCOPY) -O binary --pad-to 0x1000 main.axf main.bin
	$(CHECKSUM) main.bin

clean:
	rm -f main.axf main.bin

flash: all
	@echo "Cargando código ($(SRC)) al LPC1769..."
	$(LINKSERVER) flash LPC1769 load main.bin:0x00000000
