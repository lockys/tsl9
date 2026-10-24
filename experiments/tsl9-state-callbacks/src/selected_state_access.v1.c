/* Derived from curated state_access.c; original 82A8-82D2 is supplied by the real parent. */
#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Offline RV32 architectural regions; never run on a HOST or device.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define FRAME ENTRY __attribute__((used,naked,aligned(2)))
#define INPUT(x) __asm__ volatile("" : "=r"(x) : : "memory")
#define KEEP(x) __asm__ volatile("" : "+r"(x) : : "memory")
#define BRANCH(op,left,right,target) \
    __asm__ volatile(".Lstate_branch%=:\n" #op " " #left ", " #right ", .Lstate_branch%=\n" \
                     ".reloc .-4, R_RISCV_BRANCH, " #target "\n" : : : "memory")
#define CBRANCH(op,reg,target) \
    __asm__ volatile(".Lstate_short%=:\n" #op " " #reg ", .Lstate_short%=\n" \
                     ".reloc .-2, R_RISCV_RVC_BRANCH, " #target "\n" : : : "memory")
#define TAIL(target) \
    __asm__ volatile(".Lstate_tail%=:\n.option push\n.option norvc\njal zero, .Lstate_tail%=\n.option pop\n" \
                     ".reloc .-4, R_RISCV_JAL, " #target "\n" : : : "memory")
#define CJUMP(target) \
    __asm__ volatile(".Lstate_jump%=:\nc.j .Lstate_jump%=\n" \
                     ".reloc .-2, R_RISCV_RVC_JUMP, " #target "\n" : : : "memory")

/* Original [82A8,82D2) and [10032,10158). C owns free-bank arithmetic,
 * volatile memory and constants. PC-relative AUIPC, control and register
 * handoff are explicit architecture ports. Regions require original-PC
 * placement and adjacent fallthrough; they are not independent C ABI entries.
 * ROM slots40048/4004C are freshly loaded, with unknown installed identity.
 * 13C4E is genuinely unresolved. No array bounds, RAM ownership, field names,
 * IRQ exclusion or successful operation on physical hardware are assumed.
 */

REGION void tsl9_callback_external_10032(void)
{
    register uintptr_t a5 __asm__("a5")=0x40000u; KEEP(a5);
    register uintptr_t t1 __asm__("t1")=*(volatile uint32_t *)(a5+72u); KEEP(t1);
    register uint32_t a2 __asm__("a2")=3; KEEP(a2);
    register uint32_t a1 __asm__("a1")=0; KEEP(a1);
    register uintptr_t gp __asm__("gp"); INPUT(gp);
    register uintptr_t a0 __asm__("a0")=gp+300u; KEEP(a0);
    __asm__ volatile("jr t1\n" : : "r"(t1),"r"(a0),"r"(a1),"r"(a2) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_feature_external_10044(void)
{
    register uintptr_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5")=*(volatile uint8_t *)(a0+4u); KEEP(a5);
    register uint32_t a4 __asm__("a4")=*(volatile uint8_t *)(a0+5u); KEEP(a4);
    a5<<=8; KEEP(a5);
    a4<<=16; KEEP(a4);
    a5+=a4; KEEP(a5);
    a4=*(volatile uint8_t *)(a0+3u); KEEP(a4);
    a5+=a4; KEEP(a5);
    a4=*(volatile uint8_t *)(a0+6u); KEEP(a4);
    a4<<=24; KEEP(a4);
    a5+=a4; KEEP(a5);
    a4=UINT32_MAX; KEEP(a4);
    BRANCH(beq,a5,a4,tsl9_state_10088);
    __builtin_unreachable();
}
REGION void tsl9_state_10066(void)
{
    register uint32_t a4 __asm__("a4")=100; KEEP(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5/=a4; KEEP(a5);
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    a4-=198u; KEEP(a4);
    a4=*(volatile uint32_t *)(uintptr_t)a4; KEEP(a4);
    BRANCH(beq,a4,a5,tsl9_state_10088);
    __builtin_unreachable();
}
REGION void tsl9_state_1007c(void)
{
    register uintptr_t a4 __asm__("a4");
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    *(volatile uint32_t *)(a4-212u)=a5;
    TAIL(tsl9_state_external_13c4e);
    __builtin_unreachable();
}
FRAME void tsl9_state_10088(void) { __asm__ volatile("ret\n"); }
REGION void tsl9_state_get_1008a(void)
{
    register uintptr_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x1fffc" : "=r"(a5) : : "memory");
    a5-=226u; KEEP(a5);
    register uint32_t a0 __asm__("a0")=*(volatile uint32_t *)a5; KEEP(a0);
    __asm__ volatile("ret\n" : : "r"(a0),"r"(a5) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_feature_external_10096(void)
{
    register uintptr_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5")=*(volatile uint8_t *)(a0+4u); KEEP(a5);
    register uint32_t a4 __asm__("a4")=*(volatile uint8_t *)(a0+3u); KEEP(a4);
    a5&=63u; KEEP(a5);
    a5<<=8; KEEP(a5);
    a5|=a4; KEEP(a5);
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    a4-=254u; KEEP(a4);
    a4=(uint32_t)*(volatile int16_t *)(uintptr_t)(a4+4u); KEEP(a4);
    a5<<=18; KEEP(a5);
    a5=(uint32_t)((int32_t)a5>>18); KEEP(a5);
    BRANCH(beq,a4,a5,tsl9_state_100c6);
    __builtin_unreachable();
}
REGION void tsl9_state_100ba(void)
{
    register uintptr_t a4 __asm__("a4");
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    *(volatile uint16_t *)(a4-270u)=(uint16_t)a5;
    TAIL(tsl9_state_external_13c4e);
    __builtin_unreachable();
}
FRAME void tsl9_state_100c6(void) { __asm__ volatile("ret\n"); }
REGION void tsl9_state_get_100c8(void)
{
    register uintptr_t a5 __asm__("a5");
    __asm__ volatile("auipc a5, 0x1fffc" : "=r"(a5) : : "memory");
    a5-=288u; KEEP(a5);
    register uint32_t a0 __asm__("a0")=(uint32_t)*(volatile int16_t *)(a5+4u); KEEP(a0);
    __asm__ volatile("ret\n" : : "r"(a0),"r"(a5) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_feature_external_100d6(void)
{
    register uintptr_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5")=*(volatile uint8_t *)(a0+4u); KEEP(a5);
    register uintptr_t a4 __asm__("a4");
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    a4=*(volatile uint8_t *)(a4-296u); KEEP(a4);
    a5&=1u; KEEP(a5);
    BRANCH(beq,a4,a5,tsl9_state_100f4);
    __builtin_unreachable();
}
REGION void tsl9_state_100e8(void)
{
    register uintptr_t a4 __asm__("a4");
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    *(volatile uint8_t *)(a4-310u)=(uint8_t)a5;
    TAIL(tsl9_state_external_13c4e);
    __builtin_unreachable();
}
FRAME void tsl9_state_100f4(void) { __asm__ volatile("ret\n"); }
REGION void tsl9_state_get_100f6(void)
{
    register uintptr_t a0 __asm__("a0");
    __asm__ volatile("auipc a0, 0x1fffc" : "=r"(a0) : : "memory");
    a0=*(volatile uint8_t *)(a0-324u); KEEP(a0);
    __asm__ volatile("ret\n" : : "r"(a0) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_feature_external_10100(void)
{
    register uintptr_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5")=*(volatile uint8_t *)(a0+4u); KEEP(a5);
    register uint32_t a4 __asm__("a4")=*(volatile uint8_t *)(a0+3u); KEEP(a4);
    register uintptr_t a1 __asm__("a1"); INPUT(a1);
    a1<<=1; KEEP(a1);
    a5&=7u; KEEP(a5);
    a5<<=8; KEEP(a5);
    a5|=a4; KEEP(a5);
    __asm__ volatile("auipc a4, 0x1fffc" : "=r"(a4) : : "memory");
    a4-=360u; KEEP(a4);
    a1+=a4; KEEP(a1);
    a4=(uint32_t)*(volatile int16_t *)(a1+6u); KEEP(a4);
    a5<<=21; KEEP(a5);
    a5=(uint32_t)((int32_t)a5>>21); KEEP(a5);
    BRANCH(beq,a4,a5,tsl9_state_1012e);
    __builtin_unreachable();
}
REGION void tsl9_state_10126(void)
{
    register uintptr_t a1 __asm__("a1"); INPUT(a1);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    *(volatile uint16_t *)(a1+6u)=(uint16_t)a5;
    TAIL(tsl9_state_external_13c4e);
    __builtin_unreachable();
}
FRAME void tsl9_state_1012e(void) { __asm__ volatile("ret\n"); }
REGION void tsl9_state_get_10130(void)
{
    register uintptr_t gp __asm__("gp"); INPUT(gp);
    register uint32_t a5 __asm__("a5")=*(volatile uint8_t *)(gp+357u); KEEP(a5);
    a5-=7u; KEEP(a5);
    a5&=255u; KEEP(a5);
    register uint32_t a4 __asm__("a4")=1; KEEP(a4);
    BRANCH(bgeu,a4,a5,tsl9_state_10154);
    __builtin_unreachable();
}
REGION void tsl9_state_10140(void)
{
    register uintptr_t a0 __asm__("a0"); INPUT(a0);
    register uintptr_t a5 __asm__("a5")=a0<<1; KEEP(a5);
    __asm__ volatile("auipc a0, 0x1fffc" : "=r"(a0) : : "memory");
    a0-=412u; KEEP(a0);
    a0+=a5; KEEP(a0);
    a0=(uint32_t)*(volatile int16_t *)(a0+6u); KEEP(a0);
    __asm__ volatile("ret\n" : : "r"(a0),"r"(a5) : "memory");
    __builtin_unreachable();
}
REGION void tsl9_state_10154(void)
{
    register uint32_t a0 __asm__("a0")=0; KEEP(a0);
    __asm__ volatile("ret\n" : : "r"(a0) : "memory");
    __builtin_unreachable();
}
