#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 architectural regions only; never execute on a host or device.
#endif

/* Complete original [0x18BA2,0x18CA4), including reachable post-RET blocks.
 * C owns every load/store, unsigned bit operation and constant. Explicit
 * architectural branch/fall-through/return ports preserve the physical bank.
 * These regions are not ordinary C ABI functions. No resident/chip identity,
 * MMIO completion, valid pointers, IRQ behavior or hardware result is assumed.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define PORT(x) __asm__ volatile("" : "+r"(x) : : "memory")
#define LIVE(...) __asm__ volatile("" : __VA_ARGS__ : : "memory")
#define BR4(text,target) __asm__ volatile(".Lfilter%=:\n" text ", .Lfilter%=\n.reloc .-4, R_RISCV_BRANCH, " #target : : : "memory")
#define BR2(text,target) __asm__ volatile(".Lfilter%=:\n" text ", .Lfilter%=\n.reloc .-2, R_RISCV_RVC_BRANCH, " #target : : : "memory")
#define JUMP(target) __asm__ volatile(".Lfilter%=:\nc.j .Lfilter%=\n.reloc .-2, R_RISCV_RVC_JUMP, " #target : : : "memory")
#define U8(base,off) (*(volatile uint8_t *)(uintptr_t)((base)+(off)))
#define U16(base,off) (*(volatile uint16_t *)(uintptr_t)((base)+(off)))
#define U32(base,off) (*(volatile uint32_t *)(uintptr_t)((base)+(off)))

REGION void tsl9_filter_program_18ba2(void)
{
    register uint32_t a0 __asm__("a0"); LIVE("=r"(a0));
    register uint32_t a4 __asm__("a4")=UINT32_C(0x40006400); PORT(a4);
    register uint32_t a3 __asm__("a3")=U32(a4,512); PORT(a3);
    register uint32_t a5 __asm__("a5")=U8(a0,10); PORT(a5);
    register uint32_t a6 __asm__("a6")=1; PORT(a6);
    a3|=1u; PORT(a3); U32(a4,512)=a3;
    register uint32_t a1 __asm__("a1")=U32(a4,540); PORT(a1);
    register uint32_t a2 __asm__("a2")=a6<<(a5&31u); PORT(a2);
    a3=~a2; PORT(a3); a1&=a3; PORT(a1); U32(a4,540)=a1;
    a1=U8(a0,12); PORT(a1);
    BR2("c.bnez a1",tsl9_filter_scale_test_18c5a);
    __builtin_unreachable();
}

REGION void tsl9_filter_scale16_18bd4(void)
{
    register uint32_t a0 __asm__("a0"); register uint32_t a3 __asm__("a3");
    register uint32_t a4 __asm__("a4"); register uint32_t a5 __asm__("a5");
    LIVE("=r"(a0),"=r"(a3),"=r"(a4),"=r"(a5));
    register uint32_t a1 __asm__("a1")=U32(a4,524); PORT(a1);
    register uint32_t a6 __asm__("a6")=U16(a0,2); PORT(a6);
    a5<<=3; PORT(a5); a1&=a3; PORT(a1); U32(a4,524)=a1;
    a1=U16(a0,6); PORT(a1); a5+=a4; PORT(a5);
    a4=U16(a0,4); PORT(a4); a1<<=16; PORT(a1); a1|=a6; PORT(a1);
    U32(a5,576)=a1; a1=U16(a0,0); PORT(a1); a4<<=16; PORT(a4);
    __builtin_unreachable();
}

REGION void tsl9_filter_fr2_18bfe(void)
{
    register uint32_t a1 __asm__("a1"); register uint32_t a4 __asm__("a4");
    register uint32_t a5 __asm__("a5"); LIVE("=r"(a1),"=r"(a4),"=r"(a5));
    a4|=a1; PORT(a4); U32(a5,580)=a4; __builtin_unreachable();
}

REGION void tsl9_filter_mode_18c04(void)
{
    register uint32_t a0 __asm__("a0"); LIVE("=r"(a0));
    register uint32_t a4 __asm__("a4")=U8(a0,11); PORT(a4);
    register uint32_t a5 __asm__("a5")=UINT32_C(0x40006400); PORT(a5);
    BR2("c.bnez a4",tsl9_filter_mode_list_18c8a); __builtin_unreachable();
}

REGION void tsl9_filter_mode_mask_18c12(void)
{
    register uint32_t a3 __asm__("a3"); register uint32_t a5 __asm__("a5");
    LIVE("=r"(a3),"=r"(a5));
    register uint32_t a4 __asm__("a4")=U32(a5,516); PORT(a4);
    a4&=a3; PORT(a4); __builtin_unreachable();
}

REGION void tsl9_filter_mode_store_18c18(void)
{
    register uint32_t a4 __asm__("a4"); register uint32_t a5 __asm__("a5");
    LIVE("=r"(a4),"=r"(a5)); U32(a5,516)=a4; __builtin_unreachable();
}

REGION void tsl9_filter_fifo_18c1c(void)
{
    register uint32_t a0 __asm__("a0"); LIVE("=r"(a0));
    register uint32_t a4 __asm__("a4")=U16(a0,8); PORT(a4);
    register uint32_t a5 __asm__("a5")=UINT32_C(0x40006400); PORT(a5);
    BR2("c.bnez a4",tsl9_filter_fifo_test_18c92); __builtin_unreachable();
}

REGION void tsl9_filter_fifo0_18c2a(void)
{
    register uint32_t a3 __asm__("a3"); register uint32_t a5 __asm__("a5");
    LIVE("=r"(a3),"=r"(a5));
    register uint32_t a4 __asm__("a4")=U32(a5,532); PORT(a4);
    a3&=a4; PORT(a3); U32(a5,532)=a3; __builtin_unreachable();
}

REGION void tsl9_filter_activation_18c34(void)
{
    register uint32_t a0 __asm__("a0"); LIVE("=r"(a0));
    register uint32_t a4 __asm__("a4")=U32(a0,16); PORT(a4);
    register uint32_t a5 __asm__("a5")=1; PORT(a5);
    BR4("bne a4, a5",tsl9_filter_finish_18c4a); __builtin_unreachable();
}

REGION void tsl9_filter_activate_18c3c(void)
{
    register uint32_t a2 __asm__("a2"); LIVE("=r"(a2));
    register uint32_t a5 __asm__("a5")=UINT32_C(0x40006000); PORT(a5);
    register uint32_t a4 __asm__("a4")=U32(a5,1564); PORT(a4);
    a2|=a4; PORT(a2); U32(a5,1564)=a2; __builtin_unreachable();
}

REGION void tsl9_filter_finish_18c4a(void)
{
    register uint32_t a5 __asm__("a5")=UINT32_C(0x40006000); PORT(a5);
    register uint32_t a4 __asm__("a4")=U32(a5,1536); PORT(a4);
    a4&=UINT32_C(0xFFFFFFFE); PORT(a4); U32(a5,1536)=a4;
    __asm__ volatile("ret" : : : "memory"); __builtin_unreachable();
}

REGION void tsl9_filter_scale_test_18c5a(void)
{
    BR4("bne a1, a6",tsl9_filter_mode_18c04); __builtin_unreachable();
}

REGION void tsl9_filter_scale32_18c5e(void)
{
    register uint32_t a0 __asm__("a0"); register uint32_t a2 __asm__("a2");
    register uint32_t a4 __asm__("a4"); register uint32_t a5 __asm__("a5");
    LIVE("=r"(a0),"=r"(a2),"=r"(a4),"=r"(a5));
    register uint32_t a1 __asm__("a1")=U32(a4,524); PORT(a1);
    register uint32_t a6 __asm__("a6")=U16(a0,2); PORT(a6);
    a5<<=3; PORT(a5); a1|=a2; PORT(a1); U32(a4,524)=a1;
    a1=U16(a0,0); PORT(a1); a5+=a4; PORT(a5);
    a4=U16(a0,4); PORT(a4); a1<<=16; PORT(a1); a1|=a6; PORT(a1);
    U32(a5,576)=a1; a4<<=16; PORT(a4); a1=U16(a0,6); PORT(a1);
    JUMP(tsl9_filter_fr2_18bfe); __builtin_unreachable();
}

REGION void tsl9_filter_mode_list_18c8a(void)
{
    register uint32_t a2 __asm__("a2"); register uint32_t a5 __asm__("a5");
    LIVE("=r"(a2),"=r"(a5));
    register uint32_t a4 __asm__("a4")=U32(a5,516); PORT(a4);
    a4|=a2; PORT(a4); JUMP(tsl9_filter_mode_store_18c18); __builtin_unreachable();
}

REGION void tsl9_filter_fifo_test_18c92(void)
{
    register uint32_t a3 __asm__("a3")=1; PORT(a3);
    BR4("bne a4, a3",tsl9_filter_activation_18c34); __builtin_unreachable();
}

REGION void tsl9_filter_fifo1_18c98(void)
{
    register uint32_t a2 __asm__("a2"); register uint32_t a5 __asm__("a5");
    LIVE("=r"(a2),"=r"(a5));
    register uint32_t a4 __asm__("a4")=U32(a5,532); PORT(a4);
    a4|=a2; PORT(a4); U32(a5,532)=a4;
    JUMP(tsl9_filter_activation_18c34); __builtin_unreachable();
}
