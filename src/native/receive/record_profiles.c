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

/* Four complete record-profile functions:978B/310i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x18232..0x18238. */
REGION void tsl9_record_dispatch_provider_18232(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lrecord_profiles_edge_18234:\n.option push\n.option norvc\nbltu a5,a0,.Lrecord_profiles_edge_18234\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1842e\n");
    __builtin_unreachable();
}

/* Original0x18238..0x1825A. */
REGION void tsl9_record_profiles_block_18238(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a1 = a0 + UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = original_gp + UINT32_C(0x00000054); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a5 = a1 << UINT32_C(0x00000003); LIVE;
    a1 = *(volatile uint32_t *)(uintptr_t)(a3 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    a1 = a1 + a5; LIVE;
    a5 = UINT32_C(0x00000004); LIVE;
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".Lrecord_profiles_edge_18256:\n.option push\n.option norvc\nbltu a5,a0,.Lrecord_profiles_edge_18256\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1834a\n");
    __builtin_unreachable();
}

/* Original0x1825A..0x18264. */
REGION void tsl9_record_profiles_block_1825a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff4\n.option pop\n");
    a0 = a0 + UINT32_C(0x000006e2); LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18264..0x18274. */
REGION void tsl9_record_profiles_block_18264(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000006de)); LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lrecord_profiles_edge_18270:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_profiles_edge_18270\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1840e\n");
    __builtin_unreachable();
}

/* Original0x18274..0x1827E. */
REGION void tsl9_record_profiles_block_18274(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000010); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_profiles_edge_1827a:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_1827a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0x1827E..0x1831E. */
REGION void tsl9_record_profiles_block_1827e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fff4\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x000006ba)); LIVE;
    a2 = a5 >> UINT32_C(0x0000001b); LIVE;
    a5 = a4 & UINT32_C(0x0000007f); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a5 = a5 | a2; LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a5, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a3, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000699)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00001000); LIVE;
    a2 = a5 + UINT32_C(0xffffffff); LIVE;
    a3 = a4 >> UINT32_C(0x00000008); LIVE;
    a3 = a3 & a2; LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x0000068e)); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsltu a3, a3, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000676)) = (uint8_t)a3; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000067a)); LIVE;
    a4 = a4 >> UINT32_C(0x00000014); LIVE;
    PORT(".option push\n.option norvc\nslt a4, a4, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000661)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000663)); LIVE;
    a5 = a5 & a2; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nslt a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000646)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000063d)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000101); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fff4\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x00000632)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000062c)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000061c)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x1831E..0x18324. */
REGION void tsl9_record_profiles_block_1831e(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_profiles_edge_18320:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_18320\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_9454\n");
    __builtin_unreachable();
}

/* Original0x18324..0x18344. */
REGION void tsl9_record_profiles_block_18324(void)
{
    REGS;
    a5 = UINT32_C(0x000001f4); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000032); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_profiles_literal_18330:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_output_builder_provider_17cf4\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_profiles_literal_18330\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0x000005f8)) = (uint16_t)a5; LIVE;
    PORT(".Lrecord_profiles_edge_18340:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_18340\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x18344..0x1834A. */
REGION void tsl9_record_profiles_block_18344(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1834A..0x18354. */
REGION void tsl9_record_profiles_block_1834a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fff4\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000604); LIVE;
    PORT(".option push\n.option rvc\njalr a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18354..0x18364. */
REGION void tsl9_record_profiles_block_18354(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000600)); LIVE;
    a5 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lrecord_profiles_edge_18360:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_profiles_edge_18360\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1840e\n");
    __builtin_unreachable();
}

/* Original0x18364..0x1836E. */
REGION void tsl9_record_profiles_block_18364(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x00000011); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_profiles_edge_1836a:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_1836a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0x1836E..0x1840E. */
REGION void tsl9_record_profiles_block_1836e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fff4\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x000005dc)); LIVE;
    a2 = a5 >> UINT32_C(0x0000001b); LIVE;
    a5 = a4 & UINT32_C(0x0000007f); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a5 = a5 | a2; LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a5, a3\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a3, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x000005bb)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00001000); LIVE;
    a2 = a5 + UINT32_C(0xffffffff); LIVE;
    a3 = a4 >> UINT32_C(0x00000008); LIVE;
    a3 = a3 & a2; LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x000005b0)); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsltu a3, a3, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000598)) = (uint8_t)a3; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000059c)); LIVE;
    a4 = a4 >> UINT32_C(0x00000014); LIVE;
    PORT(".option push\n.option norvc\nslt a4, a4, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000583)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000585)); LIVE;
    a5 = a5 & a2; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nslt a5, a5, a4\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000568)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000055f)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000101); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fff4\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0x00000554)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000054e)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000053e)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x1840E..0x1841A. */
REGION void tsl9_record_profiles_block_1840e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000524)); LIVE;
    PORT(".Lrecord_profiles_edge_18416:\n.option push\n.option norvc\nbnez a5,.Lrecord_profiles_edge_18416\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1831e\n");
    __builtin_unreachable();
}

/* Original0x1841A..0x18426. */
REGION void tsl9_record_profiles_block_1841a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000052a)); LIVE;
    PORT(".Lrecord_profiles_edge_18422:\n.option push\n.option norvc\nbnez a5,.Lrecord_profiles_edge_18422\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1831e\n");
    __builtin_unreachable();
}

/* Original0x18426..0x1842C. */
REGION void tsl9_record_profiles_block_18426(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_profiles_edge_18428:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_18428\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_9508\n");
    __builtin_unreachable();
}

/* Original0x1842C..0x1842E. */
REGION void tsl9_record_profiles_block_1842c(void)
{
    REGS;
    PORT(".Lrecord_profiles_edge_1842c:\n.option push\n.option rvc\nc.j .Lrecord_profiles_edge_1842c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_profiles_block_18344\n");
    __builtin_unreachable();
}

/* Original0x1842E..0x18430. */
REGION void tsl9_record_profiles_block_1842e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18430..0x1843A. */
REGION void tsl9_record_profiles_provider_18430(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000502)); LIVE;
    PORT(".Lrecord_profiles_edge_18438:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_profiles_edge_18438\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_18488\n");
    __builtin_unreachable();
}

/* Original0x1843A..0x18440. */
REGION void tsl9_record_profiles_block_1843a(void)
{
    REGS;
    a5 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_profiles_edge_1843e:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_profiles_edge_1843e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_18488\n");
    __builtin_unreachable();
}

/* Original0x18440..0x1845A. */
REGION void tsl9_record_profiles_block_18440(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004ee)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004d4)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lrecord_profiles_edge_18456:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_18456\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_17c4e\n");
    __builtin_unreachable();
}

/* Original0x1845A..0x18466. */
REGION void tsl9_record_profiles_block_1845a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004ea)); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a0 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lrecord_profiles_edge_18464:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_profiles_edge_18464\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_18482\n");
    __builtin_unreachable();
}

/* Original0x18466..0x1846A. */
REGION void tsl9_record_profiles_block_18466(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_profiles_edge_18468:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_profiles_edge_18468\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_18482\n");
    __builtin_unreachable();
}

/* Original0x1846A..0x1847E. */
REGION void tsl9_record_profiles_block_1846a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004da)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000004ae)) = (uint32_t)0; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1847E..0x18482. */
REGION void tsl9_record_profiles_block_1847e(void)
{
    REGS;
    PORT(".Lrecord_profiles_edge_1847e:\n.option push\n.option norvc\njal zero,.Lrecord_profiles_edge_1847e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_17c4e\n");
    __builtin_unreachable();
}

/* Original0x18482..0x18488. */
REGION void tsl9_record_profiles_block_18482(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18488..0x18492. */
REGION void tsl9_record_profiles_block_18488(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004bc)); LIVE;
    PORT(".Lrecord_profiles_edge_18490:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_profiles_edge_18490\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_184a8\n");
    __builtin_unreachable();
}

/* Original0x18492..0x18496. */
REGION void tsl9_record_profiles_block_18492(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_profiles_edge_18494:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_profiles_edge_18494\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_184a8\n");
    __builtin_unreachable();
}

/* Original0x18496..0x184A8. */
REGION void tsl9_record_profiles_block_18496(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004ae)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000482)) = (uint32_t)0; LIVE;
    PORT(".Lrecord_profiles_edge_184a6:\n.option push\n.option rvc\nc.j .Lrecord_profiles_edge_184a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_profiles_block_1847e\n");
    __builtin_unreachable();
}

/* Original0x184A8..0x184AA. */
REGION void tsl9_record_profiles_block_184a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x184AA..0x184B8. */
REGION void tsl9_record_profiles_provider_184aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 9\n.option pop\n");
    PORT(".Lrecord_profiles_edge_184b4:\n.option push\n.option norvc\nbltu s1,a0,.Lrecord_profiles_edge_184b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_185d4\n");
    __builtin_unreachable();
}

/* Original0x184B8..0x184CA. */
REGION void tsl9_record_profiles_block_184b8(void)
{
    REGS;
    a1 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsltu a1, a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 20\n.option pop\n");
    a1 = a1 + UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_profiles_edge_184c6:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_184c6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0x184CA..0x18514. */
REGION void tsl9_record_profiles_block_184ca(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000018)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a2 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000014)); LIVE;
    a3 = a5 >> UINT32_C(0x00000008); LIVE;
    a4 = a2 >> UINT32_C(0x0000001b); LIVE;
    a2 = a5 & UINT32_C(0x0000007f); LIVE;
    a2 = a2 << UINT32_C(0x00000005); LIVE;
    a2 = a2 | a4; LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a1 = a4 + UINT32_C(0xffffffff); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000001c)); LIVE;
    a3 = a3 & a1; LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a4 = a4 & a1; LIVE;
    a5 = a5 >> UINT32_C(0x00000014); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a1 = UINT32_C(0x0000005a); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)a2; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint16_t)a3; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000011)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000012)) = (uint8_t)a1; LIVE;
    PORT(".Lrecord_profiles_edge_18510:\n.option push\n.option norvc\nbltu s1,a2,.Lrecord_profiles_edge_18510\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_18540\n");
    __builtin_unreachable();
}

/* Original0x18514..0x1851A. */
REGION void tsl9_record_profiles_block_18514(void)
{
    REGS;
    a2 = UINT32_C(0x0000000a); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0x1851A..0x18520. */
REGION void tsl9_record_profiles_block_1851a(void)
{
    REGS;
    a2 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lrecord_profiles_edge_1851c:\n.option push\n.option norvc\nbltu a2,a3,.Lrecord_profiles_edge_1851c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1854e\n");
    __builtin_unreachable();
}

/* Original0x18520..0x18526. */
REGION void tsl9_record_profiles_block_18520(void)
{
    REGS;
    a3 = UINT32_C(0x0000001e); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint16_t)a3; LIVE;
    __builtin_unreachable();
}

/* Original0x18526..0x1852C. */
REGION void tsl9_record_profiles_block_18526(void)
{
    REGS;
    a3 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_profiles_edge_18528:\n.option push\n.option norvc\nbltu a3,a5,.Lrecord_profiles_edge_18528\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1855c\n");
    __builtin_unreachable();
}

/* Original0x1852C..0x18532. */
REGION void tsl9_record_profiles_block_1852c(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0x18532..0x18538. */
REGION void tsl9_record_profiles_block_18532(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lrecord_profiles_edge_18534:\n.option push\n.option norvc\nbltu a5,a4,.Lrecord_profiles_edge_18534\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1856a\n");
    __builtin_unreachable();
}

/* Original0x18538..0x1853A. */
REGION void tsl9_record_profiles_block_18538(void)
{
    REGS;
    a5 = UINT32_C(0x0000000a); LIVE;
    __builtin_unreachable();
}

/* Original0x1853A..0x18540. */
REGION void tsl9_record_profiles_block_1853a(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000011)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_profiles_edge_1853e:\n.option push\n.option rvc\nc.j .Lrecord_profiles_edge_1853e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_profiles_block_18572\n");
    __builtin_unreachable();
}

/* Original0x18540..0x18548. */
REGION void tsl9_record_profiles_block_18540(void)
{
    REGS;
    a1 = UINT32_C(0x000000fa); LIVE;
    PORT(".Lrecord_profiles_edge_18544:\n.option push\n.option norvc\nbleu a2,a1,.Lrecord_profiles_edge_18544\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1851a\n");
    __builtin_unreachable();
}

/* Original0x18548..0x1854E. */
REGION void tsl9_record_profiles_block_18548(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint16_t)a1; LIVE;
    PORT(".Lrecord_profiles_edge_1854c:\n.option push\n.option rvc\nc.j .Lrecord_profiles_edge_1854c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_profiles_block_1851a\n");
    __builtin_unreachable();
}

/* Original0x1854E..0x18556. */
REGION void tsl9_record_profiles_block_1854e(void)
{
    REGS;
    a2 = UINT32_C(0x000001d6); LIVE;
    PORT(".Lrecord_profiles_edge_18552:\n.option push\n.option norvc\nbleu a3,a2,.Lrecord_profiles_edge_18552\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_18526\n");
    __builtin_unreachable();
}

/* Original0x18556..0x1855C. */
REGION void tsl9_record_profiles_block_18556(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint16_t)a2; LIVE;
    PORT(".Lrecord_profiles_edge_1855a:\n.option push\n.option rvc\nc.j .Lrecord_profiles_edge_1855a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_profiles_block_18526\n");
    __builtin_unreachable();
}

/* Original0x1855C..0x18564. */
REGION void tsl9_record_profiles_block_1855c(void)
{
    REGS;
    a3 = UINT32_C(0x0000004b); LIVE;
    PORT(".Lrecord_profiles_edge_18560:\n.option push\n.option norvc\nbleu a5,a3,.Lrecord_profiles_edge_18560\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_18532\n");
    __builtin_unreachable();
}

/* Original0x18564..0x1856A. */
REGION void tsl9_record_profiles_block_18564(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)) = (uint8_t)a3; LIVE;
    PORT(".Lrecord_profiles_edge_18568:\n.option push\n.option rvc\nc.j .Lrecord_profiles_edge_18568\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_profiles_block_18532\n");
    __builtin_unreachable();
}

/* Original0x1856A..0x18572. */
REGION void tsl9_record_profiles_block_1856a(void)
{
    REGS;
    a5 = UINT32_C(0x00000032); LIVE;
    PORT(".Lrecord_profiles_edge_1856e:\n.option push\n.option norvc\nbltu a5,a4,.Lrecord_profiles_edge_1856e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_1853a\n");
    __builtin_unreachable();
}

/* Original0x18572..0x18584. */
REGION void tsl9_record_profiles_block_18572(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(original_sp + UINT32_C(0x00000010)); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".Lrecord_profiles_edge_18582:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_profiles_edge_18582\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_185c0\n");
    __builtin_unreachable();
}

/* Original0x18584..0x1859C. */
REGION void tsl9_record_profiles_block_18584(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option rvc\naddi s0, s0, 2\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s0, s0, 0x3\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option rvc\naddi a1, sp, 12\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x1859C..0x185A0. */
REGION void tsl9_record_profiles_block_1859c(void)
{
    REGS;
    PORT(".Lrecord_profiles_edge_1859c:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_1859c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_writer_13138\n");
    __builtin_unreachable();
}

/* Original0x185A0..0x185B4. */
REGION void tsl9_record_profiles_block_185a0(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_profiles_literal_185a8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_960e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_profiles_literal_185a8\n.option pop\n");
    PORT(".Lrecord_profiles_edge_185b0:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_185b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x185B4..0x185B6. */
REGION void tsl9_record_profiles_block_185b4(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x185B6..0x185C0. */
REGION void tsl9_record_profiles_block_185b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x185C0..0x185D4. */
REGION void tsl9_record_profiles_block_185c0(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_profiles_literal_185c8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_registered_callbacks_provider_9508\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_profiles_literal_185c8\n.option pop\n");
    PORT(".Lrecord_profiles_edge_185d0:\n.option push\n.option norvc\njal ra,.Lrecord_profiles_edge_185d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x185D4..0x185D8. */
REGION void tsl9_record_profiles_block_185d4(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_profiles_edge_185d6:\n.option push\n.option rvc\nc.j .Lrecord_profiles_edge_185d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_profiles_block_185b6\n");
    __builtin_unreachable();
}

/* Original0x185D8..0x185EA. */
REGION void tsl9_feature_external_185d8(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    a5 = a4 + UINT32_C(0xfffffffd); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_profiles_edge_185e6:\n.option push\n.option norvc\nbltu a3,a5,.Lrecord_profiles_edge_185e6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_profiles_block_185f2\n");
    __builtin_unreachable();
}

/* Original0x185EA..0x185F2. */
REGION void tsl9_record_profiles_block_185ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000033a)) = (uint8_t)a4; LIVE;
    __builtin_unreachable();
}

/* Original0x185F2..0x185FE. */
REGION void tsl9_record_profiles_block_185f2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fff4\n.option pop\n");
    a5 = a5 + UINT32_C(0x0000032e); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lrecord_profiles_edge_185fc:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_profiles_edge_185fc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_profiles_block_18602\n");
    __builtin_unreachable();
}

/* Original0x185FE..0x18602. */
REGION void tsl9_record_profiles_block_185fe(void)
{
    REGS;
    PORT(".Lrecord_profiles_edge_185fe:\n.option push\n.option norvc\njal zero,.Lrecord_profiles_edge_185fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_17c4e\n");
    __builtin_unreachable();
}

/* Original0x18602..0x18604. */
REGION void tsl9_record_profiles_block_18602(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}
