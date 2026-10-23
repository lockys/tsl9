#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Offline private RV32 regions only; not a HOST model or flashable firmware.
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
#define JUMP(target) __asm__ volatile(".option push\n.option norvc\nj " #target "\n.option pop" : : : "memory")
#define CALL(target) __asm__ volatile(".option push\n.option norvc\njal ra, " #target "\n.option pop" : : : "memory")
#define BRANCH(op,left,right,target) \
    __asm__ volatile(".Lcallback_branch%=:\n" #op " " #left ", " #right ", .Lcallback_branch%=\n" \
                     ".reloc .-4, R_RISCV_BRANCH, " #target "\n" : : : "memory")
#define CBRANCH(op,reg,target) \
    __asm__ volatile(".Lcallback_short%=:\n" #op " " #reg ", .Lcallback_short%=\n" \
                     ".reloc .-2, R_RISCV_RVC_BRANCH, " #target "\n" : : : "memory")
#define ADDRESS(reg,target) \
    __asm__ volatile(".Lcallback_address%=:\nauipc " #reg ", %%pcrel_hi(" #target ")\n" \
                     "addi " #reg ", " #reg ", %%pcrel_lo(.Lcallback_address%=)\n" \
                     : "=r"(reg) : : "memory")

/* Free-bank arithmetic, normal memory and GP data are C. Register/frame,
 * control and PC-relative effects are explicit architectural ports.
 * Region boundaries are original machine boundaries, not normal C ABI calls.
 * No assumption that a callback/resident preserves SP/S0/RA or memory.
 * Volatile loads retain separate observations; they do not prove validity,
 * atomicity, fault freedom, caller bounds, IRQ exclusion or hardware identity.
 */

REGION void tsl9_callback_guard_828c(void)
{
    register uintptr_t a0 __asm__("a0");
    __asm__ volatile("auipc a0, 0x20004" : "=r"(a0) : : "memory");
    a0=*(volatile uint8_t *)(a0-728u); KEEP(a0);
    a0=(a0<4u); KEEP(a0);
    a0^=1u; KEEP(a0);
    __asm__ volatile("ret" : : "r"(a0) : "memory");
    __builtin_unreachable();
}

/* Header sum then a length-delimited payload, omitting the selected index.
 * The first load is a 16-bit load, not two replacement byte loads. */
REGION void tsl9_callback_checksum_ed00(void)
{
    register uintptr_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4")=*(volatile uint16_t *)a0; KEEP(a4);
    register uint32_t a2 __asm__("a2")=*(volatile uint8_t *)(a0+2u); KEEP(a2);
    register uint32_t a5 __asm__("a5")=a4>>8; KEEP(a5);
    a5+=a4; KEEP(a5);
    a5&=255u; KEEP(a5);
    a4=0; KEEP(a4);
    __builtin_unreachable();
}
REGION void tsl9_callback_checksum_ed14(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a3 __asm__("a3")=a4&255u; KEEP(a3);
    BRANCH(bltu,a3,a2,tsl9_callback_checksum_ed20);
    __builtin_unreachable();
}
REGION void tsl9_callback_checksum_ed1c(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    register uint32_t a0 __asm__("a0")=a5; KEEP(a0);
    __asm__ volatile("ret" : : "r"(a0) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_callback_checksum_ed20(void)
{
    BRANCH(beq,a1,a3,tsl9_callback_checksum_ed32);
    __builtin_unreachable();
}
REGION void tsl9_callback_checksum_ed24(void)
{
    register uintptr_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    register uintptr_t a3 __asm__("a3")=a0+a4; KEEP(a3);
    a3=*(volatile uint8_t *)(a3+3u); KEEP(a3);
    a5+=a3; KEEP(a5);
    a5&=255u; KEEP(a5);
    __builtin_unreachable();
}
REGION void tsl9_callback_checksum_ed32(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    ++a4; KEEP(a4);
    __asm__ volatile(".Lcallback_loop%=:\nc.j .Lcallback_loop%=\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_callback_checksum_ed14\n"
                     : : "r"(a4) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_callback_predicate_1069e(void)
{
    __asm__ volatile("addi sp, sp, -16\n");
}
REGION void tsl9_callback_predicate_106a0(void)
{
    register uint32_t a1 __asm__("a1")=7; KEEP(a1);
    __asm__ volatile("sw s0, 8(sp)\nsw ra, 12(sp)\nmv s0, a0\n" : : "r"(a1) : "memory");
    CALL(tsl9_callback_checksum_ed00);
    __builtin_unreachable();
}
REGION void tsl9_callback_predicate_106ac(void)
{
    register uint32_t a5 __asm__("a5");
    __asm__ volatile("lbu a5, 10(s0)" : "=r"(a5) : : "memory");
    __asm__ volatile("lw ra, 12(sp)\nlw s0, 8(sp)" : : "r"(a5) : "memory");
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0=a5-a0; KEEP(a0);
    a0=(a0==0u); KEEP(a0);
    __asm__ volatile("addi sp, sp, 16\nret" : : "r"(a0) : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_feature_external_106e8(void)
{
    __asm__ volatile("addi sp, sp, -16\nsw ra, 12(sp)\n"
                     ".option push\n.option norvc\njal ra, tsl9_callback_guard_828c\n.option pop\n");
}
REGION void tsl9_callback_count_106f0(void)
{
    CBRANCH(c.bnez,a0,tsl9_callback_count_10704);
    __builtin_unreachable();
}
REGION void tsl9_callback_count_106f2(void)
{
    register uintptr_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x1fffc" : "=r"(a5) : : "memory");
    a5=*(volatile uint8_t *)(a5-1854u); KEEP(a5);
    ++a5; KEEP(a5);
    register uintptr_t a4 __asm__("a4");
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    *(volatile uint8_t *)(a4-1864u)=(uint8_t)a5;
    __builtin_unreachable();
}
FRAME void tsl9_callback_count_10704(void)
{
    __asm__ volatile("lw ra, 12(sp)\naddi sp, sp, 16\nret\n");
}

FRAME void tsl9_feature_external_1074c(void)
{
    __asm__ volatile("addi sp, sp, -16\nsw ra, 12(sp)\nsw s0, 8(sp)\nmv s0, a0\n"
                     ".option push\n.option norvc\njal ra, tsl9_callback_external_d272\n.option pop\n");
}
REGION void tsl9_callback_state_10758(void)
{
    CALL(tsl9_callback_external_b0fc);
    __builtin_unreachable();
}
REGION void tsl9_callback_state_1075c(void)
{
    register uint32_t a0 __asm__("a0")=0; KEEP(a0);
    CALL(tsl9_queue_clear_820c);
    CALL(tsl9_callback_external_10032);
    __builtin_unreachable();
}
REGION void tsl9_callback_state_10766(void)
{
    register uint32_t a0 __asm__("a0");
    __asm__ volatile("andi a0, s0, 255" : "=r"(a0) : : "memory");
    register uintptr_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x1fffc" : "=r"(a5) : : "memory");
    *(volatile uint8_t *)(a5-1974u)=0;
    __asm__ volatile("auipc a5, 0x1fffc" : "=r"(a5) : : "memory");
    *(volatile uint8_t *)(a5-1981u)=(uint8_t)a0;
    CALL(tsl9_callback_external_12b24);
    __builtin_unreachable();
}
REGION void tsl9_callback_state_1077e(void)
{
    CBRANCH(c.beqz,s0,tsl9_callback_state_10794);
    __builtin_unreachable();
}
REGION void tsl9_callback_state_10780(void)
{
    register uint32_t a3 __asm__("a3")=0; KEEP(a3);
    register uint32_t a2 __asm__("a2")=500; KEEP(a2);
    register uint32_t a1 __asm__("a1")=1; KEEP(a1);
    register uintptr_t a0 __asm__("a0"); ADDRESS(a0,tsl9_callback_external_9b36);
    CALL(tsl9_callback_external_9124);
    __builtin_unreachable();
}
REGION void tsl9_callback_state_10794(void)
{
    register uint32_t a0 __asm__("a0")=0; KEEP(a0);
    CALL(tsl9_callback_external_13d48);
    __builtin_unreachable();
}
REGION void tsl9_callback_state_1079a(void)
{
    register uint32_t a5 __asm__("a5")=6; KEEP(a5);
    BRANCH(bne,s0,a5,tsl9_callback_state_107b8);
    __builtin_unreachable();
}
FRAME void tsl9_callback_state_107a0(void)
{
    __asm__ volatile("lw s0, 8(sp)\nlw ra, 12(sp)\n");
}
REGION void tsl9_callback_state_107a4(void)
{
    register uint32_t a3 __asm__("a3")=0; KEEP(a3);
    register uint32_t a2 __asm__("a2")=20; KEEP(a2);
    register uint32_t a1 __asm__("a1")=1; KEEP(a1);
    register uintptr_t a0 __asm__("a0"); ADDRESS(a0,tsl9_callback_external_10630);
    __asm__ volatile("addi sp, sp, 16" : : "r"(a0),"r"(a1),"r"(a2),"r"(a3) : "memory");
    JUMP(tsl9_callback_external_9124);
    __builtin_unreachable();
}
FRAME void tsl9_callback_state_107b8(void)
{
    __asm__ volatile("lw ra, 12(sp)\nlw s0, 8(sp)\naddi sp, sp, 16\nret\n");
}
REGION void tsl9_callback_deferred_107c0(void)
{
    register uint32_t a0 __asm__("a0")=0; KEEP(a0);
    JUMP(tsl9_feature_external_1074c);
    __builtin_unreachable();
}

FRAME void tsl9_feature_external_1083c(void)
{
    __asm__ volatile("addi sp, sp, -16\nmv a5, a0\nmv a0, a1\n"
                     "sw s0, 8(sp)\nsw ra, 12(sp)\njalr a5\n");
}
REGION void tsl9_callback_wrapper_10848(void)
{
    __asm__ volatile("mv s0, a0" : : : "memory");
    CBRANCH(c.beqz,a0,tsl9_callback_wrapper_10866);
    __builtin_unreachable();
}
REGION void tsl9_callback_wrapper_1084c(void)
{
    register uint32_t a0 __asm__("a0")=0; KEEP(a0);
    CALL(tsl9_queue_clear_820c);
    __builtin_unreachable();
}
REGION void tsl9_callback_wrapper_10852(void)
{
    register uint32_t a3 __asm__("a3")=0; KEEP(a3);
    register uint32_t a2 __asm__("a2")=2000; KEEP(a2);
    register uint32_t a1 __asm__("a1")=0; KEEP(a1);
    register uintptr_t a0 __asm__("a0"); ADDRESS(a0,tsl9_callback_deferred_107c0);
    CALL(tsl9_callback_external_9124);
    __builtin_unreachable();
}
FRAME void tsl9_callback_wrapper_10866(void)
{
    __asm__ volatile("mv a0, s0\nlw ra, 12(sp)\nlw s0, 8(sp)\naddi sp, sp, 16\nret\n");
}
