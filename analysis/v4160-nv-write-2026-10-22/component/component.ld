OUTPUT_ARCH(riscv)
ENTRY(tsl9_nv_write_callback_197be)
PHDRS { code PT_LOAD FLAGS(5); }
SECTIONS {
  .text 0 : { *(.text.*) } :code
  /DISCARD/ : { *(.comment) }
}
