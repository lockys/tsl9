/* R70 ET_REL assertion plan; does not serialize final VMA/LMA. */
INCLUDE layout/known-runtime-layout.ld
SECTIONS {
 .tsl9_runtime_initializer 0x1A7E0 : { KEEP(*(.rodata.tsl9_init_image)) }
 .tsl9_runtime_ram 0x20004000 (NOLOAD) : { KEEP(*(.bss.tsl9_runtime_ram)) }
}
ASSERT(ADDR(.tsl9_runtime_initializer) == 0x1A7E0, "initializer plan");
ASSERT(SIZEOF(.tsl9_runtime_initializer) == 136, "initializer exact size");
ASSERT(ADDR(.tsl9_runtime_ram) == 0x20004000, "RAM plan");
ASSERT(SIZEOF(.tsl9_runtime_ram) == 35152, "RAM exact size");
