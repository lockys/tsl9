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

/* Five complete public-SDK state8/provider bodies:1432B/492i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43728..0x43758. */
REGION void tsl9_candidate_tmos_start_task_43728(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x40024\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s4, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nsw zero, 524(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000019d)); LIVE;
    PORT(".Lresident_state8_service_edge_43754:\n.option push\n.option norvc\nbleu a5,a0,.Lresident_state8_service_edge_43754\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_43764\n");
    __builtin_unreachable();
}

/* Original0x43758..0x43764. */
REGION void tsl9_resident_state8_service_block_43758(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlw s7, 480(a5)\n.option pop\n");
    PORT(".Lresident_state8_service_edge_43760:\n.option push\n.option norvc\nbnez s7,.Lresident_state8_service_edge_43760\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_4376e\n");
    __builtin_unreachable();
}

/* Original0x43764..0x4376E. */
REGION void tsl9_resident_state8_service_block_43764(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s4, 524(a5)\n.option pop\n");
    PORT(".Lresident_state8_service_edge_4376c:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_4376c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_437b2\n");
    __builtin_unreachable();
}

/* Original0x4376E..0x437AA. */
REGION void tsl9_resident_state8_service_block_4376e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s2, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, 564\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s5, a1\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s6, 4(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu a1, 8(s2)\n.option pop\n");
    a5 = UINT32_C(0xfe364000); LIVE;
    a5 = a5 + UINT32_C(0xfffffc80); LIVE;
    PORT(".option push\n.option rvc\nadd s6, s6, a5\n.option pop\n");
    a5 = a1 * a2; LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a2\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, a1, a2\n.option pop\n");
    a0 = a5 + UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a0, a5\n.option pop\n");
    a2 = UINT32_C(0x00000640); LIVE;
    a1 = a1 + a5; LIVE;
    PORT(".Lresident_state8_service_edge_437a6:\n.option push\n.option norvc\njal ra,.Lresident_state8_service_edge_437a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x437AA..0x437AE. */
REGION void tsl9_resident_state8_service_block_437aa(void)
{
    REGS;
    PORT(".Lresident_state8_service_edge_437aa:\n.option push\n.option norvc\nbleu a0,s6,.Lresident_state8_service_edge_437aa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_437ca\n");
    __builtin_unreachable();
}

/* Original0x437AE..0x437B2. */
REGION void tsl9_resident_state8_service_block_437ae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s4, 524(s1)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x437B2..0x437B4. */
REGION void tsl9_resident_state8_service_block_437b2(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x437B4..0x437CA. */
REGION void tsl9_resident_state8_service_block_437b4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x437CA..0x437CC. */
REGION void tsl9_resident_state8_service_block_437ca(void)
{
    REGS;
    PORT(".option push\n.option rvc\njalr s7\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x437CC..0x437EE. */
REGION void tsl9_resident_state8_service_block_437cc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a1, 8(s2)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    a2 = UINT32_C(0x00000640); LIVE;
    PORT(".option push\n.option norvc\nmul a5, a1, s3\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nmulhu a1, a1, s3\n.option pop\n");
    a0 = a5 + UINT32_C(0x00000320); LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a0, a5\n.option pop\n");
    a1 = a1 + a5; LIVE;
    PORT(".Lresident_state8_service_edge_437ea:\n.option push\n.option norvc\njal ra,.Lresident_state8_service_edge_437ea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_external_flash_6df1a\n");
    __builtin_unreachable();
}

/* Original0x437EE..0x437FC. */
REGION void tsl9_resident_state8_service_block_437ee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nadd a5, a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a4, 4(s2)\n.option pop\n");
    PORT(".Lresident_state8_service_edge_437f8:\n.option push\n.option norvc\nbltu a5,a0,.Lresident_state8_service_edge_437f8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_43800\n");
    __builtin_unreachable();
}

/* Original0x437FC..0x43800. */
REGION void tsl9_resident_state8_service_block_437fc(void)
{
    REGS;
    PORT(".Lresident_state8_service_edge_437fc:\n.option push\n.option norvc\nbltu a5,a4,.Lresident_state8_service_edge_437fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_43804\n");
    __builtin_unreachable();
}

/* Original0x43800..0x43804. */
REGION void tsl9_resident_state8_service_block_43800(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub s1, a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43804..0x43810. */
REGION void tsl9_resident_state8_service_block_43804(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s5\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lresident_state8_service_literal_43808:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_timer_lookup_20000314\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_service_literal_43808\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43810..0x43812. */
REGION void tsl9_resident_state8_service_block_43810(void)
{
    REGS;
    PORT(".Lresident_state8_service_edge_43810:\n.option push\n.option rvc\nc.beqz a0,.Lresident_state8_service_edge_43810\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_43820\n");
    __builtin_unreachable();
}

/* Original0x43812..0x43814. */
REGION void tsl9_resident_state8_service_block_43812(void)
{
    REGS;
    PORT(".option push\n.option rvc\nsw s1, 8(a0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43814..0x43820. */
REGION void tsl9_resident_state8_service_block_43814(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s4, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_service_edge_4381e:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_4381e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_437b4\n");
    __builtin_unreachable();
}

/* Original0x43820..0x43832. */
REGION void tsl9_resident_state8_service_block_43820(void)
{
    REGS;
    PORT(".option push\n.option norvc\nori a1, s0, -256\n.option pop\n");
    a1 = a1 << UINT32_C(0x00000010); LIVE;
    a1 = a1 >> UINT32_C(0x00000010); LIVE;
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_state8_service_literal_4382a:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_service_literal_4382a\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43832..0x43834. */
REGION void tsl9_resident_state8_service_block_43832(void)
{
    REGS;
    PORT(".Lresident_state8_service_edge_43832:\n.option push\n.option rvc\nc.bnez a0,.Lresident_state8_service_edge_43832\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_43846\n");
    __builtin_unreachable();
}

/* Original0x43834..0x4383E. */
REGION void tsl9_resident_state8_service_block_43834(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000220)); LIVE;
    PORT(".Lresident_state8_service_edge_4383c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_service_edge_4383c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_43764\n");
    __builtin_unreachable();
}

/* Original0x4383E..0x43844. */
REGION void tsl9_resident_state8_service_block_4383e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43844..0x43846. */
REGION void tsl9_resident_state8_service_block_43844(void)
{
    REGS;
    PORT(".Lresident_state8_service_edge_43844:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_43844\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_43764\n");
    __builtin_unreachable();
}

/* Original0x43846..0x43850. */
REGION void tsl9_resident_state8_service_block_43846(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000001e8)); LIVE;
    PORT(".Lresident_state8_service_edge_4384e:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_service_edge_4384e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_4386c\n");
    __builtin_unreachable();
}

/* Original0x43850..0x43854. */
REGION void tsl9_resident_state8_service_block_43850(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000001e8)) = (uint32_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0x43854..0x4386A. */
REGION void tsl9_resident_state8_service_block_43854(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option rvc\nsw s1, 8(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh s5, 2(a0)\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb s0, 0(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xa100\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a5, 1(a0). */
    PORT(".option push\n.option rvc\n.2byte 0xb11c\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint32_t)0; LIVE;
    PORT(".Lresident_state8_service_edge_43868:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_43868\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_43814\n");
    __builtin_unreachable();
}

/* Original0x4386A..0x4386C. */
REGION void tsl9_resident_state8_service_block_4386a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x4386C..0x43870. */
REGION void tsl9_resident_state8_service_block_4386c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lresident_state8_service_edge_4386e:\n.option push\n.option rvc\nc.bnez a4,.Lresident_state8_service_edge_4386e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_4386a\n");
    __builtin_unreachable();
}

/* Original0x43870..0x43874. */
REGION void tsl9_resident_state8_service_block_43870(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_state8_service_edge_43872:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_43872\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_43854\n");
    __builtin_unreachable();
}

/* Original0x63C54..0x63C5E. */
REGION void tsl9_candidate_register_config_63c54(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000050c)); LIVE;
    PORT(".Lresident_state8_service_edge_63c5c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_service_edge_63c5c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_63c76\n");
    __builtin_unreachable();
}

/* Original0x63C5E..0x63C76. */
REGION void tsl9_resident_state8_service_block_63c5e(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nlw a6, 8(a5)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nor a4, a4, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000000c)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x63C76..0x63C98. */
REGION void tsl9_resident_state8_service_block_63c76(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option norvc\nlbu a6, 1296(a4)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x20003000); LIVE;
    a3 = a0 & UINT32_C(0x00000002); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    PORT(".option push\n.option norvc\nandi a6, a6, 1\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000514); LIVE;
    PORT(".Lresident_state8_service_edge_63c96:\n.option push\n.option rvc\nc.beqz a3,.Lresident_state8_service_edge_63c96\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_63cfa\n");
    __builtin_unreachable();
}

/* Original0x63C98..0x63CDC. */
REGION void tsl9_resident_state8_service_block_63c98(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a0 = UINT32_C(0xffffd000); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    a3 = a3 & a0; LIVE;
    a0 = UINT32_C(0x00002000); LIVE;
    a3 = a3 | a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00090000); LIVE;
    a3 = a3 + UINT32_C(0x00000086); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x08302000); LIVE;
    a3 = a3 + UINT32_C(0xfffffff1); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00031000); LIVE;
    a3 = a3 + UINT32_C(0x00000619); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00003000); LIVE;
    a3 = a3 + UINT32_C(0xfffff8de); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000028)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x01006000); LIVE;
    a3 = a3 + UINT32_C(0x00000310); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x003fa000); LIVE;
    PORT(".Lresident_state8_service_edge_63cd8:\n.option push\n.option norvc\nbnez a6,.Lresident_state8_service_edge_63cd8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_63ce0\n");
    __builtin_unreachable();
}

/* Original0x63CDC..0x63CE0. */
REGION void tsl9_resident_state8_service_block_63cdc(void)
{
    REGS;
    a3 = UINT32_C(0x0034a000); LIVE;
    __builtin_unreachable();
}

/* Original0x63CE0..0x63CEC. */
REGION void tsl9_resident_state8_service_block_63ce0(void)
{
    REGS;
    a3 = a3 + UINT32_C(0x000004df); LIVE;
    a1 = a1 << UINT32_C(0x00000007); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a3; LIVE;
    a1 = a1 + UINT32_C(0x00000364); LIVE;
    __builtin_unreachable();
}

/* Original0x63CEC..0x63CF0. */
REGION void tsl9_resident_state8_service_block_63cec(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_state8_service_edge_63cee:\n.option push\n.option rvc\nc.beqz a2,.Lresident_state8_service_edge_63cee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_63cf4\n");
    __builtin_unreachable();
}

/* Original0x63CF0..0x63CF4. */
REGION void tsl9_resident_state8_service_block_63cf0(void)
{
    REGS;
    a2 = a2 << UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000010)) = (uint32_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0x63CF4..0x63CFA. */
REGION void tsl9_resident_state8_service_block_63cf4(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000004)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63CFA..0x63D2E. */
REGION void tsl9_resident_state8_service_block_63cfa(void)
{
    REGS;
    a3 = UINT32_C(0x00090000); LIVE;
    a3 = a3 + UINT32_C(0x00000083); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000020)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x08102000); LIVE;
    a3 = a3 + UINT32_C(0xfffff901); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000014)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00031000); LIVE;
    a3 = a3 + UINT32_C(0x00000624); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000018)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x00003000); LIVE;
    a3 = a3 + UINT32_C(0xfffff8be); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000028)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0x01006000); LIVE;
    a3 = a3 + UINT32_C(0x00000310); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000024)) = (uint32_t)a3; LIVE;
    PORT(".Lresident_state8_service_edge_63d2a:\n.option push\n.option norvc\nbeqz a6,.Lresident_state8_service_edge_63d2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_63d56\n");
    __builtin_unreachable();
}

/* Original0x63D2E..0x63D36. */
REGION void tsl9_resident_state8_service_block_63d2e(void)
{
    REGS;
    a3 = UINT32_C(0x003fa000); LIVE;
    a3 = a3 + UINT32_C(0x000002ce); LIVE;
    __builtin_unreachable();
}

/* Original0x63D36..0x63D4C. */
REGION void tsl9_resident_state8_service_block_63d36(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000010)) = (uint32_t)a3; LIVE;
    a3 = UINT32_C(0xffffd000); LIVE;
    PORT(".option push\n.option norvc\naddi a6, a3, -1\n.option pop\n");
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nli a7, 1\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nand a3, a3, a6\n.option pop\n");
    PORT(".Lresident_state8_service_edge_63d48:\n.option push\n.option norvc\nbne a0,a7,.Lresident_state8_service_edge_63d48\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_63d60\n");
    __builtin_unreachable();
}

/* Original0x63D4C..0x63D50. */
REGION void tsl9_resident_state8_service_block_63d4c(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a1 = a1 << UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0x63D50..0x63D56. */
REGION void tsl9_resident_state8_service_block_63d50(void)
{
    REGS;
    a1 = a1 + UINT32_C(0x0000003c); LIVE;
    PORT(".Lresident_state8_service_edge_63d54:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_63d54\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_63cec\n");
    __builtin_unreachable();
}

/* Original0x63D56..0x63D60. */
REGION void tsl9_resident_state8_service_block_63d56(void)
{
    REGS;
    a3 = UINT32_C(0x00322000); LIVE;
    a3 = a3 + UINT32_C(0x000002d0); LIVE;
    PORT(".Lresident_state8_service_edge_63d5e:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_63d5e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_63d36\n");
    __builtin_unreachable();
}

/* Original0x63D60..0x63D6A. */
REGION void tsl9_resident_state8_service_block_63d60(void)
{
    REGS;
    a0 = UINT32_C(0x00001000); LIVE;
    a3 = a3 | a0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a3; LIVE;
    a1 = a1 << UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_state8_service_edge_63d68:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_63d68\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_63d50\n");
    __builtin_unreachable();
}

/* Original0x6434A..0x6436A. */
REGION void tsl9_candidate_register_config_6434a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a0 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a2 = a0 + UINT32_C(0x00000540); LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000508)); LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 1(a2). */
    PORT(".option push\n.option rvc\n.2byte 0x321c\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a6, a5, 127\n.option pop\n");
    PORT(".Lresident_state8_service_edge_64368:\n.option push\n.option rvc\nc.beqz a1,.Lresident_state8_service_edge_64368\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_643f6\n");
    __builtin_unreachable();
}

/* Original0x6436A..0x6437E. */
REGION void tsl9_resident_state8_service_block_6436a(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000004)); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a2 = a2 & UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nor a2, a2, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a2; LIVE;
    a2 = a1 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_service_edge_6437c:\n.option push\n.option rvc\nc.beqz a2,.Lresident_state8_service_edge_6437c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_6438c\n");
    __builtin_unreachable();
}

/* Original0x6437E..0x64388. */
REGION void tsl9_resident_state8_service_block_6437e(void)
{
    REGS;
    a1 = a1 & UINT32_C(0x00000030); LIVE;
    a2 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_state8_service_edge_64384:\n.option push\n.option norvc\nbeq a1,a2,.Lresident_state8_service_edge_64384\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_643f0\n");
    __builtin_unreachable();
}

/* Original0x64388..0x6438C. */
REGION void tsl9_resident_state8_service_block_64388(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffc18); LIVE;
    __builtin_unreachable();
}

/* Original0x6438C..0x643D2. */
REGION void tsl9_resident_state8_service_block_6438c(void)
{
    REGS;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    PORT(".option push\n.option rvc\nlui a6, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a6, a6, -1536\n.option pop\n");
    a2 = a2 | UINT32_C(0x00000002); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)) = (uint32_t)a2; LIVE;
    PORT(".option push\n.option norvc\ndivu a2, a5, a6\n.option pop\n");
    PORT(".option push\n.option norvc\nlui a7, 0xfe100\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a7, a7, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nremu a5, a5, a6\n.option pop\n");
    a2 = a2 & UINT32_C(0x0000001f); LIVE;
    a1 = a2 << UINT32_C(0x00000014); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)); LIVE;
    PORT(".option push\n.option norvc\nand a2, a2, a7\n.option pop\n");
    a2 = a2 | a1; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)) = (uint32_t)a2; LIVE;
    a2 = UINT32_C(0x000000fa); LIVE;
    a1 = UINT32_C(0xfffc0000); LIVE;
    a5 = a5 << UINT32_C(0x0000000a); LIVE;
    PORT(".option push\n.option norvc\ndivu a5, a5, a2\n.option pop\n");
    a2 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)); LIVE;
    a2 = a2 & a1; LIVE;
    a5 = a5 << UINT32_C(0x0000000e); LIVE;
    a5 = a5 >> UINT32_C(0x0000000e); LIVE;
    a5 = a5 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000044)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x643D2..0x643DA. */
REGION void tsl9_resident_state8_service_block_643d2(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000540)); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_state8_service_edge_643d8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_service_edge_643d8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_643ee\n");
    __builtin_unreachable();
}

/* Original0x643DA..0x643EE. */
REGION void tsl9_resident_state8_service_block_643da(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    a4 = a5 | UINT32_C(0x00000040); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xffffff80); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x643EE..0x643F0. */
REGION void tsl9_resident_state8_service_block_643ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x643F0..0x643F6. */
REGION void tsl9_resident_state8_service_block_643f0(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffff830); LIVE;
    PORT(".Lresident_state8_service_edge_643f4:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_643f4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_6438c\n");
    __builtin_unreachable();
}

/* Original0x643F6..0x6440A. */
REGION void tsl9_resident_state8_service_block_643f6(void)
{
    REGS;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x0000002c)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nor a5, a5, a6\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    PORT(".Lresident_state8_service_edge_64408:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_64408\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_643d2\n");
    __builtin_unreachable();
}

/* Original0x64F04..0x64F36. */
REGION void tsl9_candidate_external_flash_64f04(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -64\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s5, 36(sp)\n.option pop\n");
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s6, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s7, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s8, 24(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw s5, 524(a5)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000020c)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option norvc\nfence.i\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s1, 1344\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    PORT(".Lresident_state8_service_edge_64f34:\n.option push\n.option rvc\nc.bnez a4,.Lresident_state8_service_edge_64f34\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_64f54\n");
    __builtin_unreachable();
}

/* Original0x64F36..0x64F3C. */
REGION void tsl9_resident_state8_service_block_64f36(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s5, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x64F3C..0x64F54. */
REGION void tsl9_resident_state8_service_block_64f3c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 60(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 56(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 52(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 48(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s5, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s6, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s7, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s8, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 64\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64F54..0x64F5E. */
REGION void tsl9_resident_state8_service_block_64f54(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000460)); LIVE;
    PORT(".Lresident_state8_service_edge_64f5c:\n.option push\n.option rvc\nc.beqz a4,.Lresident_state8_service_edge_64f5c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_64f66\n");
    __builtin_unreachable();
}

/* Original0x64F5E..0x64F66. */
REGION void tsl9_resident_state8_service_block_64f5e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw s5, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_state8_service_edge_64f64:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_64f64\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_64f3c\n");
    __builtin_unreachable();
}

/* Original0x64F66..0x64F7A. */
REGION void tsl9_resident_state8_service_block_64f66(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s8, a2\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s4, s1, 1344\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s7, a3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a2, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".Lresident_state8_service_edge_64f78:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_service_edge_64f78\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_64fce\n");
    __builtin_unreachable();
}

/* Original0x64F7A..0x64F8A. */
REGION void tsl9_resident_state8_service_block_64f7a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1376\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 1376\n.option pop\n");
    PORT(".Lresident_state8_service_edge_64f88:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_service_edge_64f88\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_64fa2\n");
    __builtin_unreachable();
}

/* Original0x64F8A..0x64F9E. */
REGION void tsl9_resident_state8_service_block_64f8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 29(s4)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    a1 = UINT32_C(0x00000049); LIVE;
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_state8_service_literal_64f96:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_heap_allocate_20000040\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_service_literal_64f96\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64F9E..0x64FA2. */
REGION void tsl9_resident_state8_service_block_64f9e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nsw a0, 4(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64FA2..0x64FA6. */
REGION void tsl9_resident_state8_service_block_64fa2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    PORT(".Lresident_state8_service_edge_64fa4:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_service_edge_64fa4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_64fb2\n");
    __builtin_unreachable();
}

/* Original0x64FA6..0x64FB2. */
REGION void tsl9_resident_state8_service_block_64fa6(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s5, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_service_edge_64fb0:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_64fb0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_64f3c\n");
    __builtin_unreachable();
}

/* Original0x64FB2..0x64FBC. */
REGION void tsl9_resident_state8_service_block_64fb2(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a4, 2(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2038\n.option pop\n");
    /* Conditional Xwchc: qk.c.sb a4, 0(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xa398\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    PORT(".Lresident_state8_service_edge_64fb8:\n.option push\n.option norvc\nbeqz s2,.Lresident_state8_service_edge_64fb8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_6500c\n");
    __builtin_unreachable();
}

/* Original0x64FBC..0x64FBE. */
REGION void tsl9_resident_state8_service_block_64fbc(void)
{
    REGS;
    PORT(".Lresident_state8_service_edge_64fbc:\n.option push\n.option rvc\nc.beqz a2,.Lresident_state8_service_edge_64fbc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_6500c\n");
    __builtin_unreachable();
}

/* Original0x64FBE..0x64FCE. */
REGION void tsl9_resident_state8_service_block_64fbe(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.sb a2, 1(a5). */
    PORT(".option push\n.option rvc\n.2byte 0xb390\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a0, 4(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a1, s2\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".Lresident_state8_service_literal_64fc6:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_service_literal_64fc6\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x64FCE..0x64FE2. */
REGION void tsl9_resident_state8_service_block_64fce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s6, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s6, 1300\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 7(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x33fc\n.option pop\n");
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\naddi s2, s6, 1300\n.option pop\n");
    PORT(".Lresident_state8_service_edge_64fde:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_state8_service_edge_64fde\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_64ff2\n");
    __builtin_unreachable();
}

/* Original0x64FE2..0x64FEC. */
REGION void tsl9_resident_state8_service_block_64fe2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s2)\n.option pop\n");
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".Lresident_state8_service_edge_64fe8:\n.option push\n.option norvc\nbeq a5,a4,.Lresident_state8_service_edge_64fe8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_64ff2\n");
    __builtin_unreachable();
}

/* Original0x64FEC..0x64FF2. */
REGION void tsl9_resident_state8_service_block_64fec(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_service_edge_64fee:\n.option push\n.option norvc\nbne a5,a4,.Lresident_state8_service_edge_64fee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_state8_service_block_65012\n");
    __builtin_unreachable();
}

/* Original0x64FF2..0x64FF8. */
REGION void tsl9_resident_state8_service_block_64ff2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s2)\n.option pop\n");
    PORT(".Lresident_state8_service_edge_64ff6:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_service_edge_64ff6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_65000\n");
    __builtin_unreachable();
}

/* Original0x64FF8..0x65000. */
REGION void tsl9_resident_state8_service_block_64ff8(void)
{
    REGS;
    a5 = UINT32_C(0x00000108); LIVE;
    PORT(".option push\n.option norvc\nsh a5, 8(s2)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65000..0x6500C. */
REGION void tsl9_resident_state8_service_block_65000(void)
{
    REGS;
    a5 = UINT32_C(0x40024000); LIVE;
    PORT(".option push\n.option norvc\nsw s5, 524(a5)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_state8_service_edge_6500a:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_6500a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_64f3c\n");
    __builtin_unreachable();
}

/* Original0x6500C..0x65012. */
REGION void tsl9_resident_state8_service_block_6500c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)0; LIVE;
    PORT(".Lresident_state8_service_edge_65010:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_65010\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_64fce\n");
    __builtin_unreachable();
}

/* Original0x65012..0x65020. */
REGION void tsl9_resident_state8_service_block_65012(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s3, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_service_edge_6501e:\n.option push\n.option rvc\nc.beqz a4,.Lresident_state8_service_edge_6501e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_65046\n");
    __builtin_unreachable();
}

/* Original0x65020..0x6503E. */
REGION void tsl9_resident_state8_service_block_65020(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffefc)) = (uint8_t)0; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)); LIVE;
    a4 = a4 & UINT32_C(0xfffffff8); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000008); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 >> UINT32_C(0x00000003); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_service_edge_6503c:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_service_edge_6503c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_65046\n");
    __builtin_unreachable();
}

/* Original0x6503E..0x65046. */
REGION void tsl9_resident_state8_service_block_6503e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    PORT(".option push\n.option rvc\nnop\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x65046..0x65068. */
REGION void tsl9_resident_state8_service_block_65046(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000064)) = (uint32_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 4(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, s0, 1376\n.option pop\n");
    /* Conditional Xwchc: qk.c.lbu a5, 12(a5). */
    PORT(".option push\n.option rvc\n.2byte 0x27dc\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, 1376\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lresident_state8_service_edge_65066:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_service_edge_65066\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_65072\n");
    __builtin_unreachable();
}

/* Original0x65068..0x65072. */
REGION void tsl9_resident_state8_service_block_65068(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 1344(s1)\n.option pop\n");
    a5 = a1 & UINT32_C(0x00000040); LIVE;
    PORT(".Lresident_state8_service_edge_65070:\n.option push\n.option rvc\nc.bnez a5,.Lresident_state8_service_edge_65070\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_6514c\n");
    __builtin_unreachable();
}

/* Original0x65072..0x65078. */
REGION void tsl9_resident_state8_service_block_65072(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 1(s4)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0x65078..0x6507C. */
REGION void tsl9_resident_state8_service_block_65078(void)
{
    REGS;
    PORT(".Lresident_state8_service_edge_65078:\n.option push\n.option norvc\njal ra,.Lresident_state8_service_edge_65078\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_6434a\n");
    __builtin_unreachable();
}

/* Original0x6507C..0x6508E. */
REGION void tsl9_resident_state8_service_block_6507c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 1344(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a1, 28(s4)\n.option pop\n");
    a2 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x4\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".Lresident_state8_service_edge_6508a:\n.option push\n.option norvc\njal ra,.Lresident_state8_service_edge_6508a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_register_config_63c54\n");
    __builtin_unreachable();
}

/* Original0x6508E..0x650E4. */
REGION void tsl9_resident_state8_service_block_6508e(void)
{
    REGS;
    a4 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000508)); LIVE;
    PORT(".option push\n.option norvc\nlw a3, 8(s4)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlw a3, 12(s4)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint32_t)a3; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1344(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 1340(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a4\n.option pop\n");
    a2 = a5 & UINT32_C(0x00000001); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    a5 = a5 | a2; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000004)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s8, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s7, 2(s0)\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000070)) = (uint32_t)a5; LIVE;
    /* Conditional Xwchc: qk.c.lbu a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x247c\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    /* Conditional Xwchc: qk.c.sb a5, 14(s0). */
    PORT(".option push\n.option rvc\n.2byte 0xa47c\n.option pop\n");
    a5 = UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 1300(s6)\n.option pop\n");
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 7(s2)\n.option pop\n");
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000218)); LIVE;
    PORT(".Lresident_state8_service_edge_650e2:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_service_edge_650e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_650f0\n");
    __builtin_unreachable();
}

/* Original0x650E4..0x650F0. */
REGION void tsl9_resident_state8_service_block_650e4(void)
{
    REGS;
    /* Conditional Xwchc: qk.c.lbu a0, 16(s0). */
    PORT(".option push\n.option rvc\n.2byte 0x2808\n.option pop\n");
    a2 = UINT32_C(0x00000640); LIVE;
    a1 = UINT32_C(0x00000010); LIVE;
    PORT(".Lresident_state8_service_edge_650ec:\n.option push\n.option norvc\njal ra,.Lresident_state8_service_edge_650ec\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_start_task_43728\n");
    __builtin_unreachable();
}

/* Original0x650F0..0x650FA. */
REGION void tsl9_resident_state8_service_block_650f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lresident_state8_service_edge_650f8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_state8_service_edge_650f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_6515a\n");
    __builtin_unreachable();
}

/* Original0x650FA..0x65102. */
REGION void tsl9_resident_state8_service_block_650fa(void)
{
    REGS;
    a0 = UINT32_C(0x00065000); LIVE;
    a0 = a0 + UINT32_C(0x000003a0); LIVE;
    __builtin_unreachable();
}

/* Original0x65102..0x6510A. */
REGION void tsl9_resident_state8_service_block_65102(void)
{
    REGS;
    PORT(".Lresident_state8_service_literal_65102:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_callback_set_2000078a\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_state8_service_literal_65102\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x6510A..0x6514C. */
REGION void tsl9_resident_state8_service_block_6510a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a4, 1288(s1)\n.option pop\n");
    a3 = UINT32_C(0x00330000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xfffffe7f); LIVE;
    a5 = a5 | UINT32_C(0x00000100); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)) = (uint32_t)a5; LIVE;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000008)) = (uint32_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlw a5, 1340(s3)\n.option pop\n");
    a4 = UINT32_C(0x00000059); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000050)) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\nsb zero, 5(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb zero, 1(s2)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    PORT(".Lresident_state8_service_edge_6514a:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_6514a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_65000\n");
    __builtin_unreachable();
}

/* Original0x6514C..0x6515A. */
REGION void tsl9_resident_state8_service_block_6514c(void)
{
    REGS;
    a1 = a1 & UINT32_C(0x00000030); LIVE;
    a1 = a1 | UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nlw a0, 4(s4)\n.option pop\n");
    PORT(".Lresident_state8_service_edge_65158:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_65158\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_65078\n");
    __builtin_unreachable();
}

/* Original0x6515A..0x65164. */
REGION void tsl9_resident_state8_service_block_6515a(void)
{
    REGS;
    a0 = UINT32_C(0x00065000); LIVE;
    a0 = a0 + UINT32_C(0x00000164); LIVE;
    PORT(".Lresident_state8_service_edge_65162:\n.option push\n.option rvc\nc.j .Lresident_state8_service_edge_65162\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_state8_service_block_65102\n");
    __builtin_unreachable();
}

/* Original0x2000078A..0x20000794. */
REGION void tsl9_candidate_callback_set_2000078a(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffffef8)) = (uint32_t)a0; LIVE;
    PORT(".Lresident_state8_service_edge_20000792:\n.option push\n.option rvc\nc.beqz a0,.Lresident_state8_service_edge_20000792\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_state8_service_block_2000079e\n");
    __builtin_unreachable();
}

/* Original0x20000794..0x2000079E. */
REGION void tsl9_resident_state8_service_block_20000794(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffefc)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x2000079E..0x200007A0. */
REGION void tsl9_resident_state8_service_block_2000079e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
