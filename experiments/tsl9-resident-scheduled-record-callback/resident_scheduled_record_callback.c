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

/* Two complete conditional SDK scheduled-record bodies:174B/62i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x568F6..0x56912. */
REGION void tsl9_candidate_external_flash_568f6(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000a8)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".Lresident_scheduled_record_callback_edge_5690e:\n.option push\n.option norvc\nbne a4,a0,.Lresident_scheduled_record_callback_edge_5690e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduled_record_callback_block_56916\n");
    __builtin_unreachable();
}

/* Original0x56912..0x56916. */
REGION void tsl9_resident_scheduled_record_callback_block_56912(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000a8)) = (uint32_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x56916..0x5691C. */
REGION void tsl9_resident_scheduled_record_callback_block_56916(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 288(s0)\n.option pop\n");
    PORT(".Lresident_scheduled_record_callback_edge_5691a:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduled_record_callback_edge_5691a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduled_record_callback_block_56928\n");
    __builtin_unreachable();
}

/* Original0x5691C..0x56928. */
REGION void tsl9_resident_scheduled_record_callback_block_5691c(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000080); LIVE;
    PORT(".Lresident_scheduled_record_callback_edge_56924:\n.option push\n.option norvc\njal ra,.Lresident_scheduled_record_callback_edge_56924\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56928..0x5692E. */
REGION void tsl9_resident_scheduled_record_callback_block_56928(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 68(s0)\n.option pop\n");
    PORT(".Lresident_scheduled_record_callback_edge_5692c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduled_record_callback_edge_5692c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduled_record_callback_block_5693a\n");
    __builtin_unreachable();
}

/* Original0x5692E..0x5693A. */
REGION void tsl9_resident_scheduled_record_callback_block_5692e(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000013); LIVE;
    a1 = UINT32_C(0x00000081); LIVE;
    PORT(".Lresident_scheduled_record_callback_edge_56936:\n.option push\n.option norvc\njal ra,.Lresident_scheduled_record_callback_edge_56936\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x5693A..0x56946. */
REGION void tsl9_resident_scheduled_record_callback_block_5693a(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lhu a0, 8(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x240a\n.option pop\n");
    a2 = UINT32_C(0x00000005); LIVE;
    a1 = UINT32_C(0x00000081); LIVE;
    PORT(".Lresident_scheduled_record_callback_edge_56942:\n.option push\n.option norvc\njal ra,.Lresident_scheduled_record_callback_edge_56942\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_5e3a8\n");
    __builtin_unreachable();
}

/* Original0x56946..0x56962. */
REGION void tsl9_resident_scheduled_record_callback_block_56946(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x00000514); LIVE;
    /* Conditional Xwchc: qk.c.lbu a4, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33f8\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 10(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 16(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, 84(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000005); LIVE;
    PORT(".Lresident_scheduled_record_callback_edge_5695e:\n.option push\n.option norvc\nbne a3,a4,.Lresident_scheduled_record_callback_edge_5695e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_scheduled_record_callback_block_56966\n");
    __builtin_unreachable();
}

/* Original0x56962..0x56966. */
REGION void tsl9_resident_scheduled_record_callback_block_56962(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x56966..0x56972. */
REGION void tsl9_resident_scheduled_record_callback_block_56966(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56CDC..0x56CDE. */
REGION void tsl9_candidate_external_flash_56cdc(void)
{
    REGS;
    PORT(".Lresident_scheduled_record_callback_edge_56cdc:\n.option push\n.option rvc\nc.beqz a0,.Lresident_scheduled_record_callback_edge_56cdc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduled_record_callback_block_56d0c\n");
    __builtin_unreachable();
}

/* Original0x56CDE..0x56CF0. */
REGION void tsl9_resident_scheduled_record_callback_block_56cde(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 15(a0). */
    PORT(".option push\n.option rvc\n.2byte 0x357c\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a1 = UINT32_C(0x0000003e); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_scheduled_record_callback_edge_56cee:\n.option push\n.option rvc\nc.beqz a5,.Lresident_scheduled_record_callback_edge_56cee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_scheduled_record_callback_block_56cf2\n");
    __builtin_unreachable();
}

/* Original0x56CF0..0x56CF2. */
REGION void tsl9_resident_scheduled_record_callback_block_56cf0(void)
{
    REGS;
    a1 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x56CF2..0x56CF6. */
REGION void tsl9_resident_scheduled_record_callback_block_56cf2(void)
{
    REGS;
    PORT(".Lresident_scheduled_record_callback_edge_56cf2:\n.option push\n.option norvc\njal ra,.Lresident_scheduled_record_callback_edge_56cf2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_568f6\n");
    __builtin_unreachable();
}

/* Original0x56CF6..0x56D0C. */
REGION void tsl9_resident_scheduled_record_callback_block_56cf6(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 43(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 16(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 40(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x56D0C..0x56D0E. */
REGION void tsl9_resident_scheduled_record_callback_block_56d0c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
