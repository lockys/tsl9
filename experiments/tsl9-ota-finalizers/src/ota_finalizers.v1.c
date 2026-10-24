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

/* Two complete original OTA finalizer functions:182B/69i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9EA6..0x9EB2. */
REGION void tsl9_ota_reply_external_9ea6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9EB2..0x9EB4. */
REGION void tsl9_ota_finalizers_block_9eb2(void)
{
    REGS;
    PORT(".Lota_finalizers_edge_9eb2:\n.option push\n.option rvc\nc.jal .Lota_finalizers_edge_9eb2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_callback_flow_external_9e84\n");
    __builtin_unreachable();
}

/* Original0x9EB4..0x9EC0. */
REGION void tsl9_ota_finalizers_block_9eb4(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)) = (uint32_t)a0; LIVE;
    PORT(".Lota_finalizers_edge_9ebc:\n.option push\n.option norvc\nbeq s1,a5,.Lota_finalizers_edge_9ebc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_finalizers_block_9edc\n");
    __builtin_unreachable();
}

/* Original0x9EC0..0x9ECE. */
REGION void tsl9_ota_finalizers_block_9ec0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, -1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 8\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, 12(sp)\n.option pop\n");
    PORT(".Lota_finalizers_edge_9ecc:\n.option push\n.option rvc\nc.jal .Lota_finalizers_edge_9ecc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_main_runtime_entry_9e5c\n");
    __builtin_unreachable();
}

/* Original0x9ECE..0x9ED0. */
REGION void tsl9_ota_finalizers_block_9ece(void)
{
    REGS;
    PORT(".Lota_finalizers_edge_9ece:\n.option push\n.option rvc\nc.bnez s0,.Lota_finalizers_edge_9ece\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_finalizers_block_9eb2\n");
    __builtin_unreachable();
}

/* Original0x9ED0..0x9ED2. */
REGION void tsl9_ota_finalizers_block_9ed0(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x9ED2..0x9EDC. */
REGION void tsl9_ota_finalizers_block_9ed2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9EDC..0x9EE0. */
REGION void tsl9_ota_finalizers_block_9edc(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_finalizers_edge_9ede:\n.option push\n.option rvc\nc.j .Lota_finalizers_edge_9ede\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_finalizers_block_9ed2\n");
    __builtin_unreachable();
}

/* Original0x16E0C..0x16E20. */
REGION void tsl9_ota_reply_external_16e0c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    a5 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lota_finalizers_edge_16e1e:\n.option push\n.option rvc\nc.beqz a5,.Lota_finalizers_edge_16e1e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_finalizers_block_16e2a\n");
    __builtin_unreachable();
}

/* Original0x16E20..0x16E2A. */
REGION void tsl9_ota_finalizers_block_16e20(void)
{
    REGS;
    a5 = UINT32_C(0x40011000); LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff814)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x16E2A..0x16E30. */
REGION void tsl9_ota_finalizers_block_16e2a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a5, s0, 2\n.option pop\n");
    PORT(".Lota_finalizers_edge_16e2e:\n.option push\n.option rvc\nc.beqz a5,.Lota_finalizers_edge_16e2e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_ota_finalizers_block_16e3a\n");
    __builtin_unreachable();
}

/* Original0x16E30..0x16E3A. */
REGION void tsl9_ota_finalizers_block_16e30(void)
{
    REGS;
    a5 = UINT32_C(0x40011000); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff814)) = (uint32_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x16E3A..0x16E42. */
REGION void tsl9_ota_finalizers_block_16e3a(void)
{
    REGS;
    a0 = UINT32_C(0x000000c0); LIVE;
    PORT(".Lota_finalizers_edge_16e3e:\n.option push\n.option norvc\njal ra,.Lota_finalizers_edge_16e3e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_spi_transfer_entry_16896\n");
    __builtin_unreachable();
}

/* Original0x16E42..0x16E50. */
REGION void tsl9_ota_finalizers_block_16e42(void)
{
    REGS;
    a5 = UINT32_C(0x40011000); LIVE;
    a4 = UINT32_C(0x00000011); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff810)) = (uint32_t)a4; LIVE;
    PORT(".Lota_finalizers_edge_16e4c:\n.option push\n.option norvc\njal ra,.Lota_finalizers_edge_16e4c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0x16E50..0x16E58. */
REGION void tsl9_ota_finalizers_block_16e50(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 2\n.option pop\n");
    PORT(".option push\n.option norvc\nli s3, 128\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16E58..0x16E5C. */
REGION void tsl9_ota_finalizers_block_16e58(void)
{
    REGS;
    PORT(".Lota_finalizers_edge_16e58:\n.option push\n.option norvc\njal ra,.Lota_finalizers_edge_16e58\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0x16E5C..0x16E64. */
REGION void tsl9_ota_finalizers_block_16e5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsub a0, a0, s2\n.option pop\n");
    PORT(".Lota_finalizers_edge_16e60:\n.option push\n.option norvc\nbleu a0,s1,.Lota_finalizers_edge_16e60\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_finalizers_block_16e74\n");
    __builtin_unreachable();
}

/* Original0x16E64..0x16E66. */
REGION void tsl9_ota_finalizers_block_16e64(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x16E66..0x16E74. */
REGION void tsl9_ota_finalizers_block_16e66(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x16E74..0x16E7C. */
REGION void tsl9_ota_finalizers_block_16e74(void)
{
    REGS;
    a1 = UINT32_C(0x0000000e); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lota_finalizers_edge_16e78:\n.option push\n.option norvc\njal ra,.Lota_finalizers_edge_16e78\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_register_read_entry_16994\n");
    __builtin_unreachable();
}

/* Original0x16E7C..0x16E84. */
REGION void tsl9_ota_finalizers_block_16e7c(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x000000e0); LIVE;
    PORT(".Lota_finalizers_edge_16e80:\n.option push\n.option norvc\nbne a0,s3,.Lota_finalizers_edge_16e80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_ota_finalizers_block_16e58\n");
    __builtin_unreachable();
}

/* Original0x16E84..0x16E88. */
REGION void tsl9_ota_finalizers_block_16e84(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lota_finalizers_edge_16e86:\n.option push\n.option rvc\nc.j .Lota_finalizers_edge_16e86\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_ota_finalizers_block_16e66\n");
    __builtin_unreachable();
}
