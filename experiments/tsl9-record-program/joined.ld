OUTPUT_ARCH(riscv)
SECTIONS {
  .program_graph : ALIGN(2) {
    KEEP(*(.full_plus_leaf))
    KEEP(*(.text.tsl9_program_arm_93aa))
    KEEP(*(.text.tsl9_program_arm_body_93c0))
    KEEP(*(.text.tsl9_program_arm_return_93ec))
    KEEP(*(.text.tsl9_program_disarm_93ee))
    KEEP(*(.text.tsl9_program_allocate_9410))
    KEEP(*(.text.tsl9_program_old_pointer_941e))
    KEEP(*(.text.tsl9_program_free_9424))
    KEEP(*(.text.tsl9_program_cleanup_942c))
    KEEP(*(.text.tsl9_program_allocate_tail_943e))
    KEEP(*(.text.tsl9_queue_external_9454))
    KEEP(*(.text.tsl9_program_small_9464))
    KEEP(*(.text.tsl9_program_prepare_9472))
    KEEP(*(.text.tsl9_program_test_948e))
    KEEP(*(.text.tsl9_program_finish_9492))
    KEEP(*(.text.tsl9_program_restore_tail_949e))
    KEEP(*(.text.tsl9_program_fill_94a8))
    KEEP(*(.text.tsl9_program_large_94be))
    KEEP(*(.text.tsl9_program_special_94cc))
    KEEP(*(.text.tsl9_program_failure_94e4))
  }
  /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
  ASSERT(SIZEOF(.program_graph) == 2250, "Genuine1926 plus324 bytes")
  ASSERT(tsl9_program_arm_93aa == 1926, "New original code begins after parent")
}
