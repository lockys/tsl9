#include "target_config_storage.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "Original RV32 register/ROM/GP/Flash mapping required; do not run on host"
#endif
#define TSL9_NATIVE __attribute__((naked, noinline, used))
/* Readable instruction reconstruction, no original firmware blob or dummy target.
 * Flash helpers retain fresh status polls with no invented timeout/error behavior.
 * ROM4004C copy units and mapping 08077B00 are unverified; do not execute/flash.
 * 935C and its identity-related downstream chain are intentionally opaque. */
#ifdef __cplusplus
extern "C" {
#endif
extern unsigned char __tsl9_config_records[];
extern void tsl9_runtime_unported_935c(void);
#ifdef __cplusplus
}
#endif
static void tsl9_config_persist_9d76(void) __asm__("tsl9_config_persist_9d76") TSL9_NATIVE;
static void tsl9_config_read_9d9e(void) __asm__("tsl9_config_read_9d9e") TSL9_NATIVE;
static void tsl9_storage_page_9b6c(void) __asm__("tsl9_storage_page_9b6c") TSL9_NATIVE;
static void tsl9_storage_status_18be4(void) __asm__("tsl9_storage_status_18be4") TSL9_NATIVE;
static void tsl9_storage_unlock_18bec(void) __asm__("tsl9_storage_unlock_18bec") TSL9_NATIVE;
static void tsl9_storage_lock_18c0a(void) __asm__("tsl9_storage_lock_18c0a") TSL9_NATIVE;
static void tsl9_storage_erase_18c18(void) __asm__("tsl9_storage_erase_18c18") TSL9_NATIVE;
static void tsl9_storage_program_18c46(void) __asm__("tsl9_storage_program_18c46") TSL9_NATIVE;

/* Original 0x9e2c..0x9e66: 21 instructions, 58 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_9e2c"))) void tsl9_config_init(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -32 # original 0x9e2c\n"
        ".option norvc\n"
        "sb zero, 177(gp) # original 0x9e2e\n"
        ".option rvc\n"
        "sw ra, 28(sp) # original 0x9e32\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_config_read_9d9e # original 0x9e34\n"
        ".option rvc\n"
        "sw a0, 8(sp) # original 0x9e36\n"
        ".option norvc\n"
        "lbu a5, 9(sp) # original 0x9e38\n"
        ".option rvc\n"
        "sw a1, 12(sp) # original 0x9e3c\n"
        ".option rvc\n"
        "li a4, 16 # original 0x9e3e\n"
        ".option norvc\n"
        "bne a4, a5, .Lconfig_9e2c_9e4e # original 0x9e40\n"
        ".option norvc\n"
        "lbu a5, 12(sp) # original 0x9e44\n"
        ".option norvc\n"
        "andi a5, a5, 255 # original 0x9e48\n"
        ".option rvc\n"
        "beqz a5, .Lconfig_9e2c_9e5c # original 0x9e4c\n"
        ".Lconfig_9e2c_9e4e:\n"
        ".option rvc\n"
        "li a5, 16 # original 0x9e4e\n"
        ".option norvc\n"
        "sb a5, 9(sp) # original 0x9e50\n"
        ".option rvc\n"
        "addi a0, sp, 8 # original 0x9e54\n"
        ".option norvc\n"
        "sb zero, 12(sp) # original 0x9e56\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_config_persist_9d76 # original 0x9e5a\n"
        ".Lconfig_9e2c_9e5c:\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_935c # original 0x9e5c\n"
        ".option rvc\n"
        "lw ra, 28(sp) # original 0x9e60\n"
        ".option rvc\n"
        "addi sp, sp, 32 # original 0x9e62\n"
        ".option rvc\n"
        "ret # original 0x9e64\n"
        ".option pop\n"
    );
}

/* Original 0x14a54..0x14a92: 22 instructions, 62 bytes. */
TSL9_NATIVE __attribute__((section(".text.tsl9_runtime_unported_14a54"))) void tsl9_records_init(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x14a54\n"
        ".option rvc\n"
        "addi sp, sp, -16 # original 0x14a58\n"
        ".option rvc\n"
        "lw a5, 72(a5) # original 0x14a5a\n"
        ".option rvc\n"
        "sw s0, 8(sp) # original 0x14a5c\n"
        ".Lconfig_pair_14a54_10:\n"
        ".option norvc\n"
        "auipc s0, %pcrel_hi(__tsl9_config_records) # original 0x14a5e\n"
        ".option norvc\n"
        "addi s0, s0, %pcrel_lo(.Lconfig_pair_14a54_10) # original 0x14a62\n"
        ".option rvc\n"
        "sw ra, 12(sp) # original 0x14a66\n"
        ".option rvc\n"
        "mv a0, s0 # original 0x14a68\n"
        ".option rvc\n"
        "li a2, 10 # original 0x14a6a\n"
        ".option rvc\n"
        "li a1, 0 # original 0x14a6c\n"
        ".option rvc\n"
        "jalr a5 # original 0x14a6e\n"
        ".option rvc\n"
        "li a5, -2 # original 0x14a70\n"
        ".option norvc\n"
        "sh a5, 2(s0) # original 0x14a72\n"
        ".option norvc\n"
        "sb zero, 4(s0) # original 0x14a76\n"
        ".option norvc\n"
        "sb zero, 5(s0) # original 0x14a7a\n"
        ".option norvc\n"
        "sh a5, 6(s0) # original 0x14a7e\n"
        ".option norvc\n"
        "sb zero, 8(s0) # original 0x14a82\n"
        ".option norvc\n"
        "sb zero, 9(s0) # original 0x14a86\n"
        ".option rvc\n"
        "lw ra, 12(sp) # original 0x14a8a\n"
        ".option rvc\n"
        "lw s0, 8(sp) # original 0x14a8c\n"
        ".option rvc\n"
        "addi sp, sp, 16 # original 0x14a8e\n"
        ".option rvc\n"
        "ret # original 0x14a90\n"
        ".option pop\n"
    );
}

/* Original 0x9d76..0x9d9e: 15 instructions, 40 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_config_persist_9d76"))) void tsl9_config_persist_9d76(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x9d76\n"
        ".option rvc\n"
        "lw a5, 76(a5) # original 0x9d7a\n"
        ".option rvc\n"
        "addi sp, sp, -272 # original 0x9d7c\n"
        ".option norvc\n"
        "sw ra, 268(sp) # original 0x9d7e\n"
        ".option rvc\n"
        "mv a1, a0 # original 0x9d82\n"
        ".option rvc\n"
        "li a2, 8 # original 0x9d84\n"
        ".option rvc\n"
        "mv a0, sp # original 0x9d86\n"
        ".option rvc\n"
        "jalr a5 # original 0x9d88\n"
        ".option norvc\n"
        "lui a0, 0x8078 # original 0x9d8a\n"
        ".option rvc\n"
        "mv a1, sp # original 0x9d8e\n"
        ".option norvc\n"
        "addi a0, a0, -1280 # original 0x9d90\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_storage_page_9b6c # original 0x9d94\n"
        ".option norvc\n"
        "lw ra, 268(sp) # original 0x9d96\n"
        ".option rvc\n"
        "addi sp, sp, 272 # original 0x9d9a\n"
        ".option rvc\n"
        "ret # original 0x9d9c\n"
        ".option pop\n"
    );
}

/* Original 0x9d9e..0x9dc0: 14 instructions, 34 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_config_read_9d9e"))) void tsl9_config_read_9d9e(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40 # original 0x9d9e\n"
        ".option rvc\n"
        "lw a5, 76(a5) # original 0x9da2\n"
        ".option rvc\n"
        "addi sp, sp, -32 # original 0x9da4\n"
        ".option norvc\n"
        "lui a1, 0x8078 # original 0x9da6\n"
        ".option rvc\n"
        "sw ra, 28(sp) # original 0x9daa\n"
        ".option rvc\n"
        "mv a0, sp # original 0x9dac\n"
        ".option norvc\n"
        "addi a1, a1, -1280 # original 0x9dae\n"
        ".option rvc\n"
        "li a2, 8 # original 0x9db2\n"
        ".option rvc\n"
        "jalr a5 # original 0x9db4\n"
        ".option rvc\n"
        "lw ra, 28(sp) # original 0x9db6\n"
        ".option rvc\n"
        "lw a0, 0(sp) # original 0x9db8\n"
        ".option rvc\n"
        "lw a1, 4(sp) # original 0x9dba\n"
        ".option rvc\n"
        "addi sp, sp, 32 # original 0x9dbc\n"
        ".option rvc\n"
        "ret # original 0x9dbe\n"
        ".option pop\n"
    );
}

/* Original 0x9b6c..0x9bac: 23 instructions, 64 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_storage_page_9b6c"))) void tsl9_storage_page_9b6c(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        "addi sp, sp, -32 # original 0x9b6c\n"
        ".option rvc\n"
        "sw s0, 24(sp) # original 0x9b6e\n"
        ".option rvc\n"
        "sw s1, 20(sp) # original 0x9b70\n"
        ".option rvc\n"
        "sw ra, 28(sp) # original 0x9b72\n"
        ".option rvc\n"
        "mv s1, a0 # original 0x9b74\n"
        ".option rvc\n"
        "sw a1, 12(sp) # original 0x9b76\n"
        ".option norvc\n"
        "li s0, 136 # original 0x9b78\n"
        ".option norvc\n"
        "csrc 0x800, s0 # original 0x9b7c\n"
        ".option norvc\n"
        "jal ra, tsl9_storage_unlock_18bec # original 0x9b80\n"
        ".option norvc\n"
        "li a0, 49 # original 0x9b84\n"
        ".option norvc\n"
        "jal ra, tsl9_storage_status_18be4 # original 0x9b88\n"
        ".option rvc\n"
        "mv a0, s1 # original 0x9b8c\n"
        ".option norvc\n"
        "jal ra, tsl9_storage_erase_18c18 # original 0x9b8e\n"
        ".option rvc\n"
        "lw a1, 12(sp) # original 0x9b92\n"
        ".option rvc\n"
        "mv a0, s1 # original 0x9b94\n"
        ".option norvc\n"
        "jal ra, tsl9_storage_program_18c46 # original 0x9b96\n"
        ".option norvc\n"
        "jal ra, tsl9_storage_lock_18c0a # original 0x9b9a\n"
        ".option norvc\n"
        "csrs 0x800, s0 # original 0x9b9e\n"
        ".option rvc\n"
        "lw ra, 28(sp) # original 0x9ba2\n"
        ".option rvc\n"
        "lw s0, 24(sp) # original 0x9ba4\n"
        ".option rvc\n"
        "lw s1, 20(sp) # original 0x9ba6\n"
        ".option rvc\n"
        "addi sp, sp, 32 # original 0x9ba8\n"
        ".option rvc\n"
        "ret # original 0x9baa\n"
        ".option pop\n"
    );
}

/* Original 0x18be4..0x18bec: 3 instructions, 8 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_storage_status_18be4"))) void tsl9_storage_status_18be4(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40022 # original 0x18be4\n"
        ".option rvc\n"
        "sw a0, 12(a5) # original 0x18be8\n"
        ".option rvc\n"
        "ret # original 0x18bea\n"
        ".option pop\n"
    );
}

/* Original 0x18bec..0x18c0a: 10 instructions, 30 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_storage_unlock_18bec"))) void tsl9_storage_unlock_18bec(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a3, 0x45670 # original 0x18bec\n"
        ".option norvc\n"
        "lui a5, 0x40022 # original 0x18bf0\n"
        ".option norvc\n"
        "addi a3, a3, 291 # original 0x18bf4\n"
        ".option norvc\n"
        "lui a4, 0xcdef9 # original 0x18bf8\n"
        ".option rvc\n"
        "sw a3, 4(a5) # original 0x18bfc\n"
        ".option norvc\n"
        "addi a4, a4, -1621 # original 0x18bfe\n"
        ".option rvc\n"
        "sw a4, 4(a5) # original 0x18c02\n"
        ".option rvc\n"
        "sw a3, 36(a5) # original 0x18c04\n"
        ".option rvc\n"
        "sw a4, 36(a5) # original 0x18c06\n"
        ".option rvc\n"
        "ret # original 0x18c08\n"
        ".option pop\n"
    );
}

/* Original 0x18c0a..0x18c18: 6 instructions, 14 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_storage_lock_18c0a"))) void tsl9_storage_lock_18c0a(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a4, 0x40022 # original 0x18c0a\n"
        ".option rvc\n"
        "lw a5, 16(a4) # original 0x18c0e\n"
        ".option rvc\n"
        "lui a3, 0x8 # original 0x18c10\n"
        ".option rvc\n"
        "or a5, a5, a3 # original 0x18c12\n"
        ".option rvc\n"
        "sw a5, 16(a4) # original 0x18c14\n"
        ".option rvc\n"
        "ret # original 0x18c16\n"
        ".option pop\n"
    );
}

/* Original 0x18c18..0x18c46: 19 instructions, 46 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_storage_erase_18c18"))) void tsl9_storage_erase_18c18(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a5, 0x40022 # original 0x18c18\n"
        ".option rvc\n"
        "lw a4, 16(a5) # original 0x18c1c\n"
        ".option norvc\n"
        "lui a3, 0x20 # original 0x18c1e\n"
        ".option norvc\n"
        "andi a0, a0, -256 # original 0x18c22\n"
        ".option rvc\n"
        "or a4, a4, a3 # original 0x18c26\n"
        ".option rvc\n"
        "sw a4, 16(a5) # original 0x18c28\n"
        ".option rvc\n"
        "sw a0, 20(a5) # original 0x18c2a\n"
        ".option rvc\n"
        "lw a4, 16(a5) # original 0x18c2c\n"
        ".option norvc\n"
        "ori a4, a4, 64 # original 0x18c2e\n"
        ".option rvc\n"
        "sw a4, 16(a5) # original 0x18c32\n"
        ".Lconfig_18c18_18c34:\n"
        ".option rvc\n"
        "lw a4, 12(a5) # original 0x18c34\n"
        ".option rvc\n"
        "andi a4, a4, 1 # original 0x18c36\n"
        ".option rvc\n"
        "bnez a4, .Lconfig_18c18_18c34 # original 0x18c38\n"
        ".option rvc\n"
        "lw a4, 16(a5) # original 0x18c3a\n"
        ".option rvc\n"
        "lui a3, 0xfffe0 # original 0x18c3c\n"
        ".option rvc\n"
        "addi a3, a3, -1 # original 0x18c3e\n"
        ".option rvc\n"
        "and a4, a4, a3 # original 0x18c40\n"
        ".option rvc\n"
        "sw a4, 16(a5) # original 0x18c42\n"
        ".option rvc\n"
        "ret # original 0x18c44\n"
        ".option pop\n"
    );
}

/* Original 0x18c46..0x18caa: 38 instructions, 100 bytes. */
static TSL9_NATIVE __attribute__((section(".text.tsl9_storage_program_18c46"))) void tsl9_storage_program_18c46(void)
{
    __asm__ volatile (
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        "lui a4, 0x40022 # original 0x18c46\n"
        ".option rvc\n"
        "lw a5, 16(a4) # original 0x18c4a\n"
        ".option rvc\n"
        "lui a3, 0x10 # original 0x18c4c\n"
        ".option norvc\n"
        "andi a0, a0, -256 # original 0x18c4e\n"
        ".option rvc\n"
        "or a5, a5, a3 # original 0x18c52\n"
        ".option rvc\n"
        "sw a5, 16(a4) # original 0x18c54\n"
        ".Lconfig_18c46_18c56:\n"
        ".option rvc\n"
        "lw a5, 12(a4) # original 0x18c56\n"
        ".option rvc\n"
        "andi a5, a5, 1 # original 0x18c58\n"
        ".option rvc\n"
        "bnez a5, .Lconfig_18c46_18c56 # original 0x18c5a\n"
        ".option norvc\n"
        "lui a4, 0x40022 # original 0x18c5c\n"
        ".Lconfig_18c46_18c60:\n"
        ".option rvc\n"
        "lw a5, 12(a4) # original 0x18c60\n"
        ".option rvc\n"
        "andi a5, a5, 2 # original 0x18c62\n"
        ".option rvc\n"
        "bnez a5, .Lconfig_18c46_18c60 # original 0x18c64\n"
        ".option norvc\n"
        "lui a4, 0x40022 # original 0x18c66\n"
        ".option norvc\n"
        "li a2, 256 # original 0x18c6a\n"
        ".Lconfig_18c46_18c6e:\n"
        ".option norvc\n"
        "add a3, a1, a5 # original 0x18c6e\n"
        ".option norvc\n"
        "lw a6, 0(a3) # original 0x18c72\n"
        ".option norvc\n"
        "add a3, a0, a5 # original 0x18c76\n"
        ".option norvc\n"
        "sw a6, 0(a3) # original 0x18c7a\n"
        ".Lconfig_18c46_18c7e:\n"
        ".option rvc\n"
        "lw a3, 12(a4) # original 0x18c7e\n"
        ".option rvc\n"
        "andi a3, a3, 2 # original 0x18c80\n"
        ".option rvc\n"
        "bnez a3, .Lconfig_18c46_18c7e # original 0x18c82\n"
        ".option rvc\n"
        "addi a5, a5, 4 # original 0x18c84\n"
        ".option norvc\n"
        "bne a5, a2, .Lconfig_18c46_18c6e # original 0x18c86\n"
        ".option rvc\n"
        "lw a5, 16(a4) # original 0x18c8a\n"
        ".option norvc\n"
        "lui a3, 0x200 # original 0x18c8c\n"
        ".option rvc\n"
        "or a5, a5, a3 # original 0x18c90\n"
        ".option rvc\n"
        "sw a5, 16(a4) # original 0x18c92\n"
        ".option norvc\n"
        "lui a5, 0x40022 # original 0x18c94\n"
        ".Lconfig_18c46_18c98:\n"
        ".option rvc\n"
        "lw a4, 12(a5) # original 0x18c98\n"
        ".option rvc\n"
        "andi a4, a4, 1 # original 0x18c9a\n"
        ".option rvc\n"
        "bnez a4, .Lconfig_18c46_18c98 # original 0x18c9c\n"
        ".option rvc\n"
        "lw a4, 16(a5) # original 0x18c9e\n"
        ".option rvc\n"
        "lui a3, 0xffff0 # original 0x18ca0\n"
        ".option rvc\n"
        "addi a3, a3, -1 # original 0x18ca2\n"
        ".option rvc\n"
        "and a4, a4, a3 # original 0x18ca4\n"
        ".option rvc\n"
        "sw a4, 16(a5) # original 0x18ca6\n"
        ".option rvc\n"
        "ret # original 0x18ca8\n"
        ".option pop\n"
    );
}

/* Same-body shared entry; retains original page helper and register contract. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_storage_page_9b6c(void)
    __attribute__((alias("tsl9_storage_page_9b6c"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R59: exact-body hidden aliases for HAL callbacks; no duplicated code. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_flash_unlock_18bec(void)
    __attribute__((alias("tsl9_storage_unlock_18bec"), visibility("hidden"), used));
extern void tsl9_internal_flash_lock_18c0a(void)
    __attribute__((alias("tsl9_storage_lock_18c0a"), visibility("hidden"), used));
extern void tsl9_internal_flash_erase_18c18(void)
    __attribute__((alias("tsl9_storage_erase_18c18"), visibility("hidden"), used));
extern void tsl9_internal_flash_program_18c46(void)
    __attribute__((alias("tsl9_storage_program_18c46"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R68 scoped startup-check binding: exact existing 9D9E body, no copy. */
#ifdef __cplusplus
extern "C" {
#endif
extern void tsl9_internal_config_read_9d9e(void)
    __attribute__((alias("tsl9_config_read_9d9e"), visibility("hidden"), used));
#ifdef __cplusplus
}
#endif

/* R75 exact-entry hidden aliases; existing bodies unchanged. */
#if defined(__riscv) && __riscv_xlen == 32
__asm__(
        ".global tsl9_internal_r75_9d76\n"
        ".hidden tsl9_internal_r75_9d76\n"
        ".set tsl9_internal_r75_9d76, tsl9_config_persist_9d76\n"
);
#endif
