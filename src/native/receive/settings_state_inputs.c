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

/* Fourteen complete settings/state input functions:1112B/353i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xABC4..0xABCE. */
REGION void tsl9_feature_external_abc4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000031c)); LIVE;
    PORT(".Lsettings_state_inputs_edge_abcc:\n.option push\n.option rvc\nc.bnez a5,.Lsettings_state_inputs_edge_abcc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_abf0\n");
    __builtin_unreachable();
}

/* Original0xABCE..0xABE0. */
REGION void tsl9_settings_state_inputs_block_abce(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a0 = a0 & UINT32_C(0x0000001f); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsettings_state_inputs_edge_abde:\n.option push\n.option rvc\nc.jal .Lsettings_state_inputs_edge_abde\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_provider_ab7c\n");
    __builtin_unreachable();
}

/* Original0xABE0..0xABE2. */
REGION void tsl9_settings_state_inputs_block_abe0(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_abe0:\n.option push\n.option rvc\nc.beqz a0,.Lsettings_state_inputs_edge_abe0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_abea\n");
    __builtin_unreachable();
}

/* Original0xABE2..0xABEA. */
REGION void tsl9_settings_state_inputs_block_abe2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_abe6:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_abe6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xABEA..0xABF0. */
REGION void tsl9_settings_state_inputs_block_abea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xABF0..0xABF2. */
REGION void tsl9_settings_state_inputs_block_abf0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB14A..0xB150. */
REGION void tsl9_feature_external_b14a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c5)); LIVE;
    PORT(".Lsettings_state_inputs_edge_b14e:\n.option push\n.option rvc\nc.beqz a5,.Lsettings_state_inputs_edge_b14e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_b174\n");
    __builtin_unreachable();
}

/* Original0xB150..0xB174. */
REGION void tsl9_settings_state_inputs_block_b150(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c5)) = (uint8_t)0; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0xffffff87); LIVE;
    a5 = a5 | UINT32_C(0x00000048); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_b170:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b170\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xB174..0xB176. */
REGION void tsl9_settings_state_inputs_block_b174(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB176..0xB182. */
REGION void tsl9_record_dispatch_provider_b176(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b17e:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b17e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xB182..0xB188. */
REGION void tsl9_settings_state_inputs_block_b182(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsettings_state_inputs_edge_b184:\n.option push\n.option norvc\nbne a0,a5,.Lsettings_state_inputs_edge_b184\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b1a8\n");
    __builtin_unreachable();
}

/* Original0xB188..0xB192. */
REGION void tsl9_settings_state_inputs_block_b188(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 196(gp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 197(gp)\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b190:\n.option push\n.option rvc\nc.bnez s0,.Lsettings_state_inputs_edge_b190\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_b196\n");
    __builtin_unreachable();
}

/* Original0xB192..0xB196. */
REGION void tsl9_settings_state_inputs_block_b192(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_b192:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b192\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_f666\n");
    __builtin_unreachable();
}

/* Original0xB196..0xB19C. */
REGION void tsl9_settings_state_inputs_block_b196(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b198:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b198\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xB19C..0xB1A8. */
REGION void tsl9_settings_state_inputs_block_b19c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b1a4:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b1a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xB1A8..0xB1AE. */
REGION void tsl9_settings_state_inputs_block_b1a8(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsettings_state_inputs_edge_b1aa:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b1aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_9508\n");
    __builtin_unreachable();
}

/* Original0xB1AE..0xB1B0. */
REGION void tsl9_settings_state_inputs_block_b1ae(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_b1ae:\n.option push\n.option rvc\nc.j .Lsettings_state_inputs_edge_b1ae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_settings_state_inputs_block_b19c\n");
    __builtin_unreachable();
}

/* Original0xB1B6..0xB1C4. */
REGION void tsl9_feature_external_b1b6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c6)); LIVE;
    a4 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x18\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b1c0:\n.option push\n.option norvc\nbgez a4,.Lsettings_state_inputs_edge_b1c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b21e\n");
    __builtin_unreachable();
}

/* Original0xB1C4..0xB1D8. */
REGION void tsl9_settings_state_inputs_block_b1c4(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c6)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsettings_state_inputs_edge_b1d4:\n.option push\n.option norvc\nbleu a5,a4,.Lsettings_state_inputs_edge_b1d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b200\n");
    __builtin_unreachable();
}

/* Original0xB1D8..0xB1DE. */
REGION void tsl9_settings_state_inputs_block_b1d8(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lsettings_state_inputs_edge_b1da:\n.option push\n.option norvc\nbeq a5,a4,.Lsettings_state_inputs_edge_b1da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b212\n");
    __builtin_unreachable();
}

/* Original0xB1DE..0xB1F0. */
REGION void tsl9_settings_state_inputs_block_b1de(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)); LIVE;
    a1 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000010); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_b1ec:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b1ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_checksum_ed00\n");
    __builtin_unreachable();
}

/* Original0xB1F0..0xB200. */
REGION void tsl9_settings_state_inputs_block_b1f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a0, 10(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b1fc:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b1fc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xB200..0xB20C. */
REGION void tsl9_settings_state_inputs_block_b200(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x00000007); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a4 = a4 & UINT32_C(0xffffffe3); LIVE;
    a5 = a5 | a4; LIVE;
    __builtin_unreachable();
}

/* Original0xB20C..0xB212. */
REGION void tsl9_settings_state_inputs_block_b20c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_b210:\n.option push\n.option rvc\nc.j .Lsettings_state_inputs_edge_b210\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_settings_state_inputs_block_b1de\n");
    __builtin_unreachable();
}

/* Original0xB212..0xB21E. */
REGION void tsl9_settings_state_inputs_block_b212(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0xffffffe3); LIVE;
    a5 = a5 | UINT32_C(0x00000018); LIVE;
    PORT(".Lsettings_state_inputs_edge_b21c:\n.option push\n.option rvc\nc.j .Lsettings_state_inputs_edge_b21c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_settings_state_inputs_block_b20c\n");
    __builtin_unreachable();
}

/* Original0xB21E..0xB220. */
REGION void tsl9_settings_state_inputs_block_b21e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB220..0xB242. */
REGION void tsl9_record_dispatch_provider_b220(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x000000c4); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000002)); LIVE;
    a3 = UINT32_C(0x00000003); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nrem a5, a5, a3\n.option pop\n");
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000002)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_b23e:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b23e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0xB242..0xB254. */
REGION void tsl9_main_services_provider_b242(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000c4); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB254..0xB264. */
REGION void tsl9_settings_state_inputs_entry_b254(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000060)); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lsettings_state_inputs_edge_b262:\n.option push\n.option rvc\nc.beqz a5,.Lsettings_state_inputs_edge_b262\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_b298\n");
    __builtin_unreachable();
}

/* Original0xB264..0xB270. */
REGION void tsl9_settings_state_inputs_block_b264(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffc88); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lsettings_state_inputs_edge_b26e:\n.option push\n.option rvc\nc.beqz a5,.Lsettings_state_inputs_edge_b26e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_b298\n");
    __builtin_unreachable();
}

/* Original0xB270..0xB288. */
REGION void tsl9_settings_state_inputs_block_b270(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".Lsettings_state_inputs_literal_b272:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_settings_state_inputs_entry_b254\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsettings_state_inputs_literal_b272\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc74)) = (uint32_t)0; LIVE;
    PORT(".Lsettings_state_inputs_edge_b284:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b284\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xB288..0xB298. */
REGION void tsl9_settings_state_inputs_block_b288(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".Lsettings_state_inputs_literal_b28a:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_settings_state_inputs_entry_b29a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsettings_state_inputs_literal_b28a\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b294:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b294\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xB298..0xB29A. */
REGION void tsl9_settings_state_inputs_block_b298(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB29A..0xB2A2. */
REGION void tsl9_settings_state_inputs_entry_b29a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b29e:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b29e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_f65c\n");
    __builtin_unreachable();
}

/* Original0xB2A2..0xB2A4. */
REGION void tsl9_settings_state_inputs_block_b2a2(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_b2a2:\n.option push\n.option rvc\nc.bnez a0,.Lsettings_state_inputs_edge_b2a2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_b2f8\n");
    __builtin_unreachable();
}

/* Original0xB2A4..0xB2A8. */
REGION void tsl9_settings_state_inputs_block_b2a4(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_b2a4:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b2a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d3e8\n");
    __builtin_unreachable();
}

/* Original0xB2A8..0xB2AA. */
REGION void tsl9_settings_state_inputs_block_b2a8(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_b2a8:\n.option push\n.option rvc\nc.bnez a0,.Lsettings_state_inputs_edge_b2a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_b2f8\n");
    __builtin_unreachable();
}

/* Original0xB2AA..0xB2D8. */
REGION void tsl9_settings_state_inputs_block_b2aa(void)
{
    REGS;
    a5 = UINT32_C(0x0a050000); LIVE;
    a5 = a5 + UINT32_C(0x00000100); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)) = (uint32_t)a5; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi a4, sp, 32\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000060)); LIVE;
    a5 = a5 >> UINT32_C(0x00000006); LIVE;
    a5 = a5 + a4; LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffffc)); LIVE;
    a5 = UINT32_C(0x0000f000); LIVE;
    a5 = a5 + UINT32_C(0xfffffa60); LIVE;
    a2 = a2 * a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a2; LIVE;
    PORT(".Lsettings_state_inputs_edge_b2d4:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_b2d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xB2D8..0xB2F8. */
REGION void tsl9_settings_state_inputs_block_b2d8(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a0 = a0 + a2; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc10)) = (uint32_t)a0; LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsettings_state_inputs_literal_b2ea:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_settings_state_inputs_entry_b254\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lsettings_state_inputs_literal_b2ea\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_b2f4:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b2f4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xB2F8..0xB2FE. */
REGION void tsl9_settings_state_inputs_block_b2f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB2FE..0xB316. */
REGION void tsl9_feature_external_b2fe(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c7)); LIVE;
    a3 = a5 + UINT32_C(0xfffffffc); LIVE;
    a3 = (uint32_t)(a3 == UINT32_C(0)); LIVE;
    a4 = a4 & UINT32_C(0x00000007); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000160)) = (uint8_t)a3; LIVE;
    PORT(".Lsettings_state_inputs_edge_b314:\n.option push\n.option rvc\nc.bnez a4,.Lsettings_state_inputs_edge_b314\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_b322\n");
    __builtin_unreachable();
}

/* Original0xB316..0xB31C. */
REGION void tsl9_settings_state_inputs_block_b316(void)
{
    REGS;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsettings_state_inputs_edge_b318:\n.option push\n.option norvc\nbne a5,a4,.Lsettings_state_inputs_edge_b318\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b340\n");
    __builtin_unreachable();
}

/* Original0xB31C..0xB322. */
REGION void tsl9_settings_state_inputs_block_b31c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c7)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB322..0xB328. */
REGION void tsl9_settings_state_inputs_block_b322(void)
{
    REGS;
    a3 = UINT32_C(0x00000005); LIVE;
    PORT(".Lsettings_state_inputs_edge_b324:\n.option push\n.option norvc\nbne a4,a3,.Lsettings_state_inputs_edge_b324\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b336\n");
    __builtin_unreachable();
}

/* Original0xB328..0xB32E. */
REGION void tsl9_settings_state_inputs_block_b328(void)
{
    REGS;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsettings_state_inputs_edge_b32a:\n.option push\n.option norvc\nbeq a5,a4,.Lsettings_state_inputs_edge_b32a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b370\n");
    __builtin_unreachable();
}

/* Original0xB32E..0xB336. */
REGION void tsl9_settings_state_inputs_block_b32e(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c7)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB336..0xB33C. */
REGION void tsl9_settings_state_inputs_block_b336(void)
{
    REGS;
    a3 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsettings_state_inputs_edge_b338:\n.option push\n.option norvc\nbne a4,a3,.Lsettings_state_inputs_edge_b338\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b370\n");
    __builtin_unreachable();
}

/* Original0xB33C..0xB340. */
REGION void tsl9_settings_state_inputs_block_b33c(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_b33c:\n.option push\n.option norvc\nbne a5,a4,.Lsettings_state_inputs_edge_b33c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b370\n");
    __builtin_unreachable();
}

/* Original0xB340..0xB364. */
REGION void tsl9_settings_state_inputs_block_b340(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    a4 = a4 >> UINT32_C(0x00000006); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a4 = a4 | a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x0000000a); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb9e)); LIVE;
    PORT(".Lsettings_state_inputs_edge_b360:\n.option push\n.option norvc\nbeq a4,a5,.Lsettings_state_inputs_edge_b360\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b370\n");
    __builtin_unreachable();
}

/* Original0xB364..0xB370. */
REGION void tsl9_settings_state_inputs_block_b364(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb92)) = (uint16_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_b36c:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b36c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xB370..0xB372. */
REGION void tsl9_settings_state_inputs_block_b370(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB372..0xB382. */
REGION void tsl9_feature_external_b372(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb7e)); LIVE;
    PORT(".Lsettings_state_inputs_edge_b37e:\n.option push\n.option norvc\nbeq a4,a5,.Lsettings_state_inputs_edge_b37e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_b38e\n");
    __builtin_unreachable();
}

/* Original0xB382..0xB38E. */
REGION void tsl9_settings_state_inputs_block_b382(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb72)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_b38a:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_b38a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xB38E..0xB390. */
REGION void tsl9_settings_state_inputs_block_b38e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCF96..0xCFB0. */
REGION void tsl9_feature_external_cf96(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffa2)); LIVE;
    a0 = a0 >> UINT32_C(0x00000005); LIVE;
    PORT(".Lsettings_state_inputs_edge_cfac:\n.option push\n.option norvc\nbeq a5,a0,.Lsettings_state_inputs_edge_cfac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_cff4\n");
    __builtin_unreachable();
}

/* Original0xCFB0..0xCFC8. */
REGION void tsl9_settings_state_inputs_block_cfb0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff94)) = (uint8_t)a0; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e4)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lsettings_state_inputs_edge_cfc4:\n.option push\n.option norvc\nbltu a4,a5,.Lsettings_state_inputs_edge_cfc4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_d030\n");
    __builtin_unreachable();
}

/* Original0xCFC8..0xCFD4. */
REGION void tsl9_settings_state_inputs_block_cfc8(void)
{
    REGS;
    a5 = a0 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsettings_state_inputs_edge_cfd0:\n.option push\n.option norvc\nbltu a4,a5,.Lsettings_state_inputs_edge_cfd0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_cfe0\n");
    __builtin_unreachable();
}

/* Original0xCFD4..0xCFE0. */
REGION void tsl9_settings_state_inputs_block_cfd4(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 + UINT32_C(0x0000003e); LIVE;
    PORT(".Lsettings_state_inputs_edge_cfdc:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_cfdc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xCFE0..0xCFF4. */
REGION void tsl9_settings_state_inputs_block_cfe0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffff58); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e4)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_cff0:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_cff0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xCFF4..0xCFFC. */
REGION void tsl9_settings_state_inputs_block_cff4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 7(s0)\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_cff8:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_cff8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_a00c\n");
    __builtin_unreachable();
}

/* Original0xCFFC..0xD00C. */
REGION void tsl9_settings_state_inputs_block_cffc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 7(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff45)); LIVE;
    PORT(".Lsettings_state_inputs_edge_d008:\n.option push\n.option norvc\nbeq a5,a0,.Lsettings_state_inputs_edge_d008\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_d040\n");
    __builtin_unreachable();
}

/* Original0xD00C..0xD022. */
REGION void tsl9_settings_state_inputs_block_d00c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff39)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xffffff30)); LIVE;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lsettings_state_inputs_edge_d01e:\n.option push\n.option norvc\nbne a4,a5,.Lsettings_state_inputs_edge_d01e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_d026\n");
    __builtin_unreachable();
}

/* Original0xD022..0xD026. */
REGION void tsl9_settings_state_inputs_block_d022(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_d022:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_d022\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_f9ec\n");
    __builtin_unreachable();
}

/* Original0xD026..0xD030. */
REGION void tsl9_settings_state_inputs_block_d026(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_d02c:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_d02c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xD030..0xD036. */
REGION void tsl9_settings_state_inputs_block_d030(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lsettings_state_inputs_edge_d032:\n.option push\n.option norvc\nbne a0,a5,.Lsettings_state_inputs_edge_d032\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_cfe0\n");
    __builtin_unreachable();
}

/* Original0xD036..0xD03A. */
REGION void tsl9_settings_state_inputs_block_d036(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_d036:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_d036\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_cc54\n");
    __builtin_unreachable();
}

/* Original0xD03A..0xD03E. */
REGION void tsl9_settings_state_inputs_block_d03a(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_d03a:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_d03a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_bce0\n");
    __builtin_unreachable();
}

/* Original0xD03E..0xD040. */
REGION void tsl9_settings_state_inputs_block_d03e(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_d03e:\n.option push\n.option rvc\nc.j .Lsettings_state_inputs_edge_d03e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_settings_state_inputs_block_cfe0\n");
    __builtin_unreachable();
}

/* Original0xD040..0xD048. */
REGION void tsl9_settings_state_inputs_block_d040(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD104..0xD11C. */
REGION void tsl9_feature_external_d104(void)
{
    REGS;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e8)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    PORT(".Lsettings_state_inputs_edge_d118:\n.option push\n.option norvc\nbne a1,a2,.Lsettings_state_inputs_edge_d118\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_d134\n");
    __builtin_unreachable();
}

/* Original0xD11C..0xD124. */
REGION void tsl9_settings_state_inputs_block_d11c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e9)); LIVE;
    PORT(".Lsettings_state_inputs_edge_d120:\n.option push\n.option norvc\nbne a1,a3,.Lsettings_state_inputs_edge_d120\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_d134\n");
    __builtin_unreachable();
}

/* Original0xD124..0xD12C. */
REGION void tsl9_settings_state_inputs_block_d124(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ea)); LIVE;
    PORT(".Lsettings_state_inputs_edge_d128:\n.option push\n.option norvc\nbne a1,a4,.Lsettings_state_inputs_edge_d128\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_d134\n");
    __builtin_unreachable();
}

/* Original0xD12C..0xD134. */
REGION void tsl9_settings_state_inputs_block_d12c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000eb)); LIVE;
    PORT(".Lsettings_state_inputs_edge_d130:\n.option push\n.option norvc\nbeq a1,a5,.Lsettings_state_inputs_edge_d130\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_d148\n");
    __builtin_unreachable();
}

/* Original0xD134..0xD148. */
REGION void tsl9_settings_state_inputs_block_d134(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e8)) = (uint8_t)a2; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e9)) = (uint8_t)a3; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ea)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000eb)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_d144:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_d144\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xD148..0xD14A. */
REGION void tsl9_settings_state_inputs_block_d148(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF0D0..0xF0E4. */
REGION void tsl9_feature_external_f0d0(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a3 = UINT32_C(0x0000000e); LIVE;
    a4 = a4 >> UINT32_C(0x00000004); LIVE;
    a5 = a4 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lsettings_state_inputs_edge_f0e0:\n.option push\n.option norvc\nbltu a3,a5,.Lsettings_state_inputs_edge_f0e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_f148\n");
    __builtin_unreachable();
}

/* Original0xF0E4..0xF0EC. */
REGION void tsl9_settings_state_inputs_block_f0e4(void)
{
    REGS;
    a3 = UINT32_C(0x0000000f); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsettings_state_inputs_edge_f0e8:\n.option push\n.option norvc\nbeq a4,a3,.Lsettings_state_inputs_edge_f0e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_f0fe\n");
    __builtin_unreachable();
}

/* Original0xF0EC..0xF0FE. */
REGION void tsl9_settings_state_inputs_block_f0ec(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x00007000); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a4\n.option pop\n");
    a3 = a3 + UINT32_C(0xfffffada); LIVE;
    a5 = a5 & a3; LIVE;
    a5 = (uint32_t)(a5 != UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0xF0FE..0xF10A. */
REGION void tsl9_settings_state_inputs_block_f0fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffd\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xfffffea9)); LIVE;
    PORT(".Lsettings_state_inputs_edge_f106:\n.option push\n.option norvc\nbeq a3,a5,.Lsettings_state_inputs_edge_f106\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_f148\n");
    __builtin_unreachable();
}

/* Original0xF10A..0xF118. */
REGION void tsl9_settings_state_inputs_block_f10a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xfffffe99)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_f116:\n.option push\n.option rvc\nc.beqz a5,.Lsettings_state_inputs_edge_f116\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_f132\n");
    __builtin_unreachable();
}

/* Original0xF118..0xF11E. */
REGION void tsl9_settings_state_inputs_block_f118(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lsettings_state_inputs_edge_f11a:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_f11a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_entry_b254\n");
    __builtin_unreachable();
}

/* Original0xF11E..0xF126. */
REGION void tsl9_settings_state_inputs_block_f11e(void)
{
    REGS;
    a0 = UINT32_C(0x00000064); LIVE;
    PORT(".Lsettings_state_inputs_edge_f122:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_f122\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_actions_provider_de82\n");
    __builtin_unreachable();
}

/* Original0xF126..0xF12A. */
REGION void tsl9_settings_state_inputs_block_f126(void)
{
    REGS;
    a0 = UINT32_C(0x0000005d); LIVE;
    __builtin_unreachable();
}

/* Original0xF12A..0xF132. */
REGION void tsl9_settings_state_inputs_block_f12a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_f12e:\n.option push\n.option norvc\njal zero,.Lsettings_state_inputs_edge_f12e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xF132..0xF138. */
REGION void tsl9_settings_state_inputs_block_f132(void)
{
    REGS;
    a5 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lsettings_state_inputs_edge_f134:\n.option push\n.option norvc\nbeq a4,a5,.Lsettings_state_inputs_edge_f134\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_f142\n");
    __builtin_unreachable();
}

/* Original0xF138..0xF13E. */
REGION void tsl9_settings_state_inputs_block_f138(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lsettings_state_inputs_edge_f13a:\n.option push\n.option norvc\nbeq a4,a5,.Lsettings_state_inputs_edge_f13a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_f142\n");
    __builtin_unreachable();
}

/* Original0xF13E..0xF142. */
REGION void tsl9_settings_state_inputs_block_f13e(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_f13e:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_f13e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_b520\n");
    __builtin_unreachable();
}

/* Original0xF142..0xF148. */
REGION void tsl9_settings_state_inputs_block_f142(void)
{
    REGS;
    a0 = UINT32_C(0x0000005c); LIVE;
    PORT(".Lsettings_state_inputs_edge_f146:\n.option push\n.option rvc\nc.j .Lsettings_state_inputs_edge_f146\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_settings_state_inputs_block_f12a\n");
    __builtin_unreachable();
}

/* Original0xF148..0xF14A. */
REGION void tsl9_settings_state_inputs_block_f148(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF14A..0xF164. */
REGION void tsl9_feature_external_f14a(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffe3f)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lsettings_state_inputs_edge_f160:\n.option push\n.option norvc\nbeq a4,a5,.Lsettings_state_inputs_edge_f160\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_f196\n");
    __builtin_unreachable();
}

/* Original0xF164..0xF16E. */
REGION void tsl9_settings_state_inputs_block_f164(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffe31)) = (uint8_t)a5; LIVE;
    PORT(".Lsettings_state_inputs_edge_f16c:\n.option push\n.option rvc\nc.bnez a5,.Lsettings_state_inputs_edge_f16c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_settings_state_inputs_block_f172\n");
    __builtin_unreachable();
}

/* Original0xF16E..0xF172. */
REGION void tsl9_settings_state_inputs_block_f16e(void)
{
    REGS;
    PORT(".Lsettings_state_inputs_edge_f16e:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_f16e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_e20c\n");
    __builtin_unreachable();
}

/* Original0xF172..0xF182. */
REGION void tsl9_settings_state_inputs_block_f172(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffe23)); LIVE;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    PORT(".Lsettings_state_inputs_edge_f17e:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_f17e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_provider_17bc4\n");
    __builtin_unreachable();
}

/* Original0xF182..0xF196. */
REGION void tsl9_settings_state_inputs_block_f182(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffe13)); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x00000052); LIVE;
    PORT(".Lsettings_state_inputs_edge_f192:\n.option push\n.option norvc\njal ra,.Lsettings_state_inputs_edge_f192\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xF196..0xF1AA. */
REGION void tsl9_settings_state_inputs_block_f196(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffdf9)); LIVE;
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lsettings_state_inputs_edge_f1a6:\n.option push\n.option norvc\nbeq a4,a5,.Lsettings_state_inputs_edge_f1a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_settings_state_inputs_block_f1ba\n");
    __builtin_unreachable();
}

/* Original0xF1AA..0xF1BA. */
REGION void tsl9_settings_state_inputs_block_f1aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffde9)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffde2)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xF1BA..0xF1C2. */
REGION void tsl9_settings_state_inputs_block_f1ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
