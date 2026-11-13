OUTPUT_ARCH(riscv)
PHDRS { none PT_NULL; }
SECTIONS {
.bd5a 0xbd5a : { *setter.o(.leaf) } :none
.bd64 0xbd64 : { *getter.o(.leaf) } :none
.ram 0x20004000 (NOLOAD) : { KEEP(*(.bss.tsl9v4160.ram)) record_flag_bf13 = __tsl9v4160_ram + 0x7f13; } :none
/DISCARD/ : { *(.text) *(.riscv.attributes) }
}
