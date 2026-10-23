#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private SPI write regions only; never execute on a host or device.
#endif

/* Original [0x168DE,0x16994). C supplies selector masks, constants and
 * volatile MMIO stores. Explicit architecture ports retain then-live SP/S0/S1,
 * saved-slot order, opaque-call residues and loop controls. These fallthrough
 * regions are not ordinary C-callable functions. No physical pin, controller,
 * board, successful transfer or OTA compatibility is inferred here. */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define FRAME ENTRY __attribute__((naked, used, aligned(2)))
#define REGS \
    register uint32_t a0 __asm__("a0"); \
    register uint32_t a1 __asm__("a1"); \
    register uint32_t a2 __asm__("a2"); \
    register uint32_t a3 __asm__("a3"); \
    register uint32_t a4 __asm__("a4"); \
    register uint32_t a5 __asm__("a5"); \
    __asm__ volatile("" : "=r"(a0), "=r"(a1), "=r"(a2), "=r"(a3), "=r"(a4), "=r"(a5) : : "memory")
#define LIVE __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) : : "memory")
#define CALL(label, target) \
    __asm__ volatile(label ":\n.option push\n.option norvc\njal ra, " label "\n.option pop\n" \
                     ".reloc .-4, R_RISCV_JAL, " target "\n" \
                     : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) : : "memory")

FRAME void tsl9_tagged_external_168de(void)
{
    __asm__ volatile("addi sp, sp, -32\nsw s0, 24(sp)\nsw s1, 20(sp)\nsw ra, 28(sp)\n");
}

REGION void tsl9_spi_write_guard1_168e6(void)
{
    REGS;
    a5 = a0 & 1u; LIVE;
    __asm__ volatile("mv s0, a2\nmv s1, a3\n" : : "r"(a2), "r"(a3) : "memory");
    __asm__ volatile(".Lwrite_skip1:\nc.beqz a5, .Lwrite_skip1\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_spi_write_guard2_168fa\n"
                     : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_spi_write_select1_168f0(void)
{
    REGS;
    a5 = 0x40011000; LIVE;
    a4 = 16; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 - 2028u) = a4;
    LIVE;
    __builtin_unreachable();
}

REGION void tsl9_spi_write_guard2_168fa(void)
{
    REGS;
    a0 &= 2u; LIVE;
    __asm__ volatile(".Lwrite_skip2:\nc.beqz a0, .Lwrite_skip2\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_spi_write_command_16908\n"
                     : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_spi_write_select2_168fe(void)
{
    REGS;
    a5 = 0x40011000; LIVE;
    a4 = 1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 - 2028u) = a4;
    LIVE;
    __builtin_unreachable();
}

REGION void tsl9_spi_write_command_16908(void)
{
    REGS;
    a0 = 2; LIVE;
    __asm__ volatile("sw a1, 12(sp)\n" : : "r"(a1) : "memory");
    CALL(".Lwrite_command", "tsl9_spi_transfer_entry_16896");
    __builtin_unreachable();
}

REGION void tsl9_spi_write_address_16910(void)
{
    REGS;
    __asm__ volatile("lw a1, 12(sp)\nadd s1, s1, s0\n" : "=r"(a1) : : "memory");
    a0 = a1; LIVE;
    CALL(".Lwrite_address", "tsl9_spi_transfer_entry_16896");
    __builtin_unreachable();
}

REGION void tsl9_spi_write_test_1691a(void)
{
    REGS;
    __asm__ volatile(".Lwrite_more:\nbne s0, s1, .Lwrite_more\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_spi_write_payload_16932\n"
                     : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_spi_write_finish_1691e(void)
{
    REGS;
    __asm__ volatile("lw ra, 28(sp)\nlw s0, 24(sp)\n" : : : "memory");
    a5 = 0x40011000; LIVE;
    a4 = 17; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 - 2032u) = a4;
    LIVE;
    __asm__ volatile("lw s1, 20(sp)\naddi sp, sp, 32\nret\n" : : "r"(a0) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_spi_write_payload_16932(void)
{
    REGS;
    __asm__ volatile("lbu a0, 0(s0)\naddi s0, s0, 1\n" : "=r"(a0) : : "memory");
    CALL(".Lwrite_payload", "tsl9_spi_transfer_entry_16896");
    __asm__ volatile(".Lwrite_repeat:\nc.j .Lwrite_repeat\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_spi_write_test_1691a\n"
                     : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_tagged_external_1693e(void)
{
    __asm__ volatile("addi sp, sp, -32\nsw ra, 28(sp)\n");
}

REGION void tsl9_spi_modify_guard1_16942(void)
{
    REGS;
    a5 = a0 & 1u; LIVE;
    __asm__ volatile(".Lmodify_skip1:\nc.beqz a5, .Lmodify_skip1\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_spi_modify_guard2_16952\n"
                     : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_select1_16948(void)
{
    REGS;
    a5 = 0x40011000; LIVE;
    a4 = 16; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 - 2028u) = a4;
    LIVE;
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_guard2_16952(void)
{
    REGS;
    a0 &= 2u; LIVE;
    __asm__ volatile(".Lmodify_skip2:\nc.beqz a0, .Lmodify_skip2\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_spi_modify_command_16960\n"
                     : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_select2_16956(void)
{
    REGS;
    a5 = 0x40011000; LIVE;
    a4 = 1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 - 2028u) = a4;
    LIVE;
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_command_16960(void)
{
    REGS;
    a0 = 5; LIVE;
    __asm__ volatile("sw a3, 12(sp)\nsw a2, 8(sp)\nsw a1, 4(sp)\n" : : "r"(a1), "r"(a2), "r"(a3) : "memory");
    CALL(".Lmodify_command", "tsl9_spi_transfer_entry_16896");
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_address_1696c(void)
{
    REGS;
    __asm__ volatile("lw a1, 4(sp)\n" : "=r"(a1) : : "memory");
    a0 = a1; LIVE;
    CALL(".Lmodify_address", "tsl9_spi_transfer_entry_16896");
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_mask_16974(void)
{
    REGS;
    __asm__ volatile("lw a2, 8(sp)\n" : "=r"(a2) : : "memory");
    a0 = a2; LIVE;
    CALL(".Lmodify_mask", "tsl9_spi_transfer_entry_16896");
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_value_1697c(void)
{
    REGS;
    __asm__ volatile("lw a3, 12(sp)\n" : "=r"(a3) : : "memory");
    a0 = a3; LIVE;
    CALL(".Lmodify_value", "tsl9_spi_transfer_entry_16896");
    __builtin_unreachable();
}

REGION void tsl9_spi_modify_finish_16984(void)
{
    REGS;
    __asm__ volatile("lw ra, 28(sp)\n" : : : "memory");
    a5 = 0x40011000; LIVE;
    a4 = 17; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 - 2032u) = a4;
    LIVE;
    __asm__ volatile("addi sp, sp, 32\nret\n" : : "r"(a0) : "memory");
    __builtin_unreachable();
}
