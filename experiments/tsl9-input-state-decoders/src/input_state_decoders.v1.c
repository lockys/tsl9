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

/* Sixteen complete input/state decoder functions:1822B/594i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xA054..0xA066. */
REGION void tsl9_feature_external_a054(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s3, a0\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a062:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a062\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_predicate_1069e\n");
    __builtin_unreachable();
}

/* Original0xA066..0xA06A. */
REGION void tsl9_input_state_decoders_block_a066(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a066:\n.option push\n.option norvc\nbeqz a0,.Linput_state_decoders_edge_a066\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1e8\n");
    __builtin_unreachable();
}

/* Original0xA06A..0xA06E. */
REGION void tsl9_input_state_decoders_block_a06a(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a06a:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a06a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xA06E..0xA072. */
REGION void tsl9_input_state_decoders_block_a06e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a070:\n.option push\n.option rvc\nc.beqz a0,.Linput_state_decoders_edge_a070\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_a082\n");
    __builtin_unreachable();
}

/* Original0xA072..0xA082. */
REGION void tsl9_input_state_decoders_block_a072(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s0, 9(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 224\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s0, s0, -64\n.option pop\n");
    PORT(".option push\n.option norvc\nseqz s0, s0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA082..0xA086. */
REGION void tsl9_input_state_decoders_block_a082(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a082:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a082\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_entry_81de\n");
    __builtin_unreachable();
}

/* Original0xA086..0xA08E. */
REGION void tsl9_input_state_decoders_block_a086(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nmv s2, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a08c:\n.option push\n.option rvc\nc.bnez a0,.Linput_state_decoders_edge_a08c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_a098\n");
    __builtin_unreachable();
}

/* Original0xA08E..0xA098. */
REGION void tsl9_input_state_decoders_block_a08e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s1, 11(s3)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -2\n.option pop\n");
    PORT(".option push\n.option norvc\nsnez s1, s1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA098..0xA0A0. */
REGION void tsl9_input_state_decoders_block_a098(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b1)); LIVE;
    PORT(".Linput_state_decoders_edge_a09c:\n.option push\n.option norvc\nbeq a5,s2,.Linput_state_decoders_edge_a09c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a0c4\n");
    __builtin_unreachable();
}

/* Original0xA0A0..0xA0AC. */
REGION void tsl9_input_state_decoders_block_a0a0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s2, 177(gp)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s2, 175(gp)\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a0a8:\n.option push\n.option norvc\nbeqz s2,.Linput_state_decoders_edge_a0a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1b8\n");
    __builtin_unreachable();
}

/* Original0xA0AC..0xA0AE. */
REGION void tsl9_input_state_decoders_block_a0ac(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a0ac:\n.option push\n.option rvc\nc.beqz s1,.Linput_state_decoders_edge_a0ac\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_a0c4\n");
    __builtin_unreachable();
}

/* Original0xA0AE..0xA0C4. */
REGION void tsl9_input_state_decoders_block_a0ae(void)
{
    REGS;
    a2 = UINT32_C(0x00001000); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000770); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Linput_state_decoders_literal_a0b8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_rom_dependency_entry_9f74\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_a0b8\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a0c0:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a0c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA0C4..0xA0C8. */
REGION void tsl9_input_state_decoders_block_a0c4(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a0c4:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a0c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xA0C8..0xA0CC. */
REGION void tsl9_input_state_decoders_block_a0c8(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a0c8:\n.option push\n.option norvc\nbeqz a0,.Linput_state_decoders_edge_a0c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1e8\n");
    __builtin_unreachable();
}

/* Original0xA0CC..0xA0D0. */
REGION void tsl9_input_state_decoders_block_a0cc(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a0cc:\n.option push\n.option norvc\nbeqz s0,.Linput_state_decoders_edge_a0cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1e8\n");
    __builtin_unreachable();
}

/* Original0xA0D0..0xA0D4. */
REGION void tsl9_input_state_decoders_block_a0d0(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a0d0:\n.option push\n.option norvc\nbeqz s1,.Linput_state_decoders_edge_a0d0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1e8\n");
    __builtin_unreachable();
}

/* Original0xA0D4..0xA0E2. */
REGION void tsl9_input_state_decoders_block_a0d4(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a2 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA0E2..0xA0E6. */
REGION void tsl9_input_state_decoders_block_a0e2(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a0e2:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a0e2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_81f8\n");
    __builtin_unreachable();
}

/* Original0xA0E6..0xA0EE. */
REGION void tsl9_input_state_decoders_block_a0e6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000aa)); LIVE;
    PORT(".Linput_state_decoders_edge_a0ea:\n.option push\n.option norvc\nbeq a5,a0,.Linput_state_decoders_edge_a0ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1f6\n");
    __builtin_unreachable();
}

/* Original0xA0EE..0xA100. */
REGION void tsl9_input_state_decoders_block_a0ee(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000aa)) = (uint8_t)a0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b0)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b0)) = (uint8_t)a5; LIVE;
    PORT(".Linput_state_decoders_edge_a0fe:\n.option push\n.option rvc\nc.beqz a0,.Linput_state_decoders_edge_a0fe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_a1d6\n");
    __builtin_unreachable();
}

/* Original0xA100..0xA114. */
REGION void tsl9_input_state_decoders_block_a100(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000007d0); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_literal_a108:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_a2ea\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_a108\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a110:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a110\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA114..0xA132. */
REGION void tsl9_input_state_decoders_block_a114(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x00000008)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000a)); LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    a5 = a5 + UINT32_C(0xfffff857); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    a4 = UINT32_C(0x000000b2); LIVE;
    PORT(".Linput_state_decoders_edge_a12e:\n.option push\n.option norvc\nbltu a4,a5,.Linput_state_decoders_edge_a12e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1e8\n");
    __builtin_unreachable();
}

/* Original0xA132..0xA136. */
REGION void tsl9_input_state_decoders_block_a132(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a132:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a132\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_81ee\n");
    __builtin_unreachable();
}

/* Original0xA136..0xA140. */
REGION void tsl9_input_state_decoders_block_a136(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x000007a8); LIVE;
    PORT(".Linput_state_decoders_edge_a13c:\n.option push\n.option norvc\nbeq a0,a4,.Linput_state_decoders_edge_a13c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a168\n");
    __builtin_unreachable();
}

/* Original0xA140..0xA146. */
REGION void tsl9_input_state_decoders_block_a140(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Linput_state_decoders_edge_a142:\n.option push\n.option norvc\nbeq a0,a5,.Linput_state_decoders_edge_a142\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a1fc\n");
    __builtin_unreachable();
}

/* Original0xA146..0xA168. */
REGION void tsl9_input_state_decoders_block_a146(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b0)); LIVE;
    a4 = a5 << UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_literal_a14e:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_static_data_1ab48\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_a14e\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00001000); LIVE;
    a4 = a4 + UINT32_C(0xfffff802); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0xA168..0xA1AC. */
REGION void tsl9_input_state_decoders_block_a168(void)
{
    REGS;
    a4 = a5 >> UINT32_C(0x00000008); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000a)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000b)); LIVE;
    a3 = a4 & UINT32_C(0x0000000f); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000b)) = (uint8_t)a5; LIVE;
    a4 = a4 & UINT32_C(0xfffffff0); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a4 = a4 | a3; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000009)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)); LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0xfffffff0); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 | a4; LIVE;
    a1 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)) = (uint8_t)a5; LIVE;
    PORT(".Linput_state_decoders_edge_a1a8:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a1a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_checksum_ed00\n");
    __builtin_unreachable();
}

/* Original0xA1AC..0xA1B6. */
REGION void tsl9_input_state_decoders_block_a1ac(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a1b2:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a1b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xA1B6..0xA1B8. */
REGION void tsl9_input_state_decoders_block_a1b6(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a1b6:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_a1b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_a1e8\n");
    __builtin_unreachable();
}

/* Original0xA1B8..0xA1C8. */
REGION void tsl9_input_state_decoders_block_a1b8(void)
{
    REGS;
    PORT(".Linput_state_decoders_literal_a1b8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_rom_dependency_entry_9f74\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_a1b8\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000aa)) = (uint8_t)0; LIVE;
    PORT(".Linput_state_decoders_edge_a1c4:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a1c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA1C8..0xA1D4. */
REGION void tsl9_input_state_decoders_block_a1c8(void)
{
    REGS;
    PORT(".Linput_state_decoders_literal_a1c8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_a2ea\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_a1c8\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a1d0:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a1d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA1D4..0xA1D6. */
REGION void tsl9_input_state_decoders_block_a1d4(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a1d4:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_a1d4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_a0c4\n");
    __builtin_unreachable();
}

/* Original0xA1D6..0xA1E2. */
REGION void tsl9_input_state_decoders_block_a1d6(void)
{
    REGS;
    PORT(".Linput_state_decoders_literal_a1d6:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_a2ea\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_a1d6\n.option pop\n");
    PORT(".Linput_state_decoders_edge_a1de:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_a1de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0xA1E2..0xA1E8. */
REGION void tsl9_input_state_decoders_block_a1e2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000af)); LIVE;
    PORT(".Linput_state_decoders_edge_a1e6:\n.option push\n.option rvc\nc.bnez a5,.Linput_state_decoders_edge_a1e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_a114\n");
    __builtin_unreachable();
}

/* Original0xA1E8..0xA1F6. */
REGION void tsl9_input_state_decoders_block_a1e8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA1F6..0xA1FA. */
REGION void tsl9_input_state_decoders_block_a1f6(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a1f6:\n.option push\n.option norvc\nbnez a5,.Linput_state_decoders_edge_a1f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_a114\n");
    __builtin_unreachable();
}

/* Original0xA1FA..0xA1FC. */
REGION void tsl9_input_state_decoders_block_a1fa(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_a1fa:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_a1fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_a1e2\n");
    __builtin_unreachable();
}

/* Original0xA1FC..0xA204. */
REGION void tsl9_input_state_decoders_block_a1fc(void)
{
    REGS;
    a5 = UINT32_C(0x00001000); LIVE;
    a5 = a5 + UINT32_C(0xfffff85c); LIVE;
    PORT(".Linput_state_decoders_edge_a202:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_a202\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_a168\n");
    __builtin_unreachable();
}

/* Original0xA2EA..0xA2EE. */
REGION void tsl9_input_state_decoders_entry_a2ea(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_edge_a2ec:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_a2ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_rom_dependency_entry_a204\n");
    __builtin_unreachable();
}

/* Original0xAAE2..0xAAF2. */
REGION void tsl9_input_state_decoders_entry_aae2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000404)) = (uint8_t)0; LIVE;
    a0 = UINT32_C(0x0000009c); LIVE;
    PORT(".Linput_state_decoders_edge_aaee:\n.option push\n.option norvc\njal zero,.Linput_state_decoders_edge_aaee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xAAF2..0xAB02. */
REGION void tsl9_input_state_decoders_entry_aaf2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003f2)) = (uint8_t)0; LIVE;
    a0 = UINT32_C(0x0000009a); LIVE;
    PORT(".Linput_state_decoders_edge_aafe:\n.option push\n.option norvc\njal zero,.Linput_state_decoders_edge_aafe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xADD6..0xADE8. */
REGION void tsl9_feature_external_add6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = a5 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_edge_ade4:\n.option push\n.option norvc\nbleu a4,a3,.Linput_state_decoders_edge_ade4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_ae0c\n");
    __builtin_unreachable();
}

/* Original0xADE8..0xADF2. */
REGION void tsl9_input_state_decoders_block_ade8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000f8)); LIVE;
    PORT(".Linput_state_decoders_edge_adf0:\n.option push\n.option rvc\nc.bnez a4,.Linput_state_decoders_edge_adf0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_ae0c\n");
    __builtin_unreachable();
}

/* Original0xADF2..0xADFC. */
REGION void tsl9_input_state_decoders_block_adf2(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Linput_state_decoders_edge_adf8:\n.option push\n.option norvc\nbltu a3,a5,.Linput_state_decoders_edge_adf8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_ae06\n");
    __builtin_unreachable();
}

/* Original0xADFC..0xAE02. */
REGION void tsl9_input_state_decoders_block_adfc(void)
{
    REGS;
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a0 = a0 >> UINT32_C(0x00000005); LIVE;
    __builtin_unreachable();
}

/* Original0xAE02..0xAE06. */
REGION void tsl9_input_state_decoders_block_ae02(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_edge_ae04:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_ae04\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_entry_ad48\n");
    __builtin_unreachable();
}

/* Original0xAE06..0xAE0C. */
REGION void tsl9_input_state_decoders_block_ae06(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    PORT(".Linput_state_decoders_edge_ae0a:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_ae0a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_ae02\n");
    __builtin_unreachable();
}

/* Original0xAE0C..0xAE0E. */
REGION void tsl9_input_state_decoders_block_ae0c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAE0E..0xAE3A. */
REGION void tsl9_input_state_decoders_entry_ae0e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000c4)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    a0 = a0 & UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000000bd)); LIVE;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Linput_state_decoders_edge_ae36:\n.option push\n.option norvc\nbeq a5,a0,.Linput_state_decoders_edge_ae36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_ae4c\n");
    __builtin_unreachable();
}

/* Original0xAE3A..0xAE4A. */
REGION void tsl9_input_state_decoders_block_ae3a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000000af)) = (uint8_t)a0; LIVE;
    a0 = a0 + UINT32_C(0xfffffffd); LIVE;
    a0 = (uint32_t)(a0 < UINT32_C(0x00000004)); LIVE;
    PORT(".Linput_state_decoders_edge_ae48:\n.option push\n.option rvc\nc.jal .Linput_state_decoders_edge_ae48\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_state_controls_entry_ad48\n");
    __builtin_unreachable();
}

/* Original0xAE4A..0xAE4C. */
REGION void tsl9_input_state_decoders_block_ae4a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAE4C..0xAE58. */
REGION void tsl9_input_state_decoders_block_ae4c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a4, 0(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000399); LIVE;
    PORT(".Linput_state_decoders_edge_ae54:\n.option push\n.option norvc\nbne a4,a5,.Linput_state_decoders_edge_ae54\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_af4c\n");
    __builtin_unreachable();
}

/* Original0xAE58..0xAE62. */
REGION void tsl9_input_state_decoders_block_ae58(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 11(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_edge_ae5e:\n.option push\n.option norvc\nbne a4,a5,.Linput_state_decoders_edge_ae5e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_af4c\n");
    __builtin_unreachable();
}

/* Original0xAE62..0xAE70. */
REGION void tsl9_input_state_decoders_block_ae62(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a2 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAE70..0xAE84. */
REGION void tsl9_input_state_decoders_block_ae70(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s3, gp, 184\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s2, 0x20001\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s2, 109(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a5, 0(s3)\n.option pop\n");
    PORT(".Linput_state_decoders_edge_ae80:\n.option push\n.option norvc\nbeqz s2,.Linput_state_decoders_edge_ae80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_af40\n");
    __builtin_unreachable();
}

/* Original0xAE84..0xAE86. */
REGION void tsl9_input_state_decoders_block_ae84(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_ae84:\n.option push\n.option rvc\nc.bnez a5,.Linput_state_decoders_edge_ae84\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_ae8e\n");
    __builtin_unreachable();
}

/* Original0xAE86..0xAE8A. */
REGION void tsl9_input_state_decoders_block_ae86(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_ae86:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_ae86\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xAE8A..0xAE8E. */
REGION void tsl9_input_state_decoders_block_ae8a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b8)) = (uint32_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0xAE8E..0xAE9C. */
REGION void tsl9_input_state_decoders_block_ae8e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    a5 = a5 & UINT32_C(0x0000003c); LIVE;
    PORT(".Linput_state_decoders_edge_ae98:\n.option push\n.option norvc\nbeq a5,a4,.Linput_state_decoders_edge_ae98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_af0a\n");
    __builtin_unreachable();
}

/* Original0xAE9C..0xAE9E. */
REGION void tsl9_input_state_decoders_block_ae9c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s2, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAE9E..0xAEA8. */
REGION void tsl9_input_state_decoders_block_ae9e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000004d)); LIVE;
    PORT(".Linput_state_decoders_edge_aea6:\n.option push\n.option rvc\nc.beqz a5,.Linput_state_decoders_edge_aea6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_aebc\n");
    __builtin_unreachable();
}

/* Original0xAEA8..0xAEBC. */
REGION void tsl9_input_state_decoders_block_aea8(void)
{
    REGS;
    a4 = UINT32_C(0x00000006); LIVE;
    a5 = a5 + UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000bc)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000bd)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000037)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xAEBC..0xAEC2. */
REGION void tsl9_input_state_decoders_block_aebc(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000bc)); LIVE;
    PORT(".Linput_state_decoders_edge_aec0:\n.option push\n.option rvc\nc.beqz a5,.Linput_state_decoders_edge_aec0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_af48\n");
    __builtin_unreachable();
}

/* Original0xAEC2..0xAEE0. */
REGION void tsl9_input_state_decoders_block_aec2(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000bc)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000bd)); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a4 = a5 << UINT32_C(0x00000002); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & UINT32_C(0xffffffc3); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xAEE0..0xAEFE. */
REGION void tsl9_input_state_decoders_block_aee0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)); LIVE;
    a1 = UINT32_C(0x00000007); LIVE;
    a5 = a5 >> UINT32_C(0x0000000c); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 << UINT32_C(0x00000004); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)) = (uint8_t)a5; LIVE;
    PORT(".Linput_state_decoders_edge_aefa:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_aefa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_checksum_ed00\n");
    __builtin_unreachable();
}

/* Original0xAEFE..0xAF08. */
REGION void tsl9_input_state_decoders_block_aefe(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000e)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Linput_state_decoders_edge_af04:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_af04\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xAF08..0xAF0A. */
REGION void tsl9_input_state_decoders_block_af08(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_af08:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_af08\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_af4c\n");
    __builtin_unreachable();
}

/* Original0xAF0A..0xAF0E. */
REGION void tsl9_input_state_decoders_block_af0a(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_af0a:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_af0a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_entry_81de\n");
    __builtin_unreachable();
}

/* Original0xAF0E..0xAF12. */
REGION void tsl9_input_state_decoders_block_af0e(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000002); LIVE;
    PORT(".Linput_state_decoders_edge_af10:\n.option push\n.option rvc\nc.beqz a0,.Linput_state_decoders_edge_af10\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_ae9c\n");
    __builtin_unreachable();
}

/* Original0xAF12..0xAF16. */
REGION void tsl9_input_state_decoders_block_af12(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_af12:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_af12\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xAF16..0xAF1A. */
REGION void tsl9_input_state_decoders_block_af16(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".Linput_state_decoders_edge_af18:\n.option push\n.option rvc\nc.beqz a0,.Linput_state_decoders_edge_af18\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_ae9c\n");
    __builtin_unreachable();
}

/* Original0xAF1A..0xAF1E. */
REGION void tsl9_input_state_decoders_block_af1a(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_af1a:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_af1a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xAF1E..0xAF2E. */
REGION void tsl9_input_state_decoders_block_af1e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s3)\n.option pop\n");
    a0 = a0 - a5; LIVE;
    a5 = UINT32_C(0x00003000); LIVE;
    a5 = a5 + UINT32_C(0xfffffedf); LIVE;
    PORT(".Linput_state_decoders_edge_af2a:\n.option push\n.option norvc\nbltu a5,a0,.Linput_state_decoders_edge_af2a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_ae9c\n");
    __builtin_unreachable();
}

/* Original0xAF2E..0xAF40. */
REGION void tsl9_input_state_decoders_block_af2e(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & UINT32_C(0xffffffc3); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint8_t)a5; LIVE;
    PORT(".Linput_state_decoders_edge_af3e:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_af3e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_ae9e\n");
    __builtin_unreachable();
}

/* Original0xAF40..0xAF42. */
REGION void tsl9_input_state_decoders_block_af40(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_af40:\n.option push\n.option rvc\nc.beqz a5,.Linput_state_decoders_edge_af40\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_ae9c\n");
    __builtin_unreachable();
}

/* Original0xAF42..0xAF48. */
REGION void tsl9_input_state_decoders_block_af42(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b8)) = (uint32_t)0; LIVE;
    PORT(".Linput_state_decoders_edge_af46:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_af46\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_ae9e\n");
    __builtin_unreachable();
}

/* Original0xAF48..0xAF4C. */
REGION void tsl9_input_state_decoders_block_af48(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_af48:\n.option push\n.option norvc\nbnez s2,.Linput_state_decoders_edge_af48\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_aee0\n");
    __builtin_unreachable();
}

/* Original0xAF4C..0xAF5C. */
REGION void tsl9_input_state_decoders_block_af4c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000004); LIVE;
    a5 = a5 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 + UINT32_C(0x0000000d); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Linput_state_decoders_edge_af58:\n.option push\n.option norvc\nbltu a4,a5,.Linput_state_decoders_edge_af58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_b016\n");
    __builtin_unreachable();
}

/* Original0xAF5C..0xAF62. */
REGION void tsl9_input_state_decoders_block_af5c(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Linput_state_decoders_edge_af5e:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_af5e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_action_support_entry_aa2e\n");
    __builtin_unreachable();
}

/* Original0xAF62..0xAF66. */
REGION void tsl9_input_state_decoders_block_af62(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_af62:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_af62\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17320\n");
    __builtin_unreachable();
}

/* Original0xAF66..0xAF70. */
REGION void tsl9_input_state_decoders_block_af66(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff84)); LIVE;
    PORT(".Linput_state_decoders_edge_af6e:\n.option push\n.option rvc\nc.bnez a5,.Linput_state_decoders_edge_af6e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_af84\n");
    __builtin_unreachable();
}

/* Original0xAF70..0xAF84. */
REGION void tsl9_input_state_decoders_block_af70(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000098); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xffffff74)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".Linput_state_decoders_edge_af80:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_af80\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xAF84..0xAF96. */
REGION void tsl9_input_state_decoders_block_af84(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff5f)); LIVE;
    a2 = a2 >> UINT32_C(0x00000004); LIVE;
    PORT(".Linput_state_decoders_edge_af92:\n.option push\n.option norvc\nbeq a5,a2,.Linput_state_decoders_edge_af92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_aff6\n");
    __builtin_unreachable();
}

/* Original0xAF96..0xAFC4. */
REGION void tsl9_input_state_decoders_block_af96(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff51)) = (uint8_t)a2; LIVE;
    a2 = a2 & UINT32_C(0x00000003); LIVE;
    PORT(".Linput_state_decoders_literal_afa0:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_aaf2\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_afa0\n.option pop\n");
    a3 = UINT32_C(0x00000099); LIVE;
    a2 = (uint32_t)(a2 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x20001\n.option pop\n");
    a1 = a1 + UINT32_C(0xffffff33); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = a0 + UINT32_C(0xffffff2c); LIVE;
    PORT(".Linput_state_decoders_edge_afc0:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_afc0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_ab08\n");
    __builtin_unreachable();
}

/* Original0xAFC4..0xAFF4. */
REGION void tsl9_input_state_decoders_block_afc4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0xffffff23)); LIVE;
    a2 = a2 >> UINT32_C(0x00000002); LIVE;
    a2 = a2 & UINT32_C(0x00000003); LIVE;
    PORT(".Linput_state_decoders_literal_afd0:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_aae2\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Linput_state_decoders_literal_afd0\n.option pop\n");
    a3 = UINT32_C(0x0000009b); LIVE;
    a2 = (uint32_t)(a2 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option norvc\nauipc a1, 0x20001\n.option pop\n");
    a1 = a1 + UINT32_C(0xffffff05); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffefe); LIVE;
    PORT(".Linput_state_decoders_edge_aff0:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_aff0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_ab08\n");
    __builtin_unreachable();
}

/* Original0xAFF4..0xAFF6. */
REGION void tsl9_input_state_decoders_block_aff4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xAFF6..0xB000. */
REGION void tsl9_input_state_decoders_block_aff6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 4(s0)\n.option pop\n");
    a0 = a0 & UINT32_C(0x0000001f); LIVE;
    PORT(".Linput_state_decoders_edge_affc:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_affc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_ab7c\n");
    __builtin_unreachable();
}

/* Original0xB000..0xB002. */
REGION void tsl9_input_state_decoders_block_b000(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_b000:\n.option push\n.option rvc\nc.bnez a0,.Linput_state_decoders_edge_b000\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_b004\n");
    __builtin_unreachable();
}

/* Original0xB002..0xB004. */
REGION void tsl9_input_state_decoders_block_b002(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_b002:\n.option push\n.option rvc\nc.beqz s1,.Linput_state_decoders_edge_b002\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_b008\n");
    __builtin_unreachable();
}

/* Original0xB004..0xB008. */
REGION void tsl9_input_state_decoders_block_b004(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_b004:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_b004\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xB008..0xB016. */
REGION void tsl9_input_state_decoders_block_b008(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB016..0xB022. */
REGION void tsl9_input_state_decoders_block_b016(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc s2, 0x20001\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s2, -300(s2)\n.option pop\n");
    PORT(".Linput_state_decoders_edge_b01e:\n.option push\n.option norvc\nbeqz s2,.Linput_state_decoders_edge_b01e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_af84\n");
    __builtin_unreachable();
}

/* Original0xB022..0xB034. */
REGION void tsl9_input_state_decoders_block_b022(void)
{
    REGS;
    a0 = UINT32_C(0x0000009d); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffec4)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nmv s1, s2\n.option pop\n");
    PORT(".Linput_state_decoders_edge_b030:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_b030\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xB034..0xB036. */
REGION void tsl9_input_state_decoders_block_b034(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_b034:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_b034\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_af84\n");
    __builtin_unreachable();
}

/* Original0xB036..0xB042. */
REGION void tsl9_feature_external_b036(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Linput_state_decoders_edge_b03e:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_b03e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_predicate_1069e\n");
    __builtin_unreachable();
}

/* Original0xB042..0xB044. */
REGION void tsl9_input_state_decoders_block_b042(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_b042:\n.option push\n.option rvc\nc.beqz a0,.Linput_state_decoders_edge_b042\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_b054\n");
    __builtin_unreachable();
}

/* Original0xB044..0xB04A. */
REGION void tsl9_input_state_decoders_block_b044(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_edge_b046:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_b046\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_clear_820c\n");
    __builtin_unreachable();
}

/* Original0xB04A..0xB054. */
REGION void tsl9_input_state_decoders_block_b04a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Linput_state_decoders_edge_b052:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_b052\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_entry_ae0e\n");
    __builtin_unreachable();
}

/* Original0xB054..0xB05C. */
REGION void tsl9_input_state_decoders_block_b054(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB05C..0xB068. */
REGION void tsl9_feature_external_b05c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Linput_state_decoders_edge_b064:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_b064\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_predicate_1069e\n");
    __builtin_unreachable();
}

/* Original0xB068..0xB06A. */
REGION void tsl9_input_state_decoders_block_b068(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_b068:\n.option push\n.option rvc\nc.beqz a0,.Linput_state_decoders_edge_b068\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_b07a\n");
    __builtin_unreachable();
}

/* Original0xB06A..0xB070. */
REGION void tsl9_input_state_decoders_block_b06a(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Linput_state_decoders_edge_b06c:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_b06c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_clear_820c\n");
    __builtin_unreachable();
}

/* Original0xB070..0xB07A. */
REGION void tsl9_input_state_decoders_block_b070(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Linput_state_decoders_edge_b078:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_b078\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_entry_ae0e\n");
    __builtin_unreachable();
}

/* Original0xB07A..0xB082. */
REGION void tsl9_input_state_decoders_block_b07a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC472..0xC47A. */
REGION void tsl9_feature_external_c472(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Linput_state_decoders_edge_c478:\n.option push\n.option rvc\nc.beqz a5,.Linput_state_decoders_edge_c478\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c482\n");
    __builtin_unreachable();
}

/* Original0xC47A..0xC480. */
REGION void tsl9_input_state_decoders_block_c47a(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_edge_c47c:\n.option push\n.option norvc\nbeq a5,a4,.Linput_state_decoders_edge_c47c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c510\n");
    __builtin_unreachable();
}

/* Original0xC480..0xC482. */
REGION void tsl9_input_state_decoders_block_c480(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC482..0xC4A4. */
REGION void tsl9_input_state_decoders_block_c482(void)
{
    REGS;
    a1 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a4 = UINT32_C(0x00000002); LIVE;
    a3 = UINT32_C(0x00000079); LIVE;
    a2 = UINT32_C(0x00000078); LIVE;
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000d8); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Linput_state_decoders_edge_c4a0:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_c4a0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xC4A4..0xC4A6. */
REGION void tsl9_input_state_decoders_block_c4a4(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_c4a4:\n.option push\n.option rvc\nc.beqz a0,.Linput_state_decoders_edge_c4a4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c4c8\n");
    __builtin_unreachable();
}

/* Original0xC4A6..0xC4B8. */
REGION void tsl9_input_state_decoders_block_c4a6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000008); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    a5 = a5 & UINT32_C(0x00000018); LIVE;
    PORT(".Linput_state_decoders_edge_c4b4:\n.option push\n.option norvc\nbne a5,a4,.Linput_state_decoders_edge_c4b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c4c8\n");
    __builtin_unreachable();
}

/* Original0xC4B8..0xC4C2. */
REGION void tsl9_input_state_decoders_block_c4b8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000d8)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Linput_state_decoders_edge_c4be:\n.option push\n.option norvc\nbeq a5,a4,.Linput_state_decoders_edge_c4be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c504\n");
    __builtin_unreachable();
}

/* Original0xC4C2..0xC4C8. */
REGION void tsl9_input_state_decoders_block_c4c2(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Linput_state_decoders_edge_c4c4:\n.option push\n.option norvc\nbeq a5,a4,.Linput_state_decoders_edge_c4c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c50c\n");
    __builtin_unreachable();
}

/* Original0xC4C8..0xC4E4. */
REGION void tsl9_input_state_decoders_block_c4c8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 8(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a1 = a1 >> UINT32_C(0x00000002); LIVE;
    a3 = UINT32_C(0x00000081); LIVE;
    a2 = UINT32_C(0x00000080); LIVE;
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000d9); LIVE;
    PORT(".Linput_state_decoders_edge_c4e0:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_c4e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xC4E4..0xC504. */
REGION void tsl9_input_state_decoders_block_c4e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a3 = UINT32_C(0x00000089); LIVE;
    a2 = UINT32_C(0x00000088); LIVE;
    a1 = a1 >> UINT32_C(0x00000006); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000da); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Linput_state_decoders_edge_c500:\n.option push\n.option norvc\njal zero,.Linput_state_decoders_edge_c500\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xC504..0xC506. */
REGION void tsl9_input_state_decoders_block_c504(void)
{
    REGS;
    a0 = UINT32_C(0x00000005); LIVE;
    __builtin_unreachable();
}

/* Original0xC506..0xC50A. */
REGION void tsl9_input_state_decoders_block_c506(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_c506:\n.option push\n.option norvc\njal ra,.Linput_state_decoders_edge_c506\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_18232\n");
    __builtin_unreachable();
}

/* Original0xC50A..0xC50C. */
REGION void tsl9_input_state_decoders_block_c50a(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_c50a:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_c50a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_c4c8\n");
    __builtin_unreachable();
}

/* Original0xC50C..0xC510. */
REGION void tsl9_input_state_decoders_block_c50c(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".Linput_state_decoders_edge_c50e:\n.option push\n.option rvc\nc.j .Linput_state_decoders_edge_c50e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_input_state_decoders_block_c506\n");
    __builtin_unreachable();
}

/* Original0xC510..0xC51C. */
REGION void tsl9_input_state_decoders_block_c510(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    a5 = UINT32_C(0x00000013); LIVE;
    a3 = a4 & UINT32_C(0x0000000c); LIVE;
    PORT(".Linput_state_decoders_edge_c51a:\n.option push\n.option rvc\nc.bnez a3,.Linput_state_decoders_edge_c51a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC51C..0xC524. */
REGION void tsl9_input_state_decoders_block_c51c(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x00000030); LIVE;
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".Linput_state_decoders_edge_c522:\n.option push\n.option rvc\nc.bnez a3,.Linput_state_decoders_edge_c522\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC524..0xC530. */
REGION void tsl9_input_state_decoders_block_c524(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a5 = UINT32_C(0x00000015); LIVE;
    a2 = a3 & UINT32_C(0x0000000c); LIVE;
    PORT(".Linput_state_decoders_edge_c52e:\n.option push\n.option rvc\nc.bnez a2,.Linput_state_decoders_edge_c52e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC530..0xC538. */
REGION void tsl9_input_state_decoders_block_c530(void)
{
    REGS;
    a2 = a3 & UINT32_C(0x00000030); LIVE;
    a5 = UINT32_C(0x00000016); LIVE;
    PORT(".Linput_state_decoders_edge_c536:\n.option push\n.option rvc\nc.bnez a2,.Linput_state_decoders_edge_c536\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC538..0xC540. */
REGION void tsl9_input_state_decoders_block_c538(void)
{
    REGS;
    a2 = a4 & UINT32_C(0x000000c0); LIVE;
    a5 = UINT32_C(0x00000017); LIVE;
    PORT(".Linput_state_decoders_edge_c53e:\n.option push\n.option rvc\nc.bnez a2,.Linput_state_decoders_edge_c53e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC540..0xC54A. */
REGION void tsl9_input_state_decoders_block_c540(void)
{
    REGS;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a5 = UINT32_C(0x00000018); LIVE;
    a2 = a2 & UINT32_C(0x00000003); LIVE;
    PORT(".Linput_state_decoders_edge_c548:\n.option push\n.option rvc\nc.bnez a2,.Linput_state_decoders_edge_c548\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC54A..0xC552. */
REGION void tsl9_input_state_decoders_block_c54a(void)
{
    REGS;
    a2 = a3 & UINT32_C(0x000000c0); LIVE;
    a5 = UINT32_C(0x00000019); LIVE;
    PORT(".Linput_state_decoders_edge_c550:\n.option push\n.option rvc\nc.bnez a2,.Linput_state_decoders_edge_c550\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC552..0xC558. */
REGION void tsl9_input_state_decoders_block_c552(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    a5 = UINT32_C(0x0000001a); LIVE;
    PORT(".Linput_state_decoders_edge_c556:\n.option push\n.option rvc\nc.bnez a4,.Linput_state_decoders_edge_c556\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC558..0xC56A. */
REGION void tsl9_input_state_decoders_block_c558(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\nli t1, 8\n.option pop\n");
    a5 = UINT32_C(0x0000002b); LIVE;
    a2 = a4 & UINT32_C(0x0000000c); LIVE;
    PORT(".Linput_state_decoders_edge_c566:\n.option push\n.option norvc\nbeq a2,t1,.Linput_state_decoders_edge_c566\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC56A..0xC57A. */
REGION void tsl9_input_state_decoders_block_c56a(void)
{
    REGS;
    a2 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".option push\n.option norvc\nli a7, 32\n.option pop\n");
    a5 = UINT32_C(0x0000002c); LIVE;
    PORT(".Linput_state_decoders_edge_c576:\n.option push\n.option norvc\nbeq a2,a7,.Linput_state_decoders_edge_c576\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC57A..0xC58A. */
REGION void tsl9_input_state_decoders_block_c57a(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x000000c0); LIVE;
    a2 = UINT32_C(0x00000080); LIVE;
    a5 = UINT32_C(0x0000002d); LIVE;
    PORT(".Linput_state_decoders_edge_c586:\n.option push\n.option norvc\nbeq a4,a2,.Linput_state_decoders_edge_c586\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC58A..0xC59C. */
REGION void tsl9_input_state_decoders_block_c58a(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a5 = UINT32_C(0x0000002e); LIVE;
    PORT(".option push\n.option norvc\nandi a6, a4, 3\n.option pop\n");
    PORT(".Linput_state_decoders_edge_c598:\n.option push\n.option norvc\nbeq a6,a1,.Linput_state_decoders_edge_c598\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC59C..0xC5A8. */
REGION void tsl9_input_state_decoders_block_c59c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a6, a4, 12\n.option pop\n");
    a5 = UINT32_C(0x0000002f); LIVE;
    PORT(".Linput_state_decoders_edge_c5a4:\n.option push\n.option norvc\nbeq a6,t1,.Linput_state_decoders_edge_c5a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5A8..0xC5B4. */
REGION void tsl9_input_state_decoders_block_c5a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a6, a4, 48\n.option pop\n");
    a5 = UINT32_C(0x00000030); LIVE;
    PORT(".Linput_state_decoders_edge_c5b0:\n.option push\n.option norvc\nbeq a6,a7,.Linput_state_decoders_edge_c5b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5B4..0xC5C0. */
REGION void tsl9_input_state_decoders_block_c5b4(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x000000c0); LIVE;
    a5 = UINT32_C(0x00000031); LIVE;
    PORT(".Linput_state_decoders_edge_c5bc:\n.option push\n.option norvc\nbeq a4,a2,.Linput_state_decoders_edge_c5bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5C0..0xC5D0. */
REGION void tsl9_input_state_decoders_block_c5c0(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = UINT32_C(0x00000032); LIVE;
    a0 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Linput_state_decoders_edge_c5cc:\n.option push\n.option norvc\nbeq a0,a1,.Linput_state_decoders_edge_c5cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5D0..0xC5D8. */
REGION void tsl9_input_state_decoders_block_c5d0(void)
{
    REGS;
    a3 = a3 & UINT32_C(0x00000003); LIVE;
    a5 = UINT32_C(0x0000001f); LIVE;
    PORT(".Linput_state_decoders_edge_c5d4:\n.option push\n.option norvc\nbeq a3,a1,.Linput_state_decoders_edge_c5d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5D8..0xC5E4. */
REGION void tsl9_input_state_decoders_block_c5d8(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x000000c0); LIVE;
    a5 = UINT32_C(0x00000020); LIVE;
    PORT(".Linput_state_decoders_edge_c5e0:\n.option push\n.option norvc\nbeq a3,a2,.Linput_state_decoders_edge_c5e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5E4..0xC5F4. */
REGION void tsl9_input_state_decoders_block_c5e4(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x00000030); LIVE;
    a2 = UINT32_C(0x00000020); LIVE;
    a5 = UINT32_C(0x00000021); LIVE;
    PORT(".Linput_state_decoders_edge_c5f0:\n.option push\n.option norvc\nbeq a3,a2,.Linput_state_decoders_edge_c5f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5F4..0xC5FE. */
REGION void tsl9_input_state_decoders_block_c5f4(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x0000000c); LIVE;
    a3 = UINT32_C(0x00000008); LIVE;
    a5 = UINT32_C(0x00000000); LIVE;
    PORT(".Linput_state_decoders_edge_c5fa:\n.option push\n.option norvc\nbne a4,a3,.Linput_state_decoders_edge_c5fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c602\n");
    __builtin_unreachable();
}

/* Original0xC5FE..0xC602. */
REGION void tsl9_input_state_decoders_block_c5fe(void)
{
    REGS;
    a5 = UINT32_C(0x00000022); LIVE;
    __builtin_unreachable();
}

/* Original0xC602..0xC60E. */
REGION void tsl9_input_state_decoders_block_c602(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a2 = original_gp + UINT32_C(0x000000d0); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a5\n.option pop\n");
    PORT(".Linput_state_decoders_edge_c60a:\n.option push\n.option norvc\njal zero,.Linput_state_decoders_edge_c60a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_ebac\n");
    __builtin_unreachable();
}

/* Original0xC60E..0xC616. */
REGION void tsl9_feature_external_c60e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Linput_state_decoders_edge_c614:\n.option push\n.option rvc\nc.bnez a5,.Linput_state_decoders_edge_c614\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c678\n");
    __builtin_unreachable();
}

/* Original0xC616..0xC628. */
REGION void tsl9_input_state_decoders_block_c616(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000a)); LIVE;
    a5 = a4 & UINT32_C(0x00000004); LIVE;
    PORT(".Linput_state_decoders_edge_c626:\n.option push\n.option rvc\nc.beqz a5,.Linput_state_decoders_edge_c626\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c642\n");
    __builtin_unreachable();
}

/* Original0xC628..0xC636. */
REGION void tsl9_input_state_decoders_block_c628(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a2 = UINT32_C(0x00000009); LIVE;
    a1 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Linput_state_decoders_edge_c632:\n.option push\n.option norvc\nbne a1,a2,.Linput_state_decoders_edge_c632\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c642\n");
    __builtin_unreachable();
}

/* Original0xC636..0xC642. */
REGION void tsl9_input_state_decoders_block_c636(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint8_t)a5; LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC642..0xC646. */
REGION void tsl9_input_state_decoders_block_c642(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000008); LIVE;
    PORT(".Linput_state_decoders_edge_c644:\n.option push\n.option rvc\nc.beqz a4,.Linput_state_decoders_edge_c644\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c676\n");
    __builtin_unreachable();
}

/* Original0xC646..0xC656. */
REGION void tsl9_input_state_decoders_block_c646(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbe8)); LIVE;
    a5 = a5 & UINT32_C(0x0000000c); LIVE;
    a4 = UINT32_C(0x00000008); LIVE;
    PORT(".Linput_state_decoders_edge_c652:\n.option push\n.option norvc\nbne a5,a4,.Linput_state_decoders_edge_c652\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c676\n");
    __builtin_unreachable();
}

/* Original0xC656..0xC666. */
REGION void tsl9_input_state_decoders_block_c656(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a4 = UINT32_C(0x00000040); LIVE;
    a2 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Linput_state_decoders_edge_c662:\n.option push\n.option norvc\nbne a2,a4,.Linput_state_decoders_edge_c662\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_c676\n");
    __builtin_unreachable();
}

/* Original0xC666..0xC672. */
REGION void tsl9_input_state_decoders_block_c666(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xC672..0xC676. */
REGION void tsl9_input_state_decoders_block_c672(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_c672:\n.option push\n.option norvc\njal zero,.Linput_state_decoders_edge_c672\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xC676..0xC678. */
REGION void tsl9_input_state_decoders_block_c676(void)
{
    REGS;
    PORT(".Linput_state_decoders_edge_c676:\n.option push\n.option rvc\nc.bnez a3,.Linput_state_decoders_edge_c676\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_input_state_decoders_block_c672\n");
    __builtin_unreachable();
}

/* Original0xC678..0xC67A. */
REGION void tsl9_input_state_decoders_block_c678(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC67A..0xC694. */
REGION void tsl9_main_services_provider_c67a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlui s0, 0x40\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 72(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x0000000c); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffff88e); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC694..0xC6A8. */
REGION void tsl9_input_state_decoders_block_c694(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw t1, 72(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000008); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000d0); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD76C..0xD77C. */
REGION void tsl9_state_request_records_provider_d76c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007fe)); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Linput_state_decoders_edge_d778:\n.option push\n.option norvc\nbne a4,a5,.Linput_state_decoders_edge_d778\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_d7a2\n");
    __builtin_unreachable();
}

/* Original0xD77C..0xD788. */
REGION void tsl9_input_state_decoders_block_d77c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffe\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000007f0)); LIVE;
    PORT(".Linput_state_decoders_edge_d784:\n.option push\n.option norvc\nbne a5,a4,.Linput_state_decoders_edge_d784\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_d7a2\n");
    __builtin_unreachable();
}

/* Original0xD788..0xD794. */
REGION void tsl9_input_state_decoders_block_d788(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007e3)); LIVE;
    PORT(".Linput_state_decoders_edge_d790:\n.option push\n.option norvc\nbne a4,a5,.Linput_state_decoders_edge_d790\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_input_state_decoders_block_d7a2\n");
    __builtin_unreachable();
}

/* Original0xD794..0xD7A2. */
REGION void tsl9_input_state_decoders_block_d794(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000007d9)); LIVE;
    a0 = a0 + UINT32_C(0xfffffffe); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0xD7A2..0xD7A4. */
REGION void tsl9_input_state_decoders_block_d7a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD7A4..0xD7B0. */
REGION void tsl9_input_state_decoders_entry_d7a4(void)
{
    REGS;
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007c8)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD7B0..0xD7BC. */
REGION void tsl9_input_state_decoders_entry_d7b0(void)
{
    REGS;
    a5 = UINT32_C(0x00000015); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007bc)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD7BC..0xD7C8. */
REGION void tsl9_input_state_decoders_entry_d7bc(void)
{
    REGS;
    a5 = UINT32_C(0x00000016); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007b0)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD7C8..0xD7D4. */
REGION void tsl9_input_state_decoders_entry_d7c8(void)
{
    REGS;
    a5 = UINT32_C(0x00000017); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007a4)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
