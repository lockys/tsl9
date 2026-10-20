#include "target_events.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "Target event entries require RV32"
#endif
/* Fixed server Runtime V4.1.00 only; no physical core/IRQ ABI assertion.
 * Preserve GP, raw original software frame and exact incidental register use. */
static void event_18bda(void) __asm__("tsl9_event_exti_clear_18bda");
static void event_18fc6(void) __asm__("tsl9_event_rtc_wait_18fc6");
static void event_18fd6(void) __asm__("tsl9_event_rtc_clear_core_18fd6");
static void event_18fea(void) __asm__("tsl9_event_rtc_clear_18fea");

/* Original 0x8440..0x848e (78 bytes). */
/* CSRS ORs bit5 into CSR804; slot0 supplies MEPC. This is not the LLE frame. */
__attribute__((naked, used, section(".text.tsl9_context_restore_irq")))
void tsl9_context_restore_irq(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "li a1, 32\n"
        "csrs 0x804, a1\n"
        "lw a1, 0(sp)\n"
        "csrw mepc, a1\n"
        "lw ra, 4(sp)\n"
        "lw tp, 8(sp)\n"
        "lw t0, 12(sp)\n"
        "lw t1, 16(sp)\n"
        "lw t2, 20(sp)\n"
        "lw s0, 24(sp)\n"
        "lw s1, 28(sp)\n"
        "lw a0, 32(sp)\n"
        "lw a1, 36(sp)\n"
        "lw a2, 40(sp)\n"
        "lw a3, 44(sp)\n"
        "lw a4, 48(sp)\n"
        "lw a5, 52(sp)\n"
        "lw a6, 56(sp)\n"
        "lw a7, 60(sp)\n"
        "lw s2, 64(sp)\n"
        "lw s3, 68(sp)\n"
        "lw s4, 72(sp)\n"
        "lw s5, 76(sp)\n"
        "lw s6, 80(sp)\n"
        "lw s7, 84(sp)\n"
        "lw s8, 88(sp)\n"
        "lw s9, 92(sp)\n"
        "lw s10, 96(sp)\n"
        "lw s11, 100(sp)\n"
        "lw t3, 104(sp)\n"
        "lw t4, 108(sp)\n"
        "lw t5, 112(sp)\n"
        "lw t6, 116(sp)\n"
        "addi sp, sp, 128\n"
        "mret\n"
        ".option pop\n");
}

/* Original 0x16d22..0x16d6e (76 bytes). */
/* Each pending read and GP-byte RMW is fresh; acknowledge bit before flag update. */
__attribute__((naked, used, section(".text.tsl9_exti_5_9_irq")))
void tsl9_exti_5_9_irq(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "lui a5, 0x40010\n"
        "lw a4, 1044(a5)\n"
        "addi a5, a5, 1024\n"
        "andi a4, a4, 64\n"
        "beqz a4, 1f\n"
        "li a4, 64\n"
        "sw a4, 20(a5)\n"
        "lbu a5, 360(gp)\n"
        "ori a5, a5, 1\n"
        "sb a5, 360(gp)\n"
        "1: lui a5, 0x40010\n"
        "lw a4, 1044(a5)\n"
        "addi a5, a5, 1024\n"
        "andi a4, a4, 128\n"
        "beqz a4, 2f\n"
        "li a4, 128\n"
        "sw a4, 20(a5)\n"
        "lbu a5, 360(gp)\n"
        "ori a5, a5, 2\n"
        "sb a5, 360(gp)\n"
        "2: mret\n"
        ".option pop\n");
}

/* Original 0x19928..0x19944 (28 bytes). */
/* GP+392 W32, EXTI bit17 W32, RTC bit1 U16 clear then bit5 poll. No software frame. */
__attribute__((naked, used, section(".text.tsl9_rtc_alarm_irq")))
void tsl9_rtc_alarm_irq(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "li a5, 1\n"
        "lui a0, 0x20\n"
        "sw a5, 392(gp)\n"
        ".option norvc\n"
        "jal ra, tsl9_event_exti_clear_18bda\n"
        ".option rvc\n"
        "li a0, 2\n"
        ".option norvc\n"
        "jal ra, tsl9_event_rtc_clear_18fea\n"
        "jal ra, tsl9_event_rtc_wait_18fc6\n"
        ".option rvc\n"
        "mret\n"
        ".option pop\n");
}

/* Original 0x18bda..0x18be4 (10 bytes). */
__attribute__((naked, used, section(".text.tsl9_event_exti_clear_18bda")))
static void event_18bda(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "lui a5, 0x40010\n"
        "sw a0, 1044(a5)\n"
        "ret\n"
        ".option pop\n");
}

/* Original 0x18fc6..0x18fd6 (16 bytes). */
/* Original unbounded native poll. Never execute in a host test. */
__attribute__((naked, used, section(".text.tsl9_event_rtc_wait_18fc6")))
static void event_18fc6(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "lui a4, 0x40003\n"
        "1: lhu a5, -2044(a4)\n"
        "andi a5, a5, 32\n"
        "beqz a5, 1b\n"
        "ret\n"
        ".option pop\n");
}

/* Original 0x18fd6..0x18fea (20 bytes). */
__attribute__((naked, used, section(".text.tsl9_event_rtc_clear_core_18fd6")))
static void event_18fd6(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "lui a5, 0x40003\n"
        "lhu a4, -2044(a5)\n"
        "not a0, a0\n"
        "and a0, a0, a4\n"
        "sh a0, -2044(a5)\n"
        "ret\n"
        ".option pop\n");
}

/* Original 0x18fea..0x18fee (4 bytes). */
__attribute__((naked, used, section(".text.tsl9_event_rtc_clear_18fea")))
static void event_18fea(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        ".option norvc\n"
        "j tsl9_event_rtc_clear_core_18fd6\n"
        ".option rvc\n"
        ".option pop\n");
}

/* R41: one hidden internal identity for the existing private body.
 * This is a symbol alias, not a duplicate implementation or fixed address. */
void tsl9_internal_rtc_wait_18fc6(void) __asm__("tsl9_internal_rtc_wait_18fc6")
    __attribute__((alias("tsl9_event_rtc_wait_18fc6"), visibility("hidden"), used));

