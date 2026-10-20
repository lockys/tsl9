#include "target_ble_dependencies.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "RV32 original-register entries required; never execute on host."
#endif
#define TSL9_NATIVE __attribute__((naked,noinline,used))
/* Fixed server V4.1.00 executable code only. Preserve register state, stack read/write order and compressed calls/tails.
 * SP+7..10 prior reads feed a3/a4 across the call; do not remove them or zero
 * untouched record bytes. Numeric RAM relationships allocate no storage.
 * Physical ABI, record ownership, scheduler and transport success are unknown. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_timer_start_9388(void);
extern void tsl9_internal_timer_prepare_93ee(void);
extern void tsl9_runtime_unported_12864(void);
extern unsigned char __tsl9_feature_state_c91c[];
extern unsigned char __tsl9_timer_state[];
#ifdef __cplusplus
}
#endif

/* Original0x17a22..0x17a84: 29 instructions/98 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_17a22"))) void tsl9_runtime_unported_17a22(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -32 # original 17a22\n"
        ".option norvc\n"
        "li a5, 1267 # original 17a24\n"
        ".option norvc\n"
        "sh a5, 4(sp) # original 17a28\n"
        ".option rvc\n"
        "li a5, 3 # original 17a2c\n"
        ".option norvc\n"
        "sb a5, 6(sp) # original 17a2e\n"
        ".option norvc\n"
        ".Ldependency62pc_17a32:\n"
        "auipc a5, %pcrel_hi(__tsl9_feature_state_c91c) # original 17a32\n"
        ".option norvc\n"
        "addi a5, a5, %pcrel_lo(.Ldependency62pc_17a32) # original 17a36\n"
        ".option rvc\n"
        "lw a5, 8(a5) # original 17a3a\n"
        ".option norvc\n"
        "lbu a3, 7(sp) # original 17a3c\n"
        ".option rvc\n"
        "addi a0, sp, 4 # original 17a40\n"
        ".option norvc\n"
        "andi a4, a5, 255 # original 17a42\n"
        ".option norvc\n"
        "sb a4, 7(sp) # original 17a46\n"
        ".option norvc\n"
        "srli a4, a5, 0x8 # original 17a4a\n"
        ".option norvc\n"
        "andi a4, a4, 255 # original 17a4e\n"
        ".option norvc\n"
        "lbu a3, 8(sp) # original 17a52\n"
        ".option norvc\n"
        "sb a4, 8(sp) # original 17a56\n"
        ".option norvc\n"
        "srli a4, a5, 0x10 # original 17a5a\n"
        ".option norvc\n"
        "andi a4, a4, 255 # original 17a5e\n"
        ".option norvc\n"
        "lbu a3, 9(sp) # original 17a62\n"
        ".option norvc\n"
        "sb a4, 9(sp) # original 17a66\n"
        ".option norvc\n"
        "lbu a4, 10(sp) # original 17a6a\n"
        ".option rvc\n"
        "srli a5, a5, 0x18 # original 17a6e\n"
        ".option rvc\n"
        "sw ra, 28(sp) # original 17a70\n"
        ".option norvc\n"
        "sb zero, 15(sp) # original 17a72\n"
        ".option norvc\n"
        "sb a5, 10(sp) # original 17a76\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_12864 # original 17a7a\n"
        ".option rvc\n"
        "lw ra, 28(sp) # original 17a7e\n"
        ".option rvc\n"
        "addi sp, sp, 32 # original 17a80\n"
        ".option rvc\n"
        "ret # original 17a82\n"
        ".option pop\n"
    );
}

/* Original0x95ec..0x9636: 24 instructions/74 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_event_reference_95ec"))) void tsl9_event_reference_95ec(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 95ec\n"
        ".option rvc\n"
        "li a0, 3 # original 95ee\n"
        ".option rvc\n"
        "sw ra, 12(sp) # original 95f0\n"
        ".option rvc\n"
        ".Ldependency62transfer_95f2:\n"
        ".2byte 0x2001 # original 95f2 compressed transfer; immediate relocation\n"
        ".reloc .Ldependency62transfer_95f2, R_RISCV_RVC_JUMP, tsl9_internal_timer_prepare_93ee\n"
        ".option norvc\n"
        ".Ldependency62pc_95f4:\n"
        "auipc a5, %pcrel_hi(__tsl9_timer_state+16) # original 95f4\n"
        ".option norvc\n"
        "sw a0, %pcrel_lo(.Ldependency62pc_95f4)(a5) # original 95f8\n"
        ".option rvc\n"
        "beqz a0, .Ldependency62_95ec_9630 # original 95fc\n"
        ".option norvc\n"
        "li a5, 1165 # original 95fe\n"
        ".option norvc\n"
        "sh a5, 0(a0) # original 9602\n"
        ".option norvc\n"
        "li a5, 130 # original 9606\n"
        ".option norvc\n"
        "sh a5, 2(a0) # original 960a\n"
        ".option norvc\n"
        "li a5, 1465 # original 960e\n"
        ".option norvc\n"
        "sh a5, 6(a0) # original 9612\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 9616\n"
        ".option norvc\n"
        "li a5, 150 # original 9618\n"
        ".option norvc\n"
        "sh zero, 4(a0) # original 961c\n"
        ".option norvc\n"
        "sh a5, 8(a0) # original 9620\n"
        ".option norvc\n"
        "sh zero, 10(a0) # original 9624\n"
        ".option norvc\n"
        "sh zero, 12(a0) # original 9628\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 962c\n"
        ".option rvc\n"
        ".Ldependency62transfer_962e:\n"
        ".2byte 0xa001 # original 962e compressed transfer; immediate relocation\n"
        ".reloc .Ldependency62transfer_962e, R_RISCV_RVC_JUMP, tsl9_internal_timer_start_9388\n"
        ".Ldependency62_95ec_9630:\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 9630\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 9632\n"
        ".option rvc\n"
        "ret # original 9634\n"
        ".option pop\n"
    );
}
