
MEMORY
{
  FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 512K
  SRAM (rwx) : ORIGIN = 0x10000000, LENGTH = 32K
}

SECTIONS
{
  .text :
  {
    KEEP(*(.vectors))
    *(.text*)
    *(.rodata*)
    _etext = .;
  } > FLASH

  .data : AT (_etext)
  {
    _data = .;
    *(.data*)
    _edata = .;
  } > SRAM

  .bss :
  {
    _bss = .;
    *(.bss*)
    *(COMMON)
    _ebss = .;
  } > SRAM

  _stack_top = ORIGIN(SRAM) + LENGTH(SRAM);
}
