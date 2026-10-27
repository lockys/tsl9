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

/* Two complete conditional SDK initializer providers:38B/11i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x57AC4..0x57AD8. */
REGION void tsl9_candidate_external_flash_57ac4(void)
{
    REGS;
    a0 = UINT32_C(0x20003000); LIVE;
    a2 = UINT32_C(0x0000001c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    a0 = a0 + UINT32_C(0x00000454); LIVE;
    PORT(".Lresident_init_final_literal_57ad0:\n.option push\n.option norvc\nauipc t1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_memset_2000039c\njalr zero,0(t1)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_init_final_literal_57ad0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x63704..0x63716. */
REGION void tsl9_candidate_external_flash_63704(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000c4)) = (uint32_t)0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000000c0)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
