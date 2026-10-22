OUTPUT_ARCH(riscv)
ENTRY(tsl9_adc_config_1892e)
PHDRS
{
    caller PT_LOAD FLAGS(5);
    adc PT_LOAD FLAGS(5);
}
SECTIONS
{
    .caller 0x19896 : { KEEP(*(.text.tsl9_adc_call_site)) } :caller
    .adc 0x1B000 : { KEEP(*(.text.tsl9_adc_config_1892e)) } :adc
    /DISCARD/ : { *(.comment) }
}
