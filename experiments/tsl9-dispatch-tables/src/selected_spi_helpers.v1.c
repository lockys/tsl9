/* Derived from curated spi_filter_helpers.c. Only the three clock
 * definitions already owned by the parent are omitted. Other C text and
 * symbolic references are unchanged. */
#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private helpers only; never execute on a host or device.
#endif
/* Original 81B0..81CA,16858..16896,169DC..16A30. Resident targets, clock
 * units, scheduling/IRQ behavior, device identity and ordinary ABI are unknown.
 * Every port after a call reads then-live physical registers/stack. */
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



FRAME void tsl9_channel_external_16858(void) { __asm__ volatile("addi sp,sp,-16"); }
REGION void tsl9_channel_timer_args_1685a(void) {
    REGS; a5=0x20000; LIVE;
    __asm__ volatile("sw a5,8(sp)"::"r"(a5):"memory");
    a5=4; LIVE;
    __asm__ volatile("addi a4,sp,16\nsh a5,12(sp)":"=r"(a4):"r"(a5):"memory");
    a0<<=1; LIVE; a0+=a4; LIVE;
    __asm__ volatile("lbu a5,363(gp)":"=r"(a5)::"memory");
    a4=0x40000; LIVE;
    __asm__ volatile(".Ltimer_zero:\nc.beqz a1,.Ltimer_zero\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_channel_timer_zero_16888"::"r"(a1):"memory"); __builtin_unreachable();
}
REGION void tsl9_channel_timer_nonzero_16876(void) {
    REGS; a1=*(volatile uint16_t *)(uintptr_t)(a0-8u); LIVE;
    __asm__ volatile("lw t1,556(a4)"::"r"(a4):"memory");
    a2=1600; LIVE; a0=a5; LIVE;
    __asm__ volatile("addi sp,sp,16\njr t1"::"r"(a0),"r"(a1),"r"(a2),"r"(a4),"r"(a5):"memory"); __builtin_unreachable();
}
REGION void tsl9_channel_timer_zero_16888(void) {
    REGS; a1=*(volatile uint16_t *)(uintptr_t)(a0-8u); LIVE;
    __asm__ volatile("lw t1,92(a4)"::"r"(a4):"memory");
    a0=a5; LIVE;
    __asm__ volatile("addi sp,sp,16\njr t1"::"r"(a0),"r"(a1),"r"(a2),"r"(a4),"r"(a5):"memory"); __builtin_unreachable();
}
FRAME void tsl9_channel_external_169dc(void) {
    __asm__ volatile("addi sp,sp,-32\nmv a3,a1\nsw s0,24(sp)");
}
REGION void tsl9_channel_mode_write_169e2(void) {
    REGS; a2=224; LIVE;
    __asm__ volatile("mv s0,a1"::"r"(a1):"memory");
    a1=15; LIVE;
    __asm__ volatile("sw ra,28(sp)\nsw s1,20(sp)\nsw s2,16(sp)\nsw s3,12(sp)\nmv s3,a0"::"r"(a0):"memory");
    CALL(".Lmode_write",tsl9_tagged_external_1693e); __builtin_unreachable();
}
REGION void tsl9_channel_clock_start_169f8(void) {
    REGS; CALL(".Lclock_start",tsl9_channel_external_81b0); __builtin_unreachable();
}
FRAME void tsl9_channel_poll_setup_169fc(void) { __asm__ volatile("mv s2,a0\nli s1,5"); }
REGION void tsl9_channel_poll_clock_16a00(void) {
    REGS; CALL(".Lclock_poll",tsl9_channel_external_81b0);
    __asm__ volatile("sub a0,a0,s2\n.Lmode_in_time:\nbgeu s1,a0,.Lmode_in_time\n.reloc .-4,R_RISCV_BRANCH,tsl9_channel_poll_read_16a1c":"+r"(a0)::"memory"); __builtin_unreachable();
}
REGION void tsl9_channel_timeout_16a0c(void) { REGS; a0=1; LIVE; __builtin_unreachable(); }
FRAME void tsl9_channel_mode_return_16a0e(void) {
    __asm__ volatile("lw ra,28(sp)\nlw s0,24(sp)\nlw s1,20(sp)\nlw s2,16(sp)\nlw s3,12(sp)\naddi sp,sp,32\nret");
}
REGION void tsl9_channel_poll_read_16a1c(void) {
    REGS; a1=14; LIVE; __asm__ volatile("mv a0,s3":"=r"(a0)::"memory");
    CALL(".Lmode_read",tsl9_register_read_entry_16994); a0&=224u; LIVE;
    __asm__ volatile(".Lmode_again:\nbne s0,a0,.Lmode_again\n.reloc .-4,R_RISCV_BRANCH,tsl9_channel_poll_clock_16a00"::"r"(a0):"memory"); __builtin_unreachable();
}
REGION void tsl9_channel_mode_done_16a2c(void) {
    REGS; a0=0; LIVE;
    __asm__ volatile(".Lmode_done:\nc.j .Lmode_done\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_channel_mode_return_16a0e"::"r"(a0):"memory"); __builtin_unreachable();
}
