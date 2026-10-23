OUTPUT_ARCH(riscv)
ENTRY(tsl9_candidate_copy_arch_20000332)
SECTIONS {
  .copy 0x20000332 : ALIGN(2) {
    KEEP(*(.text.tsl9_candidate_copy_arch_20000332))
    KEEP(*(.text.tsl9_candidate_copy_source_guard_20000344))
    KEEP(*(.text.tsl9_candidate_copy_count_20000346))
    KEEP(*(.text.tsl9_candidate_copy_restore_2000034a))
    KEEP(*(.text.tsl9_candidate_copy_loop_20000354))
    KEEP(*(.text.tsl9_candidate_copy_finish_2000036a))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.copy) == 58, "SDK candidate58B only")
}
