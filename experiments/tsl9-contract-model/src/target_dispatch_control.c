#include "target_dispatch_control.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "RV32 target only; do not execute on the host."
#endif
#define TSL9_NATIVE __attribute__((naked,noinline,used))
/* Static V4.1.00 reconstruction; no memory allocation or hardware compatibility claim.
 * ROM slot 4004C and opaque address 1041A remain unbound physical dependencies. */
#ifdef __cplusplus
extern "C" {
#endif
extern unsigned char __tsl9_state_bfb4[];
extern unsigned char tsl9_control_reference_1041a[];
extern void tsl9_internal_rf_cancel_1049a(void);
extern void tsl9_internal_scheduler_register_9102(void);
extern void tsl9_runtime_unported_105c8(void);
extern void tsl9_runtime_unported_8202(void);
#ifdef __cplusplus
}
#endif
static TSL9_NATIVE void tsl9_control_limit_8282(void) __asm__("tsl9_control_limit_8282");
static TSL9_NATIVE void tsl9_control_zero_1063c(void) __asm__("tsl9_control_zero_1063c");

/* Original 0x8282..0x8294; 5 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_control_limit_8282"))) void tsl9_control_limit_8282(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Lctl53pc_8282:\n"
        "auipc a0, %pcrel_hi(__tsl9_state_bfb4-4) # original 8282\n"
        ".option norvc\n"
        "lbu a0, %pcrel_lo(.Lctl53pc_8282)(a0) # original 8286\n"
        ".option norvc\n"
        "sltiu a0, a0, 4 # original 828a\n"
        ".option norvc\n"
        "xori a0, a0, 1 # original 828e\n"
        ".option rvc\n"
        "ret # original 8292\n"
        ".option pop\n"
    );
}

/* Original 0x829e..0x82c8; 16 instructions, 42 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_829e"))) void tsl9_runtime_unported_829e(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 829e\n"
        ".option norvc\n"
        "lw t1, 76(a5) # original 82a2\n"
        ".option rvc\n"
        "li a5, 12 # original 82a6\n"
        ".option norvc\n"
        "mul a1, a1, a5 # original 82a8\n"
        ".option norvc\n"
        ".Lctl53pc_82ac:\n"
        "auipc a5, %pcrel_hi(__tsl9_state_bfb4+512) # original 82ac\n"
        ".option norvc\n"
        "addi a5, a5, %pcrel_lo(.Lctl53pc_82ac) # original 82b0\n"
        ".option rvc\n"
        "mv a4, a2 # original 82b4\n"
        ".option rvc\n"
        "li a2, 12 # original 82b6\n"
        ".option rvc\n"
        "add a5, a5, a1 # original 82b8\n"
        ".option rvc\n"
        "beqz a0, .Lctl53_829e_82c2 # original 82ba\n"
        ".option rvc\n"
        "mv a1, a5 # original 82bc\n"
        ".option rvc\n"
        "mv a0, a4 # original 82be\n"
        ".Lctl53_829e_82c0:\n"
        ".option rvc\n"
        "jr t1 # original 82c0\n"
        ".Lctl53_829e_82c2:\n"
        ".option rvc\n"
        "mv a1, a4 # original 82c2\n"
        ".option rvc\n"
        "mv a0, a5 # original 82c4\n"
        ".option rvc\n"
        "j .Lctl53_829e_82c0 # original 82c6\n"
        ".option pop\n"
    );
}

/* Original 0x10564..0x10586; 12 instructions, 34 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_10564"))) void tsl9_runtime_unported_10564(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 10564\n"
        ".option rvc\n"
        "sw ra, 12(sp) # original 10566\n"
        ".option norvc\n"
        ".Lctl53call_10568:\n"
        ".reloc .Lctl53call_10568, R_RISCV_JAL, tsl9_control_limit_8282\n"
        ".4byte 0x000000ef # original 10568\n"
        ".option rvc\n"
        "bnez a0, .Lctl53_10564_10580 # original 1056c\n"
        ".option norvc\n"
        ".Lctl53pc_1056e:\n"
        "auipc a5, %pcrel_hi(__tsl9_state_bfb4-4) # original 1056e\n"
        ".option norvc\n"
        "lbu a5, %pcrel_lo(.Lctl53pc_1056e)(a5) # original 10572\n"
        ".option rvc\n"
        "addi a5, a5, 1 # original 10576\n"
        ".option norvc\n"
        ".Lctl53pc_10578:\n"
        "auipc a4, %pcrel_hi(__tsl9_state_bfb4-4) # original 10578\n"
        ".option norvc\n"
        "sb a5, %pcrel_lo(.Lctl53pc_10578)(a4) # original 1057c\n"
        ".Lctl53_10564_10580:\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 10580\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 10582\n"
        ".option rvc\n"
        "ret # original 10584\n"
        ".option pop\n"
    );
}

/* Original 0x1063c..0x10642; 2 instructions, 6 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_control_zero_1063c"))) void tsl9_control_zero_1063c(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "li a0, 0 # original 1063c\n"
        ".option norvc\n"
        "jal zero, tsl9_runtime_unported_105c8 # original 1063e\n"
        ".option pop\n"
    );
}

/* Original 0x10642..0x10692; 32 instructions, 80 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_10642"))) void tsl9_runtime_unported_10642(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -32 # original 10642\n"
        ".option rvc\n"
        "sw s0, 24(sp) # original 10644\n"
        ".option rvc\n"
        "mv s0, a0 # original 10646\n"
        ".option rvc\n"
        "mv a0, a4 # original 10648\n"
        ".option rvc\n"
        "sw s1, 20(sp) # original 1064a\n"
        ".option rvc\n"
        "sw ra, 28(sp) # original 1064c\n"
        ".option rvc\n"
        "sw a1, 12(sp) # original 1064e\n"
        ".option rvc\n"
        "mv s1, a2 # original 10650\n"
        ".option rvc\n"
        "jalr a3 # original 10652\n"
        ".option rvc\n"
        "beqz a0, .Lctl53_10642_1068c # original 10654\n"
        ".option norvc\n"
        "lbu a5, 0(s0) # original 10656\n"
        ".option rvc\n"
        "lw a1, 12(sp) # original 1065a\n"
        ".option rvc\n"
        "addi a5, a5, 1 # original 1065c\n"
        ".option norvc\n"
        "andi a5, a5, 255 # original 1065e\n"
        ".option norvc\n"
        "bleu a1, a5, .Lctl53_10642_10674 # original 10662\n"
        ".option norvc\n"
        "sb a5, 0(s0) # original 10666\n"
        ".Lctl53_10642_1066a:\n"
        ".option rvc\n"
        "lw ra, 28(sp) # original 1066a\n"
        ".option rvc\n"
        "lw s0, 24(sp) # original 1066c\n"
        ".option rvc\n"
        "lw s1, 20(sp) # original 1066e\n"
        ".option rvc\n"
        "addi sp, sp, 32 # original 10670\n"
        ".option rvc\n"
        "ret # original 10672\n"
        ".Lctl53_10642_10674:\n"
        ".option norvc\n"
        "sb zero, 0(s0) # original 10674\n"
        ".option rvc\n"
        "li a0, 0 # original 10678\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_8202 # original 1067a\n"
        ".option rvc\n"
        "lw s0, 24(sp) # original 1067e\n"
        ".option rvc\n"
        "lw ra, 28(sp) # original 10680\n"
        ".option rvc\n"
        "mv a0, s1 # original 10682\n"
        ".option rvc\n"
        "lw s1, 20(sp) # original 10684\n"
        ".option rvc\n"
        "addi sp, sp, 32 # original 10686\n"
        ".option norvc\n"
        "jal zero, tsl9_runtime_unported_105c8 # original 10688\n"
        ".Lctl53_10642_1068c:\n"
        ".option norvc\n"
        "sb zero, 0(s0) # original 1068c\n"
        ".option rvc\n"
        "j .Lctl53_10642_1066a # original 10690\n"
        ".option pop\n"
    );
}

/* Original 0x10692..0x106b8; 12 instructions, 38 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_10692"))) void tsl9_runtime_unported_10692(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "bnez a0, .Lctl53_10692_10696 # original 10692\n"
        ".option rvc\n"
        "li a0, 1 # original 10694\n"
        ".Lctl53_10692_10696:\n"
        ".option norvc\n"
        "li a2, 1000 # original 10696\n"
        ".option norvc\n"
        "mul a2, a0, a2 # original 1069a\n"
        ".option rvc\n"
        "li a5, 1 # original 1069e\n"
        ".option norvc\n"
        ".Lctl53pc_106a0:\n"
        "auipc a4, %pcrel_hi(__tsl9_state_bfb4) # original 106a0\n"
        ".option norvc\n"
        "sb a5, %pcrel_lo(.Lctl53pc_106a0)(a4) # original 106a4\n"
        ".option rvc\n"
        "li a3, 0 # original 106a8\n"
        ".option rvc\n"
        "li a1, 0 # original 106aa\n"
        ".option norvc\n"
        ".Lctl53pc_106ac:\n"
        "auipc a0, %pcrel_hi(tsl9_internal_rf_cancel_1049a) # original 106ac\n"
        ".option norvc\n"
        "addi a0, a0, %pcrel_lo(.Lctl53pc_106ac) # original 106b0\n"
        ".option norvc\n"
        "jal zero, tsl9_internal_scheduler_register_9102 # original 106b4\n"
        ".option pop\n"
    );
}

/* Original 0x106b8..0x106ec; 21 instructions, 52 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_106b8"))) void tsl9_runtime_unported_106b8(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 106b8\n"
        ".option rvc\n"
        "mv a5, a0 # original 106ba\n"
        ".option rvc\n"
        "mv a0, a1 # original 106bc\n"
        ".option rvc\n"
        "sw s0, 8(sp) # original 106be\n"
        ".option rvc\n"
        "sw ra, 12(sp) # original 106c0\n"
        ".option rvc\n"
        "jalr a5 # original 106c2\n"
        ".option rvc\n"
        "mv s0, a0 # original 106c4\n"
        ".option rvc\n"
        "beqz a0, .Lctl53_106b8_106e2 # original 106c6\n"
        ".option rvc\n"
        "li a0, 0 # original 106c8\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_8202 # original 106ca\n"
        ".option rvc\n"
        "li a3, 0 # original 106ce\n"
        ".option norvc\n"
        "li a2, 2000 # original 106d0\n"
        ".option rvc\n"
        "li a1, 0 # original 106d4\n"
        ".option norvc\n"
        ".Lctl53pc_106d6:\n"
        "auipc a0, %pcrel_hi(tsl9_control_zero_1063c) # original 106d6\n"
        ".option norvc\n"
        "addi a0, a0, %pcrel_lo(.Lctl53pc_106d6) # original 106da\n"
        ".option norvc\n"
        "jal ra, tsl9_internal_scheduler_register_9102 # original 106de\n"
        ".Lctl53_106b8_106e2:\n"
        ".option rvc\n"
        "mv a0, s0 # original 106e2\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 106e4\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 106e6\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 106e8\n"
        ".option rvc\n"
        "ret # original 106ea\n"
        ".option pop\n"
    );
}

/* Original 0x107b2..0x107c0; 4 instructions, 14 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_107b2"))) void tsl9_runtime_unported_107b2(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "mv a1, a0 # original 107b2\n"
        ".option norvc\n"
        ".Lctl53pc_107b4:\n"
        "auipc a0, %pcrel_hi(tsl9_control_reference_1041a) # original 107b4\n"
        ".option norvc\n"
        "addi a0, a0, %pcrel_lo(.Lctl53pc_107b4) # original 107b8\n"
        ".option norvc\n"
        ".Lctl53call_107bc:\n"
        ".reloc .Lctl53call_107bc, R_RISCV_JAL, tsl9_runtime_unported_106b8\n"
        ".4byte 0x0000006f # original 107bc\n"
        ".option pop\n"
    );
}

/* Shared complete original entries; strong hidden aliases do not duplicate code. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_control_zero_1063c(void)
    __attribute__((alias("tsl9_control_zero_1063c"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R75 exact-entry hidden aliases; existing bodies unchanged. */
#if defined(__riscv) && __riscv_xlen == 32
__asm__(
        ".global tsl9_internal_r75_8282\n"
        ".hidden tsl9_internal_r75_8282\n"
        ".set tsl9_internal_r75_8282, tsl9_control_limit_8282\n"
);
#endif
