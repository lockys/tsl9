/* Diagnostic nominal placement, NOT a complete application memory map. */
ENTRY(tsl9_runtime_reset_entry)
SECTIONS
{
    .reset 0x186aa : {
        *(.text.tsl9_runtime_reset_entry)
        *(.text.tsl9_runtime_reset_memory)
    }
    .clock 0x1874a : {
        *(.text.tsl9_clock_prefix_entry)
        *(.text.tsl9_clock_prefix_body)
        *(.text.tsl9_clock_prefix_return)
    }
    .initializer 0x1ab60 : { *(.rodata.tsl9_reset_initializer) }
    .ram 0x20004000 (NOLOAD) : { *(.bss.tsl9_reset_ram) }
    .stack 0x2000fff0 (NOLOAD) : {
        *(.bss.tsl9_reset_stack)
        tsl9_runtime_reset_stack_top = .;
    }
    ASSERT(SIZEOF(.reset) == 138, "reset/control/call PC changed")
    ASSERT(tsl9_runtime_reset_memory == 0x186be, "C memory entry moved")
    ASSERT(SIZEOF(.clock) == 240, "reviewed clock size changed")
    ASSERT(SIZEOF(.initializer) == 128, "initializer size changed")
    ASSERT(SIZEOF(.ram) == 35160, "RAM bounds changed")
    ASSERT(SIZEOF(.stack) == 16, "stack frame storage changed")
}
