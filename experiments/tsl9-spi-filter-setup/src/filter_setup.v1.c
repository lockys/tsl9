#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private regions only; never execute on a host or device.
#endif
/* Original [16CC4,16DAC). C owns scalar/memory operations. Physical frame,
 * S-register and control ports retain then-live state; no ordinary callee ABI,
 * resident identity, peripheral identity, ownership or IRQ guarantee is assumed.
 * The two resident calls may change SP/S0..S6. No entry guard bounds later
 * S1/S2/S6, and the loop is not unconditionally a six-iteration C for-loop. */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define FRAME ENTRY __attribute__((naked,used,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define CALL(label,target) __asm__ volatile(label ":\n.option push\n.option norvc\njal ra," label "\n.option pop\n.reloc .-4,R_RISCV_JAL," #target : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
REGION void tsl9_channel_external_16cc4(void) {
    REGS; a5=a0-1u; LIVE; a5&=255u; LIVE; a4=1; LIVE;
    __asm__ volatile(".Lsetup_invalid:\nbltu a4,a5,.Lsetup_invalid\n.reloc .-4,R_RISCV_BRANCH,tsl9_setup_early_16daa"::"r"(a4),"r"(a5):"memory"); __builtin_unreachable();
}
REGION void tsl9_setup_resident_16cd2(void) {
    REGS; a5=0x40000; LIVE; a5=*(volatile uint32_t *)(uintptr_t)(a5+72u); LIVE; __builtin_unreachable();
}
FRAME void tsl9_setup_frame_16cd8(void) {
    __asm__ volatile("addi sp,sp,-64\nsw s0,56(sp)\nsw s1,52(sp)\nsw s2,48(sp)\nsw s3,44(sp)\nmv s1,a2\nsw ra,60(sp)");
}
REGION void tsl9_setup_clear_16ce6(void) {
    REGS; a2=12; LIVE;
    __asm__ volatile("sw s4,40(sp)\nsw s5,36(sp)\nsw s6,32(sp)\nmv s2,a1\nmv s0,a0":::"memory");
    a1=0; LIVE;
    __asm__ volatile("addi a0,sp,20\nmv s3,a3\njalr a5":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory"); __builtin_unreachable();
}
REGION void tsl9_setup_length_16cfa(void) {
    REGS; register uint32_t s1 __asm__("s1");
    __asm__ volatile("":"=r"(s1)::"memory");
    a5=12; LIVE; a2=s1&255u; LIVE;
    __asm__ volatile(".Lsetup_short:\nbgeu a5,s1,.Lsetup_short\n.reloc .-4,R_RISCV_BRANCH,tsl9_setup_copy_16d06"::"r"(a5),"r"(s1):"memory"); __builtin_unreachable();
}
REGION void tsl9_setup_clamp_16d04(void) { REGS; a2=12; LIVE; __builtin_unreachable(); }
REGION void tsl9_setup_copy_16d06(void) {
    REGS; a5=0x40000; LIVE; a5=*(volatile uint32_t *)(uintptr_t)(a5+76u); LIVE;
    __asm__ volatile("mv a1,s2\naddi a0,sp,20\njalr a5":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory"); __builtin_unreachable();
}
REGION void tsl9_setup_mode_16d12(void) {
    REGS; a1=128; LIVE; __asm__ volatile("mv a0,s0":"=r"(a0)::"memory"); CALL(".Lsetup_mode",tsl9_channel_external_169dc); __builtin_unreachable();
}
REGION void tsl9_setup_write0_16d1c(void) {
    REGS; a2=32; LIVE; a1=96; LIVE; __asm__ volatile("mv a0,s0":"=r"(a0)::"memory"); CALL(".Lsetup_write0",tsl9_register_write_entry_16a30); __builtin_unreachable();
}
REGION void tsl9_setup_write1_16d2a(void) {
    REGS; a2=32; LIVE; a1=112; LIVE;
    __asm__ volatile("mv a0,s0\nlui s5,0x10080\nlui s4,0x2":"=r"(a0)::"memory"); CALL(".Lsetup_write1",tsl9_register_write_entry_16a30); __builtin_unreachable();
}
FRAME void tsl9_setup_loop_init_16d3e(void) {
    __asm__ volatile("addi s1,sp,20\nli s2,0\naddi s5,s5,1024\naddi s4,s4,-2028\nli s6,6");
}
REGION void tsl9_setup_loop_16d4c(void) {
    REGS;
    __asm__ volatile("lhu a5,0(s1)\nsw s5,12(sp)\nsh s4,16(sp)":"=r"(a5)::"memory");
    a5&=2047u; LIVE; a4=a5>>3; LIVE; a5<<=5; LIVE;
    __asm__ volatile("sb a5,9(sp)\naddi a5,sp,12\nadd a5,a5,s2":"+r"(a5)::"memory");
    a1=*(volatile uint8_t *)(uintptr_t)a5; LIVE; a3=4; LIVE;
    __asm__ volatile("addi a2,sp,8\nmv a0,s0\naddi s2,s2,1\nsb a4,8(sp)\nsh zero,10(sp)\naddi s1,s1,2":"=r"(a2),"=r"(a0):"r"(a4):"memory");
    CALL(".Lsetup_payload",tsl9_tagged_external_168de); __builtin_unreachable();
}
REGION void tsl9_setup_test_16d82(void) {
    __asm__ volatile(".Lsetup_more:\nbne s2,s6,.Lsetup_more\n.reloc .-4,R_RISCV_BRANCH,tsl9_setup_loop_16d4c":::"memory"); __builtin_unreachable();
}
REGION void tsl9_setup_normal_16d86(void) {
    REGS; a1=0; LIVE; __asm__ volatile("mv a0,s0":"=r"(a0)::"memory"); CALL(".Lsetup_normal",tsl9_channel_external_169dc); __builtin_unreachable();
}
REGION void tsl9_setup_final_16d8e(void) {
    REGS; __asm__ volatile("mv a1,s3\nmv a0,s0":"=r"(a1),"=r"(a0)::"memory"); CALL(".Lsetup_final",tsl9_channel_external_16858); __builtin_unreachable();
}
FRAME void tsl9_setup_return_16d96(void) {
    __asm__ volatile("lw ra,60(sp)\nlw s0,56(sp)\nlw s1,52(sp)\nlw s2,48(sp)\nlw s3,44(sp)\nlw s4,40(sp)\nlw s5,36(sp)\nlw s6,32(sp)\naddi sp,sp,64\nret");
}
FRAME void tsl9_setup_early_16daa(void) { __asm__ volatile("ret"); }
