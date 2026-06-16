# --- DETECCIÓN DE SISTEMA OPERATIVO ---
ifeq ($(OS),Windows_NT)
    # --- CONFIGURACIÓN PARA WINDOWS (Tu compañero) ---
    # NOTA: Tu compañero debe cambiar estas rutas según su versión instalada de MCUXpresso IDE
    # Por ejemplo, si tiene la 11.9.0 o 25.6.0
    MCUX_DIR = C:/NXP/MCUXpressoIDE_11.9.0_1144
    
    # Rutas por defecto del compilador y herramientas en Windows
    CC = "$(MCUX_DIR)/ide/plugins/com.nxp.mcuxpresso.tools.win32_11.9.0.202311281216/tools/bin/arm-none-eabi-gcc.exe"
    OBJCOPY = "$(MCUX_DIR)/ide/plugins/com.nxp.mcuxpresso.tools.win32_11.9.0.202311281216/tools/bin/arm-none-eabi-objcopy.exe"
    CHECKSUM = "$(MCUX_DIR)/ide/plugins/com.nxp.mcuxpresso.tools.bin.win32_11.9.0.202311281216/binaries/checksum.exe"
    LINKSERVER = "C:/NXP/LinkServer_1.5.0/LinkServer.exe"
    
    RM = del /Q /F
else
    # --- CONFIGURACIÓN PARA LINUX (Tu computadora) ---
    CC = /opt/mcuxpresso-ide/ide/plugins/com.nxp.mcuxpresso.tools.linux_25.6.0.202501151204/tools/bin/arm-none-eabi-gcc
    OBJCOPY = /opt/mcuxpresso-ide/ide/plugins/com.nxp.mcuxpresso.tools.linux_25.6.0.202501151204/tools/bin/arm-none-eabi-objcopy
    CHECKSUM = /opt/mcuxpresso-ide/ide/plugins/com.nxp.mcuxpresso.tools.bin.linux_25.6.0.202501151204/binaries/checksum
    LINKSERVER = /opt/linkserver/LinkServer
    
    RM = rm -f
endif

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
	$(OBJCOPY) -O binary main.axf main.bin
	$(CHECKSUM) -p LPC1769 -v main.bin

clean:
	$(RM) main.axf main.bin

flash: all
	@echo "Cargando código ($(SRC)) al LPC1769..."
	$(LINKSERVER) flash LPC1769 load -e main.bin:0x00000000

