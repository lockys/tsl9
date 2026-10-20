#include "target_board_init.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "This module requires the original RV32 register/CSR/MMIO ABI."
#endif
#define TSL9_NATIVE __attribute__((naked, noinline, used))
/* Readable native instruction reconstruction in C11/C++17.
 * No embedded firmware array, dummy call target, memory allocation, or clock guess.
 * Exact original register side effects, instruction widths and MMIO ordering matter.
 * Helpers use the original assembly a0=mask/a1=enable ABI; they are private.
 */
static void tsl9_board_rcc_apb2_enable_18e78(void) __asm__("tsl9_board_rcc_apb2_enable_18e78") TSL9_NATIVE;
static void tsl9_board_rcc_apb1_enable_18e96(void) __asm__("tsl9_board_rcc_apb1_enable_18e96") TSL9_NATIVE;
static void tsl9_board_rcc_apb2_reset_18eb4(void) __asm__("tsl9_board_rcc_apb2_reset_18eb4") TSL9_NATIVE;
static void tsl9_board_rcc_apb1_reset_18ed2(void) __asm__("tsl9_board_rcc_apb1_reset_18ed2") TSL9_NATIVE;

/* Original 0x9a20..0x9ab0: 46 instructions, 144 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_9a20"))) void tsl9_board_clock_irq_init(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0x9a20\n"
        ".option rvc\n"
        "sw s2, 0(sp) # original 0x9a22\n"
        ".option rvc\n"
        "sw ra, 12(sp) # original 0x9a24\n"
        ".option rvc\n"
        "sw s0, 8(sp) # original 0x9a26\n"
        ".option rvc\n"
        "sw s1, 4(sp) # original 0x9a28\n"
        ".option norvc\n"
        "li s2, 136 # original 0x9a2a\n"
        ".option norvc\n"
        "csrc 0x800, s2 # original 0x9a2e\n"
        ".option norvc\n"
        "lui s1, 0x2020 # original 0x9a32\n"
        ".option norvc\n"
        "addi a0, s1, 6 # original 0x9a36\n"
        ".option rvc\n"
        "li a1, 1 # original 0x9a3a\n"
        ".option norvc\n"
        "jal ra, tsl9_board_rcc_apb1_enable_18e96 # original 0x9a3c\n"
        ".option rvc\n"
        "lui s0, 0x1 # original 0x9a40\n"
        ".option norvc\n"
        "addi a0, s0, 29 # original 0x9a42\n"
        ".option rvc\n"
        "li a1, 1 # original 0x9a46\n"
        ".option norvc\n"
        "jal ra, tsl9_board_rcc_apb2_enable_18e78 # original 0x9a48\n"
        ".option norvc\n"
        "addi a0, s1, 6 # original 0x9a4c\n"
        ".option rvc\n"
        "li a1, 1 # original 0x9a50\n"
        ".option norvc\n"
        "jal ra, tsl9_board_rcc_apb1_reset_18ed2 # original 0x9a52\n"
        ".option norvc\n"
        "addi a0, s1, 6 # original 0x9a56\n"
        ".option rvc\n"
        "li a1, 0 # original 0x9a5a\n"
        ".option norvc\n"
        "jal ra, tsl9_board_rcc_apb1_reset_18ed2 # original 0x9a5c\n"
        ".option norvc\n"
        "addi a0, s0, 29 # original 0x9a60\n"
        ".option rvc\n"
        "li a1, 1 # original 0x9a64\n"
        ".option norvc\n"
        "jal ra, tsl9_board_rcc_apb2_reset_18eb4 # original 0x9a66\n"
        ".option rvc\n"
        "li a1, 0 # original 0x9a6a\n"
        ".option norvc\n"
        "addi a0, s0, 29 # original 0x9a6c\n"
        ".option norvc\n"
        "jal ra, tsl9_board_rcc_apb2_reset_18eb4 # original 0x9a70\n"
        ".option norvc\n"
        "lui a5, 0xe000e # original 0x9a74\n"
        ".option norvc\n"
        "sb zero, 1069(a5) # original 0x9a78\n"
        ".option rvc\n"
        "lui a4, 0x2 # original 0x9a7c\n"
        ".option norvc\n"
        "sw a4, 260(a5) # original 0x9a7e\n"
        ".option norvc\n"
        "li a4, 32 # original 0x9a82\n"
        ".option norvc\n"
        "sb a4, 1060(a5) # original 0x9a86\n"
        ".option rvc\n"
        "li a4, 16 # original 0x9a8a\n"
        ".option norvc\n"
        "sw a4, 260(a5) # original 0x9a8c\n"
        ".option norvc\n"
        "li a4, 48 # original 0x9a90\n"
        ".option norvc\n"
        "sb a4, 1063(a5) # original 0x9a94\n"
        ".option norvc\n"
        "li a4, 128 # original 0x9a98\n"
        ".option norvc\n"
        "sw a4, 260(a5) # original 0x9a9c\n"
        ".option norvc\n"
        "csrs 0x800, s2 # original 0x9aa0\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0x9aa4\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0x9aa6\n"
        ".option rvc\n"
        "lw s1, 4(sp) # original 0x9aa8\n"
        ".option rvc\n"
        "lw s2, 0(sp) # original 0x9aaa\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 0x9aac\n"
        ".option rvc\n"
        "ret # original 0x9aae\n"
        ".option pop\n"
    );
}

/* Original 0x19490..0x194b8: 11 instructions, 40 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_19490"))) void tsl9_board_delay_calibrate(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "addi a5, gp, 112 # original 0x19490\n"
        ".option rvc\n"
        "lw a5, 0(a5) # original 0x19494\n"
        ".option norvc\n"
        "lui a4, 0x7a1 # original 0x19496\n"
        ".option norvc\n"
        "addi a4, a4, 512 # original 0x1949a\n"
        ".option norvc\n"
        "divu a5, a5, a4 # original 0x1949e\n"
        ".option norvc\n"
        "andi a5, a5, 255 # original 0x194a2\n"
        ".option norvc\n"
        "sb a5, 382(gp) # original 0x194a6\n"
        ".option norvc\n"
        "li a4, 1000 # original 0x194aa\n"
        ".option norvc\n"
        "mul a5, a5, a4 # original 0x194ae\n"
        ".option norvc\n"
        "sh a5, 380(gp) # original 0x194b2\n"
        ".option rvc\n"
        "ret # original 0x194b6\n"
        ".option pop\n"
    );
}

/* Original 0x9e66..0x9e8e: 15 instructions, 40 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_9e66"))) void tsl9_board_watchdog_init(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "lui a4, 0x5 # original 0x9e66\n"
        ".option norvc\n"
        "lui a5, 0x40003 # original 0x9e68\n"
        ".option norvc\n"
        "addi a4, a4, 1365 # original 0x9e6c\n"
        ".option rvc\n"
        "sw a4, 0(a5) # original 0x9e70\n"
        ".option rvc\n"
        "li a4, 3 # original 0x9e72\n"
        ".option rvc\n"
        "sw a4, 4(a5) # original 0x9e74\n"
        ".option norvc\n"
        "li a4, 1500 # original 0x9e76\n"
        ".option rvc\n"
        "sw a4, 8(a5) # original 0x9e7a\n"
        ".option rvc\n"
        "lui a4, 0xb # original 0x9e7c\n"
        ".option norvc\n"
        "addi a4, a4, -1366 # original 0x9e7e\n"
        ".option rvc\n"
        "sw a4, 0(a5) # original 0x9e82\n"
        ".option rvc\n"
        "lui a4, 0xd # original 0x9e84\n"
        ".option norvc\n"
        "addi a4, a4, -820 # original 0x9e86\n"
        ".option rvc\n"
        "sw a4, 0(a5) # original 0x9e8a\n"
        ".option rvc\n"
        "ret # original 0x9e8c\n"
        ".option pop\n"
    );
}

/* Original 0x18e78..0x18e96: 12 instructions, 30 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_board_rcc_apb2_enable_18e78"))) void tsl9_board_rcc_apb2_enable_18e78(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "beqz a1, .Ltsl9_r37_18e78_18e86 # original 0x18e78\n"
        ".option norvc\n"
        "lui a4, 0x40021 # original 0x18e7a\n"
        ".option rvc\n"
        "lw a5, 24(a4) # original 0x18e7e\n"
        ".option rvc\n"
        "or a0, a0, a5 # original 0x18e80\n"
        ".option rvc\n"
        "sw a0, 24(a4) # original 0x18e82\n"
        ".option rvc\n"
        "ret # original 0x18e84\n"
        ".Ltsl9_r37_18e78_18e86:\n"
        ".option norvc\n"
        "lui a5, 0x40021 # original 0x18e86\n"
        ".option rvc\n"
        "lw a4, 24(a5) # original 0x18e8a\n"
        ".option norvc\n"
        "not a0, a0 # original 0x18e8c\n"
        ".option rvc\n"
        "and a0, a0, a4 # original 0x18e90\n"
        ".option rvc\n"
        "sw a0, 24(a5) # original 0x18e92\n"
        ".option rvc\n"
        "ret # original 0x18e94\n"
        ".option pop\n"
    );
}

/* Original 0x18e96..0x18eb4: 12 instructions, 30 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_board_rcc_apb1_enable_18e96"))) void tsl9_board_rcc_apb1_enable_18e96(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "beqz a1, .Ltsl9_r37_18e96_18ea4 # original 0x18e96\n"
        ".option norvc\n"
        "lui a4, 0x40021 # original 0x18e98\n"
        ".option rvc\n"
        "lw a5, 28(a4) # original 0x18e9c\n"
        ".option rvc\n"
        "or a0, a0, a5 # original 0x18e9e\n"
        ".option rvc\n"
        "sw a0, 28(a4) # original 0x18ea0\n"
        ".option rvc\n"
        "ret # original 0x18ea2\n"
        ".Ltsl9_r37_18e96_18ea4:\n"
        ".option norvc\n"
        "lui a5, 0x40021 # original 0x18ea4\n"
        ".option rvc\n"
        "lw a4, 28(a5) # original 0x18ea8\n"
        ".option norvc\n"
        "not a0, a0 # original 0x18eaa\n"
        ".option rvc\n"
        "and a0, a0, a4 # original 0x18eae\n"
        ".option rvc\n"
        "sw a0, 28(a5) # original 0x18eb0\n"
        ".option rvc\n"
        "ret # original 0x18eb2\n"
        ".option pop\n"
    );
}

/* Original 0x18eb4..0x18ed2: 12 instructions, 30 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_board_rcc_apb2_reset_18eb4"))) void tsl9_board_rcc_apb2_reset_18eb4(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "beqz a1, .Ltsl9_r37_18eb4_18ec2 # original 0x18eb4\n"
        ".option norvc\n"
        "lui a4, 0x40021 # original 0x18eb6\n"
        ".option rvc\n"
        "lw a5, 12(a4) # original 0x18eba\n"
        ".option rvc\n"
        "or a0, a0, a5 # original 0x18ebc\n"
        ".option rvc\n"
        "sw a0, 12(a4) # original 0x18ebe\n"
        ".option rvc\n"
        "ret # original 0x18ec0\n"
        ".Ltsl9_r37_18eb4_18ec2:\n"
        ".option norvc\n"
        "lui a5, 0x40021 # original 0x18ec2\n"
        ".option rvc\n"
        "lw a4, 12(a5) # original 0x18ec6\n"
        ".option norvc\n"
        "not a0, a0 # original 0x18ec8\n"
        ".option rvc\n"
        "and a0, a0, a4 # original 0x18ecc\n"
        ".option rvc\n"
        "sw a0, 12(a5) # original 0x18ece\n"
        ".option rvc\n"
        "ret # original 0x18ed0\n"
        ".option pop\n"
    );
}

/* Original 0x18ed2..0x18ef0: 12 instructions, 30 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_board_rcc_apb1_reset_18ed2"))) void tsl9_board_rcc_apb1_reset_18ed2(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "beqz a1, .Ltsl9_r37_18ed2_18ee0 # original 0x18ed2\n"
        ".option norvc\n"
        "lui a4, 0x40021 # original 0x18ed4\n"
        ".option rvc\n"
        "lw a5, 16(a4) # original 0x18ed8\n"
        ".option rvc\n"
        "or a0, a0, a5 # original 0x18eda\n"
        ".option rvc\n"
        "sw a0, 16(a4) # original 0x18edc\n"
        ".option rvc\n"
        "ret # original 0x18ede\n"
        ".Ltsl9_r37_18ed2_18ee0:\n"
        ".option norvc\n"
        "lui a5, 0x40021 # original 0x18ee0\n"
        ".option rvc\n"
        "lw a4, 16(a5) # original 0x18ee4\n"
        ".option norvc\n"
        "not a0, a0 # original 0x18ee6\n"
        ".option rvc\n"
        "and a0, a0, a4 # original 0x18eea\n"
        ".option rvc\n"
        "sw a0, 16(a5) # original 0x18eec\n"
        ".option rvc\n"
        "ret # original 0x18eee\n"
        ".option pop\n"
    );
}

/* R41: one hidden internal identity for the existing private body.
 * This is a symbol alias, not a duplicate implementation or fixed address. */
void tsl9_internal_rcc_apb1_18e96(void) __asm__("tsl9_internal_rcc_apb1_18e96")
    __attribute__((alias("tsl9_board_rcc_apb1_enable_18e96"), visibility("hidden"), used));

/* R59: exact-body hidden aliases for HAL callbacks; no duplicated code. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_rcc_apb2_18e78(void)
    __attribute__((alias("tsl9_board_rcc_apb2_enable_18e78"), visibility("hidden"), used));
extern void tsl9_internal_rcc_apb2_reset_18eb4(void)
    __attribute__((alias("tsl9_board_rcc_apb2_reset_18eb4"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R75 exact-entry hidden aliases; existing bodies unchanged. */
#if defined(__riscv) && __riscv_xlen == 32
__asm__(
        ".global tsl9_internal_r75_18ed2\n"
        ".hidden tsl9_internal_r75_18ed2\n"
        ".set tsl9_internal_r75_18ed2, tsl9_board_rcc_apb1_reset_18ed2\n"
);
#endif
