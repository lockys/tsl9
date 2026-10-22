/* Explicit non-executable page packaging, after the measured 568-byte body. */
.section .rodata.tsl9v4160.source_wiring_page_tail,"a",@progbits
.balign 1
.globl tsl9_source_wiring_page_tail
.type tsl9_source_wiring_page_tail,@object
tsl9_source_wiring_page_tail:
.fill 456,1,0xff
.size tsl9_source_wiring_page_tail,.-tsl9_source_wiring_page_tail
