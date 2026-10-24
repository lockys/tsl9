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

/* Nineteen complete record/action functions:1506B/479i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9508..0x9510. */
REGION void tsl9_registered_callbacks_provider_9508(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_actions_edge_950e:\n.option push\n.option rvc\nc.jal .Lrecord_actions_edge_950e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_allocate_9410\n");
    __builtin_unreachable();
}

/* Original0x9510..0x951A. */
REGION void tsl9_record_actions_block_9510(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff9bc)) = (uint32_t)a0; LIVE;
    PORT(".Lrecord_actions_edge_9518:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_actions_edge_9518\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_9548\n");
    __builtin_unreachable();
}

/* Original0x951A..0x9548. */
REGION void tsl9_record_actions_block_951a(void)
{
    REGS;
    a5 = UINT32_C(0x000001b3); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    a4 = UINT32_C(0x00000050); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000082); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_9546:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_9546\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_arm_93aa\n");
    __builtin_unreachable();
}

/* Original0x9548..0x954E. */
REGION void tsl9_record_actions_block_9548(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x954E..0x9556. */
REGION void tsl9_record_dispatch_provider_954e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_actions_edge_9554:\n.option push\n.option rvc\nc.jal .Lrecord_actions_edge_9554\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_allocate_9410\n");
    __builtin_unreachable();
}

/* Original0x9556..0x9560. */
REGION void tsl9_record_actions_block_9556(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff976)) = (uint32_t)a0; LIVE;
    PORT(".Lrecord_actions_edge_955e:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_actions_edge_955e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_95b6\n");
    __builtin_unreachable();
}

/* Original0x9560..0x95B6. */
REGION void tsl9_record_actions_block_9560(void)
{
    REGS;
    a5 = UINT32_C(0x00000366); LIVE;
    a4 = UINT32_C(0x000002da); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint16_t)a4; LIVE;
    a5 = UINT32_C(0x00000064); LIVE;
    a4 = UINT32_C(0x00000244); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000e)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000012)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000014)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000016)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000018)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001a)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001c)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001e)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_95b4:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_95b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_arm_93aa\n");
    __builtin_unreachable();
}

/* Original0x95B6..0x95BC. */
REGION void tsl9_record_actions_block_95b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x95BC..0x95C4. */
REGION void tsl9_record_dispatch_provider_95bc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_actions_edge_95c2:\n.option push\n.option rvc\nc.jal .Lrecord_actions_edge_95c2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_allocate_9410\n");
    __builtin_unreachable();
}

/* Original0x95C4..0x95CE. */
REGION void tsl9_record_actions_block_95c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff908)) = (uint32_t)a0; LIVE;
    PORT(".Lrecord_actions_edge_95cc:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_actions_edge_95cc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_9608\n");
    __builtin_unreachable();
}

/* Original0x95CE..0x9608. */
REGION void tsl9_record_actions_block_95ce(void)
{
    REGS;
    a5 = UINT32_C(0x0000006e); LIVE;
    a4 = UINT32_C(0x00000366); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x000003d4); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint16_t)a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000e)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000012)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_9606:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_9606\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_arm_93aa\n");
    __builtin_unreachable();
}

/* Original0x9608..0x960E. */
REGION void tsl9_record_actions_block_9608(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x96A2..0x96AA. */
REGION void tsl9_record_dispatch_provider_96a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_actions_edge_96a8:\n.option push\n.option rvc\nc.jal .Lrecord_actions_edge_96a8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_allocate_9410\n");
    __builtin_unreachable();
}

/* Original0x96AA..0x96B4. */
REGION void tsl9_record_actions_block_96aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff822)) = (uint32_t)a0; LIVE;
    PORT(".Lrecord_actions_edge_96b2:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_actions_edge_96b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_9736\n");
    __builtin_unreachable();
}

/* Original0x96B4..0x9736. */
REGION void tsl9_record_actions_block_96b4(void)
{
    REGS;
    a4 = UINT32_C(0x0000024b); LIVE;
    a5 = UINT32_C(0x0000020b); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint16_t)a4; LIVE;
    a4 = UINT32_C(0x00000293); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint16_t)a4; LIVE;
    a5 = UINT32_C(0x00000032); LIVE;
    a4 = UINT32_C(0x000002ba); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000e)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000012)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000014)) = (uint16_t)a5; LIVE;
    a4 = UINT32_C(0x00000310); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001a)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000020)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x000003dc); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000018)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000024)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a4 = UINT32_C(0x00000370); LIVE;
    a5 = UINT32_C(0x00000064); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000016)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001c)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000001e)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000022)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000026)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000028)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000002a)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_9734:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_9734\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_arm_93aa\n");
    __builtin_unreachable();
}

/* Original0x9736..0x973C. */
REGION void tsl9_record_actions_block_9736(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD0A..0xBD16. */
REGION void tsl9_record_dispatch_provider_bd0a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000001f3)); LIVE;
    PORT(".Lrecord_actions_edge_bd12:\n.option push\n.option norvc\nbeq a5,a0,.Lrecord_actions_edge_bd12\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_bd38\n");
    __builtin_unreachable();
}

/* Original0xBD16..0xBD1E. */
REGION void tsl9_record_actions_block_bd16(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_actions_edge_bd1a:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_bd1a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xBD1E..0xBD24. */
REGION void tsl9_record_actions_block_bd1e(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_actions_edge_bd20:\n.option push\n.option norvc\nbeq a0,a5,.Lrecord_actions_edge_bd20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_bd32\n");
    __builtin_unreachable();
}

/* Original0xBD24..0xBD28. */
REGION void tsl9_record_actions_block_bd24(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_bd24:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_bd24\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_171de\n");
    __builtin_unreachable();
}

/* Original0xBD28..0xBD32. */
REGION void tsl9_record_actions_block_bd28(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000001e2)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xBD32..0xBD38. */
REGION void tsl9_record_actions_block_bd32(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD38..0xBD3A. */
REGION void tsl9_record_actions_block_bd38(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD5A..0xBD64. */
REGION void tsl9_record_dispatch_provider_bd5a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000001b9)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD6E..0xBD7E. */
REGION void tsl9_record_dispatch_provider_bd6e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000001a0)) = (uint8_t)a0; LIVE;
    PORT(".Lrecord_actions_edge_bd7a:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_bd7a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_actions_provider_f058\n");
    __builtin_unreachable();
}

/* Original0xBD7E..0xBD88. */
REGION void tsl9_record_actions_block_bd7e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_bd84:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_bd84\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xCC78..0xCC82. */
REGION void tsl9_record_dispatch_provider_cc78(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000002ad)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCC8C..0xCCA2. */
REGION void tsl9_record_dispatch_provider_cc8c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000293)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_actions_edge_cc9e:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_cc9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_consumer_entry_c7aa\n");
    __builtin_unreachable();
}

/* Original0xCCA2..0xCCA6. */
REGION void tsl9_record_actions_block_cca2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lrecord_actions_edge_cca4:\n.option push\n.option rvc\nc.bnez s0,.Lrecord_actions_edge_cca4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_ccae\n");
    __builtin_unreachable();
}

/* Original0xCCA6..0xCCAE. */
REGION void tsl9_record_actions_block_cca6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000027f)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xCCAE..0xCCB0. */
REGION void tsl9_record_actions_block_ccae(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_ccae:\n.option push\n.option rvc\nc.beqz a1,.Lrecord_actions_edge_ccae\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_ccb6\n");
    __builtin_unreachable();
}

/* Original0xCCB0..0xCCB6. */
REGION void tsl9_record_actions_block_ccb0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_actions_edge_ccb2:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_ccb2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xCCB6..0xCCC2. */
REGION void tsl9_record_actions_block_ccb6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lrecord_actions_edge_ccbe:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_ccbe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xD3C6..0xD3D2. */
REGION void tsl9_record_dispatch_provider_d3c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_actions_edge_d3ce:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_d3ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xD3D2..0xD3E8. */
REGION void tsl9_record_actions_block_d3d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nseqz a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffb82)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF1C2..0xF1E4. */
REGION void tsl9_feature_external_f1c2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s1, 0x1fffd\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, -561(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s2, 0x1fffd\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, -586\n.option pop\n");
    PORT(".Lrecord_actions_edge_f1e2:\n.option push\n.option rvc\nc.beqz s1,.Lrecord_actions_edge_f1e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f1fc\n");
    __builtin_unreachable();
}

/* Original0xF1E4..0xF1E8. */
REGION void tsl9_record_actions_block_f1e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 14(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF1E8..0xF1FC. */
REGION void tsl9_record_actions_block_f1e8(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a4 = a5 << UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff7); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f1fa:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_f1fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_actions_block_f214\n");
    __builtin_unreachable();
}

/* Original0xF1FC..0xF206. */
REGION void tsl9_record_actions_block_f1fc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffd9b)); LIVE;
    PORT(".Lrecord_actions_edge_f204:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_actions_edge_f204\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f238\n");
    __builtin_unreachable();
}

/* Original0xF206..0xF214. */
REGION void tsl9_record_actions_block_f206(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF214..0xF21E. */
REGION void tsl9_record_actions_block_f214(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffd\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xfffffd8b)); LIVE;
    PORT(".Lrecord_actions_edge_f21c:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_actions_edge_f21c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f254\n");
    __builtin_unreachable();
}

/* Original0xF21E..0xF222. */
REGION void tsl9_record_actions_block_f21e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 16(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF222..0xF238. */
REGION void tsl9_record_actions_block_f222(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a3\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f236:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_f236\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_actions_block_f27c\n");
    __builtin_unreachable();
}

/* Original0xF238..0xF242. */
REGION void tsl9_record_actions_block_f238(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc s1, 0x1fffd\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, -662(s1)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f240:\n.option push\n.option rvc\nc.beqz s1,.Lrecord_actions_edge_f240\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f248\n");
    __builtin_unreachable();
}

/* Original0xF242..0xF248. */
REGION void tsl9_record_actions_block_f242(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 19(s2)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f246:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_f246\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_actions_block_f1e8\n");
    __builtin_unreachable();
}

/* Original0xF248..0xF252. */
REGION void tsl9_record_actions_block_f248(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc s1, 0x1fffd\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, -685(s1)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f250:\n.option push\n.option rvc\nc.bnez s1,.Lrecord_actions_edge_f250\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f206\n");
    __builtin_unreachable();
}

/* Original0xF252..0xF254. */
REGION void tsl9_record_actions_block_f252(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f252:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_f252\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_actions_block_f214\n");
    __builtin_unreachable();
}

/* Original0xF254..0xF264. */
REGION void tsl9_record_actions_block_f254(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lrecord_actions_edge_f260:\n.option push\n.option norvc\nbeqz a5,.Lrecord_actions_edge_f260\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f3e2\n");
    __builtin_unreachable();
}

/* Original0xF264..0xF268. */
REGION void tsl9_record_actions_block_f264(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f264:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_f264\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xF268..0xF26E. */
REGION void tsl9_record_actions_block_f268(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_actions_edge_f26a:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_actions_edge_f26a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f3e2\n");
    __builtin_unreachable();
}

/* Original0xF26E..0xF27C. */
REGION void tsl9_record_actions_block_f26e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF27C..0xF286. */
REGION void tsl9_record_actions_block_f27c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffd1c)); LIVE;
    PORT(".Lrecord_actions_edge_f284:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_actions_edge_f284\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f296\n");
    __builtin_unreachable();
}

/* Original0xF286..0xF296. */
REGION void tsl9_record_actions_block_f286(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 10(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a4\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffe7); LIVE;
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 10(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF296..0xF2A0. */
REGION void tsl9_record_actions_block_f296(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffd04)); LIVE;
    PORT(".Lrecord_actions_edge_f29e:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_actions_edge_f29e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f2b6\n");
    __builtin_unreachable();
}

/* Original0xF2A0..0xF2B6. */
REGION void tsl9_record_actions_block_f2a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffcfa)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a4\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF2B6..0xF2C0. */
REGION void tsl9_record_actions_block_f2b6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffce3)); LIVE;
    PORT(".Lrecord_actions_edge_f2be:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_actions_edge_f2be\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f2d6\n");
    __builtin_unreachable();
}

/* Original0xF2C0..0xF2D6. */
REGION void tsl9_record_actions_block_f2c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffcd9)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a4\n.option pop\n");
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF2D6..0xF2E0. */
REGION void tsl9_record_actions_block_f2d6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffcbc)); LIVE;
    PORT(".Lrecord_actions_edge_f2de:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_actions_edge_f2de\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f2fa\n");
    __builtin_unreachable();
}

/* Original0xF2E0..0xF2FA. */
REGION void tsl9_record_actions_block_f2e0(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffca0)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xF2FA..0xF304. */
REGION void tsl9_record_actions_block_f2fa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffc96)); LIVE;
    PORT(".Lrecord_actions_edge_f302:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_actions_edge_f302\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f31e\n");
    __builtin_unreachable();
}

/* Original0xF304..0xF31E. */
REGION void tsl9_record_actions_block_f304(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc8c)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a4\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffc7); LIVE;
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF31E..0xF332. */
REGION void tsl9_record_actions_block_f31e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffc76)); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc6d)); LIVE;
    PORT(".Lrecord_actions_edge_f32e:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_actions_edge_f32e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f356\n");
    __builtin_unreachable();
}

/* Original0xF332..0xF336. */
REGION void tsl9_record_actions_block_f332(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f332:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_f332\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xF336..0xF33C. */
REGION void tsl9_record_actions_block_f336(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_actions_edge_f338:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_actions_edge_f338\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f356\n");
    __builtin_unreachable();
}

/* Original0xF33C..0xF356. */
REGION void tsl9_record_actions_block_f33c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a4 = a5 << UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffdf); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF356..0xF360. */
REGION void tsl9_record_actions_block_f356(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc3b)); LIVE;
    PORT(".Lrecord_actions_edge_f35e:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_actions_edge_f35e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f38e\n");
    __builtin_unreachable();
}

/* Original0xF360..0xF366. */
REGION void tsl9_record_actions_block_f360(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_actions_edge_f362:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_actions_edge_f362\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f36e\n");
    __builtin_unreachable();
}

/* Original0xF366..0xF36E. */
REGION void tsl9_record_actions_block_f366(void)
{
    REGS;
    a0 = UINT32_C(0x000003e8); LIVE;
    PORT(".Lrecord_actions_edge_f36a:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_f36a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_actions_provider_de82\n");
    __builtin_unreachable();
}

/* Original0xF36E..0xF38E. */
REGION void tsl9_record_actions_block_f36e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000007); LIVE;
    a4 = a5 << UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff1); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc0b)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xF38E..0xF398. */
REGION void tsl9_record_actions_block_f38e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc08)); LIVE;
    PORT(".Lrecord_actions_edge_f396:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_actions_edge_f396\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f400\n");
    __builtin_unreachable();
}

/* Original0xF398..0xF3A0. */
REGION void tsl9_record_actions_block_f398(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_actions_edge_f39e:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_actions_edge_f39e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f3b0\n");
    __builtin_unreachable();
}

/* Original0xF3A0..0xF3A8. */
REGION void tsl9_record_actions_block_f3a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_actions_edge_f3a6:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_actions_edge_f3a6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f3b0\n");
    __builtin_unreachable();
}

/* Original0xF3A8..0xF3B0. */
REGION void tsl9_record_actions_block_f3a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlb a5, 10(s0)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f3ac:\n.option push\n.option norvc\nbgez a5,.Lrecord_actions_edge_f3ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f400\n");
    __builtin_unreachable();
}

/* Original0xF3B0..0xF3D0. */
REGION void tsl9_record_actions_block_f3b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffb); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 10(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 10(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF3D0..0xF3E2. */
REGION void tsl9_record_actions_block_f3d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lrecord_actions_edge_f3de:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f3de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xF3E2..0xF3EC. */
REGION void tsl9_record_actions_block_f3e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffd\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xfffffbc2)); LIVE;
    PORT(".Lrecord_actions_edge_f3ea:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_actions_edge_f3ea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f3f2\n");
    __builtin_unreachable();
}

/* Original0xF3EC..0xF3F2. */
REGION void tsl9_record_actions_block_f3ec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 21(s2)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f3f0:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_f3f0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_actions_block_f222\n");
    __builtin_unreachable();
}

/* Original0xF3F2..0xF3FE. */
REGION void tsl9_record_actions_block_f3f2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbaa)); LIVE;
    PORT(".Lrecord_actions_edge_f3fa:\n.option push\n.option norvc\nbnez a5,.Lrecord_actions_edge_f3fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f26e\n");
    __builtin_unreachable();
}

/* Original0xF3FE..0xF400. */
REGION void tsl9_record_actions_block_f3fe(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f3fe:\n.option push\n.option rvc\nc.j .Lrecord_actions_edge_f3fe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_actions_block_f27c\n");
    __builtin_unreachable();
}

/* Original0xF400..0xF402. */
REGION void tsl9_record_actions_block_f400(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f400:\n.option push\n.option rvc\nc.bnez s1,.Lrecord_actions_edge_f400\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f3d0\n");
    __builtin_unreachable();
}

/* Original0xF402..0xF406. */
REGION void tsl9_record_actions_block_f402(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f402:\n.option push\n.option norvc\nbnez s3,.Lrecord_actions_edge_f402\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_actions_block_f3d0\n");
    __builtin_unreachable();
}

/* Original0xF406..0xF414. */
REGION void tsl9_record_actions_block_f406(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF672..0xF67E. */
REGION void tsl9_record_dispatch_provider_f672(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff926)) = (uint8_t)a0; LIVE;
    PORT(".Lrecord_actions_edge_f67a:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f67a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xF688..0xF6B0. */
REGION void tsl9_record_dispatch_provider_f688(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a0\n.option pop\n");
    PORT(".Lrecord_actions_literal_f68c:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_actions_provider_f4d0\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_actions_literal_f68c\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff90b)); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffd\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffff901); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff8fd); LIVE;
    PORT(".Lrecord_actions_edge_f6ac:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f6ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_actions_provider_f47e\n");
    __builtin_unreachable();
}

/* Original0xF6BA..0xF6E2. */
REGION void tsl9_record_dispatch_provider_f6ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a0\n.option pop\n");
    PORT(".Lrecord_actions_literal_f6be:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_actions_provider_f4d0\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_actions_literal_f6be\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8d7)); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffd\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffff8d1); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff8cb); LIVE;
    PORT(".Lrecord_actions_edge_f6de:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f6de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_actions_provider_f47e\n");
    __builtin_unreachable();
}

/* Original0xF6EC..0xF714. */
REGION void tsl9_record_dispatch_provider_f6ec(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a0\n.option pop\n");
    PORT(".Lrecord_actions_literal_f6f0:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_actions_provider_f578\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_actions_literal_f6f0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff8ac)); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffd\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffff8a2); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff89e); LIVE;
    PORT(".Lrecord_actions_edge_f710:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f710\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_actions_provider_f47e\n");
    __builtin_unreachable();
}

/* Original0xF71E..0xF746. */
REGION void tsl9_record_dispatch_provider_f71e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a3, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a0\n.option pop\n");
    PORT(".Lrecord_actions_literal_f722:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_actions_provider_f578\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_actions_literal_f722\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff878)); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffd\n.option pop\n");
    a1 = a1 + UINT32_C(0xfffff872); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff86c); LIVE;
    PORT(".Lrecord_actions_edge_f742:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f742\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_actions_provider_f47e\n");
    __builtin_unreachable();
}

/* Original0xF750..0xF772. */
REGION void tsl9_record_dispatch_provider_f750(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff842)) = (uint8_t)a0; LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffa6c); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f76e:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_f76e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2\n");
    __builtin_unreachable();
}

/* Original0xF772..0xF774. */
REGION void tsl9_record_actions_block_f772(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f772:\n.option push\n.option rvc\nc.beqz s1,.Lrecord_actions_edge_f772\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f782\n");
    __builtin_unreachable();
}

/* Original0xF774..0xF782. */
REGION void tsl9_record_actions_block_f774(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_f77e:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f77e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xF782..0xF78C. */
REGION void tsl9_record_actions_block_f782(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF796..0xF7B8. */
REGION void tsl9_record_dispatch_provider_f796(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffc\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000007fb)) = (uint8_t)a0; LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffa26); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_actions_edge_f7b4:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_f7b4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_f1c2\n");
    __builtin_unreachable();
}

/* Original0xF7B8..0xF7BA. */
REGION void tsl9_record_actions_block_f7b8(void)
{
    REGS;
    PORT(".Lrecord_actions_edge_f7b8:\n.option push\n.option rvc\nc.beqz s1,.Lrecord_actions_edge_f7b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_actions_block_f7c8\n");
    __builtin_unreachable();
}

/* Original0xF7BA..0xF7C8. */
REGION void tsl9_record_actions_block_f7ba(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_f7c4:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f7c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xF7C8..0xF7D2. */
REGION void tsl9_record_actions_block_f7c8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF97C..0xF988. */
REGION void tsl9_record_dispatch_provider_f97c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000115)) = (uint8_t)a0; LIVE;
    PORT(".Lrecord_actions_edge_f984:\n.option push\n.option norvc\njal ra,.Lrecord_actions_edge_f984\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xF988..0xF992. */
REGION void tsl9_record_actions_block_f988(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_actions_edge_f98e:\n.option push\n.option norvc\njal zero,.Lrecord_actions_edge_f98e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}
