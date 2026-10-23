#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private dispatch regions only; never execute on a HOST or device.
#endif

/* Handler portion of [0x14D2E,0x154A6). Ordinary C owns loads, stores,
 * free-bank argument moves, masks, comparisons and constants. Empty architectural
 * register ports prevent assumptions about then-live state or an ordinary
 * ABI. Reserved-S0 argument moves/loads and frame/control/PC operations
 * are explicit architectural ports; free-bank and GP memory operations are C.
 * GP byte meanings, physical hardware and resident ABI remain unknown.
 * Table words below are signed-relative symbol bindings, not code bytes.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS \
    register uint32_t a0 __asm__("a0"); \
    register uint32_t a1 __asm__("a1"); \
    register uint32_t a2 __asm__("a2"); \
    register uint32_t a3 __asm__("a3"); \
    register uint32_t a4 __asm__("a4"); \
    register uint32_t a5 __asm__("a5"); \
    register uint32_t gp __asm__("gp"); \
    __asm__ volatile("" : "=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5), \
                         "=r"(gp) : : "memory")
#define PORT(text) __asm__ volatile(text : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5), \
                                         "+r"(gp) : : "memory")
#define STEP() PORT("")

/* Original [0x1505c,0x15068). */
REGION void tsl9_feature_handler_1505c(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_d288\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15068,0x15072). */
REGION void tsl9_feature_handler_15068(void)
{
    REGS;
    PORT("mv a2, s0");
    a0 = UINT32_C(0); STEP();
    a1 = UINT32_C(0); STEP();
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_82a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15072,0x1507e). */
REGION void tsl9_feature_handler_15072(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_def2\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1507e,0x1508a). */
REGION void tsl9_feature_handler_1507e(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_dac8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1508a,0x15096). */
REGION void tsl9_feature_handler_1508a(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_10440\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15096,0x1509a). */
REGION void tsl9_feature_handler_15096(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(1); STEP();
    __builtin_unreachable();
}

/* Original [0x1509a,0x150a6). */
REGION void tsl9_feature_handler_1509a(void)
{
    REGS;
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    a0 = UINT32_C(0); STEP();
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_82a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150a6,0x150b2). */
REGION void tsl9_feature_handler_150a6(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_d632\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150b2,0x150be). */
REGION void tsl9_feature_handler_150b2(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_dbcc\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150be,0x150c4). */
REGION void tsl9_feature_handler_150be(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_cec0\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150c4,0x150d0). */
REGION void tsl9_feature_handler_150c4(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_cedc\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150d0,0x150dc). */
REGION void tsl9_feature_handler_150d0(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_b2fe\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150dc,0x150e2). */
REGION void tsl9_feature_handler_150dc(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_c8a2\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150e2,0x150ee). */
REGION void tsl9_feature_handler_150e2(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_c94e\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150ee,0x150fa). */
REGION void tsl9_feature_handler_150ee(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_10288\n.option pop");
    __builtin_unreachable();
}

/* Original [0x150fa,0x15106). */
REGION void tsl9_feature_handler_150fa(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_d104\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15106,0x15108). */
REGION void tsl9_feature_handler_15106(void)
{
    REGS;
    a1 = UINT32_C(1); STEP();
    __builtin_unreachable();
}

/* Original [0x15108,0x15114). */
REGION void tsl9_feature_handler_15108(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_10100\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15114,0x1511a). */
REGION void tsl9_feature_handler_15114(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(3); STEP();
    PORT(".Ldispatch_15118:\nc.j .Ldispatch_15118\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x1511a,0x15126). */
REGION void tsl9_feature_handler_1511a(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_b1b6\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15126,0x1512c). */
REGION void tsl9_feature_handler_15126(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(4); STEP();
    PORT(".Ldispatch_1512a:\nc.j .Ldispatch_1512a\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x1512c,0x15138). */
REGION void tsl9_feature_handler_1512c(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_da74\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15138,0x1513c). */
REGION void tsl9_feature_handler_15138(void)
{
    REGS;
    a1 = UINT32_C(0); STEP();
    PORT(".Ldispatch_1513a:\nc.j .Ldispatch_1513a\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15108");
    __builtin_unreachable();
}

/* Original [0x1513c,0x15148). */
REGION void tsl9_feature_handler_1513c(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_b402\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15148,0x15154). */
REGION void tsl9_feature_handler_15148(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_b372\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15154,0x15160). */
REGION void tsl9_feature_handler_15154(void)
{
    REGS;
    PORT("lbu a5, 3(s0)");
    a4 = UINT32_C(1); STEP();
    a5 = a5 & UINT32_C(3); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbne a5, a4, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_handler_1516a");
    __builtin_unreachable();
}

/* Original [0x15160,0x1516a). */
REGION void tsl9_feature_handler_15160(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(5); STEP();
    a0 = UINT32_C(0); STEP();
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_82a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1516a,0x15176). */
REGION void tsl9_feature_handler_1516a(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_d3f6\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15176,0x15182). */
REGION void tsl9_feature_handler_15176(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_d378\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15182,0x15190). */
REGION void tsl9_feature_handler_15182(void)
{
    REGS;
    PORT("mv a1, s0");
    PORT("auipc a0, 0xffffb");
    a0 = a0 + UINT32_C(1306); STEP();
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_1083c\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15190,0x15194). */
REGION void tsl9_feature_handler_15190(void)
{
    REGS;
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbeqz a0, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x15194,0x15198). */
REGION void tsl9_feature_handler_15194(void)
{
    REGS;
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_106e8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15198,0x151a4). */
REGION void tsl9_feature_handler_15198(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_f860\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151a4,0x151b0). */
REGION void tsl9_feature_handler_151a4(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_d47c\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151b0,0x151b6). */
REGION void tsl9_feature_handler_151b0(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(6); STEP();
    PORT(".Ldispatch_151b4:\nc.j .Ldispatch_151b4\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x151b6,0x151c0). */
REGION void tsl9_feature_handler_151b6(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(8); STEP();
    a0 = UINT32_C(0); STEP();
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_82a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151c0,0x151c6). */
REGION void tsl9_feature_handler_151c0(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_fa62\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151c6,0x151d2). */
REGION void tsl9_feature_handler_151c6(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_fa7c\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151d2,0x151de). */
REGION void tsl9_feature_handler_151d2(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_10044\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151de,0x151e6). */
REGION void tsl9_feature_handler_151de(void)
{
    REGS;
    PORT("lbu a5, 3(s0)");
    a5 = a5 & UINT32_C(3); STEP();
    PORT(".Ldispatch_151e4:\nc.beqz a5, .Ldispatch_151e4\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_151fe");
    __builtin_unreachable();
}

/* Original [0x151e6,0x151ec). */
REGION void tsl9_feature_handler_151e6(void)
{
    REGS;
    a4 = UINT32_C(1); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbeq a5, a4, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_handler_1520a");
    __builtin_unreachable();
}

/* Original [0x151ec,0x151f2). */
REGION void tsl9_feature_handler_151ec(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_b730\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151f2,0x151fe). */
REGION void tsl9_feature_handler_151f2(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_bd88\n.option pop");
    __builtin_unreachable();
}

/* Original [0x151fe,0x15202). */
REGION void tsl9_feature_handler_151fe(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(9); STEP();
    __builtin_unreachable();
}

/* Original [0x15202,0x15208). */
REGION void tsl9_feature_handler_15202(void)
{
    REGS;
    a0 = UINT32_C(0); STEP();
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_82a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15208,0x1520a). */
REGION void tsl9_feature_handler_15208(void)
{
    REGS;
    PORT(".Ldispatch_15208:\nc.j .Ldispatch_15208\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_151ec");
    __builtin_unreachable();
}

/* Original [0x1520a,0x15210). */
REGION void tsl9_feature_handler_1520a(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(10); STEP();
    PORT(".Ldispatch_1520e:\nc.j .Ldispatch_1520e\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15202");
    __builtin_unreachable();
}

/* Original [0x15210,0x1521c). */
REGION void tsl9_feature_handler_15210(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_10096\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1521c,0x15222). */
REGION void tsl9_feature_handler_1521c(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(11); STEP();
    PORT(".Ldispatch_15220:\nc.j .Ldispatch_15220\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x15222,0x1522e). */
REGION void tsl9_feature_handler_15222(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_c3d4\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1522e,0x15238). */
REGION void tsl9_feature_handler_1522e(void)
{
    REGS;
    a1 = UINT32_C(13); STEP();
    a0 = UINT32_C(0); STEP();
    PORT("mv a2, s0");
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_82a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15238,0x15246). */
REGION void tsl9_feature_handler_15238(void)
{
    REGS;
    PORT("mv a1, s0");
    PORT("auipc a0, 0xffffb");
    a0 = a0 + UINT32_C(1124); STEP();
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_1083c\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15246,0x1524a). */
REGION void tsl9_feature_handler_15246(void)
{
    REGS;
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbeqz a0, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x1524a,0x15250). */
REGION void tsl9_feature_handler_1524a(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_add6\n.option pop");
    __builtin_unreachable();
}

/* Original [0x15250,0x1525c). */
REGION void tsl9_feature_handler_15250(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_fba2\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1525c,0x15262). */
REGION void tsl9_feature_handler_1525c(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(12); STEP();
    PORT(".Ldispatch_15260:\nc.j .Ldispatch_15260\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x15262,0x1526e). */
REGION void tsl9_feature_handler_15262(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_d69c\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1526e,0x15278). */
REGION void tsl9_feature_handler_1526e(void)
{
    REGS;
    PORT("lbu a5, 3(s0)");
    a5 = a5 & UINT32_C(7); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbnez a5, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x15278,0x1527e). */
REGION void tsl9_feature_handler_15278(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(14); STEP();
    PORT(".Ldispatch_1527c:\nc.j .Ldispatch_1527c\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x1527e,0x1528a). */
REGION void tsl9_feature_handler_1527e(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_13bd2\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1528a,0x15296). */
REGION void tsl9_feature_handler_1528a(void)
{
    REGS;
    PORT("lbu a5, 3(s0)");
    a4 = UINT32_C(5); STEP();
    a5 = a5 & UINT32_C(7); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbne a5, a4, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x15296,0x1529c). */
REGION void tsl9_feature_handler_15296(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(16); STEP();
    PORT(".Ldispatch_1529a:\nc.j .Ldispatch_1529a\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x1529c,0x152a8). */
REGION void tsl9_feature_handler_1529c(void)
{
    REGS;
    PORT("lbu a5, 3(s0)");
    a4 = UINT32_C(5); STEP();
    a5 = a5 & UINT32_C(7); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbne a5, a4, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x152a8,0x152ae). */
REGION void tsl9_feature_handler_152a8(void)
{
    REGS;
    PORT("mv a2, s0");
    a1 = UINT32_C(17); STEP();
    PORT(".Ldispatch_152ac:\nc.j .Ldispatch_152ac\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_1509a");
    __builtin_unreachable();
}

/* Original [0x152ae,0x152ba). */
REGION void tsl9_feature_handler_152ae(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_185d8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x152ba,0x152c4). */
REGION void tsl9_feature_handler_152ba(void)
{
    REGS;
    PORT("mv a2, s0");
    a0 = UINT32_C(0); STEP();
    a1 = UINT32_C(18); STEP();
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_82a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x152c4,0x152d0). */
REGION void tsl9_feature_handler_152c4(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_c6a8\n.option pop");
    __builtin_unreachable();
}

/* Original [0x152d0,0x152dc). */
REGION void tsl9_feature_handler_152d0(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_a054\n.option pop");
    __builtin_unreachable();
}

/* Original [0x152dc,0x152e8). */
REGION void tsl9_feature_handler_152dc(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_b036\n.option pop");
    __builtin_unreachable();
}

/* Original [0x152e8,0x152f4). */
REGION void tsl9_feature_handler_152e8(void)
{
    REGS;
    PORT("mv a0, s0");
    PORT("lw s0, 8(sp)");
    PORT("lw ra, 12(sp)");
    PORT("addi sp, sp, 16");
    PORT(".option push\n.option norvc\njal zero, tsl9_feature_external_b05c\n.option pop");
    __builtin_unreachable();
}

/* Original [0x152f4,0x152fe). */
REGION void tsl9_feature_handler_152f4(void)
{
    REGS;
    PORT("lbu a5, 3(s0)");
    a4 = UINT32_C(2); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbeq a5, a4, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_handler_15326");
    __builtin_unreachable();
}

/* Original [0x152fe,0x15304). */
REGION void tsl9_feature_handler_152fe(void)
{
    REGS;
    a4 = UINT32_C(3); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbeq a5, a4, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_handler_15338");
    __builtin_unreachable();
}

/* Original [0x15304,0x1530a). */
REGION void tsl9_feature_handler_15304(void)
{
    REGS;
    a4 = UINT32_C(1); STEP();
    PORT(".Lhandler_branch_%=:\n.option push\n.option norvc\nbne a5, a4, .Lhandler_branch_%=\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x1530a,0x15326). */
REGION void tsl9_feature_handler_1530a(void)
{
    REGS;
    PORT("lbu a5, 8(s0)");
    a5 = a5 & UINT32_C(7); STEP();
    a5 = (uint32_t)(a5 < UINT32_C(4)); STEP();
    *(volatile uint8_t *)(uintptr_t)(gp + UINT32_C(348)) = (uint8_t)a5; STEP();
    PORT("lbu a5, 4(s0)");
    a5 = a5 >> 3u; STEP();
    a5 = a5 & UINT32_C(1); STEP();
    *(volatile uint8_t *)(uintptr_t)(gp + UINT32_C(355)) = (uint8_t)a5; STEP();
    PORT(".Ldispatch_15324:\nc.j .Ldispatch_15324\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x15326,0x15338). */
REGION void tsl9_feature_handler_15326(void)
{
    REGS;
    PORT("lbu a5, 8(s0)");
    a5 = a5 & UINT32_C(24); STEP();
    a5 = a5 - UINT32_C(8); STEP();
    a5 = (uint32_t)(a5 == 0u); STEP();
    *(volatile uint8_t *)(uintptr_t)(gp + UINT32_C(353)) = (uint8_t)a5; STEP();
    PORT(".Ldispatch_15336:\nc.j .Ldispatch_15336\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x15338,0x15364). */
REGION void tsl9_feature_handler_15338(void)
{
    REGS;
    PORT("lbu a5, 4(s0)");
    a5 = a5 & UINT32_C(112); STEP();
    a5 = a5 - UINT32_C(16); STEP();
    a5 = (uint32_t)(a5 == 0u); STEP();
    *(volatile uint8_t *)(uintptr_t)(gp + UINT32_C(356)) = (uint8_t)a5; STEP();
    PORT("lbu a5, 5(s0)");
    PORT("auipc a4, 0x5");
    a4 = a4 + UINT32_C(902); STEP();
    a5 = a5 >> 2u; STEP();
    a5 = a5 & UINT32_C(7); STEP();
    a5 = a5 << 2u; STEP();
    a5 = a5 + a4; STEP();
    a5 = *(volatile const uint32_t *)(uintptr_t)(a5 + UINT32_C(0)); STEP();
    a5 = a5 + a4; STEP();
    PORT("jr a5");
    __builtin_unreachable();
}

/* Original [0x15364,0x15366). */
REGION void tsl9_feature_handler_15364(void)
{
    REGS;
    a5 = UINT32_C(7); STEP();
    __builtin_unreachable();
}

/* Original [0x15366,0x1536c). */
REGION void tsl9_feature_handler_15366(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(gp + UINT32_C(357)) = (uint8_t)a5; STEP();
    PORT(".Ldispatch_1536a:\nc.j .Ldispatch_1536a\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original [0x1536c,0x15370). */
REGION void tsl9_feature_handler_1536c(void)
{
    REGS;
    a5 = UINT32_C(8); STEP();
    PORT(".Ldispatch_1536e:\nc.j .Ldispatch_1536e\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x15370,0x15376). */
REGION void tsl9_feature_handler_15370(void)
{
    REGS;
    a5 = *(volatile const uint8_t *)(uintptr_t)(gp + UINT32_C(354)); STEP();
    PORT(".Ldispatch_15374:\nc.beqz a5, .Ldispatch_15374\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_15382");
    __builtin_unreachable();
}

/* Original [0x15376,0x1537a). */
REGION void tsl9_feature_handler_15376(void)
{
    REGS;
    PORT(".option push\n.option norvc\njal ra, tsl9_feature_external_cd4e\n.option pop");
    __builtin_unreachable();
}

/* Original [0x1537a,0x1537e). */
REGION void tsl9_feature_handler_1537a(void)
{
    REGS;
    a5 = UINT32_C(10); STEP();
    PORT(".Ldispatch_1537c:\nc.bnez a0, .Ldispatch_1537c\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x1537e,0x15382). */
REGION void tsl9_feature_handler_1537e(void)
{
    REGS;
    a5 = UINT32_C(5); STEP();
    PORT(".Ldispatch_15380:\nc.j .Ldispatch_15380\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x15382,0x1538a). */
REGION void tsl9_feature_handler_15382(void)
{
    REGS;
    a4 = *(volatile const uint8_t *)(uintptr_t)(gp + UINT32_C(348)); STEP();
    a5 = UINT32_C(1); STEP();
    PORT(".Ldispatch_15388:\nc.bnez a4, .Ldispatch_15388\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x1538a,0x15390). */
REGION void tsl9_feature_handler_1538a(void)
{
    REGS;
    a4 = *(volatile const uint8_t *)(uintptr_t)(gp + UINT32_C(352)); STEP();
    PORT(".Ldispatch_1538e:\nc.bnez a4, .Ldispatch_1538e\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x15390,0x15394). */
REGION void tsl9_feature_handler_15390(void)
{
    REGS;
    a5 = UINT32_C(3); STEP();
    PORT(".Ldispatch_15392:\nc.j .Ldispatch_15392\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x15394,0x1539a). */
REGION void tsl9_feature_handler_15394(void)
{
    REGS;
    a5 = *(volatile const uint8_t *)(uintptr_t)(gp + UINT32_C(354)); STEP();
    PORT(".Ldispatch_15398:\nc.beqz a5, .Ldispatch_15398\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_1539e");
    __builtin_unreachable();
}

/* Original [0x1539a,0x1539e). */
REGION void tsl9_feature_handler_1539a(void)
{
    REGS;
    a5 = UINT32_C(6); STEP();
    PORT(".Ldispatch_1539c:\nc.j .Ldispatch_1539c\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x1539e,0x153a6). */
REGION void tsl9_feature_handler_1539e(void)
{
    REGS;
    a4 = *(volatile const uint8_t *)(uintptr_t)(gp + UINT32_C(348)); STEP();
    a5 = UINT32_C(2); STEP();
    PORT(".Ldispatch_153a4:\nc.bnez a4, .Ldispatch_153a4\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x153a6,0x153ac). */
REGION void tsl9_feature_handler_153a6(void)
{
    REGS;
    a4 = *(volatile const uint8_t *)(uintptr_t)(gp + UINT32_C(352)); STEP();
    PORT(".Ldispatch_153aa:\nc.bnez a4, .Ldispatch_153aa\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x153ac,0x153b0). */
REGION void tsl9_feature_handler_153ac(void)
{
    REGS;
    a5 = UINT32_C(4); STEP();
    PORT(".Ldispatch_153ae:\nc.j .Ldispatch_153ae\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x153b0,0x153b4). */
REGION void tsl9_feature_handler_153b0(void)
{
    REGS;
    a5 = UINT32_C(9); STEP();
    PORT(".Ldispatch_153b2:\nc.j .Ldispatch_153b2\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_handler_15366");
    __builtin_unreachable();
}

/* Original [0x153b4,0x153ba). */
REGION void tsl9_feature_handler_153b4(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(gp + UINT32_C(357)) = (uint8_t)0; STEP();
    PORT(".Ldispatch_153b8:\nc.j .Ldispatch_153b8\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_feature_return_14da2");
    __builtin_unreachable();
}

/* Original signed-relative metadata at 0x1A6D4. No target substitute. */
__asm__(
    ".section .rodata.tsl9_feature_nested_table,\"a\",@progbits\n"
    ".p2align 2\n"
    ".globl tsl9_feature_nested_table_1a6d4\n"
    ".type tsl9_feature_nested_table_1a6d4,@object\n"
    "tsl9_feature_nested_table_1a6d4:\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_15364\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_1536c\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_15370\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_15394\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_153b4\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_153b4\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_153b4\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".word 0\n.reloc .-4, R_RISCV_ADD32, tsl9_feature_handler_153b0\n.reloc .-4, R_RISCV_SUB32, tsl9_feature_nested_table_1a6d4\n"
    ".size tsl9_feature_nested_table_1a6d4,32\n"
    ".text\n"
);
