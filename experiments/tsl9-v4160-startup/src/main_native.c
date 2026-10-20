#include "main_native.h"
/* ID2966 main wrapper, original register/stack behavior retained.
 * Observed sequence: call 0x9250, call 0x8180; if the second returns,
 * return zero. Callee bodies and their runtime effects are separate obligations.
 * No dummy implementation is provided for either missing callee. */
__asm__(
    ".option push\n"
    ".option norelax\n"
    ".section .text.tsl9v4160.main,\"ax\",@progbits\n"
    ".balign 2\n"
    ".globl __tsl9v4160_main\n"
    ".type __tsl9v4160_main,@function\n"
    "__tsl9v4160_main:\n"
    ".Lmain_9008: .2byte 0x1141\n"
    ".Lmain_900a: .2byte 0xc606\n"
    ".Lmain_900c: .2byte 0x2491\n"
    ".reloc .Lmain_900c, R_RISCV_RVC_JUMP, __tsl9v4160_call_9250\n"
    ".Lmain_900e: .4byte 0x972ff0ef\n"
    ".reloc .Lmain_900e, R_RISCV_JAL, __tsl9v4160_call_8180\n"
    ".Lmain_9012: .2byte 0x40b2\n"
    ".Lmain_9014: .2byte 0x4501\n"
    ".Lmain_9016: .2byte 0x0141\n"
    ".Lmain_9018: .2byte 0x8082\n"
    ".size __tsl9v4160_main, .-__tsl9v4160_main\n"
    ".option pop\n"
);
