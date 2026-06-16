import os

with open("src/main.c", "r") as f:
    code = f.read()

replacements = [
    ("GPDMA_LLI_Type LLI_Array[NUM_LISTS];", "GPDMA_LLI_T LLI_Array[NUM_LISTS];"),
    ("GPDMA_Channel_CFG_Type dmaCFG;", "GPDMA_Channel_CFG_T dmaCFG;"),
    ("PINSEL_CFG_Type pinCFG;", "PINSEL_CFG_T pinCFG;"),
    ("pinCFG.Funcnum = PINSEL_FUNC_1; pinCFG.OpenDrain = PINSEL_PINMODE_NORMAL;", "pinCFG.func = PINSEL_FUNC_01; pinCFG.openDrain = DISABLE;"),
    ("pinCFG.Pinmode = PINSEL_PINMODE_TRISTATE; pinCFG.Pinnum = PINSEL_PIN_23; pinCFG.Portnum = PINSEL_PORT_0;", "pinCFG.mode = PINSEL_TRISTATE; pinCFG.pin = 23; pinCFG.port = 0;"),
    ("pinCFG.Pinnum = PINSEL_PIN_24;", "pinCFG.pin = 24;"),
    ("pinCFG.Funcnum = PINSEL_FUNC_1; pinCFG.Pinmode = PINSEL_PINMODE_PULLDOWN;", "pinCFG.func = PINSEL_FUNC_01; pinCFG.mode = PINSEL_PULLDOWN;"),
    ("pinCFG.Pinnum = PINSEL_PIN_10; pinCFG.Portnum = PINSEL_PORT_2;", "pinCFG.pin = 10; pinCFG.port = 2;"),
    ("pinCFG.Pinnum = PINSEL_PIN_11;", "pinCFG.pin = 11;"),
    ("pinCFG.Funcnum = PINSEL_FUNC_2; pinCFG.Pinmode = PINSEL_PINMODE_TRISTATE;", "pinCFG.func = PINSEL_FUNC_10; pinCFG.mode = PINSEL_TRISTATE;"),
    ("pinCFG.Pinnum = PINSEL_PIN_26; pinCFG.Portnum = PINSEL_PORT_0;", "pinCFG.pin = 26; pinCFG.port = 0;"),
    ("pinCFG.Funcnum = 1; pinCFG.OpenDrain = 0; pinCFG.Pinmode = 0;", "pinCFG.func = PINSEL_FUNC_01; pinCFG.openDrain = DISABLE; pinCFG.mode = PINSEL_PULLUP;"),
    ("pinCFG.Pinnum = 10; pinCFG.Portnum = 0;", "pinCFG.pin = 10; pinCFG.port = 0;"),
    ("ADC_Init(LPC_ADC, ADC_RATE);", "ADC_Init(ADC_RATE);"),
    ("ADC_ChannelCmd(LPC_ADC, 0, ENABLE);", "ADC_ChannelEnable(ADC_CHANNEL_0);"),
    ("ADC_ChannelCmd(LPC_ADC, 1, ENABLE);", "ADC_ChannelEnable(ADC_CHANNEL_1);"),
    ("ADC_BurstCmd(LPC_ADC, ENABLE);", "ADC_BurstEnable();"),
    ("ADC_IntConfig(LPC_ADC, ADC_ADINTEN0, ENABLE);", "ADC_IntEnable(ADC_INT_CH0);"),
    ("ADC_StartCmd(LPC_ADC, ADC_START_CONTINUOUS);", "ADC_StartCmd(ADC_START_CONTINUOUS);"),
    ("DAC_CONVERTER_CFG_Type dacCFG;", "DAC_CONVERTER_CFG_T dacCFG;\n    dacCFG.doubleBuffer = DISABLE;"),
    ("dacCFG.CNT_ENA = SET;", "dacCFG.dmaCounter = ENABLE;"),
    ("dacCFG.DMA_ENA = SET;", "dacCFG.dmaRequest = ENABLE;"),
    ("DAC_SetDMATimeOut(LPC_DAC, TIMEOUT);", "DAC_SetDMATimeOut(TIMEOUT);"),
    ("DAC_ConfigDAConverterControl(LPC_DAC, &dacCFG);", "DAC_ConfigDAConverterControl(&dacCFG);"),
    ("DAC_Init(LPC_DAC);", "DAC_Init();"),
    ("LLI_Array[i].DstAddr", "LLI_Array[i].dstAddr"),
    ("LLI_Array[i].SrcAddr", "LLI_Array[i].srcAddr"),
    ("LLI_Array[i].NextLLI", "LLI_Array[i].nextLLI"),
    ("LLI_Array[i].Control", "LLI_Array[i].control"),
    ("dmaCFG.ChannelNum = 0;", "dmaCFG.channelNum = GPDMA_CH_0;"),
    ("dmaCFG.TransferSize = 4095;", "dmaCFG.transferSize = 4095;"),
    ("dmaCFG.TransferWidth = 0;", "dmaCFG.src.width = GPDMA_HALFWORD; dmaCFG.dst.width = GPDMA_WORD; dmaCFG.src.burst = GPDMA_BSIZE_1; dmaCFG.dst.burst = GPDMA_BSIZE_1; dmaCFG.src.increment = ENABLE; dmaCFG.dst.increment = DISABLE; dmaCFG.intTC = DISABLE; dmaCFG.intErr = DISABLE;"),
    ("dmaCFG.TransferType = GPDMA_TRANSFERTYPE_M2P;", "dmaCFG.type = GPDMA_M2P;"),
    ("dmaCFG.SrcConn = 0;", "dmaCFG.srcConn = GPDMA_SSP0_Tx;"), 
    ("dmaCFG.DstConn = GPDMA_CONN_DAC;", "dmaCFG.dstConn = GPDMA_DAC;"),
    ("dmaCFG.SrcMemAddr", "dmaCFG.srcMemAddr"),
    ("dmaCFG.DstMemAddr", "dmaCFG.dstMemAddr"),
    ("dmaCFG.DMALLI = (uint32_t)&LLI_Array[0];", "dmaCFG.linkedList = (uint32_t)&LLI_Array[0];"),
    ("GPDMA_Setup(&dmaCFG);", "GPDMA_SetupChannel(&dmaCFG);"),
    ("GPDMA_ChannelCmd(0, ENABLE);", "GPDMA_ChannelStart(GPDMA_CH_0);"),
    ("EXTI_InitTypeDef exti;", "EXTI_CFG_T exti;"),
    ("exti.EXTI_Mode = EXTI_MODE_EDGE_SENSITIVE;", "exti.mode = EXTI_EDGE_SENSITIVE;"),
    ("exti.EXTI_polarity = EXTI_POLARITY_HIGH_ACTIVE_OR_RISING_EDGE;", "exti.polarity = EXTI_RISING_EDGE;"),
    ("exti.EXTI_Line = EXTI_EINT0;", "exti.line = EXTI_EINT0;"),
    ("exti.EXTI_Line = EXTI_EINT1;", "exti.line = EXTI_EINT1;"),
    ("EXTI_ClearEXTIFlag(EXTI_EINT0);", "EXTI_ClearFlag(EXTI_EINT0);"),
    ("GPDMA_ChannelCmd(0, DISABLE);", "GPDMA_ChannelStop(GPDMA_CH_0);"),
    ("UART_CFG_Type      UARTConfigStruct;", "UART_CFG_T      UARTConfigStruct;"),
    ("UART_FIFO_CFG_Type UARTFIFOConfigStruct;", "UART_FIFO_CFG_T UARTFIFOConfigStruct;"),
    ("UART_ConfigStructInit(&UARTConfigStruct); /* 9600-8N1 por defecto */", "UARTConfigStruct.baudRate = 9600; UARTConfigStruct.dataBits = UART_DBITS_8; UARTConfigStruct.stopBits = UART_STOPBIT_1; UARTConfigStruct.parity = UART_PARITY_NONE;"),
    ("UART_FIFOConfigStructInit(&UARTFIFOConfigStruct);", "UARTFIFOConfigStruct.resetRxBuf = ENABLE; UARTFIFOConfigStruct.resetTxBuf = ENABLE; UARTFIFOConfigStruct.dmaMode = DISABLE; UARTFIFOConfigStruct.level = UART_FIFO_TRGLEV0;"),
    ("UART_TxCmd(LPC_UART2, ENABLE);", "UART_TxEnable(LPC_UART2);"),
    ("UART_IntConfig(LPC_UART2, UART_INTCFG_RBR, DISABLE);", "UART_IntConfig(LPC_UART2, UART_INT_RBR, DISABLE);"),
    ("UART_IntConfig(LPC_UART2, UART_INTCFG_RLS, DISABLE);", "UART_IntConfig(LPC_UART2, UART_INT_RLS, DISABLE);"),
    ("DAC_SetDMATimeOut(LPC_DAC, ADCVALMAP);", "DAC_SetDMATimeOut(ADCVALMAP);"),
    ("EXTI_ClearEXTIFlag(EXTI_EINT1);", "EXTI_ClearFlag(EXTI_EINT1);"),
    ("DAC_UpdateValue(LPC_DAC, 0);", "DAC_UpdateValue(0);")
]

for old, new in replacements:
    code = code.replace(old, new)

with open("src/main.c", "w") as f:
    f.write(code)
