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

/* Ten complete output dependency functions:374B/130i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x8E6A..0x8E88. */
REGION void tsl9_record_dispatch_provider_8e6a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000090); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)) = (uint8_t)a0; LIVE;
    a4 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 88(a4)\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000002)) = (uint8_t)a1; LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9F7A..0x9F88. */
REGION void tsl9_output_dependencies_provider_9f7a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Loutput_dependencies_edge_9f86:\n.option push\n.option rvc\nc.bnez a5,.Loutput_dependencies_edge_9f86\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_dependencies_block_9f92\n");
    __builtin_unreachable();
}

/* Original0x9F88..0x9F92. */
REGION void tsl9_output_dependencies_block_9f88(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ac)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9F92..0x9F9A. */
REGION void tsl9_output_dependencies_block_9f92(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Loutput_dependencies_edge_9f96:\n.option push\n.option norvc\njal ra,.Loutput_dependencies_edge_9f96\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x9F9A..0x9F9E. */
REGION void tsl9_output_dependencies_block_9f9a(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Loutput_dependencies_edge_9f9c:\n.option push\n.option rvc\nc.beqz a0,.Loutput_dependencies_edge_9f9c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_dependencies_block_9fa6\n");
    __builtin_unreachable();
}

/* Original0x9F9E..0x9FA6. */
REGION void tsl9_output_dependencies_block_9f9e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x9FA6..0x9FB2. */
REGION void tsl9_output_dependencies_block_9fa6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ac)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x9FC8..0x9FDA. */
REGION void tsl9_output_builder_provider_9fc8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ac)) = (uint8_t)0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Loutput_dependencies_edge_9fd8:\n.option push\n.option rvc\nc.beqz a5,.Loutput_dependencies_edge_9fd8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_dependencies_block_a00a\n");
    __builtin_unreachable();
}

/* Original0x9FDA..0x9FE2. */
REGION void tsl9_output_dependencies_block_9fda(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Loutput_dependencies_edge_9fde:\n.option push\n.option norvc\njal ra,.Loutput_dependencies_edge_9fde\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x9FE2..0x9FE4. */
REGION void tsl9_output_dependencies_block_9fe2(void)
{
    REGS;
    PORT(".Loutput_dependencies_edge_9fe2:\n.option push\n.option rvc\nc.beqz a0,.Loutput_dependencies_edge_9fe2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_dependencies_block_a004\n");
    __builtin_unreachable();
}

/* Original0x9FE4..0x9FEA. */
REGION void tsl9_output_dependencies_block_9fe4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Loutput_dependencies_edge_9fe8:\n.option push\n.option rvc\nc.bnez a5,.Loutput_dependencies_edge_9fe8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_dependencies_block_a004\n");
    __builtin_unreachable();
}

/* Original0x9FEA..0xA004. */
REGION void tsl9_output_dependencies_block_9fea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00002000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000710); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Loutput_dependencies_literal_9ff6:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_output_dependencies_provider_9f7a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Loutput_dependencies_literal_9ff6\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Loutput_dependencies_edge_a000:\n.option push\n.option norvc\njal zero,.Loutput_dependencies_edge_a000\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA004..0xA00A. */
REGION void tsl9_output_dependencies_block_a004(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA00A..0xA00C. */
REGION void tsl9_output_dependencies_block_a00a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD7D4..0xD7E6. */
REGION void tsl9_output_dependencies_provider_d7d4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a1 = UINT32_C(0x00000008); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Loutput_dependencies_edge_d7e2:\n.option push\n.option norvc\njal ra,.Loutput_dependencies_edge_d7e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xD7E6..0xD7EC. */
REGION void tsl9_output_dependencies_block_d7e6(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)); LIVE;
    PORT(".Loutput_dependencies_edge_d7ea:\n.option push\n.option rvc\nc.beqz a5,.Loutput_dependencies_edge_d7ea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_output_dependencies_block_d808\n");
    __builtin_unreachable();
}

/* Original0xD7EC..0xD802. */
REGION void tsl9_output_dependencies_block_d7ec(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile int8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)); LIVE;
    PORT(".option push\n.option norvc\nseqz a0, s0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    a0 = a0 | a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000007)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Loutput_dependencies_edge_d7fe:\n.option push\n.option norvc\njal ra,.Loutput_dependencies_edge_d7fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xD802..0xD808. */
REGION void tsl9_output_dependencies_block_d802(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Loutput_dependencies_edge_d804:\n.option push\n.option norvc\njal ra,.Loutput_dependencies_edge_d804\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xD808..0xD810. */
REGION void tsl9_output_dependencies_block_d808(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD810..0xD822. */
REGION void tsl9_output_builder_provider_d810(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffe\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000076c)); LIVE;
    a4 = UINT32_C(0x00000018); LIVE;
    PORT(".Loutput_dependencies_edge_d81e:\n.option push\n.option norvc\nbeq a5,a4,.Loutput_dependencies_edge_d81e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_dependencies_block_d85e\n");
    __builtin_unreachable();
}

/* Original0xD822..0xD826. */
REGION void tsl9_output_dependencies_block_d822(void)
{
    REGS;
    PORT(".Loutput_dependencies_edge_d822:\n.option push\n.option norvc\nbltu a4,a5,.Loutput_dependencies_edge_d822\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_dependencies_block_d842\n");
    __builtin_unreachable();
}

/* Original0xD826..0xD834. */
REGION void tsl9_output_dependencies_block_d826(void)
{
    REGS;
    a4 = a5 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000012); LIVE;
    PORT(".Loutput_dependencies_edge_d830:\n.option push\n.option norvc\nbleu a4,a3,.Loutput_dependencies_edge_d830\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_dependencies_block_d854\n");
    __builtin_unreachable();
}

/* Original0xD834..0xD842. */
REGION void tsl9_output_dependencies_block_d834(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000074a)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD842..0xD848. */
REGION void tsl9_output_dependencies_block_d842(void)
{
    REGS;
    a4 = UINT32_C(0x00000019); LIVE;
    PORT(".Loutput_dependencies_edge_d844:\n.option push\n.option norvc\nbeq a5,a4,.Loutput_dependencies_edge_d844\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_dependencies_block_d862\n");
    __builtin_unreachable();
}

/* Original0xD848..0xD850. */
REGION void tsl9_output_dependencies_block_d848(void)
{
    REGS;
    a4 = UINT32_C(0x0000001a); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Loutput_dependencies_edge_d84c:\n.option push\n.option norvc\nbne a5,a4,.Loutput_dependencies_edge_d84c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_output_dependencies_block_d834\n");
    __builtin_unreachable();
}

/* Original0xD850..0xD852. */
REGION void tsl9_output_dependencies_block_d850(void)
{
    REGS;
    PORT(".Loutput_dependencies_edge_d850:\n.option push\n.option rvc\nc.jal .Loutput_dependencies_edge_d850\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_dependencies_provider_d7d4\n");
    __builtin_unreachable();
}

/* Original0xD852..0xD854. */
REGION void tsl9_output_dependencies_block_d852(void)
{
    REGS;
    PORT(".Loutput_dependencies_edge_d852:\n.option push\n.option rvc\nc.j .Loutput_dependencies_edge_d852\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_dependencies_block_d834\n");
    __builtin_unreachable();
}

/* Original0xD854..0xD85E. */
REGION void tsl9_output_dependencies_block_d854(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000071a)) = (uint8_t)a5; LIVE;
    PORT(".Loutput_dependencies_edge_d85c:\n.option push\n.option rvc\nc.j .Loutput_dependencies_edge_d85c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_dependencies_block_d834\n");
    __builtin_unreachable();
}

/* Original0xD85E..0xD862. */
REGION void tsl9_output_dependencies_block_d85e(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Loutput_dependencies_edge_d860:\n.option push\n.option rvc\nc.j .Loutput_dependencies_edge_d860\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_dependencies_block_d850\n");
    __builtin_unreachable();
}

/* Original0xD862..0xD866. */
REGION void tsl9_output_dependencies_block_d862(void)
{
    REGS;
    PORT(".Loutput_dependencies_edge_d862:\n.option push\n.option norvc\njal ra,.Loutput_dependencies_edge_d862\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_dependencies_provider_f82c\n");
    __builtin_unreachable();
}

/* Original0xD866..0xD868. */
REGION void tsl9_output_dependencies_block_d866(void)
{
    REGS;
    PORT(".Loutput_dependencies_edge_d866:\n.option push\n.option rvc\nc.j .Loutput_dependencies_edge_d866\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_output_dependencies_block_d834\n");
    __builtin_unreachable();
}

/* Original0xF818..0xF822. */
REGION void tsl9_record_dispatch_provider_f818(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffc\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000779)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF822..0xF82C. */
REGION void tsl9_record_dispatch_provider_f822(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffc\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000785)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF82C..0xF838. */
REGION void tsl9_output_dependencies_provider_f82c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffc\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000076c)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF838..0xF84A. */
REGION void tsl9_output_dependencies_provider_f838(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffc\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000758); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF84A..0xF860. */
REGION void tsl9_main_services_provider_f84a(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 72(a5)\n.option pop\n");
    a2 = UINT32_C(0x00000018); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffc\n.option pop\n");
    a0 = a0 + UINT32_C(0x0000073a); LIVE;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}
