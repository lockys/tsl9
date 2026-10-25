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

/* Eighteen complete runtime service functions:706B/236i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xA00C..0xA016. */
REGION void tsl9_settings_state_inputs_provider_a00c(void)
{
    REGS;
    a4 = UINT32_C(0x00000018); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ad)); LIVE;
    PORT(".Lruntime_service_links_edge_a012:\n.option push\n.option norvc\nbleu a0,a4,.Lruntime_service_links_edge_a012\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_service_links_block_a01a\n");
    __builtin_unreachable();
}

/* Original0xA016..0xA018. */
REGION void tsl9_runtime_service_links_block_a016(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_a016:\n.option push\n.option rvc\nc.bnez a5,.Lruntime_service_links_edge_a016\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_a022\n");
    __builtin_unreachable();
}

/* Original0xA018..0xA01A. */
REGION void tsl9_runtime_service_links_block_a018(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_a018:\n.option push\n.option rvc\nc.j .Lruntime_service_links_edge_a018\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_builder_provider_9fc8\n");
    __builtin_unreachable();
}

/* Original0xA01A..0xA01C. */
REGION void tsl9_runtime_service_links_block_a01a(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_a01a:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_service_links_edge_a01a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_a022\n");
    __builtin_unreachable();
}

/* Original0xA01C..0xA022. */
REGION void tsl9_runtime_service_links_block_a01c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ad)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xA022..0xA024. */
REGION void tsl9_runtime_service_links_block_a022(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB520..0xB530. */
REGION void tsl9_settings_state_inputs_provider_b520(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000060)); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lruntime_service_links_edge_b52e:\n.option push\n.option rvc\nc.beqz a5,.Lruntime_service_links_edge_b52e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_b570\n");
    __builtin_unreachable();
}

/* Original0xB530..0xB540. */
REGION void tsl9_runtime_service_links_block_b530(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lruntime_service_links_edge_b53c:\n.option push\n.option norvc\nbltu a4,a5,.Lruntime_service_links_edge_b53c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_service_links_block_b570\n");
    __builtin_unreachable();
}

/* Original0xB540..0xB548. */
REGION void tsl9_runtime_service_links_block_b540(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lruntime_service_links_edge_b544:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_b544\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_f65c\n");
    __builtin_unreachable();
}

/* Original0xB548..0xB54A. */
REGION void tsl9_runtime_service_links_block_b548(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_b548:\n.option push\n.option rvc\nc.bnez a0,.Lruntime_service_links_edge_b548\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_b56a\n");
    __builtin_unreachable();
}

/* Original0xB54A..0xB54E. */
REGION void tsl9_runtime_service_links_block_b54a(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_b54a:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_b54a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d3e8\n");
    __builtin_unreachable();
}

/* Original0xB54E..0xB550. */
REGION void tsl9_runtime_service_links_block_b54e(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_b54e:\n.option push\n.option rvc\nc.bnez a0,.Lruntime_service_links_edge_b54e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_b56a\n");
    __builtin_unreachable();
}

/* Original0xB550..0xB56A. */
REGION void tsl9_runtime_service_links_block_b550(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00001000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0xfffffbb8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_literal_b55c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_settings_state_inputs_entry_b29a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lruntime_service_links_literal_b55c\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lruntime_service_links_edge_b566:\n.option push\n.option norvc\njal zero,.Lruntime_service_links_edge_b566\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xB56A..0xB570. */
REGION void tsl9_runtime_service_links_block_b56a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB570..0xB572. */
REGION void tsl9_runtime_service_links_block_b570(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB5C6..0xB5E0. */
REGION void tsl9_runtime_service_links_entry_b5c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffff926); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)) = (uint8_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBCE0..0xBCEC. */
REGION void tsl9_settings_state_inputs_provider_bce0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000232)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCC54..0xCC60. */
REGION void tsl9_settings_state_inputs_provider_cc54(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000002ce)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCC82..0xCC8C. */
REGION void tsl9_record_dispatch_provider_cc82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000002a3)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xE0BA..0xE0C4. */
REGION void tsl9_runtime_service_links_entry_e0ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lruntime_service_links_edge_e0c0:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_bd00\n");
    __builtin_unreachable();
}

/* Original0xE0C4..0xE0C8. */
REGION void tsl9_runtime_service_links_block_e0c4(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0c4:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_runtime_service_links_entry_fa3c\n");
    __builtin_unreachable();
}

/* Original0xE0C8..0xE0CE. */
REGION void tsl9_runtime_service_links_block_e0c8(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e0ca:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fd6a\n");
    __builtin_unreachable();
}

/* Original0xE0CE..0xE0D2. */
REGION void tsl9_runtime_service_links_block_e0ce(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0ce:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_runtime_service_links_entry_fa4a\n");
    __builtin_unreachable();
}

/* Original0xE0D2..0xE0D6. */
REGION void tsl9_runtime_service_links_block_e0d2(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0d2:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_runtime_service_links_entry_fafe\n");
    __builtin_unreachable();
}

/* Original0xE0D6..0xE0DA. */
REGION void tsl9_runtime_service_links_block_e0d6(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0d6:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0d6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_dependencies_provider_f838\n");
    __builtin_unreachable();
}

/* Original0xE0DA..0xE0DE. */
REGION void tsl9_runtime_service_links_block_e0da(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0da:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_runtime_service_links_entry_b5c6\n");
    __builtin_unreachable();
}

/* Original0xE0DE..0xE0E2. */
REGION void tsl9_runtime_service_links_block_e0de(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0de:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_services_provider_b242\n");
    __builtin_unreachable();
}

/* Original0xE0E2..0xE0E6. */
REGION void tsl9_runtime_service_links_block_e0e2(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0e2:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xE0E6..0xE0E8. */
REGION void tsl9_runtime_service_links_block_e0e6(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0e6:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e0e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e0f0\n");
    __builtin_unreachable();
}

/* Original0xE0E8..0xE0F0. */
REGION void tsl9_runtime_service_links_block_e0e8(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e0ec:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0xE0F0..0xE0F4. */
REGION void tsl9_runtime_service_links_block_e0f0(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0f0:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_a968\n");
    __builtin_unreachable();
}

/* Original0xE0F4..0xE0F6. */
REGION void tsl9_runtime_service_links_block_e0f4(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0f4:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e0f4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e0fa\n");
    __builtin_unreachable();
}

/* Original0xE0F6..0xE0FA. */
REGION void tsl9_runtime_service_links_block_e0f6(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0f6:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0f6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_a6aa\n");
    __builtin_unreachable();
}

/* Original0xE0FA..0xE0FE. */
REGION void tsl9_runtime_service_links_block_e0fa(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0fa:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e0fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d314\n");
    __builtin_unreachable();
}

/* Original0xE0FE..0xE100. */
REGION void tsl9_runtime_service_links_block_e0fe(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e0fe:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e0fe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e106\n");
    __builtin_unreachable();
}

/* Original0xE100..0xE106. */
REGION void tsl9_runtime_service_links_block_e100(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e102:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e102\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d2ee\n");
    __builtin_unreachable();
}

/* Original0xE106..0xE10A. */
REGION void tsl9_runtime_service_links_block_e106(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e106:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e106\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_181c4\n");
    __builtin_unreachable();
}

/* Original0xE10A..0xE10C. */
REGION void tsl9_runtime_service_links_block_e10a(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e10a:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e10a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e116\n");
    __builtin_unreachable();
}

/* Original0xE10C..0xE116. */
REGION void tsl9_runtime_service_links_block_e10c(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000003); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e112:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e112\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1811a\n");
    __builtin_unreachable();
}

/* Original0xE116..0xE11A. */
REGION void tsl9_runtime_service_links_block_e116(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e116:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e116\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_c35a\n");
    __builtin_unreachable();
}

/* Original0xE11A..0xE11C. */
REGION void tsl9_runtime_service_links_block_e11a(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e11a:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e11a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e122\n");
    __builtin_unreachable();
}

/* Original0xE11C..0xE122. */
REGION void tsl9_runtime_service_links_block_e11c(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e11e:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e11e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0xE122..0xE126. */
REGION void tsl9_runtime_service_links_block_e122(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e122:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e122\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_cd44\n");
    __builtin_unreachable();
}

/* Original0xE126..0xE128. */
REGION void tsl9_runtime_service_links_block_e126(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e126:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e126\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e130\n");
    __builtin_unreachable();
}

/* Original0xE128..0xE130. */
REGION void tsl9_runtime_service_links_block_e128(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e12c:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e12c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0xE130..0xE134. */
REGION void tsl9_runtime_service_links_block_e130(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e130:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e130\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f7d2\n");
    __builtin_unreachable();
}

/* Original0xE134..0xE136. */
REGION void tsl9_runtime_service_links_block_e134(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e134:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e134\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e13e\n");
    __builtin_unreachable();
}

/* Original0xE136..0xE13E. */
REGION void tsl9_runtime_service_links_block_e136(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e13a:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e13a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f796\n");
    __builtin_unreachable();
}

/* Original0xE13E..0xE142. */
REGION void tsl9_runtime_service_links_block_e13e(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e13e:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e13e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f6b0\n");
    __builtin_unreachable();
}

/* Original0xE142..0xE144. */
REGION void tsl9_runtime_service_links_block_e142(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e142:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e142\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e14c\n");
    __builtin_unreachable();
}

/* Original0xE144..0xE14C. */
REGION void tsl9_runtime_service_links_block_e144(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e148:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e148\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0xE14C..0xE150. */
REGION void tsl9_runtime_service_links_block_e14c(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e14c:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e14c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f714\n");
    __builtin_unreachable();
}

/* Original0xE150..0xE152. */
REGION void tsl9_runtime_service_links_block_e150(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e150:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e150\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e15a\n");
    __builtin_unreachable();
}

/* Original0xE152..0xE15A. */
REGION void tsl9_runtime_service_links_block_e152(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e156:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e156\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ec\n");
    __builtin_unreachable();
}

/* Original0xE15A..0xE15E. */
REGION void tsl9_runtime_service_links_block_e15a(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e15a:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e15a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f78c\n");
    __builtin_unreachable();
}

/* Original0xE15E..0xE160. */
REGION void tsl9_runtime_service_links_block_e15e(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e15e:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e15e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e168\n");
    __builtin_unreachable();
}

/* Original0xE160..0xE168. */
REGION void tsl9_runtime_service_links_block_e160(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e164:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e164\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f750\n");
    __builtin_unreachable();
}

/* Original0xE168..0xE16C. */
REGION void tsl9_runtime_service_links_block_e168(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e168:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e168\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f6e2\n");
    __builtin_unreachable();
}

/* Original0xE16C..0xE16E. */
REGION void tsl9_runtime_service_links_block_e16c(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e16c:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e16c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e176\n");
    __builtin_unreachable();
}

/* Original0xE16E..0xE176. */
REGION void tsl9_runtime_service_links_block_e16e(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e172:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e172\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f6ba\n");
    __builtin_unreachable();
}

/* Original0xE176..0xE17A. */
REGION void tsl9_runtime_service_links_block_e176(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e176:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e176\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_f746\n");
    __builtin_unreachable();
}

/* Original0xE17A..0xE17C. */
REGION void tsl9_runtime_service_links_block_e17a(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e17a:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e17a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e184\n");
    __builtin_unreachable();
}

/* Original0xE17C..0xE184. */
REGION void tsl9_runtime_service_links_block_e17c(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e180:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e180\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f71e\n");
    __builtin_unreachable();
}

/* Original0xE184..0xE188. */
REGION void tsl9_runtime_service_links_block_e184(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e184:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e184\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc82\n");
    __builtin_unreachable();
}

/* Original0xE188..0xE18A. */
REGION void tsl9_runtime_service_links_block_e188(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e188:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e188\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e190\n");
    __builtin_unreachable();
}

/* Original0xE18A..0xE190. */
REGION void tsl9_runtime_service_links_block_e18a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e18c:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e18c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc78\n");
    __builtin_unreachable();
}

/* Original0xE190..0xE194. */
REGION void tsl9_runtime_service_links_block_e190(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e190:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e190\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f67e\n");
    __builtin_unreachable();
}

/* Original0xE194..0xE196. */
REGION void tsl9_runtime_service_links_block_e194(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e194:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e194\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e19c\n");
    __builtin_unreachable();
}

/* Original0xE196..0xE19C. */
REGION void tsl9_runtime_service_links_block_e196(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_e198:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e198\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f672\n");
    __builtin_unreachable();
}

/* Original0xE19C..0xE1A6. */
REGION void tsl9_runtime_service_links_block_e19c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lruntime_service_links_edge_e1a2:\n.option push\n.option norvc\njal zero,.Lruntime_service_links_edge_e1a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xE1A6..0xE1B6. */
REGION void tsl9_record_dispatch_provider_e1a6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lruntime_service_links_edge_e1b2:\n.option push\n.option norvc\nbltu a4,a5,.Lruntime_service_links_edge_e1b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_service_links_block_e20a\n");
    __builtin_unreachable();
}

/* Original0xE1B6..0xE1C0. */
REGION void tsl9_runtime_service_links_block_e1b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".Lruntime_service_links_edge_e1bc:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e1bc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xE1C0..0xE1C6. */
REGION void tsl9_runtime_service_links_block_e1c0(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lruntime_service_links_edge_e1c2:\n.option push\n.option norvc\nbne a0,a5,.Lruntime_service_links_edge_e1c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_service_links_block_e1fe\n");
    __builtin_unreachable();
}

/* Original0xE1C6..0xE1CA. */
REGION void tsl9_runtime_service_links_block_e1c6(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e1c6:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e1c6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xE1CA..0xE1CC. */
REGION void tsl9_runtime_service_links_block_e1ca(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e1ca:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_e1ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_e1fe\n");
    __builtin_unreachable();
}

/* Original0xE1CC..0xE1D0. */
REGION void tsl9_runtime_service_links_block_e1cc(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e1cc:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e1cc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xE1D0..0xE1E4. */
REGION void tsl9_runtime_service_links_block_e1d0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000110); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x000007cf); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a5 = a0 - a5; LIVE;
    PORT(".Lruntime_service_links_edge_e1e0:\n.option push\n.option norvc\nbleu a5,a4,.Lruntime_service_links_edge_e1e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_service_links_block_e1f2\n");
    __builtin_unreachable();
}

/* Original0xE1E4..0xE1EE. */
REGION void tsl9_runtime_service_links_block_e1e4(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x0000000f); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lruntime_service_links_edge_e1ea:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e1ea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_external_d05c\n");
    __builtin_unreachable();
}

/* Original0xE1EE..0xE1F2. */
REGION void tsl9_runtime_service_links_block_e1ee(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_e1ee:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_e1ee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_9fc8\n");
    __builtin_unreachable();
}

/* Original0xE1F2..0xE1FE. */
REGION void tsl9_runtime_service_links_block_e1f2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s0, 272(gp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xE1FE..0xE20A. */
REGION void tsl9_runtime_service_links_block_e1fe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lruntime_service_links_edge_e206:\n.option push\n.option norvc\njal zero,.Lruntime_service_links_edge_e206\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_9508\n");
    __builtin_unreachable();
}

/* Original0xE20A..0xE20C. */
REGION void tsl9_runtime_service_links_block_e20a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xE20C..0xE220. */
REGION void tsl9_settings_state_inputs_provider_e20c(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000003e8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_literal_e214:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_runtime_service_links_entry_e0ba\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lruntime_service_links_literal_e214\n.option pop\n");
    PORT(".Lruntime_service_links_edge_e21c:\n.option push\n.option norvc\njal zero,.Lruntime_service_links_edge_e21c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xF666..0xF672. */
REGION void tsl9_settings_state_inputs_provider_f666(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff931)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF67E..0xF688. */
REGION void tsl9_record_dispatch_provider_f67e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff91a)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF78C..0xF796. */
REGION void tsl9_record_dispatch_provider_f78c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff810)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF7D2..0xF7DC. */
REGION void tsl9_record_dispatch_provider_f7d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffc\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000007c9)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF9EC..0xF9FA. */
REGION void tsl9_settings_state_inputs_provider_f9ec(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0x00000007); LIVE;
    PORT(".Lruntime_service_links_edge_f9f8:\n.option push\n.option rvc\nc.beqz a4,.Lruntime_service_links_edge_f9f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_fa22\n");
    __builtin_unreachable();
}

/* Original0xF9FA..0xFA18. */
REGION void tsl9_runtime_service_links_block_f9fa(void)
{
    REGS;
    PORT(".Lruntime_service_links_literal_f9fa:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_runtime_service_threshold_bytes_1ab58\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lruntime_service_links_literal_f9fa\n.option pop\n");
    a4 = a4 + a3; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsltu a0, a0, a5\n.option pop\n");
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000115)); LIVE;
    PORT(".Lruntime_service_links_edge_fa14:\n.option push\n.option norvc\nbeq a5,a0,.Lruntime_service_links_edge_fa14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_runtime_service_links_block_fa22\n");
    __builtin_unreachable();
}

/* Original0xFA18..0xFA22. */
REGION void tsl9_runtime_service_links_block_fa18(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000115)) = (uint8_t)a0; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_edge_fa1e:\n.option push\n.option norvc\njal zero,.Lruntime_service_links_edge_fa1e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xFA22..0xFA24. */
REGION void tsl9_runtime_service_links_block_fa22(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFA3C..0xFA4A. */
REGION void tsl9_runtime_service_links_entry_fa3c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000114); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFA4A..0xFA50. */
REGION void tsl9_runtime_service_links_entry_fa4a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000116)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFAFE..0xFB0C. */
REGION void tsl9_runtime_service_links_entry_fafe(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x0000011c); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17BC4..0x17BC6. */
REGION void tsl9_settings_state_inputs_provider_17bc4(void)
{
    REGS;
    PORT(".Lruntime_service_links_edge_17bc4:\n.option push\n.option rvc\nc.beqz a0,.Lruntime_service_links_edge_17bc4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_runtime_service_links_block_17be2\n");
    __builtin_unreachable();
}

/* Original0x17BC6..0x17BD6. */
REGION void tsl9_runtime_service_links_block_17bc6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".Lruntime_service_links_literal_17bc8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_queue_entry_178f8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lruntime_service_links_literal_17bc8\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lruntime_service_links_edge_17bd2:\n.option push\n.option norvc\njal ra,.Lruntime_service_links_edge_17bd2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0x17BD6..0x17BE2. */
REGION void tsl9_runtime_service_links_block_17bd6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lruntime_service_links_edge_17bde:\n.option push\n.option norvc\njal zero,.Lruntime_service_links_edge_17bde\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_control_entry_1798a\n");
    __builtin_unreachable();
}

/* Original0x17BE2..0x17BF6. */
REGION void tsl9_runtime_service_links_block_17be2(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000005dc); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lruntime_service_links_literal_17bea:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_queue_entry_178f8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lruntime_service_links_literal_17bea\n.option pop\n");
    PORT(".Lruntime_service_links_edge_17bf2:\n.option push\n.option norvc\njal zero,.Lruntime_service_links_edge_17bf2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
TABLE_DATA(".rodata.tsl9_runtime_service_threshold_bytes_1ab58") const uint8_t tsl9_runtime_service_threshold_bytes_1ab58[8] = {0xff, 0x33, 0x4c, 0x66, 0x7f, 0x99, 0xb2, 0xcc};
