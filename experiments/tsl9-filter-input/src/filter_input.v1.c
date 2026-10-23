#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 architecture only. Never execute this component on a host or device.
#endif

/* Complete [0x128FE,0x1299E). C owns free-bank constants, provider pointer
 * reads and unsigned shifts. Frame, physical S-register, SP-relative memory,
 * call and branch ports retain their original architectural dependencies.
 * Each post-call region reads then-live SP/S registers, not saved C locals.
 * Neither resident slot acquires an ordinary ABI or memcpy/memset contract.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define FRAME ENTRY __attribute__((naked,used,aligned(2)))
#define PORT(x) __asm__ volatile("" : "+r"(x) : : "memory")

REGION void tsl9_filter_input_128fe(void)
{
    register uint32_t a5 __asm__("a5")=UINT32_C(0x40000); PORT(a5);
    a5=*(volatile uint32_t *)(uintptr_t)(a5+72u); PORT(a5);
    __builtin_unreachable();
}

FRAME void tsl9_filter_input_frame_12904(void)
{
    __asm__ volatile("addi sp, sp, -176\nsw s0, 168(sp)\nsw s1, 164(sp)\n");
}

REGION void tsl9_filter_input_fill_1290a(void)
{
    register uint32_t a2 __asm__("a2")=112; PORT(a2);
    __asm__ volatile("sw ra, 172(sp)\nsw s2, 160(sp)\nsw s3, 156(sp)\n"
                     "sw s4, 152(sp)\nmv s1, a0\nmv s0, a1\naddi a0, sp, 32\n"
                     : : "r"(a2) : "a0","memory");
    register uint32_t a1 __asm__("a1")=0; PORT(a1);
    __asm__ volatile("jalr a5" : : "r"(a1) : "a0","a2","a3","a4","a5","memory");
    __builtin_unreachable();
}

REGION void tsl9_filter_input_cap_12920(void)
{
    register uint32_t a5 __asm__("a5")=112; PORT(a5);
    register uint32_t a2 __asm__("a2")=112; PORT(a2);
    __asm__ volatile(".Linput_large%=:\nbltu a5, s0, .Linput_large%=\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_filter_input_copy_12930"
                     : : "r"(a5),"r"(a2) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_filter_input_small_1292c(void)
{
    /* The source is the then-live reserved S0, including resident changes. */
    __asm__ volatile("andi a2, s0, 255" : : : "a2","memory");
    __builtin_unreachable();
}

REGION void tsl9_filter_input_copy_12930(void)
{
    register uint32_t a5 __asm__("a5")=UINT32_C(0x40000); PORT(a5);
    a5=*(volatile uint32_t *)(uintptr_t)(a5+76u); PORT(a5);
    __asm__ volatile("mv a1, s1\naddi a0, sp, 32\njalr a5\n"
                     : : "r"(a5) : "a0","a1","a2","a3","a4","memory");
    __builtin_unreachable();
}

FRAME void tsl9_filter_input_loop_init_1293c(void)
{
    __asm__ volatile("addi s0, sp, 32\nli s1, 0\nli s4, 1\nli s3, 1\nli s2, 14\n");
}

REGION void tsl9_filter_input_loop_12946(void)
{
    register uint32_t a2 __asm__("a2"); register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4"); register uint32_t a5 __asm__("a5");
    __asm__ volatile("lhu a2, 0(s0)\nlhu a3, 2(s0)\nlhu a4, 4(s0)\nlhu a5, 6(s0)\n"
                     "sw zero, 20(sp)\nsb s1, 22(sp)\naddi s1, s1, 1\n"
                     : "=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5) : : "memory");
    a2<<=5; PORT(a2); a3<<=5; PORT(a3); a4<<=5; PORT(a4); a5<<=5; PORT(a5);
    __asm__ volatile("addi a0, sp, 12\nandi s1, s1, 255\nsw zero, 24(sp)\n"
                     "sb s4, 23(sp)\nsh a2, 12(sp)\nsh a3, 14(sp)\nsh a4, 16(sp)\n"
                     "sh a5, 18(sp)\nsw s3, 28(sp)\naddi s0, s0, 8\n"
                     : : "r"(a2),"r"(a3),"r"(a4),"r"(a5) : "a0","memory");
    __asm__ volatile("jal ra, tsl9_filter_program_18ba2"
                     : : : "a0","a1","a2","a3","a4","a5","memory");
    __builtin_unreachable();
}

REGION void tsl9_filter_input_next_1298a(void)
{
    __asm__ volatile(".Linput_more%=:\nbne s1, s2, .Linput_more%=\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_filter_input_loop_12946" : : : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_filter_input_finish_1298e(void)
{
    __asm__ volatile("lw ra, 172(sp)\nlw s0, 168(sp)\nlw s1, 164(sp)\n"
                     "lw s2, 160(sp)\nlw s3, 156(sp)\nlw s4, 152(sp)\n"
                     "addi sp, sp, 176\nret\n");
}
