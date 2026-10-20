#include "target_reset_fidelity.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "RV32 reset only; never host-execute this component"
#endif
/* Fixed V4.1.00 observed148B span, represented without duplicating existing
 * vector defaults1848C/18490:138B reset path plus private4B MRET at18488.
 * This is a native representation split, not recovered original symbols.
 * Preserve GP+136 endpoints, five CSR writes,4B clock JAL/ROM tail and
 * incidental registers. Linker stack_top/data/ROM providers remain unknown. */
#ifdef __cplusplus
extern "C" {
#endif
extern unsigned char __tsl9_data_start[];
extern unsigned char __tsl9_stack_top[];
extern unsigned char __tsl9_data_load[];
extern unsigned char __tsl9_bss_end[];
extern unsigned char __tsl9_vector_table[];
extern unsigned char __tsl9_runtime_entry[];
extern void sc_native_init(void);
extern unsigned char __tsl9_rom_entry[];
#ifdef __cplusplus
}
#endif
static void reset_mret65(void) __asm__("tsl9_reset_mret_18488");

__attribute__((naked,noinline,used,section(".text.tsl9_reset_entry")))
void tsl9_reset_entry(void) {
 __asm__ volatile(
  ".option push\n"
  ".option norelax\n"
  ".option nopic\n"
  ".option norvc\n"
  ".Lreset65pc_183fe:\n"
  "auipc gp, %pcrel_hi(__tsl9_data_start) # original 183fe\n"
  ".option norvc\n"
  "addi gp, gp, %pcrel_lo(.Lreset65pc_183fe) # original 18402\n"
  ".option norvc\n"
  ".Lreset65pc_18406:\n"
  "auipc sp, %pcrel_hi(__tsl9_stack_top) # original 18406\n"
  ".option norvc\n"
  "addi sp, sp, %pcrel_lo(.Lreset65pc_18406) # original 1840a\n"
  ".option norvc\n"
  ".Lreset65pc_1840e:\n"
  "auipc a0, %pcrel_hi(__tsl9_data_load) # original 1840e\n"
  ".option norvc\n"
  "addi a0, a0, %pcrel_lo(.Lreset65pc_1840e) # original 18412\n"
  ".option norvc\n"
  "mv a1, gp # original 18416\n"
  ".option norvc\n"
  "addi a2, gp, 136 # original 1841a\n"
  ".option norvc\n"
  "bleu a2, a1, .Lreset65_18432 # original 1841e\n"
  ".Lreset65_18422:\n"
  ".option norvc\n"
  "lw t0, 0(a0) # original 18422\n"
  ".option norvc\n"
  "sw t0, 0(a1) # original 18426\n"
  ".option rvc\n"
  "addi a0, a0, 4 # original 1842a\n"
  ".option rvc\n"
  "addi a1, a1, 4 # original 1842c\n"
  ".option norvc\n"
  "bltu a1, a2, .Lreset65_18422 # original 1842e\n"
  ".Lreset65_18432:\n"
  ".option norvc\n"
  "addi a0, gp, 136 # original 18432\n"
  ".option norvc\n"
  ".Lreset65pc_18436:\n"
  "auipc a1, %pcrel_hi(__tsl9_bss_end) # original 18436\n"
  ".option norvc\n"
  "addi a1, a1, %pcrel_lo(.Lreset65pc_18436) # original 1843a\n"
  ".option norvc\n"
  "bleu a1, a0, .Lreset65_1844c # original 1843e\n"
  ".Lreset65_18442:\n"
  ".option norvc\n"
  "sw zero, 0(a0) # original 18442\n"
  ".option rvc\n"
  "addi a0, a0, 4 # original 18446\n"
  ".option norvc\n"
  "bltu a0, a1, .Lreset65_18442 # original 18448\n"
  ".Lreset65_1844c:\n"
  ".option rvc\n"
  "li t0, 31 # original 1844c\n"
  ".option norvc\n"
  "csrw 0xbc0, t0 # original 1844e\n"
  ".option rvc\n"
  "li t0, 3 # original 18452\n"
  ".option norvc\n"
  "csrw 0x804, t0 # original 18454\n"
  ".option norvc\n"
  "lui t0, 0x2 # original 18458\n"
  ".option norvc\n"
  "addi t0, t0, -1912 # original 1845c\n"
  ".option norvc\n"
  "csrs mstatus, t0 # original 18460\n"
  ".option norvc\n"
  ".Lreset65pc_18464:\n"
  "auipc t0, %pcrel_hi(__tsl9_vector_table) # original 18464\n"
  ".option norvc\n"
  "addi t0, t0, %pcrel_lo(.Lreset65pc_18464) # original 18468\n"
  ".option norvc\n"
  "ori t0, t0, 3 # original 1846c\n"
  ".option norvc\n"
  "csrw mtvec, t0 # original 18470\n"
  ".option norvc\n"
  "jal ra, sc_native_init # original 18474\n"
  ".option norvc\n"
  ".Lreset65pc_18478:\n"
  "auipc t0, %pcrel_hi(__tsl9_runtime_entry) # original 18478\n"
  ".option norvc\n"
  "addi t0, t0, %pcrel_lo(.Lreset65pc_18478) # original 1847c\n"
  ".option norvc\n"
  "csrw mepc, t0 # original 18480\n"
  ".option norvc\n"
  "jal zero, __tsl9_rom_entry # original 18484\n"
  ".option pop\n"
 );
}

__attribute__((naked,noinline,used,section(".text.tsl9_reset_mret_18488")))
static void reset_mret65(void) {
 __asm__ volatile(
  ".option push\n"
  ".option norelax\n"
  ".option nopic\n"
  ".option norvc\n"
  "mret # original 18488\n"
  ".option pop\n"
 );
}
