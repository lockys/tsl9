#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; no host ROM or radio model.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

/* Ten complete state/control functions:1266B/452i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x960E..0x9616. */
REGION void tsl9_record_dispatch_provider_960e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_controls_edge_9614:\n.option push\n.option rvc\nc.jal .Lstate_controls_edge_9614\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_allocate_9410\n");
    __builtin_unreachable();
}

/* Original0x9616..0x9620. */
REGION void tsl9_state_controls_block_9616(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8b6)) = (uint32_t)a0; LIVE;
    PORT(".Lstate_controls_edge_961e:\n.option push\n.option rvc\nc.beqz a0,.Lstate_controls_edge_961e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_9652\n");
    __builtin_unreachable();
}

/* Original0x9620..0x9652. */
REGION void tsl9_state_controls_block_9620(void)
{
    REGS;
    a5 = UINT32_C(0x0000048d); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x00000082); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x000005b9); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000096); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_controls_edge_9650:\n.option push\n.option rvc\nc.j .Lstate_controls_edge_9650\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_arm_93aa\n");
    __builtin_unreachable();
}

/* Original0x9652..0x9658. */
REGION void tsl9_state_controls_block_9652(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAB02..0xAB08. */
REGION void tsl9_state_controls_provider_ab02(void)
{
    REGS;
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lstate_controls_edge_ab04:\n.option push\n.option norvc\njal zero,.Lstate_controls_edge_ab04\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0xAC0A..0xAC10. */
REGION void tsl9_record_dispatch_provider_ac0a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lstate_controls_edge_ac0e:\n.option push\n.option rvc\nc.bnez a5,.Lstate_controls_edge_ac0e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_ac18\n");
    __builtin_unreachable();
}

/* Original0xAC10..0xAC12. */
REGION void tsl9_state_controls_block_ac10(void)
{
    REGS;
    PORT(".Lstate_controls_edge_ac10:\n.option push\n.option rvc\nc.bnez a0,.Lstate_controls_edge_ac10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_ac58\n");
    __builtin_unreachable();
}

/* Original0xAC12..0xAC14. */
REGION void tsl9_state_controls_block_ac12(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xAC14..0xAC18. */
REGION void tsl9_state_controls_block_ac14(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_controls_edge_ac16:\n.option push\n.option rvc\nc.j .Lstate_controls_edge_ac16\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_controls_block_ac6a\n");
    __builtin_unreachable();
}

/* Original0xAC18..0xAC24. */
REGION void tsl9_state_controls_block_ac18(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lstate_controls_edge_ac20:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_ac20\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xAC24..0xAC28. */
REGION void tsl9_state_controls_block_ac24(void)
{
    REGS;
    PORT(".Lstate_controls_edge_ac24:\n.option push\n.option norvc\nbeq a0,s0,.Lstate_controls_edge_ac24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_ac70\n");
    __builtin_unreachable();
}

/* Original0xAC28..0xAC2E. */
REGION void tsl9_state_controls_block_ac28(void)
{
    REGS;
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lstate_controls_edge_ac2a:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_ac2a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0xAC2E..0xAC30. */
REGION void tsl9_state_controls_block_ac2e(void)
{
    REGS;
    PORT(".Lstate_controls_edge_ac2e:\n.option push\n.option rvc\nc.beqz s0,.Lstate_controls_edge_ac2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_ac70\n");
    __builtin_unreachable();
}

/* Original0xAC30..0xAC3E. */
REGION void tsl9_state_controls_block_ac30(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000638)); LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_controls_edge_ac3c:\n.option push\n.option rvc\nc.beqz a5,.Lstate_controls_edge_ac3c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_ac70\n");
    __builtin_unreachable();
}

/* Original0xAC3E..0xAC58. */
REGION void tsl9_state_controls_block_ac3e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x0000012c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_controls_literal_ac4a:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_state_controls_provider_ab02\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_controls_literal_ac4a\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_controls_edge_ac54:\n.option push\n.option norvc\njal zero,.Lstate_controls_edge_ac54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xAC58..0xAC6A. */
REGION void tsl9_state_controls_block_ac58(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000610)); LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_controls_edge_ac68:\n.option push\n.option rvc\nc.beqz a5,.Lstate_controls_edge_ac68\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_ac14\n");
    __builtin_unreachable();
}

/* Original0xAC6A..0xAC70. */
REGION void tsl9_state_controls_block_ac6a(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_controls_edge_ac6c:\n.option push\n.option norvc\njal zero,.Lstate_controls_edge_ac6c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_external_d05c\n");
    __builtin_unreachable();
}

/* Original0xAC70..0xAC78. */
REGION void tsl9_state_controls_block_ac70(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD2EE..0xD30A. */
REGION void tsl9_record_dispatch_provider_d2ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffc6a); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint8_t)a0; LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    PORT(".Lstate_controls_edge_d306:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_d306\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xD30A..0xD314. */
REGION void tsl9_state_controls_block_d30a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_controls_edge_d310:\n.option push\n.option norvc\njal zero,.Lstate_controls_edge_d310\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xD332..0xD346. */
REGION void tsl9_feature_external_d332(void)
{
    REGS;
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc29)); LIVE;
    a0 = a0 >> UINT32_C(0x0000000e); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_controls_edge_d342:\n.option push\n.option norvc\nbeq a5,a0,.Lstate_controls_edge_d342\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_d376\n");
    __builtin_unreachable();
}

/* Original0xD346..0xD35E. */
REGION void tsl9_state_controls_block_d346(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc19)) = (uint8_t)a0; LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000066); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lstate_controls_edge_d35a:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_d35a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xD35E..0xD368. */
REGION void tsl9_state_controls_block_d35e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbfe)); LIVE;
    PORT(".Lstate_controls_edge_d366:\n.option push\n.option rvc\nc.beqz a5,.Lstate_controls_edge_d366\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_d36c\n");
    __builtin_unreachable();
}

/* Original0xD368..0xD36C. */
REGION void tsl9_state_controls_block_d368(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_controls_edge_d36a:\n.option push\n.option rvc\nc.jal .Lstate_controls_edge_d36a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_provider_d2ee\n");
    __builtin_unreachable();
}

/* Original0xD36C..0xD376. */
REGION void tsl9_state_controls_block_d36c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lstate_controls_edge_d372:\n.option push\n.option norvc\njal zero,.Lstate_controls_edge_d372\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xD376..0xD378. */
REGION void tsl9_state_controls_block_d376(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10C7A..0x10CAA. */
REGION void tsl9_state_controls_provider_10c7a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000002)) = (uint16_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)0; LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 296(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)) = (uint16_t)a1; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000012); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10CAA..0x10CAE. */
REGION void tsl9_state_controls_block_10caa(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    PORT(".Lstate_controls_edge_10cac:\n.option push\n.option rvc\nc.beqz a0,.Lstate_controls_edge_10cac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_10cd6\n");
    __builtin_unreachable();
}

/* Original0x10CAE..0x10CB8. */
REGION void tsl9_state_controls_block_10cae(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 76(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\naddi a1, sp, 2\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10CB8..0x10CCA. */
REGION void tsl9_state_controls_block_10cb8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 268(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x1fffb\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000318)); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10CCA..0x10CCC. */
REGION void tsl9_state_controls_block_10cca(void)
{
    REGS;
    PORT(".Lstate_controls_edge_10cca:\n.option push\n.option rvc\nc.beqz a0,.Lstate_controls_edge_10cca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_10cd6\n");
    __builtin_unreachable();
}

/* Original0x10CCC..0x10CD6. */
REGION void tsl9_state_controls_block_10ccc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 300(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000012); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10CD6..0x10CE0. */
REGION void tsl9_state_controls_block_10cd6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10D60..0x10D74. */
REGION void tsl9_registered_callbacks_provider_10d60(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fffb\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 624\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".Lstate_controls_edge_10d72:\n.option push\n.option rvc\nc.beqz a5,.Lstate_controls_edge_10d72\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_10d90\n");
    __builtin_unreachable();
}

/* Original0x10D74..0x10D82. */
REGION void tsl9_state_controls_block_10d74(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s1, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 380(s1)\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)); LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10D82..0x10D88. */
REGION void tsl9_state_controls_block_10d82(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 104(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10D88..0x10D90. */
REGION void tsl9_state_controls_block_10d88(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000254)) = (uint32_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x10D90..0x10D9A. */
REGION void tsl9_state_controls_block_10d90(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10E82..0x10EAC. */
REGION void tsl9_registered_callbacks_provider_10e82(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffb\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000150); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)a0; LIVE;
    a0 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\naddi a2, sp, 12\n.option pop\n");
    a3 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x000000f0); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint8_t)0; LIVE;
    PORT(".Lstate_controls_edge_10ea8:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_10ea8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_ota_external_13e98\n");
    __builtin_unreachable();
}

/* Original0x10EAC..0x10EB2. */
REGION void tsl9_state_controls_block_10eac(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10EB2..0x10ED6. */
REGION void tsl9_registered_callbacks_provider_10eb2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fffb\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 286\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    PORT(".Lstate_controls_edge_10ed2:\n.option push\n.option norvc\nbeqz a5,.Lstate_controls_edge_10ed2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_11074\n");
    __builtin_unreachable();
}

/* Original0x10ED6..0x10EF0. */
REGION void tsl9_state_controls_block_10ed6(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000058)); LIVE;
    a2 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    a2 = a2 + UINT32_C(0xffffff40); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000000ee)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10EF0..0x10EF2. */
REGION void tsl9_state_controls_block_10ef0(void)
{
    REGS;
    PORT(".Lstate_controls_edge_10ef0:\n.option push\n.option rvc\nc.bnez s1,.Lstate_controls_edge_10ef0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_10f00\n");
    __builtin_unreachable();
}

/* Original0x10EF2..0x10EFA. */
REGION void tsl9_state_controls_block_10ef2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000023)); LIVE;
    PORT(".Lstate_controls_edge_10ef8:\n.option push\n.option rvc\nc.beqz a4,.Lstate_controls_edge_10ef8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_10f00\n");
    __builtin_unreachable();
}

/* Original0x10EFA..0x10F00. */
REGION void tsl9_state_controls_block_10efa(void)
{
    REGS;
    a5 = a5 + a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x10F00..0x10F10. */
REGION void tsl9_state_controls_block_10f00(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000023)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)); LIVE;
    PORT(".Lstate_controls_edge_10f0c:\n.option push\n.option norvc\nbltu a4,a3,.Lstate_controls_edge_10f0c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_11034\n");
    __builtin_unreachable();
}

/* Original0x10F10..0x10F1E. */
REGION void tsl9_state_controls_block_10f10(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s4, gp, 92\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, s4\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 129\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10F1E..0x10F32. */
REGION void tsl9_state_controls_block_10f1e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a1, 0(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a1, a1, s1\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x00000003); LIVE;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10F32..0x10F34. */
REGION void tsl9_state_controls_block_10f32(void)
{
    REGS;
    PORT(".Lstate_controls_edge_10f32:\n.option push\n.option rvc\nc.bnez a0,.Lstate_controls_edge_10f32\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_11002\n");
    __builtin_unreachable();
}

/* Original0x10F34..0x10F3C. */
REGION void tsl9_state_controls_block_10f34(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, s1, 43\n.option pop\n");
    PORT(".Lstate_controls_edge_10f38:\n.option push\n.option norvc\nbne s1,s5,.Lstate_controls_edge_10f38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_10f1e\n");
    __builtin_unreachable();
}

/* Original0x10F3C..0x10F48. */
REGION void tsl9_state_controls_block_10f3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s4, 0\n.option pop\n");
    PORT(".option push\n.option norvc\nli s6, 43\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s7, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nli s5, 3\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10F48..0x10F62. */
REGION void tsl9_state_controls_block_10f48(void)
{
    REGS;
    PORT(".option push\n.option norvc\nmul a0, s4, s6\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 0(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nandi s1, s4, 255\n.option pop\n");
    a0 = a0 + a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 64(s7)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10F62..0x10F64. */
REGION void tsl9_state_controls_block_10f62(void)
{
    REGS;
    PORT(".Lstate_controls_edge_10f62:\n.option push\n.option rvc\nc.bnez a0,.Lstate_controls_edge_10f62\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_10f6c\n");
    __builtin_unreachable();
}

/* Original0x10F64..0x10F6A. */
REGION void tsl9_state_controls_block_10f64(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s4, s4, 1\n.option pop\n");
    PORT(".Lstate_controls_edge_10f66:\n.option push\n.option norvc\nbne s4,s5,.Lstate_controls_edge_10f66\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_10f48\n");
    __builtin_unreachable();
}

/* Original0x10F6A..0x10F6C. */
REGION void tsl9_state_controls_block_10f6a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10F6C..0x10FAC. */
REGION void tsl9_state_controls_block_10f6c(void)
{
    REGS;
    a0 = UINT32_C(0x0000002b); LIVE;
    PORT(".option push\n.option norvc\nmul s1, s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s4, 0x40\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s1\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 8(s0)\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000022)); LIVE;
    PORT(".option push\n.option norvc\nlw a5, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s1\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option norvc\nlw a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a1, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 76(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s1\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000001); LIVE;
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10FAC..0x10FC0. */
REGION void tsl9_state_controls_block_10fac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a1, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 76(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s1\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    a1 = a1 + UINT32_C(0x00000007); LIVE;
    a0 = a0 + UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10FC0..0x10FD8. */
REGION void tsl9_state_controls_block_10fc0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a1, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 76(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s1\n.option pop\n");
    a2 = UINT32_C(0x0000000a); LIVE;
    a1 = a1 + UINT32_C(0x00000025); LIVE;
    a0 = a0 + UINT32_C(0x00000021); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10FD8..0x10FDC. */
REGION void tsl9_state_controls_block_10fd8(void)
{
    REGS;
    PORT(".Lstate_controls_edge_10fd8:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_10fd8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_130d6\n");
    __builtin_unreachable();
}

/* Original0x10FDC..0x10FEC. */
REGION void tsl9_state_controls_block_10fdc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 92(s4)\n.option pop\n");
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffff2)); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10FEC..0x11002. */
REGION void tsl9_state_controls_block_10fec(void)
{
    REGS;
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul a0, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s3, 0x1fffb\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, -6\n.option pop\n");
    a5 = UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option rvc\nadd s3, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 10(s3)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11002..0x11006. */
REGION void tsl9_state_controls_block_11002(void)
{
    REGS;
    PORT(".Lstate_controls_edge_11002:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_11002\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10d60\n");
    __builtin_unreachable();
}

/* Original0x11006..0x1100C. */
REGION void tsl9_state_controls_block_11006(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_controls_edge_11008:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_11008\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_10e82\n");
    __builtin_unreachable();
}

/* Original0x1100C..0x11034. */
REGION void tsl9_state_controls_block_1100c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_controls_literal_11026:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_960e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_controls_literal_11026\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lstate_controls_edge_11030:\n.option push\n.option norvc\njal zero,.Lstate_controls_edge_11030\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x11034..0x11052. */
REGION void tsl9_state_controls_block_11034(void)
{
    REGS;
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul a0, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s3, 0x1fffb\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, s3, -78\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a1 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000025)); LIVE;
    PORT(".option push\n.option rvc\nadd s3, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a0, 2(s3)\n.option pop\n");
    PORT(".Lstate_controls_edge_1104e:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_1104e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_10c7a\n");
    __builtin_unreachable();
}

/* Original0x11052..0x1105E. */
REGION void tsl9_state_controls_block_11052(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 8(s0)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000023)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000023)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x1105E..0x11074. */
REGION void tsl9_state_controls_block_1105e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11074..0x11096. */
REGION void tsl9_state_controls_block_11074(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 12\n.option pop\n");
    PORT(".option push\n.option norvc\nmul s1, s3, s1\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffb\n.option pop\n");
    a0 = a0 + UINT32_C(0xffffff72); LIVE;
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, gp, 92\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s6, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nli s5, 129\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x11096..0x110A8. */
REGION void tsl9_state_controls_block_11096(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a0, 0(s4)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 60(s6)\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nadd a0, a0, s2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x110A8..0x110AA. */
REGION void tsl9_state_controls_block_110a8(void)
{
    REGS;
    PORT(".Lstate_controls_edge_110a8:\n.option push\n.option rvc\nc.beqz a0,.Lstate_controls_edge_110a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_110ee\n");
    __builtin_unreachable();
}

/* Original0x110AA..0x110BA. */
REGION void tsl9_state_controls_block_110aa(void)
{
    REGS;
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nmul a0, s3, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 0(s4)\n.option pop\n");
    a4 = UINT32_C(0x00000009); LIVE;
    PORT(".option push\n.option rvc\nadd s2, s2, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x110BA..0x110C2. */
REGION void tsl9_state_controls_block_110ba(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)); LIVE;
    PORT(".Lstate_controls_edge_110be:\n.option push\n.option norvc\nbltu a4,a5,.Lstate_controls_edge_110be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_1105e\n");
    __builtin_unreachable();
}

/* Original0x110C2..0x110D2. */
REGION void tsl9_state_controls_block_110c2(void)
{
    REGS;
    a3 = a5 + UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint8_t)a3; LIVE;
    PORT(".option push\n.option rvc\nadd a5, a5, s2\n.option pop\n");
    a1 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000021)); LIVE;
    PORT(".Lstate_controls_edge_110d0:\n.option push\n.option rvc\nc.beqz a1,.Lstate_controls_edge_110d0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_110ba\n");
    __builtin_unreachable();
}

/* Original0x110D2..0x110EE. */
REGION void tsl9_state_controls_block_110d2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lstate_controls_edge_110ea:\n.option push\n.option norvc\njal zero,.Lstate_controls_edge_110ea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_10c7a\n");
    __builtin_unreachable();
}

/* Original0x110EE..0x110F6. */
REGION void tsl9_state_controls_block_110ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s2, s2, 43\n.option pop\n");
    PORT(".Lstate_controls_edge_110f2:\n.option push\n.option norvc\nbne s2,s5,.Lstate_controls_edge_110f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_11096\n");
    __builtin_unreachable();
}

/* Original0x110F6..0x110F8. */
REGION void tsl9_state_controls_block_110f6(void)
{
    REGS;
    PORT(".Lstate_controls_edge_110f6:\n.option push\n.option rvc\nc.j .Lstate_controls_edge_110f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_state_controls_block_1105e\n");
    __builtin_unreachable();
}

/* Original0x167A6..0x167C2. */
REGION void tsl9_state_controls_provider_167a6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, gp, 96\n.option pop\n");
    PORT(".option push\n.option norvc\nli s2, 254\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x167C2..0x167D0. */
REGION void tsl9_state_controls_block_167c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a5, a5, s0\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lstate_controls_edge_167cc:\n.option push\n.option norvc\nbne a4,s1,.Lstate_controls_edge_167cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_167d8\n");
    __builtin_unreachable();
}

/* Original0x167D0..0x167D8. */
REGION void tsl9_state_controls_block_167d0(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    PORT(".Lstate_controls_edge_167d4:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_167d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_dependencies_provider_155d0\n");
    __builtin_unreachable();
}

/* Original0x167D8..0x167DE. */
REGION void tsl9_state_controls_block_167d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 2\n.option pop\n");
    PORT(".Lstate_controls_edge_167da:\n.option push\n.option norvc\nbne s0,s2,.Lstate_controls_edge_167da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_167c2\n");
    __builtin_unreachable();
}

/* Original0x167DE..0x167EE. */
REGION void tsl9_state_controls_block_167de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s5, 7\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s3, gp, 100\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, gp, 104\n.option pop\n");
    PORT(".option push\n.option norvc\nli s2, 36\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x167EE..0x16808. */
REGION void tsl9_state_controls_block_167ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 0(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, s5\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000001)); LIVE;
    a5 = a4 & UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".Lstate_controls_edge_16804:\n.option push\n.option norvc\nbne a5,s1,.Lstate_controls_edge_16804\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_16814\n");
    __builtin_unreachable();
}

/* Original0x16808..0x1680C. */
REGION void tsl9_state_controls_block_16808(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_controls_edge_1680a:\n.option push\n.option rvc\nc.beqz a4,.Lstate_controls_edge_1680a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_16814\n");
    __builtin_unreachable();
}

/* Original0x1680C..0x16814. */
REGION void tsl9_state_controls_block_1680c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_controls_edge_16810:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_16810\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_control_entry_1798a\n");
    __builtin_unreachable();
}

/* Original0x16814..0x1682E. */
REGION void tsl9_state_controls_block_16814(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 0(s4)\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a4, a4, s5\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000001)); LIVE;
    a5 = a4 & UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".Lstate_controls_edge_1682a:\n.option push\n.option norvc\nbne s1,a5,.Lstate_controls_edge_1682a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_1683a\n");
    __builtin_unreachable();
}

/* Original0x1682E..0x16832. */
REGION void tsl9_state_controls_block_1682e(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lstate_controls_edge_16830:\n.option push\n.option rvc\nc.beqz a4,.Lstate_controls_edge_16830\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_controls_block_1683a\n");
    __builtin_unreachable();
}

/* Original0x16832..0x1683A. */
REGION void tsl9_state_controls_block_16832(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lstate_controls_edge_16836:\n.option push\n.option norvc\njal ra,.Lstate_controls_edge_16836\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_control_entry_1798a\n");
    __builtin_unreachable();
}

/* Original0x1683A..0x16846. */
REGION void tsl9_state_controls_block_1683a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s5, s5, 7\n.option pop\n");
    PORT(".Lstate_controls_edge_16842:\n.option push\n.option norvc\nbne s0,s2,.Lstate_controls_edge_16842\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_controls_block_167ee\n");
    __builtin_unreachable();
}

/* Original0x16846..0x16858. */
REGION void tsl9_state_controls_block_16846(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
