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

/* Nine complete original action-primitives functions:684B/231i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x10D9A..0x10DAC. */
REGION void tsl9_record_dispatch_provider_10d9a(void)
{
    REGS;
    a5 = UINT32_C(0x00010000); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000252)); LIVE;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_edge_10da8:\n.option push\n.option norvc\nbeq a4,a5,.Laction_primitives_edge_10da8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_action_primitives_block_10dca\n");
    __builtin_unreachable();
}

/* Original0x10DAC..0x10DBA. */
REGION void tsl9_action_primitives_block_10dac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000024e)); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Laction_primitives_edge_10db6:\n.option push\n.option norvc\nbeq a4,a5,.Laction_primitives_edge_10db6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_action_primitives_block_10dca\n");
    __builtin_unreachable();
}

/* Original0x10DBA..0x10DC8. */
REGION void tsl9_action_primitives_block_10dba(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x0000024c)); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Laction_primitives_edge_10dc4:\n.option push\n.option norvc\nbne a4,a5,.Laction_primitives_edge_10dc4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_action_primitives_block_10dca\n");
    __builtin_unreachable();
}

/* Original0x10DC8..0x10DCA. */
REGION void tsl9_action_primitives_block_10dc8(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x10DCA..0x10DCC. */
REGION void tsl9_action_primitives_block_10dca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1552A..0x15532. */
REGION void tsl9_record_dispatch_provider_1552a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000166)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x15532..0x1555A. */
REGION void tsl9_record_dispatch_provider_15532(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a0 & UINT32_C(0x00000001); LIVE;
    a4 = a5 << UINT32_C(0x00000003); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Laction_primitives_edge_15556:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_15556\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_13138\n");
    __builtin_unreachable();
}

/* Original0x1555A..0x15560. */
REGION void tsl9_action_primitives_block_1555a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_edge_1555c:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_1555c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_clear_820c\n");
    __builtin_unreachable();
}

/* Original0x15560..0x15566. */
REGION void tsl9_action_primitives_block_15560(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_edge_15562:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_15562\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0x15566..0x1556C. */
REGION void tsl9_action_primitives_block_15566(void)
{
    REGS;
    PORT(".option push\n.option norvc\nxori s1, s0, 1\n.option pop\n");
    PORT(".Laction_primitives_edge_1556a:\n.option push\n.option rvc\nc.bnez s0,.Laction_primitives_edge_1556a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1557e\n");
    __builtin_unreachable();
}

/* Original0x1556C..0x15570. */
REGION void tsl9_action_primitives_block_1556c(void)
{
    REGS;
    PORT(".Laction_primitives_edge_1556c:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_1556c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_9af0\n");
    __builtin_unreachable();
}

/* Original0x15570..0x1557E. */
REGION void tsl9_action_primitives_block_15570(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Laction_primitives_edge_1557a:\n.option push\n.option norvc\njal zero,.Laction_primitives_edge_1557a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0x1557E..0x15582. */
REGION void tsl9_action_primitives_block_1557e(void)
{
    REGS;
    PORT(".Laction_primitives_edge_1557e:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_1557e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_9ae4\n");
    __builtin_unreachable();
}

/* Original0x15582..0x15584. */
REGION void tsl9_action_primitives_block_15582(void)
{
    REGS;
    PORT(".Laction_primitives_edge_15582:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_15582\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_15570\n");
    __builtin_unreachable();
}

/* Original0x17F80..0x17F8A. */
REGION void tsl9_action_primitives_provider_17f80(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9b2)); LIVE;
    PORT(".Laction_primitives_edge_17f88:\n.option push\n.option rvc\nc.bnez a5,.Laction_primitives_edge_17f88\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_17f94\n");
    __builtin_unreachable();
}

/* Original0x17F8A..0x17F94. */
REGION void tsl9_action_primitives_block_17f8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9ba)); LIVE;
    PORT(".Laction_primitives_edge_17f92:\n.option push\n.option rvc\nc.beqz a5,.Laction_primitives_edge_17f92\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_17fa8\n");
    __builtin_unreachable();
}

/* Original0x17F94..0x17FA8. */
REGION void tsl9_action_primitives_block_17f94(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_literal_17f9c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_action_primitives_provider_17f80\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Laction_primitives_literal_17f9c\n.option pop\n");
    PORT(".Laction_primitives_edge_17fa4:\n.option push\n.option norvc\njal zero,.Laction_primitives_edge_17fa4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x17FA8..0x17FC4. */
REGION void tsl9_action_primitives_block_17fa8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s0, 0x1fff5\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -1676\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 12(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0xfffff968)) = (uint32_t)a5; LIVE;
    PORT(".Laction_primitives_edge_17fc0:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_17fc0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_17c4e\n");
    __builtin_unreachable();
}

/* Original0x17FC4..0x17FD8. */
REGION void tsl9_action_primitives_block_17fc4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a3, 12(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff961)); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff95a)); LIVE;
    PORT(".Laction_primitives_edge_17fd6:\n.option push\n.option rvc\nc.bnez a3,.Laction_primitives_edge_17fd6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_17ff4\n");
    __builtin_unreachable();
}

/* Original0x17FD8..0x17FDE. */
REGION void tsl9_action_primitives_block_17fd8(void)
{
    REGS;
    a2 = UINT32_C(0x00000014); LIVE;
    PORT(".Laction_primitives_edge_17fda:\n.option push\n.option norvc\nbltu a4,a5,.Laction_primitives_edge_17fda\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_action_primitives_block_17ffe\n");
    __builtin_unreachable();
}

/* Original0x17FDE..0x17FF4. */
REGION void tsl9_action_primitives_block_17fde(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 7(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff93f)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17FF4..0x17FF8. */
REGION void tsl9_action_primitives_block_17ff4(void)
{
    REGS;
    PORT(".Laction_primitives_edge_17ff4:\n.option push\n.option norvc\nbleu a5,a4,.Laction_primitives_edge_17ff4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_action_primitives_block_1800e\n");
    __builtin_unreachable();
}

/* Original0x17FF8..0x17FFE. */
REGION void tsl9_action_primitives_block_17ff8(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    __builtin_unreachable();
}

/* Original0x17FFE..0x1800C. */
REGION void tsl9_action_primitives_block_17ffe(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_literal_18000:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_action_primitives_provider_17f80\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Laction_primitives_literal_18000\n.option pop\n");
    PORT(".Laction_primitives_edge_18008:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_18008\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x1800C..0x1800E. */
REGION void tsl9_action_primitives_block_1800c(void)
{
    REGS;
    PORT(".Laction_primitives_edge_1800c:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_1800c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_17fde\n");
    __builtin_unreachable();
}

/* Original0x1800E..0x1802C. */
REGION void tsl9_action_primitives_block_1800e(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff916)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff90d)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff90a)) = (uint32_t)0; LIVE;
    PORT(".Laction_primitives_edge_1802a:\n.option push\n.option rvc\nc.jal .Laction_primitives_edge_1802a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_provider_17f80\n");
    __builtin_unreachable();
}

/* Original0x1802C..0x1802E. */
REGION void tsl9_action_primitives_block_1802c(void)
{
    REGS;
    PORT(".Laction_primitives_edge_1802c:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_1802c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_17fde\n");
    __builtin_unreachable();
}

/* Original0x1802E..0x18040. */
REGION void tsl9_registered_callbacks_provider_1802e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8fa)) = (uint8_t)a1; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8f1)) = (uint8_t)0; LIVE;
    PORT(".Laction_primitives_edge_1803e:\n.option push\n.option rvc\nc.bnez a2,.Laction_primitives_edge_1803e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1804c\n");
    __builtin_unreachable();
}

/* Original0x18040..0x1804C. */
REGION void tsl9_action_primitives_block_18040(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffff8e0); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a0 = a0 | a5; LIVE;
    __builtin_unreachable();
}

/* Original0x1804C..0x1805A. */
REGION void tsl9_action_primitives_block_1804c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8e0)) = (uint32_t)a0; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_edge_18056:\n.option push\n.option norvc\njal zero,.Laction_primitives_edge_18056\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_17f80\n");
    __builtin_unreachable();
}

/* Original0x1805A..0x18076. */
REGION void tsl9_action_primitives_provider_1805a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8c8)); LIVE;
    a2 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8bd)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_edge_18072:\n.option push\n.option norvc\nbltu a2,a4,.Laction_primitives_edge_18072\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_action_primitives_block_1809e\n");
    __builtin_unreachable();
}

/* Original0x18076..0x18090. */
REGION void tsl9_action_primitives_block_18076(void)
{
    REGS;
    PORT(".Laction_primitives_literal_18076:\n.option push\n.option norvc\nauipc a2,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_action_primitives_table_1ab04\naddi a2,a2,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Laction_primitives_literal_18076\n.option pop\n");
    a4 = a4 << UINT32_C(0x00000002); LIVE;
    a4 = a4 + a2; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a3 = a5 & UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    a4 = a4 + a2; LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\njr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18090..0x18092. */
REGION void tsl9_action_primitives_block_18090(void)
{
    REGS;
    PORT(".Laction_primitives_edge_18090:\n.option push\n.option rvc\nc.beqz a3,.Laction_primitives_edge_18090\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_18096\n");
    __builtin_unreachable();
}

/* Original0x18092..0x18096. */
REGION void tsl9_action_primitives_block_18092(void)
{
    REGS;
    a0 = UINT32_C(0x00110000); LIVE;
    __builtin_unreachable();
}

/* Original0x18096..0x18098. */
REGION void tsl9_action_primitives_block_18096(void)
{
    REGS;
    PORT(".Laction_primitives_edge_18096:\n.option push\n.option rvc\nc.beqz a5,.Laction_primitives_edge_18096\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1809e\n");
    __builtin_unreachable();
}

/* Original0x18098..0x1809C. */
REGION void tsl9_action_primitives_block_18098(void)
{
    REGS;
    a5 = UINT32_C(0x00440000); LIVE;
    __builtin_unreachable();
}

/* Original0x1809C..0x1809E. */
REGION void tsl9_action_primitives_block_1809c(void)
{
    REGS;
    a0 = a0 | a5; LIVE;
    __builtin_unreachable();
}

/* Original0x1809E..0x180A8. */
REGION void tsl9_action_primitives_block_1809e(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    PORT(".Laction_primitives_edge_180a4:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_180a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x180A8..0x180C6. */
REGION void tsl9_action_primitives_block_180a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff5\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff87e)); LIVE;
    a4 = UINT32_C(0x00000006); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nrem a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff86c)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x180C6..0x180C8. */
REGION void tsl9_action_primitives_block_180c6(void)
{
    REGS;
    PORT(".Laction_primitives_edge_180c6:\n.option push\n.option rvc\nc.beqz a3,.Laction_primitives_edge_180c6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_180cc\n");
    __builtin_unreachable();
}

/* Original0x180C8..0x180CC. */
REGION void tsl9_action_primitives_block_180c8(void)
{
    REGS;
    a0 = UINT32_C(0x00220000); LIVE;
    __builtin_unreachable();
}

/* Original0x180CC..0x180CE. */
REGION void tsl9_action_primitives_block_180cc(void)
{
    REGS;
    PORT(".Laction_primitives_edge_180cc:\n.option push\n.option rvc\nc.beqz a5,.Laction_primitives_edge_180cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1809e\n");
    __builtin_unreachable();
}

/* Original0x180CE..0x180D4. */
REGION void tsl9_action_primitives_block_180ce(void)
{
    REGS;
    a5 = UINT32_C(0x00880000); LIVE;
    PORT(".Laction_primitives_edge_180d2:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_180d2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_1809c\n");
    __builtin_unreachable();
}

/* Original0x180D4..0x180D6. */
REGION void tsl9_action_primitives_block_180d4(void)
{
    REGS;
    PORT(".Laction_primitives_edge_180d4:\n.option push\n.option rvc\nc.beqz a3,.Laction_primitives_edge_180d4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_180da\n");
    __builtin_unreachable();
}

/* Original0x180D6..0x180DA. */
REGION void tsl9_action_primitives_block_180d6(void)
{
    REGS;
    a0 = UINT32_C(0x00210000); LIVE;
    __builtin_unreachable();
}

/* Original0x180DA..0x180DC. */
REGION void tsl9_action_primitives_block_180da(void)
{
    REGS;
    PORT(".Laction_primitives_edge_180da:\n.option push\n.option rvc\nc.beqz a5,.Laction_primitives_edge_180da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1809e\n");
    __builtin_unreachable();
}

/* Original0x180DC..0x180E2. */
REGION void tsl9_action_primitives_block_180dc(void)
{
    REGS;
    a5 = UINT32_C(0x00840000); LIVE;
    PORT(".Laction_primitives_edge_180e0:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_180e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_1809c\n");
    __builtin_unreachable();
}

/* Original0x180E2..0x180E4. */
REGION void tsl9_action_primitives_block_180e2(void)
{
    REGS;
    PORT(".Laction_primitives_edge_180e2:\n.option push\n.option rvc\nc.beqz a3,.Laction_primitives_edge_180e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_180e8\n");
    __builtin_unreachable();
}

/* Original0x180E4..0x180E8. */
REGION void tsl9_action_primitives_block_180e4(void)
{
    REGS;
    a0 = UINT32_C(0x00120000); LIVE;
    __builtin_unreachable();
}

/* Original0x180E8..0x180EA. */
REGION void tsl9_action_primitives_block_180e8(void)
{
    REGS;
    PORT(".Laction_primitives_edge_180e8:\n.option push\n.option rvc\nc.beqz a5,.Laction_primitives_edge_180e8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1809e\n");
    __builtin_unreachable();
}

/* Original0x180EA..0x180F0. */
REGION void tsl9_action_primitives_block_180ea(void)
{
    REGS;
    a5 = UINT32_C(0x00480000); LIVE;
    PORT(".Laction_primitives_edge_180ee:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_180ee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_1809c\n");
    __builtin_unreachable();
}

/* Original0x180F0..0x180FE. */
REGION void tsl9_action_primitives_provider_180f0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Laction_primitives_edge_180fa:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_180fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_1552a\n");
    __builtin_unreachable();
}

/* Original0x180FE..0x18110. */
REGION void tsl9_action_primitives_block_180fe(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Laction_primitives_edge_1810c:\n.option push\n.option norvc\njal zero,.Laction_primitives_edge_1810c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x18110..0x1811A. */
REGION void tsl9_registered_callbacks_provider_18110(void)
{
    REGS;
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000003); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_edge_18116:\n.option push\n.option norvc\njal zero,.Laction_primitives_edge_18116\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x1811A..0x18144. */
REGION void tsl9_record_dispatch_provider_1811a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff5\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff80b)); LIVE;
    PORT(".option push\n.option norvc\nnot a5, a1\n.option pop\n");
    a5 = a5 & a4; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = a5 | a0; LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007f7)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000007ee)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".Laction_primitives_edge_18142:\n.option push\n.option rvc\nc.beqz a1,.Laction_primitives_edge_18142\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1817e\n");
    __builtin_unreachable();
}

/* Original0x18144..0x18146. */
REGION void tsl9_action_primitives_block_18144(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0x18146..0x1814A. */
REGION void tsl9_action_primitives_block_18146(void)
{
    REGS;
    PORT(".Laction_primitives_edge_18146:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_18146\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0x1814A..0x18154. */
REGION void tsl9_action_primitives_block_1814a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000007db)); LIVE;
    PORT(".Laction_primitives_edge_18152:\n.option push\n.option rvc\nc.beqz a5,.Laction_primitives_edge_18152\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_18186\n");
    __builtin_unreachable();
}

/* Original0x18154..0x1815A. */
REGION void tsl9_action_primitives_block_18154(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Laction_primitives_edge_18156:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_18156\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_1805a\n");
    __builtin_unreachable();
}

/* Original0x1815A..0x18170. */
REGION void tsl9_action_primitives_block_1815a(void)
{
    REGS;
    a2 = UINT32_C(0x00002000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0xffffff40); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Laction_primitives_literal_18164:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_action_primitives_provider_1805a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Laction_primitives_literal_18164\n.option pop\n");
    PORT(".Laction_primitives_edge_1816c:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_1816c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x18170..0x18172. */
REGION void tsl9_action_primitives_block_18170(void)
{
    REGS;
    PORT(".Laction_primitives_edge_18170:\n.option push\n.option rvc\nc.beqz s0,.Laction_primitives_edge_18170\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_18198\n");
    __builtin_unreachable();
}

/* Original0x18172..0x1817E. */
REGION void tsl9_action_primitives_block_18172(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Laction_primitives_edge_1817a:\n.option push\n.option norvc\njal zero,.Laction_primitives_edge_1817a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0x1817E..0x18180. */
REGION void tsl9_action_primitives_block_1817e(void)
{
    REGS;
    PORT(".Laction_primitives_edge_1817e:\n.option push\n.option rvc\nc.beqz a0,.Laction_primitives_edge_1817e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_action_primitives_block_1814a\n");
    __builtin_unreachable();
}

/* Original0x18180..0x18186. */
REGION void tsl9_action_primitives_block_18180(void)
{
    REGS;
    a0 = UINT32_C(0x0000012c); LIVE;
    PORT(".Laction_primitives_edge_18184:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_18184\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_18146\n");
    __builtin_unreachable();
}

/* Original0x18186..0x18192. */
REGION void tsl9_action_primitives_block_18186(void)
{
    REGS;
    PORT(".Laction_primitives_literal_18186:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_action_primitives_provider_1805a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Laction_primitives_literal_18186\n.option pop\n");
    PORT(".Laction_primitives_edge_1818e:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_1818e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0x18192..0x18196. */
REGION void tsl9_action_primitives_block_18192(void)
{
    REGS;
    PORT(".Laction_primitives_edge_18192:\n.option push\n.option norvc\njal ra,.Laction_primitives_edge_18192\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_18110\n");
    __builtin_unreachable();
}

/* Original0x18196..0x18198. */
REGION void tsl9_action_primitives_block_18196(void)
{
    REGS;
    PORT(".Laction_primitives_edge_18196:\n.option push\n.option rvc\nc.j .Laction_primitives_edge_18196\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_action_primitives_block_18170\n");
    __builtin_unreachable();
}

/* Original0x18198..0x181A0. */
REGION void tsl9_action_primitives_block_18198(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original relative jump words; valid only at the verified original layout. */
ENTRY __attribute__((used,aligned(4),section(".rodata.tsl9_action_primitives_table_1ab04"))) const uint32_t tsl9_action_primitives_table_1ab04[6] = {
    UINT32_C(0xffffd58c),
    UINT32_C(0xffffd5c2),
    UINT32_C(0xffffd5d0),
    UINT32_C(0xffffd5de),
    UINT32_C(0xffffd5d0),
    UINT32_C(0xffffd5de),
};
