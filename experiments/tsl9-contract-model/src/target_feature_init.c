#include "target_feature_init.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "Original RV32 feature state, ROM, GP and register contracts required"
#endif
#define TSL9_NATIVE __attribute__((naked, noinline, used))
/* Fixed server V4.1.00 instruction reconstruction, not physical/OTA proof.
 * Retain original initializer order, fresh ROM providers and raw registration a0.
 * Reuse state BFB4 with addend -4 for original clear origin BFB0; no allocation. */
#ifdef __cplusplus
extern "C" {
#endif
extern unsigned char __tsl9_feature_state_bed0[];
extern unsigned char __tsl9_feature_state_bee0[];
extern unsigned char __tsl9_feature_state_beec[];
extern unsigned char __tsl9_feature_state_befc[];
extern unsigned char __tsl9_feature_state_bf18[];
extern unsigned char __tsl9_feature_state_bf24[];
extern unsigned char __tsl9_feature_state_bf34[];
extern unsigned char __tsl9_feature_state_bf44[];
extern unsigned char __tsl9_feature_state_bf58[];
extern unsigned char __tsl9_feature_state_bf64[];
extern unsigned char __tsl9_feature_state_bf80[];
extern unsigned char __tsl9_feature_state_bf8c[];
extern unsigned char __tsl9_feature_state_bfa4[];
extern unsigned char __tsl9_feature_state_c91c[];
extern unsigned char __tsl9_state_bfb4[];
extern void tsl9_runtime_unported_aeec(void);
extern void tsl9_internal_tx_clear_c634(void);
#ifdef __cplusplus
}
#endif
static void tsl9_feature_init_a2a0(void) __asm__("tsl9_feature_init_a2a0") TSL9_NATIVE;
static void tsl9_feature_init_a936(void) __asm__("tsl9_feature_init_a936") TSL9_NATIVE;
static void tsl9_feature_init_aed6(void) __asm__("tsl9_feature_init_aed6") TSL9_NATIVE;
static void tsl9_feature_init_af18(void) __asm__("tsl9_feature_init_af18") TSL9_NATIVE;
static void tsl9_feature_init_b060(void) __asm__("tsl9_feature_init_b060") TSL9_NATIVE;
static void tsl9_feature_init_b46a(void) __asm__("tsl9_feature_init_b46a") TSL9_NATIVE;
static void tsl9_feature_init_c25a(void) __asm__("tsl9_feature_init_c25a") TSL9_NATIVE;
static void tsl9_feature_init_c516(void) __asm__("tsl9_feature_init_c516") TSL9_NATIVE;
static void tsl9_feature_init_cd08(void) __asm__("tsl9_feature_init_cd08") TSL9_NATIVE;
static void tsl9_feature_init_cf4c(void) __asm__("tsl9_feature_init_cf4c") TSL9_NATIVE;
static void tsl9_feature_init_cff4(void) __asm__("tsl9_feature_init_cff4") TSL9_NATIVE;
static void tsl9_feature_init_d0cc(void) __asm__("tsl9_feature_init_d0cc") TSL9_NATIVE;
static void tsl9_feature_init_d39c(void) __asm__("tsl9_feature_init_d39c") TSL9_NATIVE;
static void tsl9_feature_init_d514(void) __asm__("tsl9_feature_init_d514") TSL9_NATIVE;
static void tsl9_feature_init_d5e4(void) __asm__("tsl9_feature_init_d5e4") TSL9_NATIVE;
static void tsl9_feature_init_df2e(void) __asm__("tsl9_feature_init_df2e") TSL9_NATIVE;
static void tsl9_feature_init_ef6a(void) __asm__("tsl9_feature_init_ef6a") TSL9_NATIVE;
static void tsl9_feature_init_f6fe(void) __asm__("tsl9_feature_init_f6fe") TSL9_NATIVE;
static void tsl9_feature_init_f906(void) __asm__("tsl9_feature_init_f906") TSL9_NATIVE;
static void tsl9_feature_init_f9c2(void) __asm__("tsl9_feature_init_f9c2") TSL9_NATIVE;
static void tsl9_feature_init_fdfa(void) __asm__("tsl9_feature_init_fdfa") TSL9_NATIVE;
static void tsl9_feature_init_fee4(void) __asm__("tsl9_feature_init_fee4") TSL9_NATIVE;
static void tsl9_feature_init_1000a(void) __asm__("tsl9_feature_init_1000a") TSL9_NATIVE;
static void tsl9_feature_init_10128(void) __asm__("tsl9_feature_init_10128") TSL9_NATIVE;
static void tsl9_feature_init_10a9a(void) __asm__("tsl9_feature_init_10a9a") TSL9_NATIVE;
static void tsl9_feature_init_1836c(void) __asm__("tsl9_feature_init_1836c") TSL9_NATIVE;

/* Original 0xa2a0..0xa2b2: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_a2a0"))) void tsl9_feature_init_a2a0(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xa2a0\n"
        "lw t1, 72(a5) # original 0xa2a4\n"
        ".option rvc\n"
        "li a2, 5 # original 0xa2a8\n"
        "li a1, 0 # original 0xa2aa\n"
        ".option norvc\n"
        "addi a0, gp, 180 # original 0xa2ac\n"
        ".option rvc\n"
        "jr t1 # original 0xa2b0\n"
        ".option pop\n"
    );
}

/* Original 0xa936..0xa94c: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_a936"))) void tsl9_feature_init_a936(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xa936\n"
        "lw t1, 72(a5) # original 0xa93a\n"
        ".option rvc\n"
        "li a2, 13 # original 0xa93e\n"
        "li a1, 0 # original 0xa940\n"
        ".Lfi49_pair_a936_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bed0) # original 0xa942\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_a936_12) # original 0xa946\n"
        ".option rvc\n"
        "jr t1 # original 0xa94a\n"
        ".option pop\n"
    );
}

/* Original 0xaed6..0xaeec: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_aed6"))) void tsl9_feature_init_aed6(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xaed6\n"
        "lw t1, 72(a5) # original 0xaeda\n"
        ".option rvc\n"
        "li a2, 10 # original 0xaede\n"
        "li a1, 0 # original 0xaee0\n"
        ".Lfi49_pair_aed6_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bee0) # original 0xaee2\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_aed6_12) # original 0xaee6\n"
        ".option rvc\n"
        "jr t1 # original 0xaeea\n"
        ".option pop\n"
    );
}

/* Original 0xaf18..0xaf66: 28 instructions, 78 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_af18"))) void tsl9_feature_init_af18(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0xaf18\n"
        "sw s1, 4(sp) # original 0xaf1a\n"
        ".option norvc\n"
        "lui s1, 0x40 # original 0xaf1c\n"
        ".option rvc\n"
        "lw a5, 72(s1) # original 0xaf20\n"
        "sw s0, 8(sp) # original 0xaf22\n"
        ".option norvc\n"
        "addi s0, gp, 192 # original 0xaf24\n"
        ".option rvc\n"
        "sw ra, 12(sp) # original 0xaf28\n"
        "li a2, 4 # original 0xaf2a\n"
        "li a1, 0 # original 0xaf2c\n"
        "mv a0, s0 # original 0xaf2e\n"
        "jalr a5 # original 0xaf30\n"
        "li a5, 3 # original 0xaf32\n"
        ".option norvc\n"
        "sb a5, 1(s0) # original 0xaf34\n"
        "li a5, 771 # original 0xaf38\n"
        "sh a5, 2(s0) # original 0xaf3c\n"
        "lw a5, 128(s1) # original 0xaf40\n"
        ".Lfi49_pair_af18_44:\n"
        "auipc a0, %pcrel_hi(tsl9_runtime_unported_aeec) # original 0xaf44\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_af18_44) # original 0xaf48\n"
        ".option rvc\n"
        "jalr a5 # original 0xaf4c\n"
        ".option norvc\n"
        "sb a0, 0(s0) # original 0xaf4e\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0xaf52\n"
        ".option norvc\n"
        "lw t1, 556(s1) # original 0xaf54\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0xaf58\n"
        "lw s1, 4(sp) # original 0xaf5a\n"
        ".option norvc\n"
        "li a2, 1600 # original 0xaf5c\n"
        ".option rvc\n"
        "li a1, 1 # original 0xaf60\n"
        "addi sp, sp, 16 # original 0xaf62\n"
        "jr t1 # original 0xaf64\n"
        ".option pop\n"
    );
}

/* Original 0xb060..0xb072: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_b060"))) void tsl9_feature_init_b060(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xb060\n"
        "lw t1, 72(a5) # original 0xb064\n"
        ".option rvc\n"
        "li a2, 3 # original 0xb068\n"
        "li a1, 0 # original 0xb06a\n"
        ".option norvc\n"
        "addi a0, gp, 196 # original 0xb06c\n"
        ".option rvc\n"
        "jr t1 # original 0xb070\n"
        ".option pop\n"
    );
}

/* Original 0xb46a..0xb480: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_b46a"))) void tsl9_feature_init_b46a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xb46a\n"
        "lw t1, 72(a5) # original 0xb46e\n"
        ".option rvc\n"
        "li a2, 16 # original 0xb472\n"
        "li a1, 0 # original 0xb474\n"
        ".Lfi49_pair_b46a_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_beec) # original 0xb476\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_b46a_12) # original 0xb47a\n"
        ".option rvc\n"
        "jr t1 # original 0xb47e\n"
        ".option pop\n"
    );
}

/* Original 0xc25a..0xc270: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_c25a"))) void tsl9_feature_init_c25a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xc25a\n"
        "lw t1, 72(a5) # original 0xc25e\n"
        ".option rvc\n"
        "li a2, 28 # original 0xc262\n"
        "li a1, 0 # original 0xc264\n"
        ".Lfi49_pair_c25a_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_befc) # original 0xc266\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_c25a_12) # original 0xc26a\n"
        ".option rvc\n"
        "jr t1 # original 0xc26e\n"
        ".option pop\n"
    );
}

/* Original 0xc516..0xc544: 18 instructions, 46 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_c516"))) void tsl9_feature_init_c516(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0xc516\n"
        "sw s0, 8(sp) # original 0xc518\n"
        ".option norvc\n"
        "lui s0, 0x40 # original 0xc51a\n"
        ".option rvc\n"
        "lw a5, 72(s0) # original 0xc51e\n"
        "sw ra, 12(sp) # original 0xc520\n"
        "li a2, 12 # original 0xc522\n"
        "li a1, 0 # original 0xc524\n"
        ".Lfi49_pair_c516_16:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf18) # original 0xc526\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_c516_16) # original 0xc52a\n"
        ".option rvc\n"
        "jalr a5 # original 0xc52e\n"
        ".option norvc\n"
        "lw t1, 72(s0) # original 0xc530\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0xc534\n"
        "lw ra, 12(sp) # original 0xc536\n"
        "li a2, 8 # original 0xc538\n"
        "li a1, 0 # original 0xc53a\n"
        ".option norvc\n"
        "addi a0, gp, 208 # original 0xc53c\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 0xc540\n"
        "jr t1 # original 0xc542\n"
        ".option pop\n"
    );
}

/* Original 0xcd08..0xcd1e: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_cd08"))) void tsl9_feature_init_cd08(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xcd08\n"
        "lw t1, 72(a5) # original 0xcd0c\n"
        ".option rvc\n"
        "li a2, 16 # original 0xcd10\n"
        "li a1, 0 # original 0xcd12\n"
        ".Lfi49_pair_cd08_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf24) # original 0xcd14\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_cd08_12) # original 0xcd18\n"
        ".option rvc\n"
        "jr t1 # original 0xcd1c\n"
        ".option pop\n"
    );
}

/* Original 0xcf4c..0xcf62: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_cf4c"))) void tsl9_feature_init_cf4c(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xcf4c\n"
        "lw t1, 72(a5) # original 0xcf50\n"
        ".option rvc\n"
        "li a2, 16 # original 0xcf54\n"
        "li a1, 0 # original 0xcf56\n"
        ".Lfi49_pair_cf4c_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf34) # original 0xcf58\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_cf4c_12) # original 0xcf5c\n"
        ".option rvc\n"
        "jr t1 # original 0xcf60\n"
        ".option pop\n"
    );
}

/* Original 0xcff4..0xd006: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_cff4"))) void tsl9_feature_init_cff4(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xcff4\n"
        "lw t1, 72(a5) # original 0xcff8\n"
        ".option rvc\n"
        "li a2, 4 # original 0xcffc\n"
        "li a1, 0 # original 0xcffe\n"
        ".option norvc\n"
        "addi a0, gp, 232 # original 0xd000\n"
        ".option rvc\n"
        "jr t1 # original 0xd004\n"
        ".option pop\n"
    );
}

/* Original 0xd0cc..0xd0e2: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_d0cc"))) void tsl9_feature_init_d0cc(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xd0cc\n"
        "lw t1, 72(a5) # original 0xd0d0\n"
        ".option rvc\n"
        "li a2, 19 # original 0xd0d4\n"
        "li a1, 0 # original 0xd0d6\n"
        ".Lfi49_pair_d0cc_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf44) # original 0xd0d8\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_d0cc_12) # original 0xd0dc\n"
        ".option rvc\n"
        "jr t1 # original 0xd0e0\n"
        ".option pop\n"
    );
}

/* Original 0xd39c..0xd3b2: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_d39c"))) void tsl9_feature_init_d39c(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xd39c\n"
        "lw t1, 72(a5) # original 0xd3a0\n"
        ".option rvc\n"
        "li a2, 12 # original 0xd3a4\n"
        "li a1, 0 # original 0xd3a6\n"
        ".Lfi49_pair_d39c_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf58) # original 0xd3a8\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_d39c_12) # original 0xd3ac\n"
        ".option rvc\n"
        "jr t1 # original 0xd3b0\n"
        ".option pop\n"
    );
}

/* Original 0xd514..0xd526: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_d514"))) void tsl9_feature_init_d514(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xd514\n"
        "lw t1, 72(a5) # original 0xd518\n"
        ".option rvc\n"
        "li a2, 2 # original 0xd51c\n"
        "li a1, 0 # original 0xd51e\n"
        ".option norvc\n"
        "addi a0, gp, 240 # original 0xd520\n"
        ".option rvc\n"
        "jr t1 # original 0xd524\n"
        ".option pop\n"
    );
}

/* Original 0xd5e4..0xd5f6: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_d5e4"))) void tsl9_feature_init_d5e4(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xd5e4\n"
        "lw t1, 72(a5) # original 0xd5e8\n"
        ".option rvc\n"
        "li a2, 5 # original 0xd5ec\n"
        "li a1, 0 # original 0xd5ee\n"
        ".option norvc\n"
        "addi a0, gp, 252 # original 0xd5f0\n"
        ".option rvc\n"
        "jr t1 # original 0xd5f4\n"
        ".option pop\n"
    );
}

/* Original 0xdf2e..0xdf44: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_df2e"))) void tsl9_feature_init_df2e(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xdf2e\n"
        "lw t1, 72(a5) # original 0xdf32\n"
        ".option rvc\n"
        "li a2, 28 # original 0xdf36\n"
        "li a1, 0 # original 0xdf38\n"
        ".Lfi49_pair_df2e_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf64) # original 0xdf3a\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_df2e_12) # original 0xdf3e\n"
        ".option rvc\n"
        "jr t1 # original 0xdf42\n"
        ".option pop\n"
    );
}

/* Original 0xef6a..0xef80: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_ef6a"))) void tsl9_feature_init_ef6a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xef6a\n"
        "lw t1, 72(a5) # original 0xef6e\n"
        ".option rvc\n"
        "li a2, 12 # original 0xef72\n"
        "li a1, 0 # original 0xef74\n"
        ".Lfi49_pair_ef6a_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf80) # original 0xef76\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_ef6a_12) # original 0xef7a\n"
        ".option rvc\n"
        "jr t1 # original 0xef7e\n"
        ".option pop\n"
    );
}

/* Original 0xf6fe..0xf714: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_f6fe"))) void tsl9_feature_init_f6fe(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xf6fe\n"
        "lw t1, 72(a5) # original 0xf702\n"
        ".option rvc\n"
        "li a2, 24 # original 0xf706\n"
        "li a1, 0 # original 0xf708\n"
        ".Lfi49_pair_f6fe_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bf8c) # original 0xf70a\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_f6fe_12) # original 0xf70e\n"
        ".option rvc\n"
        "jr t1 # original 0xf712\n"
        ".option pop\n"
    );
}

/* Original 0xf906..0xf918: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_f906"))) void tsl9_feature_init_f906(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xf906\n"
        "lw t1, 72(a5) # original 0xf90a\n"
        ".option rvc\n"
        "li a2, 5 # original 0xf90e\n"
        "li a1, 0 # original 0xf910\n"
        ".option norvc\n"
        "addi a0, gp, 276 # original 0xf912\n"
        ".option rvc\n"
        "jr t1 # original 0xf916\n"
        ".option pop\n"
    );
}

/* Original 0xf9c2..0xf9d4: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_f9c2"))) void tsl9_feature_init_f9c2(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xf9c2\n"
        "lw t1, 72(a5) # original 0xf9c6\n"
        ".option rvc\n"
        "li a2, 3 # original 0xf9ca\n"
        "li a1, 0 # original 0xf9cc\n"
        ".option norvc\n"
        "addi a0, gp, 284 # original 0xf9ce\n"
        ".option rvc\n"
        "jr t1 # original 0xf9d2\n"
        ".option pop\n"
    );
}

/* Original 0xfdfa..0xfe0c: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_fdfa"))) void tsl9_feature_init_fdfa(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xfdfa\n"
        "lw t1, 72(a5) # original 0xfdfe\n"
        ".option rvc\n"
        "li a2, 4 # original 0xfe02\n"
        "li a1, 0 # original 0xfe04\n"
        ".option norvc\n"
        "addi a0, gp, 288 # original 0xfe06\n"
        ".option rvc\n"
        "jr t1 # original 0xfe0a\n"
        ".option pop\n"
    );
}

/* Original 0xfee4..0xfef6: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_fee4"))) void tsl9_feature_init_fee4(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0xfee4\n"
        "lw t1, 72(a5) # original 0xfee8\n"
        ".option rvc\n"
        "li a2, 3 # original 0xfeec\n"
        "li a1, 0 # original 0xfeee\n"
        ".option norvc\n"
        "addi a0, gp, 300 # original 0xfef0\n"
        ".option rvc\n"
        "jr t1 # original 0xfef4\n"
        ".option pop\n"
    );
}

/* Original 0x1000a..0x10020: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_1000a"))) void tsl9_feature_init_1000a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x1000a\n"
        "lw t1, 72(a5) # original 0x1000e\n"
        ".option rvc\n"
        "li a2, 12 # original 0x10012\n"
        "li a1, 0 # original 0x10014\n"
        ".Lfi49_pair_1000a_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_bfa4) # original 0x10016\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_1000a_12) # original 0x1001a\n"
        ".option rvc\n"
        "jr t1 # original 0x1001e\n"
        ".option pop\n"
    );
}

/* Original 0x10128..0x1013a: 6 instructions, 18 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_10128"))) void tsl9_feature_init_10128(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x10128\n"
        "lw t1, 72(a5) # original 0x1012c\n"
        ".option rvc\n"
        "li a2, 4 # original 0x10130\n"
        "li a1, 0 # original 0x10132\n"
        ".option norvc\n"
        "addi a0, gp, 304 # original 0x10134\n"
        ".option rvc\n"
        "jr t1 # original 0x10138\n"
        ".option pop\n"
    );
}

/* Original 0x10a9a..0x10ab0: 7 instructions, 22 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_10a9a"))) void tsl9_feature_init_10a9a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x10a9a\n"
        "lw t1, 72(a5) # original 0x10a9e\n"
        ".option rvc\n"
        "li a2, 20 # original 0x10aa2\n"
        "li a1, 0 # original 0x10aa4\n"
        ".Lfi49_pair_10a9a_12:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_state_bfb4-4) # original 0x10aa6\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_10a9a_12) # original 0x10aaa\n"
        ".option rvc\n"
        "jr t1 # original 0x10aae\n"
        ".option pop\n"
    );
}

/* Original 0x1524e..0x152d2: 37 instructions, 132 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_1524e"))) void tsl9_feature_initialize(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x1524e\n"
        ".option rvc\n"
        "lw a5, 72(a5) # original 0x15252\n"
        "addi sp, sp, -16 # original 0x15254\n"
        "sw ra, 12(sp) # original 0x15256\n"
        "li a2, 5 # original 0x15258\n"
        "li a1, 0 # original 0x1525a\n"
        ".option norvc\n"
        "addi a0, gp, 352 # original 0x1525c\n"
        ".option rvc\n"
        "jalr a5 # original 0x15260\n"
        ".option norvc\n"
        "jal ra, tsl9_feature_init_10a9a # original 0x15262\n"
        "jal ra, tsl9_feature_init_d0cc # original 0x15266\n"
        "jal ra, tsl9_feature_init_a2a0 # original 0x1526a\n"
        "jal ra, tsl9_feature_init_af18 # original 0x1526e\n"
        "jal ra, tsl9_feature_init_d5e4 # original 0x15272\n"
        "jal ra, tsl9_feature_init_cff4 # original 0x15276\n"
        "jal ra, tsl9_feature_init_1000a # original 0x1527a\n"
        "jal ra, tsl9_internal_tx_clear_c634 # original 0x1527e\n"
        "jal ra, tsl9_feature_init_fee4 # original 0x15282\n"
        "jal ra, tsl9_feature_init_d39c # original 0x15286\n"
        "jal ra, tsl9_feature_init_b060 # original 0x1528a\n"
        "jal ra, tsl9_feature_init_b46a # original 0x1528e\n"
        "jal ra, tsl9_feature_init_df2e # original 0x15292\n"
        "jal ra, tsl9_feature_init_cd08 # original 0x15296\n"
        "jal ra, tsl9_feature_init_cf4c # original 0x1529a\n"
        "jal ra, tsl9_feature_init_f6fe # original 0x1529e\n"
        "jal ra, tsl9_feature_init_f9c2 # original 0x152a2\n"
        "jal ra, tsl9_feature_init_f906 # original 0x152a6\n"
        "jal ra, tsl9_feature_init_fdfa # original 0x152aa\n"
        "jal ra, tsl9_feature_init_aed6 # original 0x152ae\n"
        "jal ra, tsl9_feature_init_a936 # original 0x152b2\n"
        "jal ra, tsl9_feature_init_c25a # original 0x152b6\n"
        "jal ra, tsl9_feature_init_c516 # original 0x152ba\n"
        "jal ra, tsl9_feature_init_d514 # original 0x152be\n"
        "jal ra, tsl9_feature_init_ef6a # original 0x152c2\n"
        "jal ra, tsl9_feature_init_10128 # original 0x152c6\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0x152ca\n"
        "addi sp, sp, 16 # original 0x152cc\n"
        ".option norvc\n"
        "jal zero, tsl9_feature_init_1836c # original 0x152ce\n"
        ".option pop\n"
    );
}

/* Original 0x1836c..0x18384: 7 instructions, 24 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_feature_init_1836c"))) void tsl9_feature_init_1836c(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x1836c\n"
        "lw t1, 72(a5) # original 0x18370\n"
        "li a2, 52 # original 0x18374\n"
        ".option rvc\n"
        "li a1, 0 # original 0x18378\n"
        ".Lfi49_pair_1836c_14:\n"
        ".option norvc\n"
        "auipc a0, %pcrel_hi(__tsl9_feature_state_c91c) # original 0x1837a\n"
        "addi a0, a0, %pcrel_lo(.Lfi49_pair_1836c_14) # original 0x1837e\n"
        ".option rvc\n"
        "jr t1 # original 0x18382\n"
        ".option pop\n"
    );
}

/* Shared complete original entries; strong hidden aliases do not duplicate code. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_feature_init_af18(void)
    __attribute__((alias("tsl9_feature_init_af18"), visibility("hidden"), used));
extern void tsl9_internal_feature_init_d0cc(void)
    __attribute__((alias("tsl9_feature_init_d0cc"), visibility("hidden"), used));
extern void tsl9_internal_feature_init_fee4(void)
    __attribute__((alias("tsl9_feature_init_fee4"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R71 original callback0xAEEC..0xAF18:44B/14ops, no external relocations.
 * void(void) is an emission anchor; original register input a1 and full a0
 * return are retained. ROM invocation/prototype and event meaning are unknown.
 * Preserve GP+193..195 LBU/SB order, threshold2 and full32-bit XOR1 result. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_aeec")))
void tsl9_runtime_unported_aeec(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "andi a5, a1, 1 # original0xaeec\n"
        ".option rvc\n"
        "li a0, 0 # original0xaef0\n"
        "beqz a5, .Lfi71_af16 # original0xaef2\n"
        ".option norvc\n"
        "addi a5, gp, 192 # original0xaef4\n"
        "addi a3, gp, 195 # original0xaef8\n"
        ".option rvc\n"
        "li a2, 2 # original0xaefc\n"
        ".Lfi71_aefe:\n"
        ".option norvc\n"
        "lbu a4, 1(a5) # original0xaefe\n"
        "bltu a2, a4, .Lfi71_af0c # original0xaf02\n"
        ".option rvc\n"
        "addi a4, a4, 1 # original0xaf06\n"
        ".option norvc\n"
        "sb a4, 1(a5) # original0xaf08\n"
        ".Lfi71_af0c:\n"
        ".option rvc\n"
        "addi a5, a5, 1 # original0xaf0c\n"
        ".option norvc\n"
        "bne a5, a3, .Lfi71_aefe # original0xaf0e\n"
        "xori a0, a1, 1 # original0xaf12\n"
        ".Lfi71_af16:\n"
        ".option rvc\n"
        "ret # original0xaf16\n"
        ".option pop\n"
    );
}


/* R76 hidden exact-entry alias; no existing instruction changed. */
#if defined(__riscv) && __riscv_xlen == 32
__asm__(
        ".global tsl9_internal_r76_b060\n"
        ".hidden tsl9_internal_r76_b060\n"
        ".set tsl9_internal_r76_b060, tsl9_feature_init_b060\n"
);
#endif
