OUTPUT_ARCH(riscv)
ENTRY(tsl9_dispatch_external_821e)
SECTIONS {
 .predicate 0x821E : ALIGN(2) { KEEP(*(.text.tsl9_dispatch_external_821e)) }
 /DISCARD/ : { *(.comment) *(.note*) *(.riscv.attributes) }
 ASSERT(SIZEOF(.predicate) == 42, "Original42-byte predicate only")
 ASSERT(tsl9_dispatch_external_821e == 0x821E, "Original predicate placement")
}
