#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 architectural regions only. Never execute on a HOST or device.
#endif

/* Original [0x93AA,0x94EE). C owns constants, record writes, index arithmetic,
 * volatile memory operations and bit operations. Explicit ports preserve
 * physical frame/register/control state and PC-relative addresses. These
 * regions are not independent ordinary C ABI functions. No installed ROM,
 * peripheral purpose, interrupt safety or memory ownership is asserted.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define FRAME ENTRY __attribute__((naked, used, aligned(2)))
#define PORT(x) __asm__ volatile("" : "+r"(x) : : "memory")
#define CJAL(label, target) __asm__ volatile(label ":\nc.jal " label "\n.reloc .-2, R_RISCV_RVC_JUMP, " #target : : : "a0", "a1", "a2", "a3", "a4", "a5", "memory")
#define CJ(label, target) __asm__ volatile(label ":\nc.j " label "\n.reloc .-2, R_RISCV_RVC_JUMP, " #target : : : "memory")

REGION void tsl9_program_arm_93aa(void)
{
    register uint32_t gp __asm__("gp");
    __asm__ volatile("" : "=r"(gp) : : "memory");
    register uint32_t a5 __asm__("a5") = gp + 84u;
    PORT(a5);
    a5 = *(volatile uint32_t *)(uintptr_t)a5;
    PORT(a5);
    register uint32_t a4 __asm__("a4") = *(volatile uint8_t *)(uintptr_t)(a5 + 2u);
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5) : "r"(a4) : "memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 - 1268u);
    PORT(a5);
    a5 |= a4;
    PORT(a5);
    __asm__ volatile(".Larm_skip:\nc.beqz a5, .Larm_skip\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_program_arm_return_93ec" : : "r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_program_arm_body_93c0(void)
{
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5) : : "memory");
    *(volatile uint8_t *)(uintptr_t)(a5 - 1278u) = 0;
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5) : : "memory");
    *(volatile uint8_t *)(uintptr_t)(a5 - 1287u) = 0;
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5) : : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 - 1300u) = 0;
    a5 = UINT32_C(0x40000000);
    PORT(a5);
    *(volatile uint16_t *)(uintptr_t)(a5 + 1060u) = 0;
    register uint32_t a4 __asm__("a4") = *(volatile uint16_t *)(uintptr_t)(a5 + 1024u);
    PORT(a4);
    a4 |= 1u;
    PORT(a4);
    *(volatile uint16_t *)(uintptr_t)(a5 + 1024u) = (uint16_t)a4;
    __builtin_unreachable();
}

FRAME void tsl9_program_arm_return_93ec(void)
{
    __asm__ volatile("ret");
}

REGION void tsl9_program_disarm_93ee(void)
{
    register uint32_t a4 __asm__("a4") = UINT32_C(0x40000000);
    PORT(a4);
    register uint32_t a3 __asm__("a3") = UINT32_MAX;
    PORT(a3);
    *(volatile uint16_t *)(uintptr_t)(a4 + 1068u) = (uint16_t)a3;
    *(volatile uint16_t *)(uintptr_t)(a4 + 1084u) = 0;
    register uint32_t a5 __asm__("a5") = *(volatile uint16_t *)(uintptr_t)(a4 + 1024u);
    PORT(a5);
    a5 <<= 16; PORT(a5);
    a5 >>= 16; PORT(a5);
    a5 &= UINT32_C(0xFFFFFFFE); PORT(a5);
    a5 <<= 16; PORT(a5);
    a5 >>= 16; PORT(a5);
    *(volatile uint16_t *)(uintptr_t)(a4 + 1024u) = (uint16_t)a5;
    __asm__ volatile("ret" : : : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_program_allocate_9410(void)
{
    __asm__ volatile("addi sp, sp, -16\nauipc a5, 0x20003\naddi a5, a5, -1366\nsw s0, 8(sp)\nmv s0, a0");
}

REGION void tsl9_program_old_pointer_941e(void)
{
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("" : "=r"(a5) : : "memory");
    register uint32_t a0 __asm__("a0") = *(volatile uint32_t *)(uintptr_t)(a5 + 16u);
    __asm__ volatile("sw ra, 12(sp)\n.Lprogram_no_old:\nc.beqz a0, .Lprogram_no_old\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_program_allocate_tail_943e" : : "r"(a0) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_program_free_9424(void)
{
    register uint32_t a5 __asm__("a5") = UINT32_C(0x40000);
    PORT(a5);
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + 104u);
    PORT(a5);
    __asm__ volatile("jalr a5" : : "r"(a5) : "a0", "a1", "a2", "a3", "a4", "memory");
    __builtin_unreachable();
}

REGION void tsl9_program_cleanup_942c(void)
{
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5) : : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 - 1376u) = 0;
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5) : : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 - 1388u) = 0;
    CJAL(".Lprogram_disarm", tsl9_program_disarm_93ee);
    __builtin_unreachable();
}

REGION void tsl9_program_allocate_tail_943e(void)
{
    register uint32_t a0 __asm__("a0") = 6;
    PORT(a0);
    __asm__ volatile("mul a0, s0, a0" : "+r"(a0) : : "memory");
    register uint32_t a5 __asm__("a5") = UINT32_C(0x40000);
    PORT(a5);
    __asm__ volatile("lw s0, 8(sp)\nlw ra, 12(sp)\nlw t1, 112(a5)\naddi sp, sp, 16\njr t1" : : "r"(a0), "r"(a5) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_queue_external_9454(void)
{
    __asm__ volatile("addi sp, sp, -16\nsw s0, 8(sp)\nsw ra, 12(sp)\nsw s1, 4(sp)\nli a5, 19\nmv s0, a0\n.Lprogram_large:\nbltu a5, a0, .Lprogram_large\n.reloc .-4, R_RISCV_BRANCH, tsl9_program_large_94be");
}

REGION void tsl9_program_small_9464(void)
{
    register uint32_t a0 __asm__("a0");
    __asm__ volatile("andi s1, a0, 255\naddi a0, s1, 1" : "=r"(a0) : : "memory");
    a0 &= 255u;
    PORT(a0);
    CJAL(".Lprogram_allocate_small", tsl9_program_allocate_9410);
    __builtin_unreachable();
}

REGION void tsl9_program_prepare_9472(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5), "=r"(a0) : : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 - 1446u) = a0;
    __asm__ volatile(".Lprogram_small_failed:\nc.beqz a0, .Lprogram_small_failed\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_program_failure_94e4" : : "r"(a0) : "memory");
    register uint32_t a3 __asm__("a3") = 4096;
    PORT(a3);
    register uint32_t a4 __asm__("a4") = a0;
    PORT(a4);
    a5 = 0;
    PORT(a5);
    a3 -= 1096u;
    PORT(a3);
    register uint32_t a2 __asm__("a2") = 40;
    PORT(a2);
    register uint32_t a1 __asm__("a1") = 80;
    PORT(a1);
    __builtin_unreachable();
}

REGION void tsl9_program_test_948e(void)
{
    __asm__ volatile(".Lprogram_more:\nbne s1, a5, .Lprogram_more\n.reloc .-4, R_RISCV_BRANCH, tsl9_program_fill_94a8" : : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_program_finish_9492(void)
{
    register uint32_t a5 __asm__("a5") = 6;
    PORT(a5);
    __asm__ volatile("mul s0, s0, a5\nadd s0, s0, a0\nsh zero, 0(s0)" : : "r"(a5) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_program_restore_tail_949e(void)
{
    __asm__ volatile("lw s0, 8(sp)\nlw ra, 12(sp)\nlw s1, 4(sp)\naddi sp, sp, 16\n.Lprogram_arm:\nc.j .Lprogram_arm\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_program_arm_93aa");
}

REGION void tsl9_program_fill_94a8(void)
{
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2");
    register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("" : "=r"(a1), "=r"(a2), "=r"(a3), "=r"(a4), "=r"(a5) : : "memory");
    a5 += 1u; PORT(a5);
    *(volatile uint16_t *)(uintptr_t)a4 = (uint16_t)a3;
    *(volatile uint16_t *)(uintptr_t)(a4 + 2u) = (uint16_t)a2;
    *(volatile uint16_t *)(uintptr_t)(a4 + 4u) = (uint16_t)a1;
    a5 &= 255u; PORT(a5);
    a4 += 6u; PORT(a4);
    CJ(".Lprogram_next", tsl9_program_test_948e);
    __builtin_unreachable();
}

REGION void tsl9_program_large_94be(void)
{
    register uint32_t a0 __asm__("a0") = 2;
    PORT(a0);
    CJAL(".Lprogram_allocate_large", tsl9_program_allocate_9410);
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x20003" : "=r"(a5), "=r"(a0) : : "memory");
    *(volatile uint32_t *)(uintptr_t)(a5 - 1526u) = a0;
    __asm__ volatile(".Lprogram_large_failed:\nc.beqz a0, .Lprogram_large_failed\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_program_failure_94e4" : : "r"(a0) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_program_special_94cc(void)
{
    register uint32_t a5 __asm__("a5") = 4096;
    PORT(a5);
    a5 -= 1096u; PORT(a5);
    register uint32_t a0 __asm__("a0");
    __asm__ volatile("" : "=r"(a0) : : "memory");
    *(volatile uint16_t *)(uintptr_t)a0 = (uint16_t)a5;
    __asm__ volatile("sh s0, 2(a0)" : : "r"(a0) : "memory");
    *(volatile uint16_t *)(uintptr_t)(a0 + 4u) = 0;
    *(volatile uint16_t *)(uintptr_t)(a0 + 6u) = 0;
    CJ(".Lprogram_special_done", tsl9_program_restore_tail_949e);
    __builtin_unreachable();
}

FRAME void tsl9_program_failure_94e4(void)
{
    __asm__ volatile("lw ra, 12(sp)\nlw s0, 8(sp)\nlw s1, 4(sp)\naddi sp, sp, 16\nret");
}
