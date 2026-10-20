#include "target_reset.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error This reset component is RV32-only; never compile it as a host substitute.
#endif
/* Basic assembly only: a C prologue before gp/sp initialization is invalid.
   The final linker's absolute ROM symbol preserves JAL x0 handoff without
   inventing an indirect jump that clobbers t0 at the ROM entry boundary.
   No address in the original binary is called/executed by host verification. */
__attribute__((naked,noreturn,used,section(".text.tsl9_reset")))
void tsl9_reset_entry(void){
 __asm__ volatile(
  ".option push\n"
  ".option norelax\n"
  ".option nopic\n"
  "li gp,0x20004000\n"
  "li sp,0x20010000\n"
  "la a0,__tsl9_data_load\n"
  "la a1,__tsl9_data_start\n"
  "la a2,__tsl9_data_end\n"
  "bgeu a1,a2,2f\n"
  "1:\n"
  "lw t0,0(a0)\n"
  "sw t0,0(a1)\n"
  "addi a0,a0,4\n"
  "addi a1,a1,4\n"
  "bltu a1,a2,1b\n"
  "2:\n"
  "la a0,__tsl9_bss_start\n"
  "la a1,__tsl9_bss_end\n"
  "bgeu a0,a1,4f\n"
  "3:\n"
  "sw zero,0(a0)\n"
  "addi a0,a0,4\n"
  "bltu a0,a1,3b\n"
  "4:\n"
  "li t0,31\n"
  "csrw 0xbc0,t0\n"
  "li t0,3\n"
  "csrw 0x804,t0\n"
  "li t0,0x1888\n"
  "csrs mstatus,t0\n"
  "la t0,__tsl9_vector_table\n"
  "ori t0,t0,3\n"
  "csrw mtvec,t0\n"
  "call sc_native_init\n"
  "la t0,__tsl9_runtime_entry\n"
  "csrw mepc,t0\n"
  "j __tsl9_rom_entry\n"
  "mret\n"
  "mret\n"
  "5: j 5b\n"
  ".option pop\n"
 );
}
