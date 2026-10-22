/* Diagnostic reset +232B clock placement; NOT a complete application memory map. */
ENTRY(tsl9_runtime_reset_entry)
SECTIONS
{
    .reset 0x186aa : {
        *(.text.tsl9_runtime_reset_entry)
        *(.text.tsl9_runtime_reset_memory)
    }
    .clock 0x1874a : {
        KEEP(*(.text.tsl9_clock_prefix_entry))
        KEEP(*(.text.tsl9_clock_prefix_body))
    }
    .initializer 0x1ab60 : { *(.rodata.tsl9_reset_initializer) }
    .ram 0x20004000 (NOLOAD) : { *(.bss.tsl9_reset_ram) }
    .stack 0x2000fff0 (NOLOAD) : {
        *(.bss.tsl9_reset_stack)
        tsl9_runtime_reset_stack_top = .;
    }
    ASSERT(SIZEOF(.reset) == 138, "reset/control/call PC changed")
    ASSERT(tsl9_runtime_reset_memory == 0x186be, "C memory entry moved")
    ASSERT(SIZEOF(.clock) == 232, "reviewed clock size changed")
    ASSERT(tsl9_clock_prefix_entry == 0x1874a, "clock entry moved")
    ASSERT(tsl9_clock_prefix_body == 0x18756, "fall-through adjacency lost")
    ASSERT(ADDR(.clock) + SIZEOF(.clock) <= 0x18834, "next-function overlap")
    ASSERT(SIZEOF(.initializer) == 128, "initializer size changed")
    ASSERT(SIZEOF(.ram) == 35160, "RAM bounds changed")
    ASSERT(SIZEOF(.stack) == 16, "stack frame storage changed")
}
