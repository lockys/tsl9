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

/* Eight complete timed-record functions:418B/138i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xBD46..0xBD50. */
REGION void tsl9_record_helpers_provider_bd46(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = a0 + UINT32_C(0x000001cb); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD50..0xBD5A. */
REGION void tsl9_record_helpers_provider_bd50(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = a0 + UINT32_C(0x000001c0); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD64..0xBD6E. */
REGION void tsl9_record_dispatch_provider_bd64(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000001af)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEDF2..0xEE00. */
REGION void tsl9_record_helpers_provider_edf2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000009); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lrecord_continuations_edge_edfc:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_edfc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xEE00..0xEE2A. */
REGION void tsl9_record_continuations_block_ee00(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000184); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint8_t)a5; LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a4 = a4 & UINT32_C(0xfffffffb); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_continuations_edge_ee26:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_ee26\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xEE2A..0xEE30. */
REGION void tsl9_record_continuations_block_ee2a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEE30..0xEE3C. */
REGION void tsl9_record_helpers_provider_ee30(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_continuations_edge_ee38:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_ee38\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_edf2\n");
    __builtin_unreachable();
}

/* Original0xEE3C..0xEE58. */
REGION void tsl9_record_continuations_block_ee3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000148)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000142)); LIVE;
    PORT(".option push\n.option norvc\nauipc s0, 0x1fffd\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 312\n.option pop\n");
    PORT(".Lrecord_continuations_edge_ee54:\n.option push\n.option norvc\nbltu a5,a4,.Lrecord_continuations_edge_ee54\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_continuations_block_ee7e\n");
    __builtin_unreachable();
}

/* Original0xEE58..0xEE64. */
REGION void tsl9_record_continuations_block_ee58(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000012e)) = (uint16_t)0; LIVE;
    PORT(".Lrecord_continuations_edge_ee60:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_ee60\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_bd50\n");
    __builtin_unreachable();
}

/* Original0xEE64..0xEE68. */
REGION void tsl9_record_continuations_block_ee64(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xEE68..0xEE7E. */
REGION void tsl9_record_continuations_block_ee68(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 0(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x00000112)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEE7E..0xEE98. */
REGION void tsl9_record_continuations_block_ee7e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a4, 4(s0)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a5 = a5 + a4; LIVE;
    a2 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_continuations_literal_ee8c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_ee30\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_continuations_literal_ee8c\n.option pop\n");
    PORT(".Lrecord_continuations_edge_ee94:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_ee94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xEE98..0xEE9A. */
REGION void tsl9_record_continuations_block_ee98(void)
{
    REGS;
    PORT(".Lrecord_continuations_edge_ee98:\n.option push\n.option rvc\nc.j .Lrecord_continuations_edge_ee98\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_continuations_block_ee68\n");
    __builtin_unreachable();
}

/* Original0xEE9A..0xEEA2. */
REGION void tsl9_record_helpers_provider_ee9a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_continuations_edge_ee9e:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_ee9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_bd50\n");
    __builtin_unreachable();
}

/* Original0xEEA2..0xEEAE. */
REGION void tsl9_record_continuations_block_eea2(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000000); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_continuations_edge_eeac:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_continuations_edge_eeac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_continuations_block_eed8\n");
    __builtin_unreachable();
}

/* Original0xEEAE..0xEEC6. */
REGION void tsl9_record_continuations_block_eeae(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_continuations_literal_eeb2:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_ee30\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_continuations_literal_eeb2\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000ca)) = (uint32_t)0; LIVE;
    PORT(".Lrecord_continuations_edge_eec2:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_eec2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xEEC6..0xEED6. */
REGION void tsl9_record_continuations_block_eec6(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000c2)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_continuations_edge_eed2:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_eed2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_edf2\n");
    __builtin_unreachable();
}

/* Original0xEED6..0xEED8. */
REGION void tsl9_record_continuations_block_eed6(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xEED8..0xEEE0. */
REGION void tsl9_record_continuations_block_eed8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEEE0..0xEEE8. */
REGION void tsl9_record_helpers_provider_eee0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".Lrecord_continuations_edge_eee6:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_continuations_edge_eee6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_continuations_block_ef5c\n");
    __builtin_unreachable();
}

/* Original0xEEE8..0xEEF4. */
REGION void tsl9_record_continuations_block_eee8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000000a4)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_continuations_edge_eef0:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_eef0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_edf2\n");
    __builtin_unreachable();
}

/* Original0xEEF4..0xEF00. */
REGION void tsl9_record_continuations_block_eef4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000099)); LIVE;
    PORT(".option push\n.option rvc\nli s0, 11\n.option pop\n");
    PORT(".Lrecord_continuations_edge_eefe:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_continuations_edge_eefe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_continuations_block_ef04\n");
    __builtin_unreachable();
}

/* Original0xEF00..0xEF04. */
REGION void tsl9_record_continuations_block_ef00(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s0, 50\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEF04..0xEF16. */
REGION void tsl9_record_continuations_block_ef04(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s0\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_continuations_literal_ef0a:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_edf2\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_continuations_literal_ef0a\n.option pop\n");
    PORT(".Lrecord_continuations_edge_ef12:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_ef12\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xEF16..0xEF2E. */
REGION void tsl9_record_continuations_block_ef16(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000078)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000006a)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_continuations_edge_ef2c:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_continuations_edge_ef2c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_continuations_block_ef56\n");
    __builtin_unreachable();
}

/* Original0xEF2E..0xEF3C. */
REGION void tsl9_record_continuations_block_ef2e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000005f)); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    PORT(".Lrecord_continuations_edge_ef3a:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_continuations_edge_ef3a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_continuations_block_ef40\n");
    __builtin_unreachable();
}

/* Original0xEF3C..0xEF40. */
REGION void tsl9_record_continuations_block_ef3c(void)
{
    REGS;
    a2 = UINT32_C(0x000000c8); LIVE;
    __builtin_unreachable();
}

/* Original0xEF40..0xEF42. */
REGION void tsl9_record_continuations_block_ef40(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0xEF42..0xEF56. */
REGION void tsl9_record_continuations_block_ef42(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_continuations_literal_ef48:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_helpers_provider_eee0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_continuations_literal_ef48\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_continuations_edge_ef52:\n.option push\n.option norvc\njal zero,.Lrecord_continuations_edge_ef52\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xEF56..0xEF5C. */
REGION void tsl9_record_continuations_block_ef56(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv a2, s0\n.option pop\n");
    PORT(".Lrecord_continuations_edge_ef5a:\n.option push\n.option rvc\nc.j .Lrecord_continuations_edge_ef5a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_continuations_block_ef42\n");
    __builtin_unreachable();
}

/* Original0xEF5C..0xEF60. */
REGION void tsl9_record_continuations_block_ef5c(void)
{
    REGS;
    PORT(".Lrecord_continuations_edge_ef5c:\n.option push\n.option norvc\njal ra,.Lrecord_continuations_edge_ef5c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_helpers_provider_bd46\n");
    __builtin_unreachable();
}

/* Original0xEF60..0xEF6C. */
REGION void tsl9_record_continuations_block_ef60(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEF6C..0xEF76. */
REGION void tsl9_record_continuations_provider_ef6c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000020)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
