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

/* Twelve complete helper/callback functions:910B/306i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xA6AA..0xA6B4. */
REGION void tsl9_record_dispatch_provider_a6aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff827)); LIVE;
    PORT(".Lrecord_helpers_edge_a6b2:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_helpers_edge_a6b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_a6d6\n");
    __builtin_unreachable();
}

/* Original0xA6B4..0xA6CC. */
REGION void tsl9_record_helpers_block_a6b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".Lrecord_helpers_literal_a6b6:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_a3cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_a6b6\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff811)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_helpers_edge_a6c8:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_a6c8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA6CC..0xA6D6. */
REGION void tsl9_record_helpers_block_a6cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_helpers_edge_a6d2:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_a6d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xA6D6..0xA6D8. */
REGION void tsl9_record_helpers_block_a6d6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB0B0..0xB0BA. */
REGION void tsl9_record_dispatch_provider_b0b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffe3b)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB572..0xB584. */
REGION void tsl9_record_dispatch_provider_b572(void)
{
    REGS;
    a5 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff975)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_helpers_edge_b580:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_b580\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xB594..0xB59C. */
REGION void tsl9_record_dispatch_provider_b594(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_helpers_edge_b59a:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_helpers_edge_b59a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_b59e\n");
    __builtin_unreachable();
}

/* Original0xB59C..0xB59E. */
REGION void tsl9_record_helpers_block_b59c(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0xB59E..0xB5AA. */
REGION void tsl9_record_helpers_block_b59e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff951)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_helpers_edge_b5a6:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_b5a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xB5AA..0xB5B4. */
REGION void tsl9_record_helpers_block_b5aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_helpers_edge_b5b0:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_b5b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xDE82..0xDE8E. */
REGION void tsl9_record_actions_provider_de82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffe\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000000fe)); LIVE;
    PORT(".option push\n.option rvc\nmv a2, a0\n.option pop\n");
    PORT(".Lrecord_helpers_edge_de8c:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_helpers_edge_de8c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_de9e\n");
    __builtin_unreachable();
}

/* Original0xDE8E..0xDE9E. */
REGION void tsl9_record_helpers_block_de8e(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_helpers_literal_de92:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_output_builder_provider_d810\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_de92\n.option pop\n");
    PORT(".Lrecord_helpers_edge_de9a:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_de9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xDE9E..0xDEA0. */
REGION void tsl9_record_helpers_block_de9e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEF76..0xEF82. */
REGION void tsl9_record_dispatch_provider_ef76(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_helpers_edge_ef7e:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_ef7e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_ee9a\n");
    __builtin_unreachable();
}

/* Original0xEF82..0xEF84. */
REGION void tsl9_record_helpers_block_ef82(void)
{
    REGS;
    PORT(".Lrecord_helpers_edge_ef82:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_helpers_edge_ef82\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f00e\n");
    __builtin_unreachable();
}

/* Original0xEF84..0xEF8A. */
REGION void tsl9_record_helpers_block_ef84(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".Lrecord_helpers_edge_ef86:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_ef86\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_bd50\n");
    __builtin_unreachable();
}

/* Original0xEF8A..0xEFA0. */
REGION void tsl9_record_helpers_block_ef8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 0(a0)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_helpers_edge_ef9c:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_helpers_edge_ef9c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_helpers_block_efee\n");
    __builtin_unreachable();
}

/* Original0xEFA0..0xEFA6. */
REGION void tsl9_record_helpers_block_efa0(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_helpers_edge_efa2:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_helpers_edge_efa2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_helpers_block_eff8\n");
    __builtin_unreachable();
}

/* Original0xEFA6..0xEFAC. */
REGION void tsl9_record_helpers_block_efa6(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_helpers_edge_efa8:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_helpers_edge_efa8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_helpers_block_f00e\n");
    __builtin_unreachable();
}

/* Original0xEFAC..0xEFB4. */
REGION void tsl9_record_helpers_block_efac(void)
{
    REGS;
    PORT(".Lrecord_helpers_literal_efac:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_1a430\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_efac\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEFB4..0xEFBE. */
REGION void tsl9_record_helpers_block_efb4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0xffffffd4)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000011); LIVE;
    __builtin_unreachable();
}

/* Original0xEFBE..0xEFEE. */
REGION void tsl9_record_helpers_block_efbe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xffffffc4)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xffffffba)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffba)) = (uint8_t)0; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_helpers_literal_efe0:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_ee30\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_efe0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_helpers_edge_efea:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_efea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xEFEE..0xEFF8. */
REGION void tsl9_record_helpers_block_efee(void)
{
    REGS;
    PORT(".Lrecord_helpers_literal_efee:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_1a454\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_efee\n.option pop\n");
    PORT(".Lrecord_helpers_edge_eff6:\n.option push\n.option rvc\nc.j .Lrecord_helpers_edge_eff6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_helpers_block_efb4\n");
    __builtin_unreachable();
}

/* Original0xEFF8..0xF00E. */
REGION void tsl9_record_helpers_block_eff8(void)
{
    REGS;
    PORT(".Lrecord_helpers_literal_eff8:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_1a478\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_eff8\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0xffffff88)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x00000035); LIVE;
    PORT(".Lrecord_helpers_edge_f00c:\n.option push\n.option rvc\nc.j .Lrecord_helpers_edge_f00c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_helpers_block_efbe\n");
    __builtin_unreachable();
}

/* Original0xF00E..0xF016. */
REGION void tsl9_record_helpers_block_f00e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF016..0xF030. */
REGION void tsl9_record_dispatch_provider_f016(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fffd\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -150\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a1, 9(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f02c:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f02c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_ee9a\n");
    __builtin_unreachable();
}

/* Original0xF030..0xF038. */
REGION void tsl9_record_helpers_block_f030(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s1, 10(s0)\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f034:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f034\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_bd46\n");
    __builtin_unreachable();
}

/* Original0xF038..0xF058. */
REGION void tsl9_record_helpers_block_f038(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_helpers_literal_f04a:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_eee0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_f04a\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f054:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_f054\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xF058..0xF05A. */
REGION void tsl9_record_actions_provider_f058(void)
{
    REGS;
    PORT(".Lrecord_helpers_edge_f058:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_helpers_edge_f058\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f08c\n");
    __builtin_unreachable();
}

/* Original0xF05A..0xF06E. */
REGION void tsl9_record_helpers_block_f05a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a2 = UINT32_C(0x00000019); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 >> UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_helpers_edge_f06a:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_helpers_edge_f06a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_helpers_block_f07c\n");
    __builtin_unreachable();
}

/* Original0xF06E..0xF078. */
REGION void tsl9_record_helpers_block_f06e(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    a2 = UINT32_C(0x00000028); LIVE;
    PORT(".Lrecord_helpers_edge_f074:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_helpers_edge_f074\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_helpers_block_f07c\n");
    __builtin_unreachable();
}

/* Original0xF078..0xF07C. */
REGION void tsl9_record_helpers_block_f078(void)
{
    REGS;
    a2 = UINT32_C(0x00000020); LIVE;
    __builtin_unreachable();
}

/* Original0xF07C..0xF08C. */
REGION void tsl9_record_helpers_block_f07c(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_helpers_literal_f080:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_edf2\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_f080\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f088:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_f088\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xF08C..0xF09C. */
REGION void tsl9_record_helpers_block_f08c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".Lrecord_helpers_literal_f08e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_edf2\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_f08e\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f098:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f098\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xF09C..0xF0B0. */
REGION void tsl9_record_helpers_block_f09c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffeec)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f0ac:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_f0ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_edf2\n");
    __builtin_unreachable();
}

/* Original0xF47E..0xF490. */
REGION void tsl9_record_actions_provider_f47e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)) = (uint8_t)a2; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a3\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f48e:\n.option push\n.option rvc\nc.beqz a2,.Lrecord_helpers_edge_f48e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f4b0\n");
    __builtin_unreachable();
}

/* Original0xF490..0xF492. */
REGION void tsl9_record_helpers_block_f490(void)
{
    REGS;
    PORT(".Lrecord_helpers_edge_f490:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_helpers_edge_f490\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f49a\n");
    __builtin_unreachable();
}

/* Original0xF492..0xF49A. */
REGION void tsl9_record_helpers_block_f492(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF49A..0xF49C. */
REGION void tsl9_record_helpers_block_f49a(void)
{
    REGS;
    PORT(".Lrecord_helpers_edge_f49a:\n.option push\n.option rvc\nc.beqz s1,.Lrecord_helpers_edge_f49a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f4a2\n");
    __builtin_unreachable();
}

/* Original0xF49C..0xF4A2. */
REGION void tsl9_record_helpers_block_f49c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f49e:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f49e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xF4A2..0xF4B0. */
REGION void tsl9_record_helpers_block_f4a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f4ac:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_f4ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xF4B0..0xF4C2. */
REGION void tsl9_record_helpers_block_f4b0(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffd1e); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".Lrecord_helpers_edge_f4be:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f4be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2\n");
    __builtin_unreachable();
}

/* Original0xF4C2..0xF4C8. */
REGION void tsl9_record_helpers_block_f4c2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lrecord_helpers_edge_f4c6:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_helpers_edge_f4c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f49a\n");
    __builtin_unreachable();
}

/* Original0xF4C8..0xF4CE. */
REGION void tsl9_record_helpers_block_f4c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f4ca:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f4ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xF4CE..0xF4D0. */
REGION void tsl9_record_helpers_block_f4ce(void)
{
    REGS;
    PORT(".Lrecord_helpers_edge_f4ce:\n.option push\n.option rvc\nc.j .Lrecord_helpers_edge_f4ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_helpers_block_f49a\n");
    __builtin_unreachable();
}

/* Original0xF4D0..0xF4DE. */
REGION void tsl9_record_actions_provider_f4d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f4da:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f4da\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xF4DE..0xF506. */
REGION void tsl9_record_helpers_block_f4de(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffac3)); LIVE;
    a5 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000032); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_helpers_literal_f4f2:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_actions_provider_f4d0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_f4f2\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffaa7)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_helpers_edge_f502:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f502\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xF506..0xF518. */
REGION void tsl9_record_helpers_block_f506(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa97)); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffd\n.option pop\n");
    a3 = a3 + UINT32_C(0xfffffa82); LIVE;
    PORT(".Lrecord_helpers_edge_f516:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_helpers_edge_f516\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f52e\n");
    __builtin_unreachable();
}

/* Original0xF518..0xF52E. */
REGION void tsl9_record_helpers_block_f518(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000011)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a4 = a5 << UINT32_C(0x00000003); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xF52E..0xF546. */
REGION void tsl9_record_helpers_block_f52e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)); LIVE;
    a5 = a5 >> UINT32_C(0x0000001b); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa6a)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa63)); LIVE;
    PORT(".Lrecord_helpers_edge_f544:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_helpers_edge_f544\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f55c\n");
    __builtin_unreachable();
}

/* Original0xF546..0xF55C. */
REGION void tsl9_record_helpers_block_f546(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000011)); LIVE;
    a4 = a5 << UINT32_C(0x00000007); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)); LIVE;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xF55C..0xF572. */
REGION void tsl9_record_helpers_block_f55c(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a5 = a5 >> UINT32_C(0x0000000f); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa3a)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_helpers_edge_f56e:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f56e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2\n");
    __builtin_unreachable();
}

/* Original0xF572..0xF578. */
REGION void tsl9_record_helpers_block_f572(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF578..0xF588. */
REGION void tsl9_record_actions_provider_f578(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f584:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f584\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xF588..0xF5AA. */
REGION void tsl9_record_helpers_block_f588(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa1e)); LIVE;
    PORT(".option push\n.option norvc\nnot s0, a5\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa0c)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nandi s0, s0, 1\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f5a6:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_helpers_edge_f5a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_helpers_block_f620\n");
    __builtin_unreachable();
}

/* Original0xF5AA..0xF5B0. */
REGION void tsl9_record_helpers_block_f5aa(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000087); LIVE;
    __builtin_unreachable();
}

/* Original0xF5B0..0xF5BE. */
REGION void tsl9_record_helpers_block_f5b0(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_helpers_literal_f5b2:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_actions_provider_f578\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_helpers_literal_f5b2\n.option pop\n");
    PORT(".Lrecord_helpers_edge_f5ba:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f5ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xF5BE..0xF5C8. */
REGION void tsl9_record_helpers_block_f5be(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9e4)); LIVE;
    PORT(".Lrecord_helpers_edge_f5c6:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_helpers_edge_f5c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f5d8\n");
    __builtin_unreachable();
}

/* Original0xF5C8..0xF5D8. */
REGION void tsl9_record_helpers_block_f5c8(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    PORT(".option push\n.option norvc\nslli a5, s0, 0x3\n.option pop\n");
    a4 = a4 & UINT32_C(0xfffffff7); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xF5D8..0xF5F0. */
REGION void tsl9_record_helpers_block_f5d8(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)); LIVE;
    a5 = a5 >> UINT32_C(0x0000001b); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff9c5)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9be)); LIVE;
    PORT(".Lrecord_helpers_edge_f5ee:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_helpers_edge_f5ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_f602\n");
    __builtin_unreachable();
}

/* Original0xF5F0..0xF602. */
REGION void tsl9_record_helpers_block_f5f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nslli a5, s0, 0x7\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s0, 9(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 127\n.option pop\n");
    PORT(".option push\n.option rvc\nor s0, s0, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 9(sp)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF602..0xF618. */
REGION void tsl9_record_helpers_block_f602(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000001); LIVE;
    a5 = a5 >> UINT32_C(0x0000000f); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff999)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_helpers_edge_f614:\n.option push\n.option norvc\njal ra,.Lrecord_helpers_edge_f614\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2\n");
    __builtin_unreachable();
}

/* Original0xF618..0xF620. */
REGION void tsl9_record_helpers_block_f618(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF620..0xF630. */
REGION void tsl9_record_helpers_block_f620(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff986)) = (uint8_t)0; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000005dc); LIVE;
    PORT(".Lrecord_helpers_edge_f62e:\n.option push\n.option rvc\nc.j .Lrecord_helpers_edge_f62e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_helpers_block_f5b0\n");
    __builtin_unreachable();
}

/* Original0x18218..0x18228. */
REGION void tsl9_record_dispatch_provider_18218(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000070d)); LIVE;
    a5 = a5 & a0; LIVE;
    PORT(".option push\n.option rvc\nmv a1, a0\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_helpers_edge_18226:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_helpers_edge_18226\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_helpers_block_1822e\n");
    __builtin_unreachable();
}

/* Original0x18228..0x1822A. */
REGION void tsl9_record_helpers_block_18228(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x1822A..0x1822E. */
REGION void tsl9_record_helpers_block_1822a(void)
{
    REGS;
    PORT(".Lrecord_helpers_edge_1822a:\n.option push\n.option norvc\njal zero,.Lrecord_helpers_edge_1822a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1811a\n");
    __builtin_unreachable();
}

/* Original0x1822E..0x18232. */
REGION void tsl9_record_helpers_block_1822e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_helpers_edge_18230:\n.option push\n.option rvc\nc.j .Lrecord_helpers_edge_18230\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_helpers_block_1822a\n");
    __builtin_unreachable();
}
