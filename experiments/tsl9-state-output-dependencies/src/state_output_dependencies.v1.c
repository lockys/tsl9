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

/* Three complete original dependency functions:80B/24i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xB6EA..0xB6F4. */
REGION void tsl9_rom_dependency_external_b6ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff822)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD05C..0xD07C. */
REGION void tsl9_rom_dependency_external_d05c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffedc); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a2 = UINT32_C(0) - a2; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint8_t)a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)a0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint8_t)a2; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)) = (uint8_t)a1; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10816..0x10818. */
REGION void tsl9_rom_dependency_external_10816(void)
{
    REGS;
    PORT(".Lstate_output_edge_10816:\n.option push\n.option rvc\nc.bnez a0,.Lstate_output_edge_10816\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_output_block_1081a\n");
    __builtin_unreachable();
}

/* Original0x10818..0x1081A. */
REGION void tsl9_state_output_block_10818(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x1081A..0x1083C. */
REGION void tsl9_state_output_block_1081a(void)
{
    REGS;
    a2 = UINT32_C(0x000003e8); LIVE;
    a2 = a0 * a2; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffb\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000794)) = (uint8_t)a5; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lstate_output_literal_10830:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_callback_flow_entry_1061c\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lstate_output_literal_10830\n.option pop\n");
    PORT(".Lstate_output_edge_10838:\n.option push\n.option norvc\njal zero,.Lstate_output_edge_10838\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}
