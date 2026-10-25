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

/* Six complete notification support functions:216B/71i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xB664..0xB67A. */
REGION void tsl9_selector_notifications_provider_b664(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffbcf)); LIVE;
    a0 = a0 & UINT32_C(0x00000060); LIVE;
    a0 = a0 + UINT32_C(0xffffffc0); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB6A8..0xB6BC. */
REGION void tsl9_selector_notifications_provider_b6a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffb8c)); LIVE;
    a0 = a0 & UINT32_C(0x00000030); LIVE;
    a0 = a0 + UINT32_C(0xffffffe0); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCC60..0xCC78. */
REGION void tsl9_record_dispatch_provider_cc60(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = a5 + UINT32_C(0x000002c4); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint8_t)a4; LIVE;
    a4 = UINT32_C(0x00000300); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCCC2..0xCCCC. */
REGION void tsl9_selector_notifications_provider_ccc2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000264)); LIVE;
    PORT(".Lnotification_support_edge_ccca:\n.option push\n.option rvc\nc.beqz a5,.Lnotification_support_edge_ccca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_notification_support_block_cce2\n");
    __builtin_unreachable();
}

/* Original0xCCCC..0xCCD6. */
REGION void tsl9_notification_support_block_cccc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lnotification_support_edge_ccd4:\n.option push\n.option rvc\nc.jal .Lnotification_support_edge_ccd4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_provider_cc8c\n");
    __builtin_unreachable();
}

/* Original0xCCD6..0xCCE2. */
REGION void tsl9_notification_support_block_ccd6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lnotification_support_edge_ccde:\n.option push\n.option norvc\njal zero,.Lnotification_support_edge_ccde\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f688\n");
    __builtin_unreachable();
}

/* Original0xCCE2..0xCCEC. */
REGION void tsl9_notification_support_block_cce2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000243)); LIVE;
    PORT(".Lnotification_support_edge_ccea:\n.option push\n.option rvc\nc.beqz a5,.Lnotification_support_edge_ccea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_notification_support_block_ccf4\n");
    __builtin_unreachable();
}

/* Original0xCCEC..0xCCF4. */
REGION void tsl9_notification_support_block_ccec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000239)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xCCF4..0xCCF6. */
REGION void tsl9_notification_support_block_ccf4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCCF6..0xCCFE. */
REGION void tsl9_selector_notifications_provider_ccf6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lnotification_support_edge_ccfa:\n.option push\n.option norvc\njal ra,.Lnotification_support_edge_ccfa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xCCFE..0xCD00. */
REGION void tsl9_notification_support_block_ccfe(void)
{
    REGS;
    PORT(".Lnotification_support_edge_ccfe:\n.option push\n.option rvc\nc.beqz a0,.Lnotification_support_edge_ccfe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_notification_support_block_cd3e\n");
    __builtin_unreachable();
}

/* Original0xCD00..0xCD14. */
REGION void tsl9_notification_support_block_cd00(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lnotification_support_edge_cd10:\n.option push\n.option norvc\nbne a5,a4,.Lnotification_support_edge_cd10\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_notification_support_block_cd38\n");
    __builtin_unreachable();
}

/* Original0xCD14..0xCD24. */
REGION void tsl9_notification_support_block_cd14(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lnotification_support_edge_cd20:\n.option push\n.option norvc\nbltu a4,a5,.Lnotification_support_edge_cd20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_notification_support_block_cd38\n");
    __builtin_unreachable();
}

/* Original0xCD24..0xCD38. */
REGION void tsl9_notification_support_block_cd24(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000201)); LIVE;
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000001f5)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xCD38..0xCD3E. */
REGION void tsl9_notification_support_block_cd38(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCD3E..0xCD44. */
REGION void tsl9_notification_support_block_cd3e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lnotification_support_edge_cd42:\n.option push\n.option rvc\nc.j .Lnotification_support_edge_cd42\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_provider_ccc2\n");
    __builtin_unreachable();
}

/* Original0xFE08..0xFE10. */
REGION void tsl9_record_dispatch_provider_fe08(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lnotification_support_edge_fe0c:\n.option push\n.option norvc\njal ra,.Lnotification_support_edge_fe0c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a9de\n");
    __builtin_unreachable();
}

/* Original0xFE10..0xFE1C. */
REGION void tsl9_notification_support_block_fe10(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lnotification_support_edge_fe18:\n.option push\n.option norvc\njal zero,.Lnotification_support_edge_fe18\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_fdf6\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
