#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private entries only; no host state model.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"); __asm__ volatile("":"=r"(a0)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0)::"memory")
#define PORT(code) __asm__ volatile(code:"+r"(a0)::"memory")

/* Eleven complete byte getters:94B/29 instructions. C volatile loads keep
 * original AUIPC or live GP addressing; RET is an explicit private ABI port.
 * Link at each original PC before interpreting PC-relative data addresses.
 * Field meaning, concurrent state, physical RAM and OTA remain unproved. */

/* Original0x181C4..0x181CE. */
REGION void tsl9_callback_flow_external_181c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff4\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000761)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0x8440..0x8446. */
REGION void tsl9_callback_flow_external_8440(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000016c)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xB1B0..0xB1B6. */
REGION void tsl9_callback_flow_external_b1b0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c4)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xC35A..0xC364. */
REGION void tsl9_callback_flow_external_c35a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffbb8)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xCD44..0xCD4E. */
REGION void tsl9_callback_flow_external_cd44(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000001e2)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xF6B0..0xF6BA. */
REGION void tsl9_callback_flow_external_f6b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff8ed)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xF6E2..0xF6EC. */
REGION void tsl9_callback_flow_external_f6e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff8bd)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xF714..0xF71E. */
REGION void tsl9_callback_flow_external_f714(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff88e)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xF746..0xF750. */
REGION void tsl9_callback_flow_external_f746(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff85e)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xFA2A..0xFA30. */
REGION void tsl9_callback_flow_external_fa2a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000116)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original0xFA36..0xFA3C. */
REGION void tsl9_callback_flow_external_fa36(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000117)); LIVE;
    PORT("ret");
    __builtin_unreachable();
}
