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

/* One complete public-SDK task registration body:48B/16i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43C4E..0x43C5E. */
REGION void tsl9_candidate_process_event_register_43c4e(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = a4 + UINT32_C(0x0000019c); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x331c\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a3, 2(a4). */
    PORT(".option push\n.option rvc\n.2byte 0x2334\n.option pop\n");
    PORT(".Lresident_task_registration_edge_43c5a:\n.option push\n.option norvc\nbleu a3,a5,.Lresident_task_registration_edge_43c5a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_task_registration_block_43c78\n");
    __builtin_unreachable();
}

/* Original0x43C5E..0x43C74. */
REGION void tsl9_resident_task_registration_block_43c5e(void)
{
    REGS;
    a3 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x000001c4)); LIVE;
    a2 = a5 + UINT32_C(0x00000001); LIVE;
    /* Conditional Xwchc: qk.c.sb a2, 1(a4). */
    PORT(".option push\n.option rvc\n.2byte 0xb310\n.option pop\n");
    a4 = a5 << UINT32_C(0x00000002); LIVE;
    a4 = a4 + a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0x43C74..0x43C78. */
REGION void tsl9_resident_task_registration_block_43c74(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43C78..0x43C7E. */
REGION void tsl9_resident_task_registration_block_43c78(void)
{
    REGS;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lresident_task_registration_edge_43c7c:\n.option push\n.option rvc\nc.j .Lresident_task_registration_edge_43c7c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_task_registration_block_43c74\n");
    __builtin_unreachable();
}
