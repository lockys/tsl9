#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private architectural blocks only; never execute on HOST/hardware.
#endif
/* Original [14D5E,1505C):766B. Scalar constants/masks are C; physical S0
 * loads/moves, stack restoration and typed control transfers are explicit
 * architectural ports. Calls may change SP/S0/GP; no ordinary ABI is assumed.
 * This file is incomplete without the genuine handler/outer/callee providers.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

REGION void tsl9_feature_mode1_14d5e(void) {
    REGS;
    __asm__ volatile("lhu a5, 0(s0)" : "=r"(a5) : : "memory");
    a4 = (uint32_t)(819); LIVE;
    __asm__ volatile(".Ltree_14d66:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14d66\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15176" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d6a(void) {
    REGS;
    __asm__ volatile(".Ltree_14d6a:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14d6a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14ed8" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d6e(void) {
    REGS;
    a4 = (uint32_t)(599); LIVE;
    __asm__ volatile(".Ltree_14d72:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14d72\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_150ee" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d76(void) {
    REGS;
    __asm__ volatile(".Ltree_14d76:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14d76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14e1a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d7a(void) {
    REGS;
    a4 = (uint32_t)(325); LIVE;
    __asm__ volatile(".Ltree_14d7e:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14d7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_150a6" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d82(void) {
    REGS;
    __asm__ volatile(".Ltree_14d82:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14d82\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14dce" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d86(void) {
    REGS;
    a4 = (uint32_t)(259); LIVE;
    __asm__ volatile(".Ltree_14d8a:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14d8a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1507e" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d8e(void) {
    REGS;
    __asm__ volatile(".Ltree_14d8e:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14d8e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14daa" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d92(void) {
    REGS;
    a4 = (uint32_t)(130); LIVE;
    __asm__ volatile(".Ltree_14d96:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14d96\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1505c" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14d9a(void) {
    REGS;
    a4 = (uint32_t)(258); LIVE;
    __asm__ volatile(".Ltree_14d9e:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14d9e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15068" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_return_14da2(void) {
    REGS;
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile("ret" : : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14daa(void) {
    REGS;
    a4 = (uint32_t)(297); LIVE;
    __asm__ volatile(".Ltree_14dae:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14dae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1508a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14db2(void) {
    REGS;
    a4 = (uint32_t)(306); LIVE;
    __asm__ volatile(".Ltree_14db6:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14db6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15096" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14dba(void) {
    REGS;
    a4 = (uint32_t)(280); LIVE;
    __asm__ volatile(".Ltree_14dbe:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14dbe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14dc2(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14dca:\n.option push\n.option norvc\njal zero,.Ltree_14dca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_cf96" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14dce(void) {
    REGS;
    a4 = (uint32_t)(553); LIVE;
    __asm__ volatile(".Ltree_14dd2:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14dd2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_150be" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14dd6(void) {
    REGS;
    __asm__ volatile(".Ltree_14dd6:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14dd6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14df6" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14dda(void) {
    REGS;
    a4 = (uint32_t)(505); LIVE;
    __asm__ volatile(".Ltree_14dde:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14dde\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_150b2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14de2(void) {
    REGS;
    a4 = (uint32_t)(524); LIVE;
    __asm__ volatile(".Ltree_14de6:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14de6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14dea(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14df2:\n.option push\n.option norvc\njal zero,.Ltree_14df2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_b390" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14df6(void) {
    REGS;
    a4 = (uint32_t)(579); LIVE;
    __asm__ volatile(".Ltree_14dfa:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14dfa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_150d0" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14dfe(void) {
    REGS;
    a4 = (uint32_t)(585); LIVE;
    __asm__ volatile(".Ltree_14e02:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_150dc" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e06(void) {
    REGS;
    a4 = (uint32_t)(568); LIVE;
    __asm__ volatile(".Ltree_14e0a:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14e0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e0e(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14e16:\n.option push\n.option norvc\njal zero,.Ltree_14e16\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_abc4" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e1a(void) {
    REGS;
    a4 = (uint32_t)(692); LIVE;
    __asm__ volatile(".Ltree_14e1e:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e1e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15126" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e22(void) {
    REGS;
    __asm__ volatile(".Ltree_14e22:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14e22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14e84" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e26(void) {
    REGS;
    a4 = (uint32_t)(614); LIVE;
    __asm__ volatile(".Ltree_14e2a:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15106" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e2e(void) {
    REGS;
    __asm__ volatile(".Ltree_14e2e:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14e2e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14e4e" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e32(void) {
    REGS;
    a4 = (uint32_t)(602); LIVE;
    __asm__ volatile(".Ltree_14e36:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_150fa" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e3a(void) {
    REGS;
    a4 = (uint32_t)(605); LIVE;
    __asm__ volatile(".Ltree_14e3e:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14e3e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e42(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14e4a:\n.option push\n.option norvc\njal zero,.Ltree_14e4a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_d332" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e4e(void) {
    REGS;
    a4 = (uint32_t)(658); LIVE;
    __asm__ volatile(".Ltree_14e52:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e52\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15114" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e56(void) {
    REGS;
    a4 = (uint32_t)(659); LIVE;
    __asm__ volatile(".Ltree_14e5a:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e5a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1511a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e5e(void) {
    REGS;
    a4 = (uint32_t)(627); LIVE;
    __asm__ volatile(".Ltree_14e62:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14e62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e66(void) {
    REGS;
    __asm__ volatile("mv a2, s0" : "=r"(a2) : : "memory");
    a1 = (uint32_t)(2); LIVE;
    a0 = (uint32_t)(0); LIVE;
    __asm__ volatile(".Ltree_14e6c:\n.option push\n.option norvc\njal ra,.Ltree_14e6c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5) : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e70(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile(".Ltree_14e72:\n.option push\n.option norvc\njal ra,.Ltree_14e72\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f14a" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5) : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e76(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    a1 = (uint32_t)(0); LIVE;
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14e80:\n.option push\n.option norvc\njal zero,.Ltree_14e80\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e84(void) {
    REGS;
    a4 = (uint32_t)(755); LIVE;
    __asm__ volatile(".Ltree_14e88:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1513c" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e8c(void) {
    REGS;
    __asm__ volatile(".Ltree_14e8c:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14e8c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14eb4" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e90(void) {
    REGS;
    a4 = (uint32_t)(737); LIVE;
    __asm__ volatile(".Ltree_14e94:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1512c" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14e98(void) {
    REGS;
    a4 = (uint32_t)(741); LIVE;
    __asm__ volatile(".Ltree_14e9c:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14e9c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15138" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ea0(void) {
    REGS;
    a4 = (uint32_t)(694); LIVE;
    __asm__ volatile(".Ltree_14ea4:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14ea4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ea8(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14eb0:\n.option push\n.option norvc\njal zero,.Ltree_14eb0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_b14a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14eb4(void) {
    REGS;
    a4 = (uint32_t)(801); LIVE;
    __asm__ volatile(".Ltree_14eb8:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14eb8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15148" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ebc(void) {
    REGS;
    a4 = (uint32_t)(818); LIVE;
    __asm__ volatile(".Ltree_14ec0:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14ec0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15154" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ec4(void) {
    REGS;
    a4 = (uint32_t)(799); LIVE;
    __asm__ volatile(".Ltree_14ec8:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14ec8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ecc(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14ed4:\n.option push\n.option norvc\njal zero,.Ltree_14ed4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_d14a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ed8(void) {
    REGS;
    a4 = (uint32_t)(991); LIVE;
    __asm__ volatile(".Ltree_14edc:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14edc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1525c" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ee0(void) {
    REGS;
    __asm__ volatile(".Ltree_14ee0:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14ee0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14fa0" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ee4(void) {
    REGS;
    a4 = (uint32_t)(923); LIVE;
    __asm__ volatile(".Ltree_14ee8:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14ee8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_152e8" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14eec(void) {
    REGS;
    __asm__ volatile(".Ltree_14eec:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14eec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14f46" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ef0(void) {
    REGS;
    a4 = (uint32_t)(826); LIVE;
    __asm__ volatile(".Ltree_14ef4:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14ef4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_151a4" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ef8(void) {
    REGS;
    __asm__ volatile(".Ltree_14ef8:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14ef8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14f18" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14efc(void) {
    REGS;
    a4 = (uint32_t)(820); LIVE;
    __asm__ volatile(".Ltree_14f00:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f00\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15182" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f04(void) {
    REGS;
    a4 = (uint32_t)(825); LIVE;
    __asm__ volatile(".Ltree_14f08:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14f08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f0c(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14f14:\n.option push\n.option norvc\njal zero,.Ltree_14f14\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f0d0" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f18(void) {
    REGS;
    a4 = (uint32_t)(880); LIVE;
    __asm__ volatile(".Ltree_14f1c:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f1c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_152d0" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f20(void) {
    REGS;
    a4 = (uint32_t)(921); LIVE;
    __asm__ volatile(".Ltree_14f24:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_152dc" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f28(void) {
    REGS;
    a4 = (uint32_t)(850); LIVE;
    __asm__ volatile(".Ltree_14f2c:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14f2c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f30(void) {
    REGS;
    __asm__ volatile("lbu a5, 3(s0)" : "=r"(a5) : : "memory");
    a5 = a5 & 3u; LIVE;
    __asm__ volatile(".Ltree_14f36:\n.option push\n.option norvc\nbeqz a5, .Ltree_14f36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_151b0" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f3a(void) {
    REGS;
    a4 = (uint32_t)(1); LIVE;
    __asm__ volatile(".Ltree_14f3c:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14f3c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f40(void) {
    REGS;
    __asm__ volatile("mv a2, s0" : "=r"(a2) : : "memory");
    a1 = (uint32_t)(7); LIVE;
    __asm__ volatile(".Ltree_14f44:\nc.j .Ltree_14f44\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_feature_handler_1509a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f46(void) {
    REGS;
    a4 = (uint32_t)(962); LIVE;
    __asm__ volatile(".Ltree_14f4a:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_151de" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f4e(void) {
    REGS;
    __asm__ volatile(".Ltree_14f4e:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14f4e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14f76" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f52(void) {
    REGS;
    a4 = (uint32_t)(947); LIVE;
    __asm__ volatile(".Ltree_14f56:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f56\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_151b6" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f5a(void) {
    REGS;
    a4 = (uint32_t)(950); LIVE;
    __asm__ volatile(".Ltree_14f5e:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f5e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_151d2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f62(void) {
    REGS;
    a4 = (uint32_t)(925); LIVE;
    __asm__ volatile(".Ltree_14f66:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14f66\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f6a(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14f72:\n.option push\n.option norvc\njal zero,.Ltree_14f72\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_d64a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f76(void) {
    REGS;
    a4 = (uint32_t)(978); LIVE;
    __asm__ volatile(".Ltree_14f7a:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1521c" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f7e(void) {
    REGS;
    a4 = (uint32_t)(984); LIVE;
    __asm__ volatile(".Ltree_14f82:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14f82\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15210" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f86(void) {
    REGS;
    a4 = (uint32_t)(963); LIVE;
    __asm__ volatile(".Ltree_14f8a:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14f8a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f8e(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile(".Ltree_14f90:\n.option push\n.option norvc\njal ra,.Ltree_14f90\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_c472" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5) : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14f94(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14f9c:\n.option push\n.option norvc\njal zero,.Ltree_14f9c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_c60e" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fa0(void) {
    REGS;
    a4 = (uint32_t)(1025); LIVE;
    __asm__ volatile(".Ltree_14fa4:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14fa4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1527e" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fa8(void) {
    REGS;
    __asm__ volatile(".Ltree_14fa8:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14fa8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_15002" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fac(void) {
    REGS;
    a4 = (uint32_t)(1001); LIVE;
    __asm__ volatile(".Ltree_14fb0:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14fb0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1522e" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fb4(void) {
    REGS;
    __asm__ volatile(".Ltree_14fb4:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_14fb4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_14fd4" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fb8(void) {
    REGS;
    a4 = (uint32_t)(994); LIVE;
    __asm__ volatile(".Ltree_14fbc:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14fbc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15222" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fc0(void) {
    REGS;
    a4 = (uint32_t)(995); LIVE;
    __asm__ volatile(".Ltree_14fc4:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14fc4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fc8(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14fd0:\n.option push\n.option norvc\njal zero,.Ltree_14fd0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_100d6" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fd4(void) {
    REGS;
    a4 = (uint32_t)(1021); LIVE;
    __asm__ volatile(".Ltree_14fd8:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14fd8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1526e" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fdc(void) {
    REGS;
    a4 = (uint32_t)(1022); LIVE;
    __asm__ volatile(".Ltree_14fe0:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_14fe0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_15262" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fe4(void) {
    REGS;
    a4 = (uint32_t)(1013); LIVE;
    __asm__ volatile(".Ltree_14fe8:\n.option push\n.option norvc\nbne a5, a4, .Ltree_14fe8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14fec(void) {
    REGS;
    __asm__ volatile("mv a2, s0" : "=r"(a2) : : "memory");
    a0 = (uint32_t)(0); LIVE;
    a1 = (uint32_t)(15); LIVE;
    __asm__ volatile(".Ltree_14ff2:\n.option push\n.option norvc\njal ra,.Ltree_14ff2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5) : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_14ff6(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_14ffe:\n.option push\n.option norvc\njal zero,.Ltree_14ffe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_a6d8" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_15002(void) {
    REGS;
    a4 = (uint32_t)(1267); LIVE;
    __asm__ volatile(".Ltree_15006:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_15006\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_152ae" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_1500a(void) {
    REGS;
    __asm__ volatile(".Ltree_1500a:\n.option push\n.option norvc\nbltu a4, a5, .Ltree_1500a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_tree_15032" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_1500e(void) {
    REGS;
    a4 = (uint32_t)(1250); LIVE;
    __asm__ volatile(".Ltree_15012:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_15012\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1528a" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_15016(void) {
    REGS;
    a4 = (uint32_t)(1251); LIVE;
    __asm__ volatile(".Ltree_1501a:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_1501a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_1529c" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_1501e(void) {
    REGS;
    a4 = (uint32_t)(1029); LIVE;
    __asm__ volatile(".Ltree_15022:\n.option push\n.option norvc\nbne a5, a4, .Ltree_15022\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_15026(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_1502e:\n.option push\n.option norvc\njal zero,.Ltree_1502e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_d1b2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_15032(void) {
    REGS;
    a4 = (uint32_t)(1657); LIVE;
    __asm__ volatile(".Ltree_15036:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_15036\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_152ba" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_1503a(void) {
    REGS;
    a4 = (uint32_t)(2047); LIVE;
    __asm__ volatile(".Ltree_1503e:\n.option push\n.option norvc\nbeq a5, a4, .Ltree_1503e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_handler_152f4" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_15042(void) {
    REGS;
    a4 = (uint32_t)(1656); LIVE;
    __asm__ volatile(".Ltree_15046:\n.option push\n.option norvc\nbne a5, a4, .Ltree_15046\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_feature_return_14da2" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_1504a(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile(".Ltree_1504c:\n.option push\n.option norvc\njal ra,.Ltree_1504c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_ff56" : "+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5) : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_feature_tree_15050(void) {
    REGS;
    __asm__ volatile("mv a0, s0" : "=r"(a0) : : "memory");
    __asm__ volatile("lw s0, 8(sp)" : : : "memory");
    __asm__ volatile("lw ra, 12(sp)" : : : "memory");
    __asm__ volatile("addi sp, sp, 16" : : : "memory");
    __asm__ volatile(".Ltree_15058:\n.option push\n.option norvc\njal zero,.Ltree_15058\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_ffa4" :  : "r"(a0),"r"(a1),"r"(a2),"r"(a3),"r"(a4),"r"(a5) : "memory");
    __builtin_unreachable();
}
