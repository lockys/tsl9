#include "target_rf_timer.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "Original RV32 GP, ROM, Timer/RF and SRAM contracts required"
#endif
#define TSL9_NATIVE __attribute__((naked, noinline, used))
/* Offline static reconstruction; never execute as host code.
 * Preserve raw32 gates, low-byte/halfword stores, unsigned arithmetic and fresh reads.
 * Timer state is shared; new state/callback addresses remain explicit UND references.
 * The 1049A self-reference has explicit standard HI20/LO12 relocations. */
#ifdef __cplusplus
extern "C" {
#endif
extern unsigned char __tsl9_timer_state[];
extern unsigned char __tsl9_state_bfb4[];
extern void tsl9_shared_timer_stop_entry(void) __asm__("tsl9_internal_timer_stop_93cc");
extern void tsl9_shared_gate_entry(void) __asm__("tsl9_internal_gate_8214");
extern void tsl9_shared_cancel_entry(void) __asm__("tsl9_internal_scheduler_cancel_908e");
extern void tsl9_shared_gpio_setup_entry(void) __asm__("tsl9_internal_gpio_setup_9a02");
extern void tsl9_shared_scheduler_register_entry(void) __asm__("tsl9_internal_scheduler_register_9102");
extern void tsl9_runtime_unported_13b5c(void);
extern void tsl9_runtime_unported_170e2(void);
#ifdef __cplusplus
}
#endif
static void tsl9_rf_flag_81aa(void) __asm__("tsl9_rf_flag_81aa") TSL9_NATIVE;
static void tsl9_rf_enabled_843a(void) __asm__("tsl9_rf_enabled_843a") TSL9_NATIVE;
static void tsl9_timer_start_9388(void) __asm__("tsl9_timer_start_9388") TSL9_NATIVE;
static void tsl9_timer_prepare_93ee(void) __asm__("tsl9_timer_prepare_93ee") TSL9_NATIVE;
static void tsl9_timer_mode_9770(void) __asm__("tsl9_timer_mode_9770") TSL9_NATIVE;
static void tsl9_rf_flag_9edc(void) __asm__("tsl9_rf_flag_9edc") TSL9_NATIVE;
static void tsl9_rf_cancel_1049a(void) __asm__("tsl9_rf_cancel_1049a") TSL9_NATIVE;
static void tsl9_rf_schedule_16f4a(void) __asm__("tsl9_rf_schedule_16f4a") TSL9_NATIVE;
static void tsl9_rf_control_17048(void) __asm__("tsl9_rf_control_17048") TSL9_NATIVE;

/* Original 0x81aa..0x81b0: 2 instructions, 6 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_rf_flag_81aa"))) void tsl9_rf_flag_81aa(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lbu a0, 175(gp) # original 0x81aa\n"
        ".option rvc\n"
        "ret # original 0x81ae\n"
        ".option pop\n"
    );
}

/* Original 0x843a..0x8440: 2 instructions, 6 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_rf_enabled_843a"))) void tsl9_rf_enabled_843a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lbu a0, 364(gp) # original 0x843a\n"
        ".option rvc\n"
        "ret # original 0x843e\n"
        ".option pop\n"
    );
}

/* Original 0x9388..0x93cc: 19 instructions, 68 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_timer_start_9388"))) void tsl9_timer_start_9388(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "addi a5, gp, 84 # original 0x9388\n"
        ".option rvc\n"
        "lw a5, 0(a5) # original 0x938c\n"
        ".option norvc\n"
        "lbu a4, 2(a5) # original 0x938e\n"
        ".Lrf46_pc_9392:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+4) # original 0x9392\n"
        "lbu a5, %pcrel_lo(.Lrf46_pc_9392)(a5) # original 0x9396\n"
        ".option rvc\n"
        "or a5, a5, a4 # original 0x939a\n"
        "beqz a5, .Lrf46_9388_93ca # original 0x939c\n"
        ".option norvc\n"
        ".Lrf46_pc_939e:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+6) # original 0x939e\n"
        "sb zero, %pcrel_lo(.Lrf46_pc_939e)(a5) # original 0x93a2\n"
        ".Lrf46_pc_93a6:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+5) # original 0x93a6\n"
        "sb zero, %pcrel_lo(.Lrf46_pc_93a6)(a5) # original 0x93aa\n"
        ".Lrf46_pc_93ae:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state) # original 0x93ae\n"
        "sw zero, %pcrel_lo(.Lrf46_pc_93ae)(a5) # original 0x93b2\n"
        "lui a5, 0x40000 # original 0x93b6\n"
        "sh zero, 1060(a5) # original 0x93ba\n"
        "lhu a4, 1024(a5) # original 0x93be\n"
        "ori a4, a4, 1 # original 0x93c2\n"
        "sh a4, 1024(a5) # original 0x93c6\n"
        ".Lrf46_9388_93ca:\n"
        ".option rvc\n"
        "ret # original 0x93ca\n"
        ".option pop\n"
    );
}

/* Original 0x93ee..0x9432: 24 instructions, 68 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_timer_prepare_93ee"))) void tsl9_timer_prepare_93ee(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0x93ee\n"
        ".option norvc\n"
        ".Lrf46_pc_93f0:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state) # original 0x93f0\n"
        "addi a5, a5, %pcrel_lo(.Lrf46_pc_93f0) # original 0x93f4\n"
        ".option rvc\n"
        "sw s0, 8(sp) # original 0x93f8\n"
        "mv s0, a0 # original 0x93fa\n"
        "lw a0, 16(a5) # original 0x93fc\n"
        "sw ra, 12(sp) # original 0x93fe\n"
        "beqz a0, .Lrf46_93ee_941c # original 0x9400\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x9402\n"
        ".option rvc\n"
        "lw a5, 104(a5) # original 0x9406\n"
        "jalr a5 # original 0x9408\n"
        ".option norvc\n"
        ".Lrf46_pc_940a:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+16) # original 0x940a\n"
        "sw zero, %pcrel_lo(.Lrf46_pc_940a)(a5) # original 0x940e\n"
        ".Lrf46_pc_9412:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+12) # original 0x9412\n"
        "sw zero, %pcrel_lo(.Lrf46_pc_9412)(a5) # original 0x9416\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_internal_timer_stop_93cc # original 0x941a\n"
        ".Lrf46_93ee_941c:\n"
        "li a0, 6 # original 0x941c\n"
        ".option norvc\n"
        "mul a0, s0, a0 # original 0x941e\n"
        "lui a5, 0x40 # original 0x9422\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0x9426\n"
        "lw ra, 12(sp) # original 0x9428\n"
        ".option norvc\n"
        "lw t1, 112(a5) # original 0x942a\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 0x942e\n"
        "jr t1 # original 0x9430\n"
        ".option pop\n"
    );
}

/* Original 0x9432..0x94cc: 54 instructions, 154 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_9432"))) void tsl9_timer_schedule(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0x9432\n"
        "sw s0, 8(sp) # original 0x9434\n"
        "sw ra, 12(sp) # original 0x9436\n"
        "sw s1, 4(sp) # original 0x9438\n"
        "li a5, 19 # original 0x943a\n"
        "mv s0, a0 # original 0x943c\n"
        ".option norvc\n"
        "bltu a5, a0, .Lrf46_9432_949c # original 0x943e\n"
        "andi s1, a0, 255 # original 0x9442\n"
        "addi a0, s1, 1 # original 0x9446\n"
        "andi a0, a0, 255 # original 0x944a\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_timer_prepare_93ee # original 0x944e\n"
        ".option norvc\n"
        ".Lrf46_pc_9450:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+16) # original 0x9450\n"
        "sw a0, %pcrel_lo(.Lrf46_pc_9450)(a5) # original 0x9454\n"
        ".option rvc\n"
        "beqz a0, .Lrf46_9432_94c2 # original 0x9458\n"
        "lui a3, 0x1 # original 0x945a\n"
        "mv a4, a0 # original 0x945c\n"
        "li a5, 0 # original 0x945e\n"
        ".option norvc\n"
        "addi a3, a3, -1096 # original 0x9460\n"
        "li a2, 40 # original 0x9464\n"
        "li a1, 80 # original 0x9468\n"
        ".Lrf46_9432_946c:\n"
        "bne s1, a5, .Lrf46_9432_9486 # original 0x946c\n"
        ".option rvc\n"
        "li a5, 6 # original 0x9470\n"
        ".option norvc\n"
        "mul s0, s0, a5 # original 0x9472\n"
        ".option rvc\n"
        "add s0, s0, a0 # original 0x9476\n"
        ".option norvc\n"
        "sh zero, 0(s0) # original 0x9478\n"
        ".Lrf46_9432_947c:\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0x947c\n"
        "lw ra, 12(sp) # original 0x947e\n"
        "lw s1, 4(sp) # original 0x9480\n"
        "addi sp, sp, 16 # original 0x9482\n"
        ".insn cj 1, 5, tsl9_timer_start_9388 # original 0x9484\n"
        ".Lrf46_9432_9486:\n"
        "addi a5, a5, 1 # original 0x9486\n"
        ".option norvc\n"
        "sh a3, 0(a4) # original 0x9488\n"
        "sh a2, 2(a4) # original 0x948c\n"
        "sh a1, 4(a4) # original 0x9490\n"
        "andi a5, a5, 255 # original 0x9494\n"
        ".option rvc\n"
        "addi a4, a4, 6 # original 0x9498\n"
        "j .Lrf46_9432_946c # original 0x949a\n"
        ".Lrf46_9432_949c:\n"
        "li a0, 2 # original 0x949c\n"
        ".insn cj 1, 1, tsl9_timer_prepare_93ee # original 0x949e\n"
        ".option norvc\n"
        ".Lrf46_pc_94a0:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+16) # original 0x94a0\n"
        "sw a0, %pcrel_lo(.Lrf46_pc_94a0)(a5) # original 0x94a4\n"
        ".option rvc\n"
        "beqz a0, .Lrf46_9432_94c2 # original 0x94a8\n"
        "lui a5, 0x1 # original 0x94aa\n"
        ".option norvc\n"
        "addi a5, a5, -1096 # original 0x94ac\n"
        "sh a5, 0(a0) # original 0x94b0\n"
        "sh s0, 2(a0) # original 0x94b4\n"
        "sh zero, 4(a0) # original 0x94b8\n"
        "sh zero, 6(a0) # original 0x94bc\n"
        ".option rvc\n"
        "j .Lrf46_9432_947c # original 0x94c0\n"
        ".Lrf46_9432_94c2:\n"
        "lw ra, 12(sp) # original 0x94c2\n"
        "lw s0, 8(sp) # original 0x94c4\n"
        "lw s1, 4(sp) # original 0x94c6\n"
        "addi sp, sp, 16 # original 0x94c8\n"
        "ret # original 0x94ca\n"
        ".option pop\n"
    );
}

/* Original 0x9770..0x977c: 5 instructions, 12 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_timer_mode_9770"))) void tsl9_timer_mode_9770(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "li a5, 250 # original 0x9770\n"
        ".option rvc\n"
        "bnez a0, .Lrf46_9770_9778 # original 0x9774\n"
        "li a5, 2 # original 0x9776\n"
        ".Lrf46_9770_9778:\n"
        "mv a0, a5 # original 0x9778\n"
        ".insn cj 1, 5, tsl9_runtime_unported_9432 # original 0x977a\n"
        ".option pop\n"
    );
}

/* Original 0x9936..0x99c6: 48 instructions, 144 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_9936"))) void tsl9_timer_initialize(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x9936\n"
        ".option rvc\n"
        "lw a5, 72(a5) # original 0x993a\n"
        "addi sp, sp, -16 # original 0x993c\n"
        "sw ra, 12(sp) # original 0x993e\n"
        "li a2, 20 # original 0x9940\n"
        "li a1, 0 # original 0x9942\n"
        ".option norvc\n"
        ".Lrf46_pc_9944:\n"
        "auipc a0, %pcrel_hi(__tsl9_timer_state) # original 0x9944\n"
        "addi a0, a0, %pcrel_lo(.Lrf46_pc_9944) # original 0x9948\n"
        ".option rvc\n"
        "jalr a5 # original 0x994c\n"
        ".option norvc\n"
        "lui a3, 0x40010 # original 0x994e\n"
        ".option rvc\n"
        "lw a5, 4(a3) # original 0x9952\n"
        "lui a4, 0x1 # original 0x9954\n"
        ".option norvc\n"
        "addi a4, a4, -1024 # original 0x9956\n"
        ".option rvc\n"
        "or a5, a5, a4 # original 0x995a\n"
        "sw a5, 4(a3) # original 0x995c\n"
        "li a2, 24 # original 0x995e\n"
        ".option norvc\n"
        "li a1, 256 # original 0x9960\n"
        "lui a0, 0x40011 # original 0x9964\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_internal_gpio_setup_9a02 # original 0x9968\n"
        ".option norvc\n"
        "addi a5, gp, 112 # original 0x996a\n"
        ".option rvc\n"
        "lw a4, 0(a5) # original 0x996e\n"
        ".option norvc\n"
        "lui a5, 0xf4 # original 0x9970\n"
        "addi a5, a5, 576 # original 0x9974\n"
        "divu a4, a4, a5 # original 0x9978\n"
        "lui a5, 0x40000 # original 0x997c\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0x9980\n"
        "addi a4, a4, -1 # original 0x9982\n"
        "slli a4, a4, 0x10 # original 0x9984\n"
        "srli a4, a4, 0x10 # original 0x9986\n"
        ".option norvc\n"
        "sh a4, 1064(a5) # original 0x9988\n"
        "lhu a4, 1052(a5) # original 0x998c\n"
        "ori a4, a4, 96 # original 0x9990\n"
        "sh a4, 1052(a5) # original 0x9994\n"
        "lhu a4, 1056(a5) # original 0x9998\n"
        "ori a4, a4, 256 # original 0x999c\n"
        "sh a4, 1056(a5) # original 0x99a0\n"
        "lhu a4, 1040(a5) # original 0x99a4\n"
        ".option rvc\n"
        "slli a4, a4, 0x10 # original 0x99a8\n"
        "srli a4, a4, 0x10 # original 0x99aa\n"
        "andi a4, a4, -2 # original 0x99ac\n"
        "slli a4, a4, 0x10 # original 0x99ae\n"
        "srli a4, a4, 0x10 # original 0x99b0\n"
        ".option norvc\n"
        "sh a4, 1040(a5) # original 0x99b2\n"
        "lhu a4, 1036(a5) # original 0x99b6\n"
        "ori a4, a4, 1 # original 0x99ba\n"
        "sh a4, 1036(a5) # original 0x99be\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 0x99c2\n"
        ".insn cj 1, 5, tsl9_internal_timer_stop_93cc # original 0x99c4\n"
        ".option pop\n"
    );
}

/* Original 0x9edc..0x9ee2: 2 instructions, 6 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_rf_flag_9edc"))) void tsl9_rf_flag_9edc(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lbu a0, 180(gp) # original 0x9edc\n"
        ".option rvc\n"
        "ret # original 0x9ee0\n"
        ".option pop\n"
    );
}

/* Original 0x1049a..0x104ae: 5 instructions, 20 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_rf_cancel_1049a"))) void tsl9_rf_cancel_1049a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Lrf46_pc_1049a:\n"
        "auipc a5, %pcrel_hi(__tsl9_state_bfb4) # original 0x1049a\n"
        "sb zero, %pcrel_lo(.Lrf46_pc_1049a)(a5) # original 0x1049e\n"
        ".Lrf46_pc_104a2:\n"
        "auipc a0, 0 # original 0x104a2\n"
        ".reloc .Lrf46_pc_104a2, R_RISCV_PCREL_HI20, tsl9_rf_cancel_1049a\n"
        ".Lrf46_lo_104a6:\n"
        "addi a0, a0, 0 # original 0x104a6\n"
        ".reloc .Lrf46_lo_104a6, R_RISCV_PCREL_LO12_I, .Lrf46_pc_104a2\n"
        "jal zero, tsl9_internal_scheduler_cancel_908e # original 0x104aa\n"
        ".option pop\n"
    );
}

/* Original 0x16f4a..0x17024: 77 instructions, 218 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_rf_schedule_16f4a"))) void tsl9_rf_schedule_16f4a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0x16f4a\n"
        "sw ra, 12(sp) # original 0x16f4c\n"
        "sw s0, 8(sp) # original 0x16f4e\n"
        "sw s1, 4(sp) # original 0x16f50\n"
        ".option norvc\n"
        "jal ra, tsl9_rf_enabled_843a # original 0x16f52\n"
        ".option rvc\n"
        "beqz a0, .Lrf46_16f4a_16fee # original 0x16f56\n"
        ".option norvc\n"
        "addi s1, gp, 84 # original 0x16f58\n"
        ".option rvc\n"
        "lw a5, 0(s1) # original 0x16f5c\n"
        "li a4, 15 # original 0x16f5e\n"
        ".option norvc\n"
        "lbu a5, 3(a5) # original 0x16f60\n"
        ".option rvc\n"
        "andi a5, a5, 15 # original 0x16f64\n"
        ".option norvc\n"
        "beq a5, a4, .Lrf46_16f4a_16fd6 # original 0x16f66\n"
        ".Lrf46_16f4a_16f6a:\n"
        ".option rvc\n"
        "lw a5, 0(s1) # original 0x16f6a\n"
        ".option norvc\n"
        "lbu s0, 3(a5) # original 0x16f6c\n"
        ".option rvc\n"
        "li a5, 15 # original 0x16f70\n"
        "andi s0, s0, 15 # original 0x16f72\n"
        ".option norvc\n"
        "bne s0, a5, .Lrf46_16f4a_16f7a # original 0x16f74\n"
        ".option rvc\n"
        "li s0, 1 # original 0x16f78\n"
        ".Lrf46_16f4a_16f7a:\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x16f7a\n"
        ".option rvc\n"
        "lw a5, 56(a5) # original 0x16f7e\n"
        "jalr a5 # original 0x16f80\n"
        "li a5, 1 # original 0x16f82\n"
        ".option norvc\n"
        "bltu a5, s0, .Lrf46_16f4a_16ff8 # original 0x16f84\n"
        "li a5, 1001 # original 0x16f88\n"
        "remu a0, a0, a5 # original 0x16f8c\n"
        "li s0, 2000 # original 0x16f90\n"
        ".Lrf46_16f4a_16f94:\n"
        ".option rvc\n"
        "lw a5, 0(s1) # original 0x16f94\n"
        ".option norvc\n"
        "lbu a5, 4(a5) # original 0x16f96\n"
        ".option rvc\n"
        "andi a5, a5, 1 # original 0x16f9a\n"
        "beqz a5, .Lrf46_16f4a_16fa0 # original 0x16f9c\n"
        "add s0, s0, a0 # original 0x16f9e\n"
        ".Lrf46_16f4a_16fa0:\n"
        ".option norvc\n"
        "li a2, 1000 # original 0x16fa0\n"
        "lui s1, 0x40 # original 0x16fa4\n"
        ".option rvc\n"
        "lw a5, 88(s1) # original 0x16fa8\n"
        "li a1, 1 # original 0x16faa\n"
        ".option norvc\n"
        "lbu a0, 365(gp) # original 0x16fac\n"
        "mul s0, s0, a2 # original 0x16fb0\n"
        "li a2, 625 # original 0x16fb4\n"
        "divu a2, s0, a2 # original 0x16fb8\n"
        ".option rvc\n"
        "jalr a5 # original 0x16fbc\n"
        "lw s0, 8(sp) # original 0x16fbe\n"
        ".option norvc\n"
        "lw t1, 88(s1) # original 0x16fc0\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0x16fc4\n"
        "lw s1, 4(sp) # original 0x16fc6\n"
        ".option norvc\n"
        "lbu a0, 365(gp) # original 0x16fc8\n"
        "li a2, 80 # original 0x16fcc\n"
        ".option rvc\n"
        "li a1, 4 # original 0x16fd0\n"
        "addi sp, sp, 16 # original 0x16fd2\n"
        "jr t1 # original 0x16fd4\n"
        ".Lrf46_16f4a_16fd6:\n"
        "li a0, 1 # original 0x16fd6\n"
        ".option norvc\n"
        "jal ra, tsl9_internal_gate_8214 # original 0x16fd8\n"
        ".option rvc\n"
        "beqz a0, .Lrf46_16f4a_16f6a # original 0x16fdc\n"
        "lw a5, 0(s1) # original 0x16fde\n"
        ".option norvc\n"
        "lbu a5, 8(a5) # original 0x16fe0\n"
        ".option rvc\n"
        "andi a5, a5, 16 # original 0x16fe4\n"
        "beqz a5, .Lrf46_16f4a_16fee # original 0x16fe6\n"
        ".option norvc\n"
        "jal ra, tsl9_rf_flag_9edc # original 0x16fe8\n"
        ".option rvc\n"
        "bnez a0, .Lrf46_16f4a_16f6a # original 0x16fec\n"
        ".Lrf46_16f4a_16fee:\n"
        "lw ra, 12(sp) # original 0x16fee\n"
        "lw s0, 8(sp) # original 0x16ff0\n"
        "lw s1, 4(sp) # original 0x16ff2\n"
        "addi sp, sp, 16 # original 0x16ff4\n"
        "ret # original 0x16ff6\n"
        ".Lrf46_16f4a_16ff8:\n"
        "li a5, 2 # original 0x16ff8\n"
        ".option norvc\n"
        "bne s0, a5, .Lrf46_16f4a_1700e # original 0x16ffa\n"
        "li a5, 2001 # original 0x16ffe\n"
        ".option rvc\n"
        "lui s0, 0x1 # original 0x17002\n"
        ".option norvc\n"
        "remu a0, a0, a5 # original 0x17004\n"
        "addi s0, s0, -1096 # original 0x17008\n"
        ".option rvc\n"
        "j .Lrf46_16f4a_16f94 # original 0x1700c\n"
        ".Lrf46_16f4a_1700e:\n"
        "lui a5, 0x1 # original 0x1700e\n"
        ".option norvc\n"
        "addi a2, a5, 904 # original 0x17010\n"
        ".option rvc\n"
        "addi s0, s0, -2 # original 0x17014\n"
        ".option norvc\n"
        "addi a5, a5, 905 # original 0x17016\n"
        "mul s0, s0, a2 # original 0x1701a\n"
        "remu a0, a0, a5 # original 0x1701e\n"
        ".option rvc\n"
        "j .Lrf46_16f4a_16f94 # original 0x17022\n"
        ".option pop\n"
    );
}

/* Original 0x17048..0x170e2: 58 instructions, 154 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_rf_control_17048"))) void tsl9_rf_control_17048(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0x17048\n"
        "sw s0, 8(sp) # original 0x1704a\n"
        "sw s1, 4(sp) # original 0x1704c\n"
        "sw ra, 12(sp) # original 0x1704e\n"
        "mv s0, a0 # original 0x17050\n"
        "mv s1, a1 # original 0x17052\n"
        "bnez a0, .Lrf46_17048_1709a # original 0x17054\n"
        ".Lrf46_17048_17056:\n"
        ".option norvc\n"
        "sb s0, 364(gp) # original 0x17056\n"
        "jal ra, tsl9_rf_schedule_16f4a # original 0x1705a\n"
        ".option rvc\n"
        "beqz s1, .Lrf46_17048_17066 # original 0x1705e\n"
        "mv a0, s0 # original 0x17060\n"
        ".option norvc\n"
        "jal ra, tsl9_timer_mode_9770 # original 0x17062\n"
        ".Lrf46_17048_17066:\n"
        ".option rvc\n"
        "beqz s0, .Lrf46_17048_170aa # original 0x17066\n"
        ".option norvc\n"
        "addi a5, gp, 84 # original 0x17068\n"
        ".option rvc\n"
        "lw a5, 0(a5) # original 0x1706c\n"
        ".option norvc\n"
        "lbu a5, 7(a5) # original 0x1706e\n"
        ".option rvc\n"
        "andi a5, a5, 7 # original 0x17072\n"
        "beqz a5, .Lrf46_17048_170a0 # original 0x17074\n"
        ".option norvc\n"
        "lui a2, 0xea # original 0x17076\n"
        "addi a2, a2, 1536 # original 0x1707a\n"
        "mul a2, a5, a2 # original 0x1707e\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0x17082\n"
        ".option norvc\n"
        "lui a4, 0x40 # original 0x17084\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0x17088\n"
        "lw s1, 4(sp) # original 0x1708a\n"
        ".option norvc\n"
        "lw t1, 88(a4) # original 0x1708c\n"
        "lbu a0, 365(gp) # original 0x17090\n"
        ".option rvc\n"
        "li a1, 2 # original 0x17094\n"
        "addi sp, sp, 16 # original 0x17096\n"
        "jr t1 # original 0x17098\n"
        ".Lrf46_17048_1709a:\n"
        ".option norvc\n"
        "jal ra, tsl9_rf_flag_81aa # original 0x1709a\n"
        ".option rvc\n"
        "bnez a0, .Lrf46_17048_17056 # original 0x1709e\n"
        ".Lrf46_17048_170a0:\n"
        "lw ra, 12(sp) # original 0x170a0\n"
        "lw s0, 8(sp) # original 0x170a2\n"
        "lw s1, 4(sp) # original 0x170a4\n"
        "addi sp, sp, 16 # original 0x170a6\n"
        "ret # original 0x170a8\n"
        ".Lrf46_17048_170aa:\n"
        ".option norvc\n"
        "lui s0, 0x40 # original 0x170aa\n"
        ".option rvc\n"
        "lw a5, 92(s0) # original 0x170ae\n"
        "li a1, 2 # original 0x170b0\n"
        ".option norvc\n"
        "lbu a0, 365(gp) # original 0x170b2\n"
        ".option rvc\n"
        "jalr a5 # original 0x170b6\n"
        "lw a5, 92(s0) # original 0x170b8\n"
        "li a1, 1 # original 0x170ba\n"
        ".option norvc\n"
        "lbu a0, 365(gp) # original 0x170bc\n"
        ".option rvc\n"
        "jalr a5 # original 0x170c0\n"
        "li a3, 0 # original 0x170c2\n"
        "li a2, 20 # original 0x170c4\n"
        "li a1, 0 # original 0x170c6\n"
        ".option norvc\n"
        ".Lrf46_pc_170c8:\n"
        "auipc a0, %pcrel_hi(tsl9_runtime_unported_13b5c) # original 0x170c8\n"
        "addi a0, a0, %pcrel_lo(.Lrf46_pc_170c8) # original 0x170cc\n"
        "jal ra, tsl9_internal_scheduler_register_9102 # original 0x170d0\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0x170d4\n"
        "lw ra, 12(sp) # original 0x170d6\n"
        "lw s1, 4(sp) # original 0x170d8\n"
        "li a0, 0 # original 0x170da\n"
        "addi sp, sp, 16 # original 0x170dc\n"
        ".option norvc\n"
        "jal zero, tsl9_rf_cancel_1049a # original 0x170de\n"
        ".option pop\n"
    );
}

/* Original 0x17176..0x171c2: 29 instructions, 76 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_17176"))) void tsl9_rf_initialize(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0x17176\n"
        "sw s0, 8(sp) # original 0x17178\n"
        ".option norvc\n"
        "lui s0, 0x40 # original 0x1717a\n"
        ".option rvc\n"
        "lw a5, 72(s0) # original 0x1717e\n"
        "sw ra, 12(sp) # original 0x17180\n"
        "li a2, 1 # original 0x17182\n"
        "li a1, 0 # original 0x17184\n"
        ".option norvc\n"
        "addi a0, gp, 364 # original 0x17186\n"
        ".option rvc\n"
        "jalr a5 # original 0x1718a\n"
        ".option norvc\n"
        "lw a5, 128(s0) # original 0x1718c\n"
        ".Lrf46_pc_17190:\n"
        "auipc a0, %pcrel_hi(tsl9_runtime_unported_170e2) # original 0x17190\n"
        "addi a0, a0, %pcrel_lo(.Lrf46_pc_17190) # original 0x17194\n"
        ".option rvc\n"
        "jalr a5 # original 0x17198\n"
        ".option norvc\n"
        "sb a0, 365(gp) # original 0x1719a\n"
        "addi a5, gp, 84 # original 0x1719e\n"
        ".option rvc\n"
        "lw a5, 0(a5) # original 0x171a2\n"
        ".option norvc\n"
        "lbu a5, 6(a5) # original 0x171a4\n"
        ".option rvc\n"
        "andi a5, a5, 1 # original 0x171a8\n"
        "beqz a5, .Lrf46_17176_171ba # original 0x171aa\n"
        "lw s0, 8(sp) # original 0x171ac\n"
        "lw ra, 12(sp) # original 0x171ae\n"
        "li a1, 0 # original 0x171b0\n"
        "li a0, 1 # original 0x171b2\n"
        "addi sp, sp, 16 # original 0x171b4\n"
        ".option norvc\n"
        "jal zero, tsl9_rf_control_17048 # original 0x171b6\n"
        ".Lrf46_17176_171ba:\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0x171ba\n"
        "lw s0, 8(sp) # original 0x171bc\n"
        "addi sp, sp, 16 # original 0x171be\n"
        "ret # original 0x171c0\n"
        ".option pop\n"
    );
}

/* Same original entry, shared across translation units without a duplicate body. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_rf_cancel_1049a(void)
    __attribute__((alias("tsl9_rf_cancel_1049a"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R61: strong hidden aliases share the original function body. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_timer_prepare_93ee(void)
    __attribute__((alias("tsl9_timer_prepare_93ee"), visibility("hidden"), used));
extern void tsl9_internal_timer_start_9388(void)
    __attribute__((alias("tsl9_timer_start_9388"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R63: original shared entry aliases, no duplicated body. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_rf_enabled_843a(void)
    __attribute__((alias("tsl9_rf_enabled_843a"), visibility("hidden"), used));
extern void tsl9_internal_timer_mode_9770(void)
    __attribute__((alias("tsl9_timer_mode_9770"), visibility("hidden"), used));
extern void tsl9_internal_rf_control_17048(void)
    __attribute__((alias("tsl9_rf_control_17048"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R73 exact-body internal aliases; no additional instructions or storage. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_rf_schedule_16f4a(void)
    __attribute__((alias("tsl9_rf_schedule_16f4a"),visibility("hidden"),used));
#ifdef __cplusplus
}
#endif
