#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private queue regions only; never execute on the host.
#endif

/* Original [0x12C58,0x12D92), including cold blocks after RET.
 * Private architectural regions, not ordinary C ABI functions. C owns
 * zero-extension, constants, fresh indirect byte read and mask operations.
 * Reserved S-register/SP/CSR state, calls and control edges are explicit
 * ports. Opaque calls may change S0..S7/SP; subsequent ports read then-live
 * physical registers. Resident identity and complete firmware stay unknown.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define FRAME ENTRY __attribute__((naked, used, aligned(2)))
#define CALL(site, target) \
    __asm__ volatile("jal ra, " #target "\n" \
                     : : : "a0", "a1", "a2", "a3", "a4", "a5", "memory")

FRAME void tsl9_queue_entry_12c58(void)
{
    __asm__ volatile("addi sp, sp, -80\nsw s1, 68(sp)\nsw s2, 64(sp)\n"
                     "sw s3, 60(sp)\nsw s4, 56(sp)\nsw s5, 52(sp)\n"
                     "sw s6, 48(sp)\nsw s7, 44(sp)\nsw ra, 76(sp)\n"
                     "sw s0, 72(sp)\nli s1, 0\n"
                     /* PC=0x12C6E; nominal placement must prove this base. */
                     "auipc s5, 0x1fff9\naddi s5, s5, 970\n"
                     "li s6, 12\nli s2, 136\nlui s3, 0x40\n"
                     "li s4, 1\naddi s7, gp, 84\n");
}

REGION void tsl9_queue_scan_12c86(void)
{
    register uint32_t value __asm__("a5");
    __asm__ volatile("mul s0, s1, s6\nadd s0, s0, s5\nlhu a5, 0(s0)\n"
                     : "=r"(value) : : "memory");
    __asm__ volatile("" : "+r"(value) : : "memory");
    value <<= 16;
    __asm__ volatile("" : "+r"(value) : : "memory");
    value >>= 16;
    __asm__ volatile(".Lqempty:\nc.beqz a5, .Lqempty\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(value) : "memory");
    __asm__ volatile("csrc 0x800, s2\nlw a5, 76(s3)\n"
                     : "=r"(value) : : "memory");
    register uint32_t length __asm__("a2") = 12;
    __asm__ volatile("" : "+r"(length) : "r"(value) : "memory");
    __asm__ volatile("mv a1, s0\naddi a0, sp, 8\njalr a5\n"
                     : : "r"(length), "r"(value)
                     : "a0", "a1", "a3", "a4", "memory");
    __builtin_unreachable();
}

REGION void tsl9_queue_release_12ca6(void)
{
    __asm__ volatile("sh zero, 0(s0)\ncsrs 0x800, s2\naddi a0, sp, 8\n"
                     : : : "a0", "memory");
    CALL(12cb0, tsl9_queue_external_82d2);
    __builtin_unreachable();
}

REGION void tsl9_queue_validate_12cb4(void)
{
    register uint32_t result __asm__("a0");
    register uint32_t value __asm__("a5");
    register uint32_t byte __asm__("a4");
    __asm__ volatile("" : "=r"(result) : : "memory");
    __asm__ volatile(".Lqhandled:\nc.bnez a0, .Lqhandled\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(result) : "memory");
    __asm__ volatile("lhu a5, 8(sp)\n" : "=r"(value) : : "memory");
    __asm__ volatile(".Lqother:\nbne a5, s4, .Lqother\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_other_12d78\n"
                     : : "r"(value) : "memory");
    __asm__ volatile("lbu a4, 10(sp)\n" : "=r"(byte) : : "memory");
    value = 4;
    __asm__ volatile(".Lqlength:\nbne a4, a5, .Lqlength\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(byte), "r"(value) : "memory");
    __asm__ volatile("lbu a4, 11(sp)\n" : "=r"(byte) : : "memory");
    value = 181;
    __asm__ volatile(".Lqmarker1:\nbne a4, a5, .Lqmarker1\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(byte), "r"(value) : "memory");
    __asm__ volatile("lbu a4, 12(sp)\n" : "=r"(byte) : : "memory");
    value = 98;
    __asm__ volatile(".Lqmarker2:\nbne a4, a5, .Lqmarker2\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(byte), "r"(value) : "memory");
    __asm__ volatile("lbu a5, 13(sp)\n" : "=r"(value) : : "memory");
    __asm__ volatile(".Lqzero:\nc.beqz a5, .Lqzero\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_zero_12d0e\n"
                     : : "r"(value) : "memory");
    byte = 90;
    __asm__ volatile(".Lqresponse:\nbeq a5, a4, .Lqresponse\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_response_12d4c\n"
                     : : "r"(value), "r"(byte) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_queue_advance_12cee(void)
{
    __asm__ volatile("addi s1, s1, 1\n" : : : "memory");
    register uint32_t count __asm__("a5") = 32;
    __asm__ volatile(".Lqnext:\nbne s1, a5, .Lqnext\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_scan_12c86\n"
                     : : "r"(count) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_queue_finish_12cf8(void)
{
    __asm__ volatile("lw ra, 76(sp)\nlw s0, 72(sp)\nlw s1, 68(sp)\n"
                     "lw s2, 64(sp)\nlw s3, 60(sp)\nlw s4, 56(sp)\n"
                     "lw s5, 52(sp)\nlw s6, 48(sp)\nlw s7, 44(sp)\n"
                     "addi sp, sp, 80\nret\n");
}

REGION void tsl9_queue_zero_12d0e(void)
{
    CALL(12d0e, tsl9_queue_external_820c);
    register uint32_t argument __asm__("a0");
    __asm__ volatile("lbu a0, 14(sp)\n" : "=r"(argument) : : "memory");
    __asm__ volatile("" : : "r"(argument) : "memory");
    CALL(12d16, tsl9_queue_external_9454);
    argument = 0;
    __asm__ volatile("" : "+r"(argument) : : "memory");
    CALL(12d1c, tsl9_queue_external_9b36);
    __asm__ volatile("lbu a0, 19(sp)\n" : "=r"(argument) : : "memory");
    register uint32_t length __asm__("a2") = 2;
    __asm__ volatile("" : "+r"(length) : "r"(argument) : "memory");
    __asm__ volatile("addi a1, sp, 20\nsh zero, 20(sp)\n"
                     : : "r"(argument), "r"(length) : "a1", "memory");
    CALL(12d2c, tsl9_queue_external_12abe);
    register uint32_t selector __asm__("a4");
    __asm__ volatile("lbu a4, 19(sp)\nsh s4, 20(sp)\n"
                     : "=r"(selector) : : "memory");
    register uint32_t compare __asm__("a5") = 2;
    __asm__ volatile("" : "+r"(compare) : "r"(selector) : "memory");
    argument = 1;
    __asm__ volatile(".Lqselector:\nbeq a4, a5, .Lqselector\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_emit_12d42\n"
                     : : "r"(selector), "r"(compare), "r"(argument) : "memory");
    argument = 2;
    __asm__ volatile("" : : "r"(argument), "r"(selector), "r"(compare) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_queue_emit_12d42(void)
{
    register uint32_t length __asm__("a2") = 2;
    __asm__ volatile("" : "+r"(length) : : "memory");
    __asm__ volatile("addi a1, sp, 20\n" : : "r"(length) : "a1", "memory");
    CALL(12d46, tsl9_queue_external_12abe);
    __asm__ volatile(".Lqemitted:\nc.j .Lqemitted\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_queue_advance_12cee\n"
                     : : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_queue_response_12d4c(void)
{
    register uint32_t byte __asm__("a4");
    register uint32_t value __asm__("a5");
    __asm__ volatile("lbu a4, 14(sp)\n" : "=r"(byte) : : "memory");
    value = 85;
    __asm__ volatile(".Lqresponse_reject:\nbne a4, a5, .Lqresponse_reject\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(byte), "r"(value) : "memory");
    __asm__ volatile("lw a5, 76(s3)\naddi a0, sp, 20\n"
                     : "=r"(value) : : "a0", "memory");
    register uint32_t length __asm__("a2") = 12;
    __asm__ volatile("" : "+r"(length) : "r"(value) : "memory");
    __asm__ volatile("addi a1, sp, 8\njalr a5\n"
                     : : "r"(length), "r"(value)
                     : "a0", "a1", "a3", "a4", "memory");
    value = 86;
    __asm__ volatile("" : "+r"(value) : : "memory");
    __asm__ volatile("addi a0, sp, 20\nsb a5, 26(sp)\nsb zero, 31(sp)\n"
                     : : "r"(value) : "a0", "memory");
    CALL(12d72, tsl9_queue_external_12a08);
    __asm__ volatile(".Lqresponded:\nc.j .Lqresponded\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_queue_advance_12cee\n"
                     : : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_queue_other_12d78(void)
{
    register uintptr_t value __asm__("a5");
    __asm__ volatile("lw a5, 0(s7)\n" : "=r"(value) : : "memory");
    value = *(volatile uint8_t *)(value + 4u);
    value &= 8u;
    __asm__ volatile(".Lqother_gated:\nc.bnez a5, .Lqother_gated\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(value) : "memory");
    CALL(12d84, tsl9_queue_external_81aa);
    register uint32_t result __asm__("a0");
    __asm__ volatile("" : "=r"(result) : : "memory");
    __asm__ volatile(".Lqother_disabled:\nc.beqz a0, .Lqother_disabled\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\n"
                     : : "r"(result) : "memory");
    __asm__ volatile("addi a0, sp, 8\n" : : : "a0", "memory");
    CALL(12d8c, tsl9_queue_external_14d2e);
    __asm__ volatile(".Lqother_done:\nc.j .Lqother_done\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_queue_advance_12cee\n"
                     : : : "memory");
    __builtin_unreachable();
}
