#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; not a host IRQ/CSR model.
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

/* Complete9A42..9AD2 initializer144B plus four19124..1919C RCC helpers120B.
 * Original16B frame,S2/RA/S0/S1 save/restore and six real calls are retained.
 * Preserve CSR0x800 clear/set mask0x88 and ordered byte/word MMIO writes.
 * Complete helper enable/disable branches keep fresh32-bit RMW and return residues.
 * C arithmetic/volatile access plus explicit stack,saved-register,CSR/control ports.
 * These19 regions require original adjacency;they are not normal C ABI functions.
 * No asynchronous IRQ-state,MCU,controller,private ABI,resident or OTA proof. */

/* Original 9A42..9A62 */
REGION void tsl9_main_provider_9a42(void)
{
    REGS;
    PORT("addi sp, sp, -16");
    PORT("sw s2, 0(sp)");
    PORT("sw ra, 12(sp)");
    PORT("sw s0, 8(sp)");
    PORT("sw s1, 4(sp)");
    PORT(".option push\n.option norvc\nli s2, 136\n.option pop\n");
    PORT(".option push\n.option norvc\ncsrc 0x800, s2\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s1, 0x2020\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, s1, 6\n.option pop\n");
    a1 = UINT32_C(1); LIVE;
    PORT(".Lirq_initializer_edge_9a5e:\n.option push\n.option norvc\njal ra,.Lirq_initializer_edge_9a5e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19142\n");
    __builtin_unreachable();
}

/* Original 9A62..9A6E */
REGION void tsl9_irq_initializer_block_9a62(void)
{
    REGS;
    PORT("lui s0, 0x1");
    PORT(".option push\n.option norvc\naddi a0, s0, 29\n.option pop\n");
    a1 = UINT32_C(1); LIVE;
    PORT(".Lirq_initializer_edge_9a6a:\n.option push\n.option norvc\njal ra,.Lirq_initializer_edge_9a6a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19124\n");
    __builtin_unreachable();
}

/* Original 9A6E..9A78 */
REGION void tsl9_irq_initializer_block_9a6e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s1, 6\n.option pop\n");
    a1 = UINT32_C(1); LIVE;
    PORT(".Lirq_initializer_edge_9a74:\n.option push\n.option norvc\njal ra,.Lirq_initializer_edge_9a74\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_1917e\n");
    __builtin_unreachable();
}

/* Original 9A78..9A82 */
REGION void tsl9_irq_initializer_block_9a78(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s1, 6\n.option pop\n");
    a1 = UINT32_C(0); LIVE;
    PORT(".Lirq_initializer_edge_9a7e:\n.option push\n.option norvc\njal ra,.Lirq_initializer_edge_9a7e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_1917e\n");
    __builtin_unreachable();
}

/* Original 9A82..9A8C */
REGION void tsl9_irq_initializer_block_9a82(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, s0, 29\n.option pop\n");
    a1 = UINT32_C(1); LIVE;
    PORT(".Lirq_initializer_edge_9a88:\n.option push\n.option norvc\njal ra,.Lirq_initializer_edge_9a88\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19160\n");
    __builtin_unreachable();
}

/* Original 9A8C..9A96 */
REGION void tsl9_irq_initializer_block_9a8c(void)
{
    REGS;
    a1 = UINT32_C(0); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s0, 29\n.option pop\n");
    PORT(".Lirq_initializer_edge_9a92:\n.option push\n.option norvc\njal ra,.Lirq_initializer_edge_9a92\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_irq_init_helper_19160\n");
    __builtin_unreachable();
}

/* Original 9A96..9AD2 */
REGION void tsl9_irq_initializer_block_9a96(void)
{
    REGS;
    a5 = UINT32_C(0xe000e000); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + 1069u) = (uint8_t)0; LIVE;
    a4 = UINT32_C(0x2000); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 260u) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(32); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + 1060u) = (uint8_t)a4; LIVE;
    a4 = UINT32_C(16); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 260u) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(48); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + 1063u) = (uint8_t)a4; LIVE;
    a4 = UINT32_C(128); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 260u) = (uint32_t)a4; LIVE;
    PORT(".option push\n.option norvc\ncsrs 0x800, s2\n.option pop\n");
    PORT("lw ra, 12(sp)");
    PORT("lw s0, 8(sp)");
    PORT("lw s1, 4(sp)");
    PORT("lw s2, 0(sp)");
    PORT("addi sp, sp, 16");
    PORT("ret");
    __builtin_unreachable();
}

/* Original 19124..19126 */
REGION void tsl9_irq_init_helper_19124(void)
{
    REGS;
    PORT(".Lirq_initializer_edge_19124:\n.option push\n.option rvc\nc.beqz a1,.Lirq_initializer_edge_19124\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_irq_initializer_block_19132\n");
    __builtin_unreachable();
}

/* Original 19126..19132 */
REGION void tsl9_irq_initializer_block_19126(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 24u); LIVE;
    a0 = a0 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 24u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 19132..19142 */
REGION void tsl9_irq_initializer_block_19132(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + 24u); LIVE;
    a0 = ~a0; LIVE;
    a0 = a0 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 24u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 19142..19144 */
REGION void tsl9_irq_init_helper_19142(void)
{
    REGS;
    PORT(".Lirq_initializer_edge_19142:\n.option push\n.option rvc\nc.beqz a1,.Lirq_initializer_edge_19142\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_irq_initializer_block_19150\n");
    __builtin_unreachable();
}

/* Original 19144..19150 */
REGION void tsl9_irq_initializer_block_19144(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 28u); LIVE;
    a0 = a0 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 28u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 19150..19160 */
REGION void tsl9_irq_initializer_block_19150(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + 28u); LIVE;
    a0 = ~a0; LIVE;
    a0 = a0 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 28u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 19160..19162 */
REGION void tsl9_irq_init_helper_19160(void)
{
    REGS;
    PORT(".Lirq_initializer_edge_19160:\n.option push\n.option rvc\nc.beqz a1,.Lirq_initializer_edge_19160\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_irq_initializer_block_1916e\n");
    __builtin_unreachable();
}

/* Original 19162..1916E */
REGION void tsl9_irq_initializer_block_19162(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 12u); LIVE;
    a0 = a0 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 12u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 1916E..1917E */
REGION void tsl9_irq_initializer_block_1916e(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + 12u); LIVE;
    a0 = ~a0; LIVE;
    a0 = a0 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 12u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 1917E..19180 */
REGION void tsl9_irq_init_helper_1917e(void)
{
    REGS;
    PORT(".Lirq_initializer_edge_1917e:\n.option push\n.option rvc\nc.beqz a1,.Lirq_initializer_edge_1917e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_irq_initializer_block_1918c\n");
    __builtin_unreachable();
}

/* Original 19180..1918C */
REGION void tsl9_irq_initializer_block_19180(void)
{
    REGS;
    a4 = UINT32_C(0x40021000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a4 + 16u); LIVE;
    a0 = a0 | a5; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a4 + 16u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}

/* Original 1918C..1919C */
REGION void tsl9_irq_initializer_block_1918c(void)
{
    REGS;
    a5 = UINT32_C(0x40021000); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + 16u); LIVE;
    a0 = ~a0; LIVE;
    a0 = a0 & a4; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + 16u) = (uint32_t)a0; LIVE;
    PORT("ret");
    __builtin_unreachable();
}
