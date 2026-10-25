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

/* Twelve complete record-field helper entries:1564B/539i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x8248..0x8250. */
REGION void tsl9_record_field_transitions_provider_8248(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lrecord_field_helpers_edge_824c:\n.option push\n.option norvc\nbltu a0,a1,.Lrecord_field_helpers_edge_824c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_827a\n");
    __builtin_unreachable();
}

/* Original0x8250..0x8254. */
REGION void tsl9_record_field_helpers_block_8250(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_8250:\n.option push\n.option norvc\nbltu a2,a0,.Lrecord_field_helpers_edge_8250\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_827a\n");
    __builtin_unreachable();
}

/* Original0x8254..0x8256. */
REGION void tsl9_record_field_helpers_block_8254(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_8254:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_8254\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_828a\n");
    __builtin_unreachable();
}

/* Original0x8256..0x8268. */
REGION void tsl9_record_field_helpers_block_8256(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a4\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_8264:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_8264\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0x8268..0x826E. */
REGION void tsl9_record_field_helpers_block_8268(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_helpers_edge_826a:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_field_helpers_edge_826a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_8282\n");
    __builtin_unreachable();
}

/* Original0x826E..0x827A. */
REGION void tsl9_record_field_helpers_block_826e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_8276:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_8276\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0x827A..0x827C. */
REGION void tsl9_record_field_helpers_block_827a(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_827a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_827a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_828a\n");
    __builtin_unreachable();
}

/* Original0x827C..0x8282. */
REGION void tsl9_record_field_helpers_block_827c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x8282..0x828A. */
REGION void tsl9_record_field_helpers_block_8282(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x828A..0x828C. */
REGION void tsl9_record_field_helpers_block_828a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA476..0xA486. */
REGION void tsl9_record_field_transitions_provider_a476(void)
{
    REGS;
    a4 = a0 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_a482:\n.option push\n.option norvc\nbltu a3,a4,.Lrecord_field_helpers_edge_a482\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a4ca\n");
    __builtin_unreachable();
}

/* Original0xA486..0xA490. */
REGION void tsl9_record_field_helpers_block_a486(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lrecord_field_helpers_edge_a48c:\n.option push\n.option norvc\nbltu a4,a3,.Lrecord_field_helpers_edge_a48c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a49c\n");
    __builtin_unreachable();
}

/* Original0xA490..0xA49C. */
REGION void tsl9_record_field_helpers_block_a490(void)
{
    REGS;
    a4 = UINT32_C(0x0000065e); LIVE;
    PORT(".option push\n.option norvc\nsrl a4, a4, a3\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_a49a:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_field_helpers_edge_a49a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a4ae\n");
    __builtin_unreachable();
}

/* Original0xA49C..0xA4A4. */
REGION void tsl9_record_field_helpers_block_a49c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    a0 = (uint32_t)(a5 != UINT32_C(0)); LIVE;
    PORT(".Lrecord_field_helpers_edge_a4a2:\n.option push\n.option rvc\nc.bnez a1,.Lrecord_field_helpers_edge_a4a2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a4a8\n");
    __builtin_unreachable();
}

/* Original0xA4A4..0xA4A8. */
REGION void tsl9_record_field_helpers_block_a4a4(void)
{
    REGS;
    a0 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0xA4A8..0xA4AE. */
REGION void tsl9_record_field_helpers_block_a4a8(void)
{
    REGS;
    a0 = a0 + UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_field_helpers_edge_a4aa:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_a4aa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0xA4AE..0xA4B2. */
REGION void tsl9_record_field_helpers_block_a4ae(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_edge_a4b0:\n.option push\n.option rvc\nc.beqz a1,.Lrecord_field_helpers_edge_a4b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a4c0\n");
    __builtin_unreachable();
}

/* Original0xA4B2..0xA4B8. */
REGION void tsl9_record_field_helpers_block_a4b2(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_field_helpers_edge_a4b4:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_helpers_edge_a4b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a4ba\n");
    __builtin_unreachable();
}

/* Original0xA4B8..0xA4BA. */
REGION void tsl9_record_field_helpers_block_a4b8(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0xA4BA..0xA4C0. */
REGION void tsl9_record_field_helpers_block_a4ba(void)
{
    REGS;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_helpers_edge_a4bc:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_a4bc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_helpers_entry_cd58\n");
    __builtin_unreachable();
}

/* Original0xA4C0..0xA4C6. */
REGION void tsl9_record_field_helpers_block_a4c0(void)
{
    REGS;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_helpers_edge_a4c2:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_helpers_edge_a4c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a4ba\n");
    __builtin_unreachable();
}

/* Original0xA4C6..0xA4CA. */
REGION void tsl9_record_field_helpers_block_a4c6(void)
{
    REGS;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".Lrecord_field_helpers_edge_a4c8:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_a4c8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_a4ba\n");
    __builtin_unreachable();
}

/* Original0xA4CA..0xA4CC. */
REGION void tsl9_record_field_helpers_block_a4ca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA4EE..0xA504. */
REGION void tsl9_record_field_transitions_provider_a4ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = a0 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_a500:\n.option push\n.option norvc\nbltu s1,a5,.Lrecord_field_helpers_edge_a500\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a602\n");
    __builtin_unreachable();
}

/* Original0xA504..0xA50A. */
REGION void tsl9_record_field_helpers_block_a504(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_a506:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_a506\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xA50A..0xA50C. */
REGION void tsl9_record_field_helpers_block_a50a(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_a50a:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_a50a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a5d6\n");
    __builtin_unreachable();
}

/* Original0xA50C..0xA520. */
REGION void tsl9_record_field_helpers_block_a50c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff9be)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lrecord_field_helpers_edge_a51e:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_helpers_edge_a51e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a5a4\n");
    __builtin_unreachable();
}

/* Original0xA520..0xA532. */
REGION void tsl9_record_field_helpers_block_a520(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff9b0)) = (uint8_t)0; LIVE;
    a4 = a5 & UINT32_C(0x00000006); LIVE;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lrecord_field_helpers_edge_a530:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_a530\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a592\n");
    __builtin_unreachable();
}

/* Original0xA532..0xA534. */
REGION void tsl9_record_field_helpers_block_a532(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_a532:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_helpers_edge_a532\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA534..0xA53E. */
REGION void tsl9_record_field_helpers_block_a534(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff99d)); LIVE;
    PORT(".Lrecord_field_helpers_edge_a53c:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_a53c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA53E..0xA544. */
REGION void tsl9_record_field_helpers_block_a53e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000161)); LIVE;
    PORT(".Lrecord_field_helpers_edge_a542:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_a542\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA544..0xA55A. */
REGION void tsl9_record_field_helpers_block_a544(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_literal_a546:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_a3cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_a546\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff983)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_helpers_edge_a556:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_a556\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA55A..0xA56E. */
REGION void tsl9_record_field_helpers_block_a55a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000160); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_field_helpers_edge_a56a:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_field_helpers_edge_a56a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA56E..0xA586. */
REGION void tsl9_record_field_helpers_block_a56e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, -1691(a5)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000001f4); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_helpers_literal_a57e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_entry_a4cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_a57e\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA586..0xA592. */
REGION void tsl9_record_field_helpers_block_a586(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_a58e:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_a58e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA592..0xA594. */
REGION void tsl9_record_field_helpers_block_a592(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_a592:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_field_helpers_edge_a592\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA594..0xA59A. */
REGION void tsl9_record_field_helpers_block_a594(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000161)); LIVE;
    PORT(".Lrecord_field_helpers_edge_a598:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_a598\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a55a\n");
    __builtin_unreachable();
}

/* Original0xA59A..0xA5A4. */
REGION void tsl9_record_field_helpers_block_a59a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA5A4..0xA5B0. */
REGION void tsl9_record_field_helpers_block_a5a4(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000026); LIVE;
    a4 = UINT32_C(0x00000020); LIVE;
    PORT(".Lrecord_field_helpers_edge_a5ac:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_field_helpers_edge_a5ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA5B0..0xA5B6. */
REGION void tsl9_record_field_helpers_block_a5b0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000161)); LIVE;
    PORT(".Lrecord_field_helpers_edge_a5b4:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_a5b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA5B6..0xA5BA. */
REGION void tsl9_record_field_helpers_block_a5b6(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_a5b6:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_a5b6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xA5BA..0xA5BC. */
REGION void tsl9_record_field_helpers_block_a5ba(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_a5ba:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_a5ba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA5BC..0xA5D6. */
REGION void tsl9_record_field_helpers_block_a5bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, -1769(a5)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000001f4); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_helpers_literal_a5cc:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_entry_a4d8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_a5cc\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_a5d4:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_a5d4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_a586\n");
    __builtin_unreachable();
}

/* Original0xA5D6..0xA5E4. */
REGION void tsl9_record_field_helpers_block_a5d6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8fb)); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_field_helpers_edge_a5e0:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_helpers_edge_a5e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA5E4..0xA602. */
REGION void tsl9_record_field_helpers_block_a5e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8e5)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_helpers_literal_a5f4:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_a3cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_a5f4\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_a5fe:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_a5fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA602..0xA610. */
REGION void tsl9_record_field_helpers_block_a602(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8cf)); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_edge_a60c:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_helpers_edge_a60c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xA610..0xA612. */
REGION void tsl9_record_field_helpers_block_a610(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_a610:\n.option push\n.option rvc\nc.jal .Lrecord_field_helpers_edge_a610\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_completion_provider_a38e\n");
    __builtin_unreachable();
}

/* Original0xA612..0xA614. */
REGION void tsl9_record_field_helpers_block_a612(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_a612:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_a612\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_a64e\n");
    __builtin_unreachable();
}

/* Original0xA614..0xA64E. */
REGION void tsl9_record_field_helpers_block_a614(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8bb)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff8b4)) = (uint8_t)0; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a2 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a5 = UINT32_C(0x000003e8); LIVE;
    PORT(".Lrecord_field_helpers_literal_a638:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_a3cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_a638\n.option pop\n");
    a2 = a2 >> UINT32_C(0x00000001); LIVE;
    a2 = a2 & UINT32_C(0x00000007); LIVE;
    a2 = a2 * a5; LIVE;
    a2 = a2 + UINT32_C(0x00000064); LIVE;
    PORT(".Lrecord_field_helpers_edge_a64c:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_a64c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_a586\n");
    __builtin_unreachable();
}

/* Original0xA64E..0xA658. */
REGION void tsl9_record_field_helpers_block_a64e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, -1917(a5)\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_a656:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_a656\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_a59a\n");
    __builtin_unreachable();
}

/* Original0xC7E8..0xC7F2. */
REGION void tsl9_record_field_transitions_provider_c7e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000073e)); LIVE;
    PORT(".Lrecord_field_helpers_edge_c7f0:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_c7f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c88a\n");
    __builtin_unreachable();
}

/* Original0xC7F2..0xC80C. */
REGION void tsl9_record_field_helpers_block_c7f2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    a3 = a5 & UINT32_C(0x00000003); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_edge_c80a:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_field_helpers_edge_c80a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c810\n");
    __builtin_unreachable();
}

/* Original0xC80C..0xC810. */
REGION void tsl9_record_field_helpers_block_c80c(void)
{
    REGS;
    a4 = a3 + UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC810..0xC82C. */
REGION void tsl9_record_field_helpers_block_c810(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc s0, 0x1ffff\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s0, 1816(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s0, s0, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nrem s0, s0, a4\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 1798(a4)\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_c82a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_c82a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c852\n");
    __builtin_unreachable();
}

/* Original0xC82C..0xC830. */
REGION void tsl9_record_field_helpers_block_c82c(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_c82c:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_c82c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xC830..0xC832. */
REGION void tsl9_record_field_helpers_block_c830(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_c830:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_field_helpers_edge_c830\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c852\n");
    __builtin_unreachable();
}

/* Original0xC832..0xC83C. */
REGION void tsl9_record_field_helpers_block_c832(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000008); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_c838:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_c838\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xC83C..0xC842. */
REGION void tsl9_record_field_helpers_block_c83c(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)); LIVE;
    PORT(".Lrecord_field_helpers_edge_c840:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_c840\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c852\n");
    __builtin_unreachable();
}

/* Original0xC842..0xC84C. */
REGION void tsl9_record_field_helpers_block_c842(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsnez a0, s0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_c848:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_c848\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_decode_entry_faf8\n");
    __builtin_unreachable();
}

/* Original0xC84C..0xC852. */
REGION void tsl9_record_field_helpers_block_c84c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_c84e:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_c84e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_fa7c\n");
    __builtin_unreachable();
}

/* Original0xC852..0xC856. */
REGION void tsl9_record_field_helpers_block_c852(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_edge_c854:\n.option push\n.option rvc\nc.bnez s0,.Lrecord_field_helpers_edge_c854\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c862\n");
    __builtin_unreachable();
}

/* Original0xC856..0xC860. */
REGION void tsl9_record_field_helpers_block_c856(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000006d3)); LIVE;
    PORT(".Lrecord_field_helpers_edge_c85e:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_c85e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c874\n");
    __builtin_unreachable();
}

/* Original0xC860..0xC862. */
REGION void tsl9_record_field_helpers_block_c860(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC862..0xC874. */
REGION void tsl9_record_field_helpers_block_c862(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 0(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC874..0xC884. */
REGION void tsl9_record_field_helpers_block_c874(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000006af)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_helpers_edge_c882:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_c882\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c860\n");
    __builtin_unreachable();
}

/* Original0xC884..0xC888. */
REGION void tsl9_record_field_helpers_block_c884(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_helpers_edge_c886:\n.option push\n.option rvc\nc.jal .Lrecord_field_helpers_edge_c886\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_consumer_entry_c7aa\n");
    __builtin_unreachable();
}

/* Original0xC888..0xC88A. */
REGION void tsl9_record_field_helpers_block_c888(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_c888:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_c888\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_c860\n");
    __builtin_unreachable();
}

/* Original0xC88A..0xC896. */
REGION void tsl9_record_field_helpers_block_c88a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000069b)); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_helpers_edge_c894:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_helpers_edge_c894\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_c89e\n");
    __builtin_unreachable();
}

/* Original0xC896..0xC89E. */
REGION void tsl9_record_field_helpers_block_c896(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC89E..0xC8A2. */
REGION void tsl9_record_field_helpers_block_c89e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCD4E..0xCD58. */
REGION void tsl9_feature_external_cd4e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000001d9)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCD58..0xCD6A. */
REGION void tsl9_record_field_helpers_entry_cd58(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = a5 + UINT32_C(0x000001cc); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)) = (uint8_t)a0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint8_t)a1; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xED36..0xED46. */
REGION void tsl9_record_field_transitions_provider_ed36(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lrecord_field_helpers_edge_ed44:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_ed44\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_eda4\n");
    __builtin_unreachable();
}

/* Original0xED46..0xED4E. */
REGION void tsl9_record_field_helpers_block_ed46(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000108)); LIVE;
    PORT(".Lrecord_field_helpers_edge_ed4a:\n.option push\n.option norvc\nbeq a5,a0,.Lrecord_field_helpers_edge_ed4a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_eda4\n");
    __builtin_unreachable();
}

/* Original0xED4E..0xED5C. */
REGION void tsl9_record_field_helpers_block_ed4e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_ed58:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_field_helpers_edge_ed58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_ed6a\n");
    __builtin_unreachable();
}

/* Original0xED5C..0xED5E. */
REGION void tsl9_record_field_helpers_block_ed5c(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_ed5c:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_ed5c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_ed70\n");
    __builtin_unreachable();
}

/* Original0xED5E..0xED6A. */
REGION void tsl9_record_field_helpers_block_ed5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 264(gp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xED6A..0xED6C. */
REGION void tsl9_record_field_helpers_block_ed6a(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_ed6a:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_ed6a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_ed5e\n");
    __builtin_unreachable();
}

/* Original0xED6C..0xED70. */
REGION void tsl9_record_field_helpers_block_ed6c(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_ed6c:\n.option push\n.option norvc\nbne a0,a4,.Lrecord_field_helpers_edge_ed6c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_ed5e\n");
    __builtin_unreachable();
}

/* Original0xED70..0xED78. */
REGION void tsl9_record_field_helpers_block_ed70(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsnez a0, s0\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_ed74:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_ed74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_bd5a\n");
    __builtin_unreachable();
}

/* Original0xED78..0xED82. */
REGION void tsl9_record_field_helpers_block_ed78(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000009); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_ed7e:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_ed7e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xED82..0xED9C. */
REGION void tsl9_record_field_helpers_block_ed82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a5, s0, 1\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000002); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffb); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)); LIVE;
    PORT(".Lrecord_field_helpers_edge_ed9a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_ed9a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_ed5e\n");
    __builtin_unreachable();
}

/* Original0xED9C..0xEDA2. */
REGION void tsl9_record_field_helpers_block_ed9c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_ed9e:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_ed9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xEDA2..0xEDA4. */
REGION void tsl9_record_field_helpers_block_eda2(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_eda2:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_eda2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_ed5e\n");
    __builtin_unreachable();
}

/* Original0xEDA4..0xEDA6. */
REGION void tsl9_record_field_helpers_block_eda4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEDA6..0xEDAE. */
REGION void tsl9_record_field_helpers_block_eda6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010a)); LIVE;
    PORT(".Lrecord_field_helpers_edge_edaa:\n.option push\n.option norvc\nbeq a4,a0,.Lrecord_field_helpers_edge_edaa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_edea\n");
    __builtin_unreachable();
}

/* Original0xEDAE..0xEDC2. */
REGION void tsl9_record_field_helpers_block_edae(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010a)) = (uint8_t)a0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x00000054); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a4 = a4 & UINT32_C(0x00000020); LIVE;
    PORT(".Lrecord_field_helpers_edge_edc0:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_helpers_edge_edc0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_edea\n");
    __builtin_unreachable();
}

/* Original0xEDC2..0xEDC4. */
REGION void tsl9_record_field_helpers_block_edc2(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_edc2:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_edc2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_ede4\n");
    __builtin_unreachable();
}

/* Original0xEDC4..0xEDCC. */
REGION void tsl9_record_field_helpers_block_edc4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_edc8:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_edc8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc82\n");
    __builtin_unreachable();
}

/* Original0xEDCC..0xEDDA. */
REGION void tsl9_record_field_helpers_block_edcc(void)
{
    REGS;
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000109)) = (uint8_t)a0; LIVE;
    PORT(".Lrecord_field_helpers_edge_edd8:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_edd8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_edec\n");
    __builtin_unreachable();
}

/* Original0xEDDA..0xEDE0. */
REGION void tsl9_record_field_helpers_block_edda(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEDE0..0xEDE4. */
REGION void tsl9_record_field_helpers_block_ede0(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_ede0:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_ede0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc78\n");
    __builtin_unreachable();
}

/* Original0xEDE4..0xEDEA. */
REGION void tsl9_record_field_helpers_block_ede4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000109)); LIVE;
    PORT(".Lrecord_field_helpers_edge_ede8:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_ede8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_ede0\n");
    __builtin_unreachable();
}

/* Original0xEDEA..0xEDEC. */
REGION void tsl9_record_field_helpers_block_edea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEDEC..0xEDF2. */
REGION void tsl9_record_field_helpers_block_edec(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF414..0xF41E. */
REGION void tsl9_record_field_transitions_provider_f414(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb83)); LIVE;
    PORT(".Lrecord_field_helpers_edge_f41c:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_f41c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_f454\n");
    __builtin_unreachable();
}

/* Original0xF41E..0xF43A. */
REGION void tsl9_record_field_helpers_block_f41e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffdac); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb69)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_helpers_edge_f436:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_f436\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2\n");
    __builtin_unreachable();
}

/* Original0xF43A..0xF450. */
REGION void tsl9_record_field_helpers_block_f43a(void)
{
    REGS;
    a2 = UINT32_C(0x00001000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000388); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_helpers_literal_f446:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_helpers_entry_f468\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_f446\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF450..0xF454. */
REGION void tsl9_record_field_helpers_block_f450(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_f450:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_f450\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xF454..0xF468. */
REGION void tsl9_record_field_helpers_block_f454(void)
{
    REGS;
    a2 = UINT32_C(0x00001000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000388); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_helpers_literal_f45e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_helpers_entry_f468\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_f45e\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_f466:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_f466\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_f450\n");
    __builtin_unreachable();
}

/* Original0xF468..0xF47E. */
REGION void tsl9_record_field_helpers_entry_f468(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb2f)) = (uint8_t)0; LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffd5e); LIVE;
    PORT(".Lrecord_field_helpers_edge_f47a:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_f47a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2\n");
    __builtin_unreachable();
}

/* Original0x1040E..0x1041A. */
REGION void tsl9_record_field_transitions_provider_1040e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_10416:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_10416\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_guard_828c\n");
    __builtin_unreachable();
}

/* Original0x1041A..0x1041C. */
REGION void tsl9_record_field_helpers_block_1041a(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_1041a:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_1041a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_10438\n");
    __builtin_unreachable();
}

/* Original0x1041C..0x10420. */
REGION void tsl9_record_field_helpers_block_1041c(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_1041c:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_1041c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0x10420..0x10426. */
REGION void tsl9_record_field_helpers_block_10420(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_helpers_edge_10422:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_field_helpers_edge_10422\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_10438\n");
    __builtin_unreachable();
}

/* Original0x10426..0x1042A. */
REGION void tsl9_record_field_helpers_block_10426(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_10426:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_10426\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x1042A..0x1042C. */
REGION void tsl9_record_field_helpers_block_1042a(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_1042a:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_field_helpers_edge_1042a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_10438\n");
    __builtin_unreachable();
}

/* Original0x1042C..0x10438. */
REGION void tsl9_record_field_helpers_block_1042c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_10434:\n.option push\n.option norvc\njal zero,.Lrecord_field_helpers_edge_10434\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0x10438..0x10440. */
REGION void tsl9_record_field_helpers_block_10438(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12AD0..0x12ADA. */
REGION void tsl9_record_field_transitions_provider_12ad0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -128\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 124(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_12ad6:\n.option push\n.option norvc\nbeq a0,a5,.Lrecord_field_helpers_edge_12ad6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_12aee\n");
    __builtin_unreachable();
}

/* Original0x12ADA..0x12ADC. */
REGION void tsl9_record_field_helpers_block_12ada(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_12ada:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_helpers_edge_12ada\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_12ae8\n");
    __builtin_unreachable();
}

/* Original0x12ADC..0x12AE2. */
REGION void tsl9_record_field_helpers_block_12adc(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_edge_12ade:\n.option push\n.option norvc\nbeq a0,a5,.Lrecord_field_helpers_edge_12ade\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_12b0c\n");
    __builtin_unreachable();
}

/* Original0x12AE2..0x12AE8. */
REGION void tsl9_record_field_helpers_block_12ae2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 124(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 128\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x12AE8..0x12AEC. */
REGION void tsl9_record_field_helpers_block_12ae8(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_12ae8:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_12ae8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_entry_1299e\n");
    __builtin_unreachable();
}

/* Original0x12AEC..0x12AEE. */
REGION void tsl9_record_field_helpers_block_12aec(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_12aec:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_12aec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_12ae2\n");
    __builtin_unreachable();
}

/* Original0x12AEE..0x12B00. */
REGION void tsl9_record_field_helpers_block_12aee(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_literal_12aee:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_helpers_static_data_19d08\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_12aee\n.option pop\n");
    a2 = UINT32_C(0x0000005e); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_12afc:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_12afc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_19bf0\n");
    __builtin_unreachable();
}

/* Original0x12B00..0x12B04. */
REGION void tsl9_record_field_helpers_block_12b00(void)
{
    REGS;
    a1 = UINT32_C(0x0000005e); LIVE;
    __builtin_unreachable();
}

/* Original0x12B04..0x12B0A. */
REGION void tsl9_record_field_helpers_block_12b04(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_12b06:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_12b06\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_128fe\n");
    __builtin_unreachable();
}

/* Original0x12B0A..0x12B0C. */
REGION void tsl9_record_field_helpers_block_12b0a(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_12b0a:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_12b0a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_12ae2\n");
    __builtin_unreachable();
}

/* Original0x12B0C..0x12B1E. */
REGION void tsl9_record_field_helpers_block_12b0c(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_literal_12b0c:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_helpers_static_data_19d68\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_helpers_literal_12b0c\n.option pop\n");
    a2 = UINT32_C(0x0000006a); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lrecord_field_helpers_edge_12b1a:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_12b1a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_19bf0\n");
    __builtin_unreachable();
}

/* Original0x12B1E..0x12B24. */
REGION void tsl9_record_field_helpers_block_12b1e(void)
{
    REGS;
    a1 = UINT32_C(0x0000006a); LIVE;
    PORT(".Lrecord_field_helpers_edge_12b22:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_12b22\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_12b04\n");
    __builtin_unreachable();
}

/* Original0x179FC..0x17A1C. */
REGION void tsl9_record_field_transitions_provider_179fc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, gp, 100\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 0(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000001)); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_edge_17a1a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_17a1a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17abc\n");
    __builtin_unreachable();
}

/* Original0x17A1C..0x17A28. */
REGION void tsl9_record_field_helpers_block_17a1c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000173)); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000174)); LIVE;
    PORT(".Lrecord_field_helpers_edge_17a24:\n.option push\n.option norvc\nbne a3,a0,.Lrecord_field_helpers_edge_17a24\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17a2c\n");
    __builtin_unreachable();
}

/* Original0x17A28..0x17A2C. */
REGION void tsl9_record_field_helpers_block_17a28(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17a28:\n.option push\n.option norvc\nbeq a1,a5,.Lrecord_field_helpers_edge_17a28\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17abc\n");
    __builtin_unreachable();
}

/* Original0x17A2C..0x17A2E. */
REGION void tsl9_record_field_helpers_block_17a2c(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17a2c:\n.option push\n.option rvc\nc.bnez a3,.Lrecord_field_helpers_edge_17a2c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17a32\n");
    __builtin_unreachable();
}

/* Original0x17A2E..0x17A32. */
REGION void tsl9_record_field_helpers_block_17a2e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016f)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x17A32..0x17A34. */
REGION void tsl9_record_field_helpers_block_17a32(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17a32:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_helpers_edge_17a32\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17a38\n");
    __builtin_unreachable();
}

/* Original0x17A34..0x17A38. */
REGION void tsl9_record_field_helpers_block_17a34(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000170)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x17A38..0x17A54. */
REGION void tsl9_record_field_helpers_block_17a38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s5, 0x40\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 76(s5)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a1\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\nmv a1, a4\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s4, 367(gp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s3, 368(gp)\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17A54..0x17A56. */
REGION void tsl9_record_field_helpers_block_17a54(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17a54:\n.option push\n.option rvc\nc.bnez s1,.Lrecord_field_helpers_edge_17a54\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17af0\n");
    __builtin_unreachable();
}

/* Original0x17A56..0x17A5A. */
REGION void tsl9_record_field_helpers_block_17a56(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17a56:\n.option push\n.option norvc\nbnez s0,.Lrecord_field_helpers_edge_17a56\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17b3e\n");
    __builtin_unreachable();
}

/* Original0x17A5A..0x17A66. */
REGION void tsl9_record_field_helpers_block_17a5a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000173)); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000174)); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    PORT(".Lrecord_field_helpers_edge_17a64:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_field_helpers_edge_17a64\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17ace\n");
    __builtin_unreachable();
}

/* Original0x17A66..0x17A68. */
REGION void tsl9_record_field_helpers_block_17a66(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17a66:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_helpers_edge_17a66\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17a84\n");
    __builtin_unreachable();
}

/* Original0x17A68..0x17A6E. */
REGION void tsl9_record_field_helpers_block_17a68(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_17a6a:\n.option push\n.option norvc\nbeq s4,a4,.Lrecord_field_helpers_edge_17a6a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ae6\n");
    __builtin_unreachable();
}

/* Original0x17A6E..0x17A72. */
REGION void tsl9_record_field_helpers_block_17a6e(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17a6e:\n.option push\n.option norvc\nbeq s3,a4,.Lrecord_field_helpers_edge_17a6e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ae6\n");
    __builtin_unreachable();
}

/* Original0x17A72..0x17A80. */
REGION void tsl9_record_field_helpers_block_17a72(void)
{
    REGS;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + UINT32_C(0x000003ff); LIVE;
    a5 = a5 & a4; LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffffc00); LIVE;
    __builtin_unreachable();
}

/* Original0x17A80..0x17A84. */
REGION void tsl9_record_field_helpers_block_17a80(void)
{
    REGS;
    a5 = a5 | a4; LIVE;
    PORT(".Lrecord_field_helpers_edge_17a82:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_17a82\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_17a96\n");
    __builtin_unreachable();
}

/* Original0x17A84..0x17A8A. */
REGION void tsl9_record_field_helpers_block_17a84(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_17a86:\n.option push\n.option norvc\nbeq s4,a4,.Lrecord_field_helpers_edge_17a86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ae6\n");
    __builtin_unreachable();
}

/* Original0x17A8A..0x17A96. */
REGION void tsl9_record_field_helpers_block_17a8a(void)
{
    REGS;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + UINT32_C(0x000003ff); LIVE;
    a5 = a5 & a4; LIVE;
    a5 = a5 | UINT32_C(0x00000400); LIVE;
    __builtin_unreachable();
}

/* Original0x17A96..0x17AA2. */
REGION void tsl9_record_field_helpers_block_17a96(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)); LIVE;
    a5 = a5 & UINT32_C(0x000000fc); LIVE;
    PORT(".Lrecord_field_helpers_edge_17aa0:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_17aa0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17ab4\n");
    __builtin_unreachable();
}

/* Original0x17AA2..0x17AB4. */
REGION void tsl9_record_field_helpers_block_17aa2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_helpers_edge_17ab0:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_17ab0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_queue_entry_1787c\n");
    __builtin_unreachable();
}

/* Original0x17AB4..0x17ABC. */
REGION void tsl9_record_field_helpers_block_17ab4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s1, 371(gp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 372(gp)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17ABC..0x17ACE. */
REGION void tsl9_record_field_helpers_block_17abc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17ACE..0x17AD0. */
REGION void tsl9_record_field_helpers_block_17ace(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17ace:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_helpers_edge_17ace\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17ae6\n");
    __builtin_unreachable();
}

/* Original0x17AD0..0x17AD6. */
REGION void tsl9_record_field_helpers_block_17ad0(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_17ad2:\n.option push\n.option norvc\nbeq s3,a4,.Lrecord_field_helpers_edge_17ad2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ae6\n");
    __builtin_unreachable();
}

/* Original0x17AD6..0x17AE6. */
REGION void tsl9_record_field_helpers_block_17ad6(void)
{
    REGS;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + UINT32_C(0x000003ff); LIVE;
    a5 = a5 & a4; LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffff800); LIVE;
    PORT(".Lrecord_field_helpers_edge_17ae4:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_17ae4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_17a80\n");
    __builtin_unreachable();
}

/* Original0x17AE6..0x17AF0. */
REGION void tsl9_record_field_helpers_block_17ae6(void)
{
    REGS;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + UINT32_C(0x000003ff); LIVE;
    a5 = a5 & a4; LIVE;
    PORT(".Lrecord_field_helpers_edge_17aee:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_17aee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_17a96\n");
    __builtin_unreachable();
}

/* Original0x17AF0..0x17AF4. */
REGION void tsl9_record_field_helpers_block_17af0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_17af2:\n.option push\n.option rvc\nc.bnez s0,.Lrecord_field_helpers_edge_17af2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17b82\n");
    __builtin_unreachable();
}

/* Original0x17AF4..0x17AF8. */
REGION void tsl9_record_field_helpers_block_17af4(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17af4:\n.option push\n.option norvc\nbeq s4,a5,.Lrecord_field_helpers_edge_17af4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ab4\n");
    __builtin_unreachable();
}

/* Original0x17AF8..0x17AFE. */
REGION void tsl9_record_field_helpers_block_17af8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000174)); LIVE;
    PORT(".Lrecord_field_helpers_edge_17afc:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_17afc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17b32\n");
    __builtin_unreachable();
}

/* Original0x17AFE..0x17B24. */
REGION void tsl9_record_field_helpers_block_17afe(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + UINT32_C(0x000003ff); LIVE;
    a5 = a5 & a4; LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffff800); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_helpers_edge_17b20:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_17b20\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_queue_entry_1787c\n");
    __builtin_unreachable();
}

/* Original0x17B24..0x17B32. */
REGION void tsl9_record_field_helpers_block_17b24(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 76(s5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a1, 0(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17B32..0x17B38. */
REGION void tsl9_record_field_helpers_block_17b32(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x17B38..0x17B3C. */
REGION void tsl9_record_field_helpers_block_17b38(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17b38:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_17b38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_queue_entry_17948\n");
    __builtin_unreachable();
}

/* Original0x17B3C..0x17B3E. */
REGION void tsl9_record_field_helpers_block_17b3c(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17b3c:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_17b3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_17ab4\n");
    __builtin_unreachable();
}

/* Original0x17B3E..0x17B44. */
REGION void tsl9_record_field_helpers_block_17b3e(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_helpers_edge_17b40:\n.option push\n.option norvc\nbeq s3,a5,.Lrecord_field_helpers_edge_17b40\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ab4\n");
    __builtin_unreachable();
}

/* Original0x17B44..0x17B4A. */
REGION void tsl9_record_field_helpers_block_17b44(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000173)); LIVE;
    PORT(".Lrecord_field_helpers_edge_17b48:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_helpers_edge_17b48\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_helpers_block_17b7a\n");
    __builtin_unreachable();
}

/* Original0x17B4A..0x17B6C. */
REGION void tsl9_record_field_helpers_block_17b4a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    a4 = UINT32_C(0xffff0000); LIVE;
    a4 = a4 + UINT32_C(0x000003ff); LIVE;
    a5 = a5 & a4; LIVE;
    a5 = a5 | UINT32_C(0x00000400); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_helpers_edge_17b68:\n.option push\n.option norvc\njal ra,.Lrecord_field_helpers_edge_17b68\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_queue_entry_1787c\n");
    __builtin_unreachable();
}

/* Original0x17B6C..0x17B7A. */
REGION void tsl9_record_field_helpers_block_17b6c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 76(s5)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a1, 0(s2)\n.option pop\n");
    a2 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x17B7A..0x17B82. */
REGION void tsl9_record_field_helpers_block_17b7a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_helpers_edge_17b80:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_17b80\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_17b38\n");
    __builtin_unreachable();
}

/* Original0x17B82..0x17B86. */
REGION void tsl9_record_field_helpers_block_17b82(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17b82:\n.option push\n.option norvc\nbeq s4,a5,.Lrecord_field_helpers_edge_17b82\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ab4\n");
    __builtin_unreachable();
}

/* Original0x17B86..0x17B8A. */
REGION void tsl9_record_field_helpers_block_17b86(void)
{
    REGS;
    PORT(".Lrecord_field_helpers_edge_17b86:\n.option push\n.option norvc\nbeq s3,a5,.Lrecord_field_helpers_edge_17b86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_helpers_block_17ab4\n");
    __builtin_unreachable();
}

/* Original0x17B8A..0x17B92. */
REGION void tsl9_record_field_helpers_block_17b8a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 8\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_field_helpers_edge_17b90:\n.option push\n.option rvc\nc.j .Lrecord_field_helpers_edge_17b90\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_helpers_block_17b38\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
