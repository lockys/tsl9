#include "target_identity_reader.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error "RV32 identity reader only; never host execute"
#endif
__attribute__((naked,noinline,used,section(".text.tsl9_runtime_unported_18caa")))
void tsl9_identity_reader_native(uint8_t *output6 __attribute__((unused))) {
 __asm__ volatile(
  ".option push\n"
  ".option norelax\n"
  ".option nopic\n"
  ".option norvc\n"
  "lui a4, 0x1ffff # original 18caa\n"
  ".option norvc\n"
  "lw a5, 2024(a4) # original 18cae\n"
  ".option norvc\n"
  "srli a3, a5, 0x8 # original 18cb2\n"
  ".option norvc\n"
  "sb a5, 0(a0) # original 18cb6\n"
  ".option norvc\n"
  "sb a3, 1(a0) # original 18cba\n"
  ".option norvc\n"
  "srli a3, a5, 0x10 # original 18cbe\n"
  ".option rvc\n"
  "srli a5, a5, 0x18 # original 18cc2\n"
  ".option norvc\n"
  "sb a3, 2(a0) # original 18cc4\n"
  ".option norvc\n"
  "sb a5, 3(a0) # original 18cc8\n"
  ".option norvc\n"
  "lw a5, 2028(a4) # original 18ccc\n"
  ".option norvc\n"
  "sb a5, 4(a0) # original 18cd0\n"
  ".option rvc\n"
  "srli a5, a5, 0x8 # original 18cd4\n"
  ".option norvc\n"
  "sb a5, 5(a0) # original 18cd6\n"
  ".option rvc\n"
  "ret # original 18cda\n"
  ".option pop\n"
 );
}

