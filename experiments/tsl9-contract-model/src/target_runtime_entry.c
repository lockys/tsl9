#include "target_runtime_entry.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "RV32 Runtime entry required"
#endif
/* Fixed server Runtime V4.1.00, not physical boot/ROM/IRQ proof.
 * gp+64 lookup and gp+112 clock require the complete initialized shared data.
 * Three .insn cj encodings preserve original RV32 C.JAL width and rd=ra.
 * Unknown native callees remain explicit; model APIs are not ABI substitutes. */
#ifdef __cplusplus
extern "C" {
#endif
extern unsigned char __tsl9_can_rx_slots[];
extern void tsl9_runtime_unported_12864(void);
extern void tsl9_runtime_unported_1290a(void);
extern void tsl9_runtime_unported_12b9c(void);
extern void tsl9_runtime_unported_12fdc(void);
extern void tsl9_runtime_unported_14a54(void);
extern void tsl9_runtime_unported_14af8(void);
extern void tsl9_runtime_unported_1524e(void);
extern void tsl9_runtime_unported_1687e(void);
extern void tsl9_runtime_unported_16dac(void);
extern void tsl9_runtime_unported_17176(void);
extern void tsl9_runtime_unported_179ca(void);
extern void tsl9_runtime_unported_19490(void);
extern void tsl9_runtime_unported_8202(void);
extern void tsl9_runtime_unported_82c8(void);
extern void tsl9_runtime_unported_8e82(void);
extern void tsl9_runtime_unported_9432(void);
extern void tsl9_runtime_unported_9936(void);
extern void tsl9_runtime_unported_9a20(void);
extern void tsl9_runtime_unported_9b14(void);
extern void tsl9_runtime_unported_9b2c(void);
extern void tsl9_runtime_unported_9e2c(void);
extern void tsl9_runtime_unported_9e66(void);
#ifdef __cplusplus
}
#endif
static void entry_8180(void) __asm__("tsl9_entry_main_8180");
static void entry_922e(void) __asm__("tsl9_entry_init_922e");
static void entry_18588(void) __asm__("tsl9_entry_clock_update_18588");
static void entry_16d6e(void) __asm__("tsl9_entry_exti_consume_16d6e");
static void entry_12a68(void) __asm__("tsl9_entry_can_consume_12a68");

/* Original 0x8fe6..0x8ff8 (8 instructions, 18 bytes). */
__attribute__((naked, used, section(".text.__tsl9_runtime_entry")))
void __tsl9_runtime_entry(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "addi sp, sp, -16\n"
        "sw ra, 12(sp)\n"
        ".insn cj 1, 1, tsl9_entry_init_922e\n"
        ".option norvc\n"
        "jal ra, tsl9_entry_main_8180\n"
        ".option rvc\n"
        "lw ra, 12(sp)\n"
        "li a0, 0\n"
        "addi sp, sp, 16\n"
        "ret\n"
        ".option pop\n");
}

/* Original 0x8180..0x81aa (15 instructions, 42 bytes). */
/* Permanent 16B frame: opaque RAM callback, EXTI, CAN, watchdog, repeat. */
__attribute__((naked, used, section(".text.tsl9_entry_main_8180")))
static void entry_8180(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "addi sp, sp, -16\n"
        "sw s0, 8(sp)\n"
        "lui s0, 0xb\n"
        "sw s1, 4(sp)\n"
        "sw s2, 0(sp)\n"
        "sw ra, 12(sp)\n"
        "lui s2, 0x20000\n"
        "lui s1, 0x40003\n"
        "addi s0, s0, -1366\n"
        ".Ltsl9_8180_8198:\n"
        "lw a5, 0(s2)\n"
        "jalr a5\n"
        ".option norvc\n"
        "jal ra, tsl9_entry_exti_consume_16d6e\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_entry_can_consume_12a68\n"
        ".option rvc\n"
        "sw s0, 0(s1)\n"
        "j .Ltsl9_8180_8198\n"
        ".option pop\n");
}

/* Original 0x922e..0x926e (19 instructions, 64 bytes). */
/* Restore caller RA/SP before the last real rd0 tail; 14 callees unported. */
__attribute__((naked, used, section(".text.tsl9_entry_init_922e")))
static void entry_922e(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "addi sp, sp, -16\n"
        "sw ra, 12(sp)\n"
        ".option norvc\n"
        "jal ra, tsl9_entry_clock_update_18588\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_9a20\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_19490\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_9e66\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_12fdc\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_runtime_unported_8e82\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_9b2c\n"
        ".option rvc\n"
        ".insn cj 1, 1, tsl9_runtime_unported_9936\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_9e2c\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_12b9c\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_14a54\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_1524e\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_16dac\n"
        ".option rvc\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_17176\n"
        ".option rvc\n"
        "lw ra, 12(sp)\n"
        "addi sp, sp, 16\n"
        ".option norvc\n"
        "j tsl9_runtime_unported_179ca\n"
        ".option rvc\n"
        ".option pop\n");
}

/* Original 0x18588..0x18636 (58 instructions, 174 bytes). */
/* Preserve every fresh MMIO/table/GP access and original RV32 shift/wrap. */
__attribute__((naked, used, section(".text.tsl9_entry_clock_update_18588")))
static void entry_18588(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "lui a4, 0x40021\n"
        "lw a5, 4(a4)\n"
        "li a3, 4\n"
        "andi a5, a5, 12\n"
        "beq a5, a3, .Ltsl9_18588_185cc\n"
        "li a3, 8\n"
        "beq a5, a3, .Ltsl9_18588_185d6\n"
        "lui a5, 0x7a1\n"
        "addi a5, a5, 512\n"
        ".Ltsl9_18588_185a4:\n"
        "sw a5, 112(gp)\n"
        "lui a5, 0x40021\n"
        "lw a5, 4(a5)\n"
        "addi a4, gp, 64\n"
        "srli a5, a5, 0x4\n"
        "andi a5, a5, 15\n"
        "add a5, a5, a4\n"
        "lbu a4, 0(a5)\n"
        "addi a5, gp, 112\n"
        "lw a5, 0(a5)\n"
        "srl a5, a5, a4\n"
        "sw a5, 112(gp)\n"
        "ret\n"
        ".Ltsl9_18588_185cc:\n"
        "lui a5, 0x1e85\n"
        "addi a5, a5, -2048\n"
        "j .Ltsl9_18588_185a4\n"
        ".Ltsl9_18588_185d6:\n"
        "lw a5, 4(a4)\n"
        "lw a4, 4(a4)\n"
        "lui a3, 0x10\n"
        "srli a5, a5, 0x12\n"
        "andi a5, a5, 15\n"
        "and a4, a4, a3\n"
        "addi a5, a5, 2\n"
        "li a3, 17\n"
        "bne a5, a3, .Ltsl9_18588_185ec\n"
        "li a5, 18\n"
        ".Ltsl9_18588_185ec:\n"
        "bnez a4, .Ltsl9_18588_18604\n"
        "lui a4, 0x40024\n"
        "lw a4, -2048(a4)\n"
        "andi a4, a4, 16\n"
        "beqz a4, .Ltsl9_18588_1862c\n"
        ".Ltsl9_18588_185fa:\n"
        "lui a4, 0x7a1\n"
        "addi a4, a4, 512\n"
        "j .Ltsl9_18588_1861c\n"
        ".Ltsl9_18588_18604:\n"
        "lui a3, 0x40021\n"
        "lw a4, 4(a3)\n"
        "lui a2, 0xc00\n"
        "and a4, a4, a2\n"
        "bne a4, a2, .Ltsl9_18588_18622\n"
        "lui a4, 0xf42\n"
        "addi a4, a4, 1024\n"
        ".Ltsl9_18588_1861c:\n"
        "mul a5, a5, a4\n"
        "j .Ltsl9_18588_185a4\n"
        ".Ltsl9_18588_18622:\n"
        "lw a4, 4(a3)\n"
        "slli a3, a4, 0xe\n"
        "bgez a3, .Ltsl9_18588_185fa\n"
        ".Ltsl9_18588_1862c:\n"
        "lui a4, 0x3d1\n"
        "addi a4, a4, -1792\n"
        "j .Ltsl9_18588_1861c\n"
        ".option pop\n");
}

/* Original 0x16d6e..0x16dac (21 instructions, 62 bytes). */
/* Clear each flag before dispatch; second byte read is fresh after the call. */
__attribute__((naked, used, section(".text.tsl9_entry_exti_consume_16d6e")))
static void entry_16d6e(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "addi sp, sp, -16\n"
        "lbu a5, 360(gp)\n"
        "sw ra, 12(sp)\n"
        "andi a4, a5, 1\n"
        "beqz a4, .Ltsl9_16d6e_16d8c\n"
        "andi a5, a5, -2\n"
        "li a0, 1\n"
        "sb a5, 360(gp)\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_1687e\n"
        ".option rvc\n"
        "sb zero, 361(gp)\n"
        ".Ltsl9_16d6e_16d8c:\n"
        "lbu a5, 360(gp)\n"
        "andi a4, a5, 2\n"
        "beqz a4, .Ltsl9_16d6e_16da6\n"
        "andi a5, a5, -3\n"
        "li a0, 2\n"
        "sb a5, 360(gp)\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_1687e\n"
        ".option rvc\n"
        "sb zero, 362(gp)\n"
        ".Ltsl9_16d6e_16da6:\n"
        "lw ra, 12(sp)\n"
        "addi sp, sp, 16\n"
        "ret\n"
        ".option pop\n");
}

/* Original 0x12a68..0x12b9c (105 instructions, 308 bytes). */
/* CSR800 clear0x88 then set0x88 is not a saved-state restore. */
__attribute__((naked, used, section(".text.tsl9_entry_can_consume_12a68")))
static void entry_12a68(void) {
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "addi sp, sp, -80\n"
        "sw s1, 68(sp)\n"
        "sw s2, 64(sp)\n"
        "sw s3, 60(sp)\n"
        "sw s4, 56(sp)\n"
        "sw s5, 52(sp)\n"
        "sw s6, 48(sp)\n"
        "sw s7, 44(sp)\n"
        "sw ra, 76(sp)\n"
        "sw s0, 72(sp)\n"
        "li s1, 0\n"
        ".option norvc\n"
        ".Ltsl9_entry_pc_12a68_12a7e:\n"
        "auipc s5, %pcrel_hi(__tsl9_can_rx_slots)\n"
        "addi s5, s5, %pcrel_lo(.Ltsl9_entry_pc_12a68_12a7e)\n"
        ".option rvc\n"
        "li s6, 12\n"
        "li s2, 136\n"
        "lui s3, 0x40\n"
        "li s4, 1\n"
        "addi s7, gp, 84\n"
        ".Ltsl9_12a68_12a96:\n"
        "mul s0, s1, s6\n"
        "add s0, s0, s5\n"
        "lhu a5, 0(s0)\n"
        "slli a5, a5, 0x10\n"
        "srli a5, a5, 0x10\n"
        "beqz a5, .Ltsl9_12a68_12afe\n"
        "csrc 0x800, s2\n"
        "lw a5, 76(s3)\n"
        "li a2, 12\n"
        "mv a1, s0\n"
        "addi a0, sp, 8\n"
        "jalr a5\n"
        "sh zero, 0(s0)\n"
        "csrs 0x800, s2\n"
        "addi a0, sp, 8\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_82c8\n"
        ".option rvc\n"
        "bnez a0, .Ltsl9_12a68_12afe\n"
        "lhu a5, 8(sp)\n"
        "bne a5, s4, .Ltsl9_12a68_12b88\n"
        "lbu a4, 10(sp)\n"
        "li a5, 4\n"
        "bne a4, a5, .Ltsl9_12a68_12afe\n"
        "lbu a4, 11(sp)\n"
        "li a5, 181\n"
        "bne a4, a5, .Ltsl9_12a68_12afe\n"
        "lbu a4, 12(sp)\n"
        "li a5, 98\n"
        "bne a4, a5, .Ltsl9_12a68_12afe\n"
        "lbu a5, 13(sp)\n"
        "beqz a5, .Ltsl9_12a68_12b1e\n"
        "li a4, 90\n"
        "beq a5, a4, .Ltsl9_12a68_12b5c\n"
        ".Ltsl9_12a68_12afe:\n"
        "addi s1, s1, 1\n"
        "li a5, 32\n"
        "bne s1, a5, .Ltsl9_12a68_12a96\n"
        "lw ra, 76(sp)\n"
        "lw s0, 72(sp)\n"
        "lw s1, 68(sp)\n"
        "lw s2, 64(sp)\n"
        "lw s3, 60(sp)\n"
        "lw s4, 56(sp)\n"
        "lw s5, 52(sp)\n"
        "lw s6, 48(sp)\n"
        "lw s7, 44(sp)\n"
        "addi sp, sp, 80\n"
        "ret\n"
        ".Ltsl9_12a68_12b1e:\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_8202\n"
        ".option rvc\n"
        "lbu a0, 14(sp)\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_9432\n"
        ".option rvc\n"
        "li a0, 0\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_9b14\n"
        ".option rvc\n"
        "lbu a0, 19(sp)\n"
        "li a2, 2\n"
        "addi a1, sp, 20\n"
        "sh zero, 20(sp)\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_1290a\n"
        ".option rvc\n"
        "lbu a4, 19(sp)\n"
        "sh s4, 20(sp)\n"
        "li a5, 2\n"
        "li a0, 1\n"
        "beq a4, a5, .Ltsl9_12a68_12b52\n"
        "li a0, 2\n"
        ".Ltsl9_12a68_12b52:\n"
        "li a2, 2\n"
        "addi a1, sp, 20\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_1290a\n"
        ".option rvc\n"
        "j .Ltsl9_12a68_12afe\n"
        ".Ltsl9_12a68_12b5c:\n"
        "lbu a4, 14(sp)\n"
        "li a5, 85\n"
        "bne a4, a5, .Ltsl9_12a68_12afe\n"
        "lw a5, 76(s3)\n"
        "addi a0, sp, 20\n"
        "li a2, 12\n"
        "addi a1, sp, 8\n"
        "jalr a5\n"
        "li a5, 86\n"
        "addi a0, sp, 20\n"
        "sb a5, 26(sp)\n"
        "sb zero, 31(sp)\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_12864\n"
        ".option rvc\n"
        "j .Ltsl9_12a68_12afe\n"
        ".Ltsl9_12a68_12b88:\n"
        "lw a5, 0(s7)\n"
        "lbu a5, 4(a5)\n"
        "andi a5, a5, 8\n"
        "bnez a5, .Ltsl9_12a68_12afe\n"
        "addi a0, sp, 8\n"
        ".option norvc\n"
        "jal ra, tsl9_runtime_unported_14af8\n"
        ".option rvc\n"
        "j .Ltsl9_12a68_12afe\n"
        ".option pop\n");
}

