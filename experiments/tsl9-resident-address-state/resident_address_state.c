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

/* Four complete required SDK tail/state/range bodies:364B/129i; installed ROM identity unproved. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x43E8E..0x43E9C. */
REGION void tsl9_candidate_range16_43e8e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_address_state_edge_43e98:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_43e98\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_rand_433a8\n");
    __builtin_unreachable();
}

/* Original0x43E9C..0x43EB2. */
REGION void tsl9_resident_address_state_block_43e9c(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsub a1, a1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nmulhsu a0, a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    a0 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x43EB2..0x43EC0. */
REGION void tsl9_candidate_range32_43eb2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lresident_address_state_edge_43ebc:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_43ebc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_tmos_rand_433a8\n");
    __builtin_unreachable();
}

/* Original0x43EC0..0x43ED2. */
REGION void tsl9_resident_address_state_block_43ec0(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsub a1, a1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nmulhu a0, a1, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nadd a0, a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x53868..0x53890. */
REGION void tsl9_candidate_address_state_53868(void)
{
    REGS;
    a1 = UINT32_C(0x20003000); LIVE;
    a0 = UINT32_C(0x20003000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    a2 = UINT32_C(0x00000006); LIVE;
    a1 = a1 + UINT32_C(0x00000204); LIVE;
    a0 = a0 + UINT32_C(0x000004a0); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 16(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s1, 0x4\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 12(sp)\n.option pop\n");
    PORT(".Lresident_address_state_literal_53888:\n.option push\n.option norvc\nauipc ra,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_candidate_copy_arch_20000332\njalr ra,0(ra)\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lresident_address_state_literal_53888\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x53890..0x5389A. */
REGION void tsl9_resident_address_state_block_53890(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a1, s1, -1\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_address_state_edge_53896:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_53896\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_range16_43e8e\n");
    __builtin_unreachable();
}

/* Original0x5389A..0x538A4. */
REGION void tsl9_resident_address_state_block_5389a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a1 = UINT32_C(0xffffffff); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_address_state_edge_538a0:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_538a0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_range32_43eb2\n");
    __builtin_unreachable();
}

/* Original0x538A4..0x538AA. */
REGION void tsl9_resident_address_state_block_538a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, s0\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, -1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x538AA..0x538B4. */
REGION void tsl9_resident_address_state_block_538aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nand a4, a5, s1\n.option pop\n");
    a3 = a0 | a4; LIVE;
    PORT(".Lresident_address_state_edge_538b2:\n.option push\n.option rvc\nc.beqz a3,.Lresident_address_state_edge_538b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_address_state_block_53966\n");
    __builtin_unreachable();
}

/* Original0x538B4..0x538B8. */
REGION void tsl9_resident_address_state_block_538b4(void)
{
    REGS;
    PORT(".Lresident_address_state_edge_538b4:\n.option push\n.option norvc\nbne a0,s2,.Lresident_address_state_edge_538b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_address_state_block_538bc\n");
    __builtin_unreachable();
}

/* Original0x538B8..0x538BC. */
REGION void tsl9_resident_address_state_block_538b8(void)
{
    REGS;
    PORT(".Lresident_address_state_edge_538b8:\n.option push\n.option norvc\nbeq a4,s1,.Lresident_address_state_edge_538b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_address_state_block_53966\n");
    __builtin_unreachable();
}

/* Original0x538BC..0x538E2. */
REGION void tsl9_resident_address_state_block_538bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlui s0, 0x20003\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s0, 952\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000f8)) = (uint8_t)a5; LIVE;
    a5 = a5 >> UINT32_C(0x00000008); LIVE;
    a5 = a5 | UINT32_C(0xffffffc0); LIVE;
    PORT(".option push\n.option rvc\nlui s3, 0x4\n.option pop\n");
    PORT(".option push\n.option rvc\nlui s1, 0x10\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x000000f4)) = (uint32_t)a0; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000f9)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, 952\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s3, s3, -1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x538E2..0x538EA. */
REGION void tsl9_resident_address_state_block_538e2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s3\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_address_state_edge_538e6:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_538e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_range16_43e8e\n");
    __builtin_unreachable();
}

/* Original0x538EA..0x538F4. */
REGION void tsl9_resident_address_state_block_538ea(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    a1 = UINT32_C(0xffffffff); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_address_state_edge_538f0:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_538f0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_range32_43eb2\n");
    __builtin_unreachable();
}

/* Original0x538F4..0x538FA. */
REGION void tsl9_resident_address_state_block_538f4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nor a5, a0, s2\n.option pop\n");
    PORT(".Lresident_address_state_edge_538f8:\n.option push\n.option rvc\nc.beqz a5,.Lresident_address_state_edge_538f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_resident_address_state_block_538e2\n");
    __builtin_unreachable();
}

/* Original0x538FA..0x53900. */
REGION void tsl9_resident_address_state_block_538fa(void)
{
    REGS;
    a5 = UINT32_C(0xffffffff); LIVE;
    PORT(".Lresident_address_state_edge_538fc:\n.option push\n.option norvc\nbne a0,a5,.Lresident_address_state_edge_538fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_address_state_block_53904\n");
    __builtin_unreachable();
}

/* Original0x53900..0x53904. */
REGION void tsl9_resident_address_state_block_53900(void)
{
    REGS;
    PORT(".Lresident_address_state_edge_53900:\n.option push\n.option norvc\nbeq s2,s3,.Lresident_address_state_edge_53900\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_address_state_block_538e2\n");
    __builtin_unreachable();
}

/* Original0x53904..0x53938. */
REGION void tsl9_resident_address_state_block_53904(void)
{
    REGS;
    a5 = a0 >> UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 252(s0)\n.option pop\n");
    a5 = a0 >> UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 253(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlh a5, 232(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsh a0, 250(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s2, 254(s0)\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsrli s2, s2, 0x8\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s2, s2, 63\n.option pop\n");
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x10\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s2, 255(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nand a0, a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nand a5, a5, s1\n.option pop\n");
    PORT(".Lresident_address_state_edge_53934:\n.option push\n.option norvc\nbne a0,a5,.Lresident_address_state_edge_53934\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_address_state_block_53958\n");
    __builtin_unreachable();
}

/* Original0x53938..0x53948. */
REGION void tsl9_resident_address_state_block_53938(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlh a4, 252(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlh a5, 234(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nand a4, a4, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nand a5, a5, s1\n.option pop\n");
    PORT(".Lresident_address_state_edge_53944:\n.option push\n.option norvc\nbne a4,a5,.Lresident_address_state_edge_53944\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_address_state_block_53958\n");
    __builtin_unreachable();
}

/* Original0x53948..0x53958. */
REGION void tsl9_resident_address_state_block_53948(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlh a4, 254(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlh a5, 236(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nand a4, a4, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nand a5, a5, s1\n.option pop\n");
    PORT(".Lresident_address_state_edge_53954:\n.option push\n.option norvc\nbeq a4,a5,.Lresident_address_state_edge_53954\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_resident_address_state_block_538e2\n");
    __builtin_unreachable();
}

/* Original0x53958..0x53966. */
REGION void tsl9_resident_address_state_block_53958(void)
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

/* Original0x53966..0x5396E. */
REGION void tsl9_resident_address_state_block_53966(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s1\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_address_state_edge_5396a:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_5396a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_range16_43e8e\n");
    __builtin_unreachable();
}

/* Original0x5396E..0x53978. */
REGION void tsl9_resident_address_state_block_5396e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a1 = UINT32_C(0xffffffff); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lresident_address_state_edge_53974:\n.option push\n.option norvc\njal ra,.Lresident_address_state_edge_53974\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_range32_43eb2\n");
    __builtin_unreachable();
}

/* Original0x53978..0x5397C. */
REGION void tsl9_resident_address_state_block_53978(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, s0\n.option pop\n");
    PORT(".Lresident_address_state_edge_5397a:\n.option push\n.option rvc\nc.j .Lresident_address_state_edge_5397a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_resident_address_state_block_538aa\n");
    __builtin_unreachable();
}

/* Original0x5E758..0x5E76C. */
REGION void tsl9_candidate_external_flash_5e758(void)
{
    REGS;
    a5 = UINT32_C(0x20003000); LIVE;
    a5 = a5 + UINT32_C(0x000003b8); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000000c8)) = (uint8_t)0; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x000000cc)) = (uint32_t)0; LIVE;
    PORT(".Lresident_address_state_edge_5e768:\n.option push\n.option norvc\njal zero,.Lresident_address_state_edge_5e768\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_candidate_address_state_53868\n");
    __builtin_unreachable();
}
