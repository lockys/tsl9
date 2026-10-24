#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Private offline RV32 regions only; not a HOST model or firmware image.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define FRAME ENTRY __attribute__((used,naked,aligned(2)))
#define KEEP(x) __asm__ volatile("" : "+r"(x) : : "memory")
#define INPUT(x) __asm__ volatile("" : "=r"(x) : : "memory")
#define BRANCH(op,left,right,target) \
    __asm__ volatile(".Lscheduler_branch%=:\n" #op " " #left ", " #right ", .Lscheduler_branch%=\n" \
                     ".reloc .-4, R_RISCV_BRANCH, " #target "\n" : : : "memory")
#define CBRANCH(op,reg,target) \
    __asm__ volatile(".Lscheduler_short%=:\n" #op " " #reg ", .Lscheduler_short%=\n" \
                     ".reloc .-2, R_RISCV_RVC_BRANCH, " #target "\n" : : : "memory")
#define CJUMP(target) \
    __asm__ volatile(".Lscheduler_jump%=:\nc.j .Lscheduler_jump%=\n" \
                     ".reloc .-2, R_RISCV_RVC_JUMP, " #target "\n" : : : "memory")

/* Whole [9124,9250), including occupied/full scans, resident calls and tails.
 * C owns free-bank arithmetic, masks, constants, GP loads and ordinary memory.
 * Physical frames, reserved live S-register operations, PC and control are
 * explicit architectural ports. Regions are not ordinary C ABI functions.
 * No callback/resident preservation, bounds, memory validity or IRQ exclusion
 * is assumed. Native bytes, not C-level universal semantics, are the claim.
 */

FRAME void tsl9_callback_external_9124(void)
{
    __asm__ volatile("addi sp, sp, -32\nsw s2, 16(sp)\nsw ra, 28(sp)\n"
                     "sw s0, 24(sp)\nsw s1, 20(sp)\nsw s3, 12(sp)\nsw s4, 8(sp)\n"
                     "auipc s2, 0x20003\naddi s2, s2, -810\n");
}
REGION void tsl9_scheduler_913a(void)
{
    CBRANCH(c.bnez,a2,tsl9_scheduler_9188);
    __builtin_unreachable();
}
FRAME void tsl9_scheduler_913c(void)
{
    __asm__ volatile("mv a5, s2\n");
}
REGION void tsl9_scheduler_913e(void)
{
    register uint32_t a4 __asm__("a4")=0; KEEP(a4);
    register uint32_t a6 __asm__("a6")=15; KEEP(a6);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_9142(void)
{
    register uintptr_t a5 __asm__("a5"); INPUT(a5);
    register uint32_t a7 __asm__("a7")=*(volatile uint32_t *)(a5+4u); KEEP(a7);
    BRANCH(bne,a7,zero,tsl9_scheduler_9180);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_914a(void)
{
    register uint32_t a5 __asm__("a5")=12; KEEP(a5);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    a5=a4*a5; KEEP(a5);
    __builtin_unreachable();
}
FRAME void tsl9_scheduler_9150(void)
{
    __asm__ volatile("lw s0, 24(sp)\n");
}
REGION void tsl9_scheduler_9152(void)
{
    register uint32_t a1 __asm__("a1")=1; KEEP(a1);
    __asm__ volatile("lw ra, 28(sp)\nlw s1, 20(sp)\nlw s3, 12(sp)\nlw s4, 8(sp)"
                     : : "r"(a1) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_scheduler_915c(void)
{
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    /* RISC-V SLL masks the count; plain C << a4 would be undefined >=32. */
    a1<<=(a4&31u); KEEP(a1);
    a1<<=16; KEEP(a1);
    a1>>=16; KEEP(a1);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_9164(void)
{
    register uintptr_t a5 __asm__("a5"); INPUT(a5);
    __asm__ volatile("add a5, a5, s2" : "+r"(a5) : : "memory");
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    *(volatile uint32_t *)(a5+4u)=a0;
    *(volatile uint8_t *)a5=0;
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    *(volatile uint32_t *)(a5+8u)=a3;
    __builtin_unreachable();
}
REGION void tsl9_scheduler_916e(void)
{
    register uintptr_t a5 __asm__("a5")=0x40000u; KEEP(a5);
    __asm__ volatile("lw s2, 16(sp)" : : "r"(a5) : "memory");
    register uintptr_t t1 __asm__("t1")=*(volatile uint32_t *)(a5+80u); KEEP(t1);
    register uintptr_t gp __asm__("gp"); INPUT(gp);
    register uint32_t a0 __asm__("a0")=*(volatile uint8_t *)(gp+166u); KEEP(a0);
    __asm__ volatile("addi sp, sp, 32\njr t1" : : "r"(t1),"r"(a0) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_scheduler_9180(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    ++a4; KEEP(a4);
    register uintptr_t a5 __asm__("a5"); INPUT(a5);
    a5+=12u; KEEP(a5);
    BRANCH(bne,a4,a6,tsl9_scheduler_9142);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_9188(void)
{
    register uintptr_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x20003\naddi a5, a5, -896" : "=r"(a5) : : "memory");
    __asm__ volatile("mv s4, a3\nmv s3, a2\nmv s0, a1" : : "r"(a5) : "memory");
    register uintptr_t a4 __asm__("a4")=a5; KEEP(a4);
    __asm__ volatile("li s1, 0" : : "r"(a4) : "memory");
    register uint32_t a3 __asm__("a3")=15; KEEP(a3);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_919c(void)
{
    register uintptr_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a2 __asm__("a2")=*(volatile uint32_t *)(a4+4u); KEEP(a2);
    BRANCH(bne,a2,a0,tsl9_scheduler_91fe);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_91a2(void)
{
    register uintptr_t a5 __asm__("a5")=12; KEEP(a5);
    __asm__ volatile("mul a5, s1, a5\nadd a5, a5, s2" : "+r"(a5) : : "memory");
    register uint32_t a0 __asm__("a0")=*(volatile uint32_t *)(a5+8u); KEEP(a0);
    CBRANCH(c.beqz,a0,tsl9_scheduler_91b6);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_91ae(void)
{
    register uintptr_t a5 __asm__("a5")=0x40000u; KEEP(a5);
    a5=*(volatile uint32_t *)(a5+104u); KEEP(a5);
    __asm__ volatile("jalr a5" : : "r"(a5) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_scheduler_91b6(void)
{
    register uint32_t a5 __asm__("a5")=12; KEEP(a5);
    __asm__ volatile("mul a5, s1, a5" : "+r"(a5) : : "memory");
    register uint32_t a1 __asm__("a1")=1; KEEP(a1);
    register uintptr_t gp __asm__("gp"); INPUT(gp);
    register uint32_t a0 __asm__("a0")=*(volatile uint8_t *)(gp+166u); KEEP(a0);
    __asm__ volatile("sll a1, a1, s1\nadd a5, a5, s2\nsb s0, 0(a5)\nsw s4, 8(a5)"
                     : "+r"(a1),"+r"(a5) : "r"(a0) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_scheduler_91d0(void)
{
    register uint32_t a5 __asm__("a5")=1000; KEEP(a5);
    register uint32_t a2 __asm__("a2");
    __asm__ volatile("mul a2, s3, a5" : "=r"(a2) : "r"(a5) : "memory");
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    a1<<=16; KEEP(a1);
    a5=625; KEEP(a5);
    a1>>=16; KEEP(a1);
    a2/=a5; KEEP(a2);
    a5=0x40000u; KEEP(a5);
    CBRANCH(c.beqz,s0,tsl9_scheduler_922c);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_91ea(void)
{
    __asm__ volatile("lw s0, 24(sp)\nlw ra, 28(sp)\nlw s1, 20(sp)\n"
                     "lw s2, 16(sp)\nlw s3, 12(sp)\nlw s4, 8(sp)" : : : "memory");
    register uintptr_t a5 __asm__("a5"); INPUT(a5);
    register uintptr_t t1 __asm__("t1")=*(volatile uint32_t *)(a5+556u); KEEP(t1);
    __asm__ volatile("addi sp, sp, 32\njr t1" : : "r"(t1) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_scheduler_91fe(void)
{
    __asm__ volatile("addi s1, s1, 1" : : : "memory");
    register uintptr_t a4 __asm__("a4"); INPUT(a4);
    a4+=12u; KEEP(a4);
    BRANCH(bne,s1,a3,tsl9_scheduler_919c);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_9206(void)
{
    register uint32_t a4 __asm__("a4")=0; KEEP(a4);
    register uint32_t a3 __asm__("a3")=15; KEEP(a3);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_920a(void)
{
    register uintptr_t a5 __asm__("a5"); INPUT(a5);
    register uint32_t a2 __asm__("a2")=*(volatile uint32_t *)(a5+4u); KEEP(a2);
    CBRANCH(c.bnez,a2,tsl9_scheduler_9244);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_920e(void)
{
    register uint32_t a5 __asm__("a5")=12; KEEP(a5);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    a5=a4*a5; KEEP(a5);
    register uint32_t a1 __asm__("a1")=1; KEEP(a1);
    a1<<=(a4&31u); KEEP(a1);
    __asm__ volatile("add a5, a5, s2" : "+r"(a5) : "r"(a1) : "memory");
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    *(volatile uint32_t *)(uintptr_t)(a5+4u)=a0;
    __asm__ volatile("sb s0, 0(a5)\nsw s4, 8(a5)" : : "r"(a5) : "memory");
    register uintptr_t gp __asm__("gp"); INPUT(gp);
    a0=*(volatile uint8_t *)(gp+166u); KEEP(a0);
    CJUMP(tsl9_scheduler_91d0);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_922c(void)
{
    register uintptr_t a5 __asm__("a5"); INPUT(a5);
    a5=*(volatile uint32_t *)(a5+88u); KEEP(a5);
    __asm__ volatile("jalr a5" : : "r"(a5) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_scheduler_9230(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0=(a0==0u); KEEP(a0);
    __builtin_unreachable();
}
FRAME void tsl9_scheduler_9234(void)
{
    __asm__ volatile("lw ra, 28(sp)\nlw s0, 24(sp)\nlw s1, 20(sp)\n"
                     "lw s2, 16(sp)\nlw s3, 12(sp)\nlw s4, 8(sp)\naddi sp, sp, 32\nret\n");
}
REGION void tsl9_scheduler_9244(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    ++a4; KEEP(a4);
    register uintptr_t a5 __asm__("a5"); INPUT(a5);
    a5+=12u; KEEP(a5);
    BRANCH(bne,a4,a3,tsl9_scheduler_920a);
    __builtin_unreachable();
}
REGION void tsl9_scheduler_924c(void)
{
    register uint32_t a0 __asm__("a0")=1; KEEP(a0);
    CJUMP(tsl9_scheduler_9234);
    __builtin_unreachable();
}
