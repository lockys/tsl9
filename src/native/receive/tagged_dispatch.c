#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 architectural regions only; never execute on a host or device.
#endif

/* Original [0x16B7C,0x16C72). C owns scalar arithmetic/constants and the
 * fresh resident-pointer load. Architectural ports retain original stack,
 * saved-register, memory and control ordering. These are private fallthrough
 * regions, not ordinary C-callable functions. Opaque calls may change SP/S0-S3;
 * every following port observes then-live registers. No memset, CAN-chip,
 * board identity, successful transmission or OTA compatibility is implied.
 */
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

REGION void tsl9_dispatch_external_16b7c(void)
{
    REGS;
    __asm__ volatile("lbu a5, 11(a0)\n" : "=r"(a5) : "r"(a0) : "memory");
    a4 = 1; LIVE;
    a5 -= 1; LIVE;
    a5 &= 255; LIVE;
    __asm__ volatile(".Ltag_invalid:\nbltu a4, a5, .Ltag_invalid\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_tagged_invalid_16c6c\n"
                     : : "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_tagged_config_16b8c(void)
{
    REGS;
    __asm__ volatile("addi a5, gp, 84\n" : "=r"(a5) : : "memory");
    a5 = *(volatile uint32_t *)(uintptr_t)a5; LIVE;
    __asm__ volatile("lbu a4, 4(a5)\n" : "=r"(a4) : "r"(a5) : "memory");
    a5 = 4; LIVE;
    a4 &= 8; LIVE;
    __asm__ volatile(".Ltag_config_blocked:\nc.bnez a4, .Ltag_config_blocked\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_tagged_early_16c6e\n"
                     : : "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_tagged_frame_16b9c(void)
{
    __asm__ volatile("addi sp, sp, -64\nsw ra, 60(sp)\nsw s0, 56(sp)\n"
                     "sw s1, 52(sp)\nsw s2, 48(sp)\nsw s3, 44(sp)\n");
}

REGION void tsl9_tagged_length_16ba8(void)
{
    REGS;
    __asm__ volatile("lbu s1, 2(a0)\n" : : "r"(a0) : "memory");
    a4 = 8; LIVE;
    __asm__ volatile(".Ltag_length_reject:\nbltu a4, s1, .Ltag_length_reject\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_tagged_finish_16c52\n"
                     : : "r"(a4), "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_tagged_header_16bb2(void)
{
    REGS;
    a5 = 0x4030; LIVE;
    __asm__ volatile("mv s0, a0\nsh a5, 12(sp)\n" : : "r"(a0), "r"(a5) : "memory");
    a2 = 11; LIVE;
    a5 = 80; LIVE;
    a1 = 0; LIVE;
    __asm__ volatile("addi a0, sp, 18\nsb a5, 14(sp)\n" : "+r"(a0) : "r"(a5) : "memory");
    CALL(".Ltag_prepare_call", "tsl9_tagged_external_8520");
    __builtin_unreachable();
}

REGION void tsl9_tagged_payload_16bd2(void)
{
    REGS;
    __asm__ volatile("lhu a5, 0(s0)\nsb s1, 20(sp)\nmv a2, s1\n"
                     : "=r"(a5), "=r"(a2) : : "memory");
    a4 = a5 >> 3; LIVE;
    a5 <<= 5; LIVE;
    __asm__ volatile("sb a5, 17(sp)\nsb a4, 16(sp)\n" : : "r"(a5), "r"(a4) : "memory");
    a5 = 0x40000; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 76); LIVE;
    __asm__ volatile("addi a1, s0, 3\naddi a0, sp, 21\njalr a5\n"
                     : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3), "+r"(a4), "+r"(a5) : : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_tagged_loop_setup_16bfa(void)
{
    __asm__ volatile("li s1, 0\nli s3, 3\n");
}

REGION void tsl9_tagged_loop_16bfe(void)
{
    REGS;
    __asm__ volatile("addi a5, sp, 12\nadd a5, a5, s1\nlbu s2, 0(a5)\n"
                     "lbu a0, 11(s0)\nmv a1, s2\n"
                     : "=r"(a5), "=r"(a0), "=r"(a1) : : "memory");
    CALL(".Ltag_busy_read", "tsl9_register_read_entry_16994");
    a0 &= 8; LIVE;
    __asm__ volatile(".Ltag_busy_branch:\nc.bnez a0, .Ltag_busy_branch\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_tagged_busy_16c62\n"
                     : : "r"(a0) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_tagged_send_16c14(void)
{
    REGS;
    __asm__ volatile("lbu a3, 2(s0)\nlbu a0, 11(s0)\naddi a1, s2, 1\n"
                     : "=r"(a3), "=r"(a0), "=r"(a1) : : "memory");
    a3 += 5; LIVE;
    a3 &= 255; LIVE;
    __asm__ volatile("addi a2, sp, 16\n" : "=r"(a2) : : "memory");
    a1 &= 255; LIVE;
    CALL(".Ltag_send_call", "tsl9_tagged_external_168de");
    __builtin_unreachable();
}

REGION void tsl9_tagged_request_16c30(void)
{
    REGS;
    __asm__ volatile("lbu a0, 11(s0)\n" : "=r"(a0) : : "memory");
    a3 = 8; LIVE;
    a2 = 8; LIVE;
    __asm__ volatile("mv a1, s2\n" : "=r"(a1) : : "memory");
    CALL(".Ltag_request_call", "tsl9_tagged_external_1693e");
    __builtin_unreachable();
}

REGION void tsl9_tagged_status_16c3e(void)
{
    REGS;
    __asm__ volatile("lbu a0, 11(s0)\nmv a1, s2\n" : "=r"(a0), "=r"(a1) : : "memory");
    CALL(".Ltag_status_read", "tsl9_register_read_entry_16994");
    a0 &= 112; LIVE;
    a5 = a0 != 0; LIVE;
    a5 <<= 2; LIVE;
    __builtin_unreachable();
}

FRAME void tsl9_tagged_finish_16c52(void)
{
    __asm__ volatile("lw ra, 60(sp)\nlw s0, 56(sp)\nlw s1, 52(sp)\n"
                     "lw s2, 48(sp)\nlw s3, 44(sp)\nmv a0, a5\naddi sp, sp, 64\nret\n");
}

REGION void tsl9_tagged_busy_16c62(void)
{
    REGS;
    __asm__ volatile("addi s1, s1, 1\n.Ltag_try_next:\nbne s1, s3, .Ltag_try_next\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_tagged_loop_16bfe\n" : : : "memory");
    a5 = 4; LIVE;
    __asm__ volatile(".Ltag_all_busy:\nc.j .Ltag_all_busy\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_tagged_finish_16c52\n" : : "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_tagged_invalid_16c6c(void)
{
    REGS;
    a5 = 4; LIVE;
    __builtin_unreachable();
}

FRAME void tsl9_tagged_early_16c6e(void)
{
    __asm__ volatile("mv a0, a5\nret\n");
}
