#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; not a host transport model.
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

/* D1A8 returns original-coordinate pointer2000BF48,without dereferencing it.
 * Complete16DAC preserves low-byte guard,full A0,32B frame,zero2B payload,
 * caller return address,and actual16CC4 call. These five regions require
 * original adjacency and private register context; physical roles are unknown. */

/* Original0xD1A8..0xD1B2. */
REGION void tsl9_callback_flow_external_d1a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffda0); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0x16DAC..0x16DBA. */
REGION void tsl9_callback_flow_external_16dac(void)
{
    REGS;
    a5 = a0 - UINT32_C(1); LIVE;
    a5 = a5 & UINT32_C(255); LIVE;
    a4 = UINT32_C(1); LIVE;
    PORT(".Lcallback_support_16db6:\n.option push\n.option norvc\nbltu a4,a5,.Lcallback_support_16db6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_callback_support_block_16dd2\n");
    __builtin_unreachable();
}

/* Original0x16DBA..0x16DCC. */
REGION void tsl9_callback_support_block_16dba(void)
{
    REGS;
    PORT("addi sp, sp, -32");
    register uintptr_t frame __asm__("sp");
    __asm__ volatile("":"=r"(frame)::"memory");
    a1 = frame + UINT32_C(12); LIVE;
    a3 = UINT32_C(0); LIVE;
    a2 = UINT32_C(2); LIVE;
    PORT("sw ra, 28(sp)");
    *(volatile uint16_t *)(uintptr_t)(frame + UINT32_C(12)) = 0; LIVE;
    PORT(".Lcallback_support_16dc8:\n.option push\n.option norvc\njal ra,.Lcallback_support_16dc8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_16cc4\n");
    __builtin_unreachable();
}

/* Original0x16DCC..0x16DD2. */
REGION void tsl9_callback_support_block_16dcc(void)
{
    REGS;
    PORT("lw ra, 28(sp)");
    PORT("addi sp, sp, 32");
    PORT("ret");
    __builtin_unreachable();
}

/* Original0x16DD2..0x16DD4. */
REGION void tsl9_callback_support_block_16dd2(void)
{
    REGS;
    PORT("ret");
    __builtin_unreachable();
}
