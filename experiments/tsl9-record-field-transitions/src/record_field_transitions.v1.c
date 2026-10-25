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

/* Nineteen complete record-field transition entries:3682B/1149i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0x9658..0x9660. */
REGION void tsl9_record_dispatch_provider_9658(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_965e:\n.option push\n.option rvc\nc.jal .Lrecord_field_transitions_edge_965e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_allocate_9410\n");
    __builtin_unreachable();
}

/* Original0x9660..0x966A. */
REGION void tsl9_record_field_transitions_block_9660(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20003\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0xfffff86c)) = (uint32_t)a0; LIVE;
    PORT(".Lrecord_field_transitions_edge_9668:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_transitions_edge_9668\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_969c\n");
    __builtin_unreachable();
}

/* Original0x966A..0x969C. */
REGION void tsl9_record_field_transitions_block_966a(void)
{
    REGS;
    a5 = UINT32_C(0x000005b9); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x00000082); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)a5; LIVE;
    a5 = UINT32_C(0x0000048d); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000096); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_969a:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_969a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_arm_93aa\n");
    __builtin_unreachable();
}

/* Original0x969C..0x96A2. */
REGION void tsl9_record_field_transitions_block_969c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x973C..0x9744. */
REGION void tsl9_record_dispatch_provider_973c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_9742:\n.option push\n.option rvc\nc.jal .Lrecord_field_transitions_edge_9742\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_allocate_9410\n");
    __builtin_unreachable();
}

/* Original0x9744..0x974E. */
REGION void tsl9_record_field_transitions_block_9744(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000788)) = (uint32_t)a0; LIVE;
    PORT(".Lrecord_field_transitions_edge_974c:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_transitions_edge_974c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_978c\n");
    __builtin_unreachable();
}

/* Original0x974E..0x978C. */
REGION void tsl9_record_field_transitions_block_974e(void)
{
    REGS;
    a5 = UINT32_C(0x000001c2); LIVE;
    a4 = UINT32_C(0x0000048d); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)) = (uint16_t)a5; LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000096); LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000a)) = (uint16_t)a3; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000c)) = (uint16_t)a4; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x0000000e)) = (uint16_t)a5; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000010)) = (uint16_t)0; LIVE;
    *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000012)) = (uint16_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_978a:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_978a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_program_arm_93aa\n");
    __builtin_unreachable();
}

/* Original0x978C..0x9792. */
REGION void tsl9_record_field_transitions_block_978c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xA4CC..0xA4D8. */
REGION void tsl9_record_field_transitions_entry_a4cc(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x20002\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffffa05)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a4d6:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a4d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_provider_a476\n");
    __builtin_unreachable();
}

/* Original0xA4D8..0xA4EE. */
REGION void tsl9_record_field_transitions_entry_a4d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20002\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffff9f8); LIVE;
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000003)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)) = (uint8_t)a4; LIVE;
    PORT(".Lrecord_field_transitions_edge_a4ec:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a4ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_provider_a476\n");
    __builtin_unreachable();
}

/* Original0xA6D8..0xA710. */
REGION void tsl9_feature_external_a6d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s0, 3(a0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 3(a0)\n.option pop\n");
    a4 = a5 >> UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0x2\n.option pop\n");
    a3 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nandi s1, s1, 3\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x000007da)); LIVE;
    PORT(".option push\n.option rvc\nmv s2, a0\n.option pop\n");
    PORT(".option push\n.option rvc\nandi s0, s0, 3\n.option pop\n");
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_a70c:\n.option push\n.option norvc\nbne a2,s1,.Lrecord_field_transitions_edge_a70c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a740\n");
    __builtin_unreachable();
}

/* Original0xA710..0xA71C. */
REGION void tsl9_record_field_transitions_block_a710(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x000007c7)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a718:\n.option push\n.option norvc\nbne a2,s0,.Lrecord_field_transitions_edge_a718\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a740\n");
    __builtin_unreachable();
}

/* Original0xA71C..0xA728. */
REGION void tsl9_record_field_transitions_block_a71c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x000007bd)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a724:\n.option push\n.option norvc\nbne a2,a4,.Lrecord_field_transitions_edge_a724\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a740\n");
    __builtin_unreachable();
}

/* Original0xA728..0xA734. */
REGION void tsl9_record_field_transitions_block_a728(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x000007b3)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a730:\n.option push\n.option norvc\nbne a2,a3,.Lrecord_field_transitions_edge_a730\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a740\n");
    __builtin_unreachable();
}

/* Original0xA734..0xA740. */
REGION void tsl9_record_field_transitions_block_a734(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x000007a6)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a73c:\n.option push\n.option norvc\nbeq a2,a5,.Lrecord_field_transitions_edge_a73c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a76c\n");
    __builtin_unreachable();
}

/* Original0xA740..0xA76C. */
REGION void tsl9_record_field_transitions_block_a740(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000799)) = (uint8_t)a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, 1934(a2)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, 1927(a2)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000783)) = (uint8_t)a3; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000077a)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_a768:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a768\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xA76C..0xA780. */
REGION void tsl9_record_field_transitions_block_a76c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 7(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000768)); LIVE;
    a5 = a5 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_a77c:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_a77c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7a6\n");
    __builtin_unreachable();
}

/* Original0xA780..0xA78C. */
REGION void tsl9_record_field_transitions_block_a780(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000758)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_a788:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a788\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_cd44\n");
    __builtin_unreachable();
}

/* Original0xA78C..0xA78E. */
REGION void tsl9_record_field_transitions_block_a78c(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a78c:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_field_transitions_edge_a78c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a7a2\n");
    __builtin_unreachable();
}

/* Original0xA78E..0xA7A2. */
REGION void tsl9_record_field_transitions_block_a78e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000074a)); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x00000054); LIVE;
    PORT(".Lrecord_field_transitions_edge_a79e:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a79e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xA7A2..0xA7A6. */
REGION void tsl9_record_field_transitions_block_a7a2(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a7a2:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a7a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xA7A6..0xA7B8. */
REGION void tsl9_record_field_transitions_block_a7a6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000732)); LIVE;
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_transitions_edge_a7b4:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_a7b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7c0\n");
    __builtin_unreachable();
}

/* Original0xA7B8..0xA7C0. */
REGION void tsl9_record_field_transitions_block_a7b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000724)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xA7C0..0xA7CA. */
REGION void tsl9_record_field_transitions_block_a7c0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b5)); LIVE;
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_a7c6:\n.option push\n.option norvc\nbeq a5,s2,.Lrecord_field_transitions_edge_a7c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a824\n");
    __builtin_unreachable();
}

/* Original0xA7CA..0xA7CC. */
REGION void tsl9_record_field_transitions_block_a7ca(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a7ca:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_a7ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a80a\n");
    __builtin_unreachable();
}

/* Original0xA7CC..0xA7D2. */
REGION void tsl9_record_field_transitions_block_a7cc(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_a7ce:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_transitions_edge_a7ce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a836\n");
    __builtin_unreachable();
}

/* Original0xA7D2..0xA7F0. */
REGION void tsl9_record_field_transitions_block_a7d2(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a3, s1, -1\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a4, s0, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x20001\n.option pop\n");
    a2 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x000006fa)); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_field_transitions_edge_a7ec:\n.option push\n.option norvc\nbeq a2,a5,.Lrecord_field_transitions_edge_a7ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a91a\n");
    __builtin_unreachable();
}

/* Original0xA7F0..0xA7F2. */
REGION void tsl9_record_field_transitions_block_a7f0(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a7f0:\n.option push\n.option rvc\nc.beqz a2,.Lrecord_field_transitions_edge_a7f0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a84c\n");
    __builtin_unreachable();
}

/* Original0xA7F2..0xA7F8. */
REGION void tsl9_record_field_transitions_block_a7f2(void)
{
    REGS;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_a7f4:\n.option push\n.option norvc\nbeq a2,a1,.Lrecord_field_transitions_edge_a7f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a956\n");
    __builtin_unreachable();
}

/* Original0xA7F8..0xA80A. */
REGION void tsl9_record_field_transitions_block_a7f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a1, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_a806:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_a806\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_179fc\n");
    __builtin_unreachable();
}

/* Original0xA80A..0xA80E. */
REGION void tsl9_record_field_transitions_block_a80a(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a80a:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a80a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_request_records_entry_fd64\n");
    __builtin_unreachable();
}

/* Original0xA80E..0xA812. */
REGION void tsl9_record_field_transitions_block_a80e(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a80e:\n.option push\n.option norvc\nbne a0,s2,.Lrecord_field_transitions_edge_a80e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7d2\n");
    __builtin_unreachable();
}

/* Original0xA812..0xA81C. */
REGION void tsl9_record_field_transitions_block_a812(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000006ca)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a81a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_a81a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a81e\n");
    __builtin_unreachable();
}

/* Original0xA81C..0xA81E. */
REGION void tsl9_record_field_transitions_block_a81c(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0xA81E..0xA824. */
REGION void tsl9_record_field_transitions_block_a81e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b5)) = (uint8_t)a0; LIVE;
    PORT(".Lrecord_field_transitions_edge_a822:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a822\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a7d2\n");
    __builtin_unreachable();
}

/* Original0xA824..0xA82E. */
REGION void tsl9_record_field_transitions_block_a824(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000006b8)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a82c:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_a82c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a7d2\n");
    __builtin_unreachable();
}

/* Original0xA82E..0xA836. */
REGION void tsl9_record_field_transitions_block_a82e(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b5)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_a834:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a834\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a7d2\n");
    __builtin_unreachable();
}

/* Original0xA836..0xA840. */
REGION void tsl9_record_field_transitions_block_a836(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000006a6)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a83e:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_transitions_edge_a83e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a7d2\n");
    __builtin_unreachable();
}

/* Original0xA840..0xA84A. */
REGION void tsl9_record_field_transitions_block_a840(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000b5)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_field_transitions_edge_a846:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a846\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_request_records_entry_fd5e\n");
    __builtin_unreachable();
}

/* Original0xA84A..0xA84C. */
REGION void tsl9_record_field_transitions_block_a84a(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a84a:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a84a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a7d2\n");
    __builtin_unreachable();
}

/* Original0xA84C..0xA850. */
REGION void tsl9_record_field_transitions_block_a84c(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a84c:\n.option push\n.option norvc\nbleu a3,a5,.Lrecord_field_transitions_edge_a84c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a8a6\n");
    __builtin_unreachable();
}

/* Original0xA850..0xA85C. */
REGION void tsl9_record_field_transitions_block_a850(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x20001\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000685)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a858:\n.option push\n.option norvc\nbleu a4,a5,.Lrecord_field_transitions_edge_a858\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a8d4\n");
    __builtin_unreachable();
}

/* Original0xA85C..0xA85E. */
REGION void tsl9_record_field_transitions_block_a85c(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a85c:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_field_transitions_edge_a85c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA85E..0xA860. */
REGION void tsl9_record_field_transitions_block_a85e(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a85e:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_field_transitions_edge_a85e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_a870\n");
    __builtin_unreachable();
}

/* Original0xA860..0xA866. */
REGION void tsl9_record_field_transitions_block_a860(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_a862:\n.option push\n.option norvc\nbleu a3,a5,.Lrecord_field_transitions_edge_a862\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a882\n");
    __builtin_unreachable();
}

/* Original0xA866..0xA870. */
REGION void tsl9_record_field_transitions_block_a866(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    a0 = UINT32_C(0x0000005f); LIVE;
    PORT(".Lrecord_field_transitions_edge_a86c:\n.option push\n.option norvc\nbeq a3,a5,.Lrecord_field_transitions_edge_a86c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a8a0\n");
    __builtin_unreachable();
}

/* Original0xA870..0xA882. */
REGION void tsl9_record_field_transitions_block_a870(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000665)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000658)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_field_transitions_edge_a880:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a880\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA882..0xA888. */
REGION void tsl9_record_field_transitions_block_a882(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_transitions_edge_a884:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a884\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_fe6a\n");
    __builtin_unreachable();
}

/* Original0xA888..0xA88C. */
REGION void tsl9_record_field_transitions_block_a888(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_transitions_edge_a88a:\n.option push\n.option rvc\nc.jal .Lrecord_field_transitions_edge_a88a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_provider_a4ee\n");
    __builtin_unreachable();
}

/* Original0xA88C..0xA890. */
REGION void tsl9_record_field_transitions_block_a88c(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a88c:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a88c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xA890..0xA89C. */
REGION void tsl9_record_field_transitions_block_a890(void)
{
    REGS;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x00000060); LIVE;
    PORT(".Lrecord_field_transitions_edge_a898:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a898\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xA89C..0xA8A0. */
REGION void tsl9_record_field_transitions_block_a89c(void)
{
    REGS;
    a0 = UINT32_C(0x0000006d); LIVE;
    __builtin_unreachable();
}

/* Original0xA8A0..0xA8A4. */
REGION void tsl9_record_field_transitions_block_a8a0(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a8a0:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a8a0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xA8A4..0xA8A6. */
REGION void tsl9_record_field_transitions_block_a8a4(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a8a4:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a8a4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a870\n");
    __builtin_unreachable();
}

/* Original0xA8A6..0xA8AA. */
REGION void tsl9_record_field_transitions_block_a8a6(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a8a6:\n.option push\n.option norvc\nbleu a4,a5,.Lrecord_field_transitions_edge_a8a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a8ec\n");
    __builtin_unreachable();
}

/* Original0xA8AA..0xA8B6. */
REGION void tsl9_record_field_transitions_block_a8aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000062b)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a8b2:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_a8b2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA8B6..0xA8C2. */
REGION void tsl9_record_field_transitions_block_a8b6(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000061d)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_a8c0:\n.option push\n.option rvc\nc.jal .Lrecord_field_transitions_edge_a8c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_provider_a4ee\n");
    __builtin_unreachable();
}

/* Original0xA8C2..0xA8C6. */
REGION void tsl9_record_field_transitions_block_a8c2(void)
{
    REGS;
    a0 = UINT32_C(0x0000006a); LIVE;
    __builtin_unreachable();
}

/* Original0xA8C6..0xA8CA. */
REGION void tsl9_record_field_transitions_block_a8c6(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a8c6:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a8c6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xA8CA..0xA8CE. */
REGION void tsl9_record_field_transitions_block_a8ca(void)
{
    REGS;
    a0 = UINT32_C(0x0000006c); LIVE;
    __builtin_unreachable();
}

/* Original0xA8CE..0xA8D2. */
REGION void tsl9_record_field_transitions_block_a8ce(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a8ce:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a8ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xA8D2..0xA8D4. */
REGION void tsl9_record_field_transitions_block_a8d2(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a8d2:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a8d2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA8D4..0xA8DA. */
REGION void tsl9_record_field_transitions_block_a8d4(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_a8d6:\n.option push\n.option norvc\nbeq a3,a5,.Lrecord_field_transitions_edge_a8d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA8DA..0xA8E6. */
REGION void tsl9_record_field_transitions_block_a8da(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005f9)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_a8e4:\n.option push\n.option rvc\nc.jal .Lrecord_field_transitions_edge_a8e4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_provider_a4ee\n");
    __builtin_unreachable();
}

/* Original0xA8E6..0xA8EC. */
REGION void tsl9_record_field_transitions_block_a8e6(void)
{
    REGS;
    a0 = UINT32_C(0x0000006b); LIVE;
    PORT(".Lrecord_field_transitions_edge_a8ea:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a8ea\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a8c6\n");
    __builtin_unreachable();
}

/* Original0xA8EC..0xA8F8. */
REGION void tsl9_record_field_transitions_block_a8ec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005f0)); LIVE;
    PORT(".Lrecord_field_transitions_edge_a8f4:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_a8f4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a8fe\n");
    __builtin_unreachable();
}

/* Original0xA8F8..0xA8FE. */
REGION void tsl9_record_field_transitions_block_a8f8(void)
{
    REGS;
    a5 = UINT32_C(0x00000007); LIVE;
    PORT(".Lrecord_field_transitions_edge_a8fa:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_a8fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA8FE..0xA90C. */
REGION void tsl9_record_field_transitions_block_a8fe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005d7)); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_field_transitions_edge_a908:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_a908\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA90C..0xA91A. */
REGION void tsl9_record_field_transitions_block_a90c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005c9)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x0000005e); LIVE;
    PORT(".Lrecord_field_transitions_edge_a918:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a918\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a8ce\n");
    __builtin_unreachable();
}

/* Original0xA91A..0xA91E. */
REGION void tsl9_record_field_transitions_block_a91a(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a91a:\n.option push\n.option norvc\nbleu a3,a2,.Lrecord_field_transitions_edge_a91a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA91E..0xA922. */
REGION void tsl9_record_field_transitions_block_a91e(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a91e:\n.option push\n.option norvc\nbleu a4,a2,.Lrecord_field_transitions_edge_a91e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA922..0xA93A. */
REGION void tsl9_record_field_transitions_block_a922(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005b0)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000005); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a2 = UINT32_C(0x000001c2); LIVE;
    PORT(".Lrecord_field_transitions_edge_a936:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_transitions_edge_a936\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a944\n");
    __builtin_unreachable();
}

/* Original0xA93A..0xA940. */
REGION void tsl9_record_field_transitions_block_a93a(void)
{
    REGS;
    a4 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lrecord_field_transitions_edge_a93c:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_transitions_edge_a93c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a944\n");
    __builtin_unreachable();
}

/* Original0xA940..0xA944. */
REGION void tsl9_record_field_transitions_block_a940(void)
{
    REGS;
    a2 = UINT32_C(0x000000fa); LIVE;
    __builtin_unreachable();
}

/* Original0xA944..0xA954. */
REGION void tsl9_record_field_transitions_block_a944(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_transitions_literal_a948:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_entry_a4cc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_a948\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_a950:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_a950\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xA954..0xA956. */
REGION void tsl9_record_field_transitions_block_a954(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a954:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a954\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA956..0xA95A. */
REGION void tsl9_record_field_transitions_block_a956(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a956:\n.option push\n.option norvc\nbleu a3,a5,.Lrecord_field_transitions_edge_a956\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a95e\n");
    __builtin_unreachable();
}

/* Original0xA95A..0xA95E. */
REGION void tsl9_record_field_transitions_block_a95a(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_a95a:\n.option push\n.option norvc\nbltu a5,a4,.Lrecord_field_transitions_edge_a95a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xA95E..0xA968. */
REGION void tsl9_record_field_transitions_block_a95e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000576)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_field_transitions_edge_a966:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_a966\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_a7f8\n");
    __builtin_unreachable();
}

/* Original0xB390..0xB3B8. */
REGION void tsl9_feature_external_b390(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    a4 = a4 & UINT32_C(0x00000007); LIVE;
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 | a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x20001\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffffb4c)); LIVE;
    PORT(".Lrecord_field_transitions_edge_b3b4:\n.option push\n.option norvc\nbne a3,a4,.Lrecord_field_transitions_edge_b3b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b3c4\n");
    __builtin_unreachable();
}

/* Original0xB3B8..0xB3C4. */
REGION void tsl9_record_field_transitions_block_b3b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x20001\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffffb42)); LIVE;
    PORT(".Lrecord_field_transitions_edge_b3c0:\n.option push\n.option norvc\nbeq a3,a5,.Lrecord_field_transitions_edge_b3c0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b3d8\n");
    __builtin_unreachable();
}

/* Original0xB3C4..0xB3D8. */
REGION void tsl9_record_field_transitions_block_b3c4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x20001\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffffb34)) = (uint16_t)a4; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb2e)) = (uint16_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_b3d4:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_b3d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xB3D8..0xB3DA. */
REGION void tsl9_record_field_transitions_block_b3d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB402..0xB40C. */
REGION void tsl9_feature_external_b402(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_field_transitions_edge_b408:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_b408\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b51e\n");
    __builtin_unreachable();
}

/* Original0xB40C..0xB432. */
REGION void tsl9_record_field_transitions_block_b40c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffad2)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc s2, 0x20001\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, -1338\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_b42e:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_b42e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b448\n");
    __builtin_unreachable();
}

/* Original0xB432..0xB448. */
REGION void tsl9_record_field_transitions_block_b432(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffaba)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffab3)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_b444:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_b444\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xB448..0xB45E. */
REGION void tsl9_record_field_transitions_block_b448(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffaa7)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa9e)); LIVE;
    PORT(".option push\n.option rvc\nli s1, 0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_b45a:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_b45a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b470\n");
    __builtin_unreachable();
}

/* Original0xB45E..0xB470. */
REGION void tsl9_record_field_transitions_block_b45e(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB470..0xB484. */
REGION void tsl9_record_field_transitions_block_b470(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa78)); LIVE;
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_field_transitions_edge_b480:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_b480\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b494\n");
    __builtin_unreachable();
}

/* Original0xB484..0xB494. */
REGION void tsl9_record_field_transitions_block_b484(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa68)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa61)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xB494..0xB4A8. */
REGION void tsl9_record_field_transitions_block_b494(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa59)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffa50)); LIVE;
    PORT(".Lrecord_field_transitions_edge_b4a4:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_b4a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b4bc\n");
    __builtin_unreachable();
}

/* Original0xB4A8..0xB4BC. */
REGION void tsl9_record_field_transitions_block_b4a8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    a5 = a5 << UINT32_C(0x00000004); LIVE;
    a4 = a4 & UINT32_C(0xffffffcf); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB4BC..0xB4C2. */
REGION void tsl9_record_field_transitions_block_b4bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 4(s2)\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_b4c0:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_b4c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_b4d2\n");
    __builtin_unreachable();
}

/* Original0xB4C2..0xB4C6. */
REGION void tsl9_record_field_transitions_block_b4c2(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_b4c2:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_b4c2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xB4C6..0xB4CE. */
REGION void tsl9_record_field_transitions_block_b4c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 4(s2)\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_b4ca:\n.option push\n.option norvc\nbltu a0,a5,.Lrecord_field_transitions_edge_b4ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_b4e0\n");
    __builtin_unreachable();
}

/* Original0xB4CE..0xB4D2. */
REGION void tsl9_record_field_transitions_block_b4ce(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_transitions_edge_b4d0:\n.option push\n.option rvc\nc.jal .Lrecord_field_transitions_edge_b4d0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_settings_state_inputs_entry_b254\n");
    __builtin_unreachable();
}

/* Original0xB4D2..0xB4D4. */
REGION void tsl9_record_field_transitions_block_b4d2(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_b4d2:\n.option push\n.option rvc\nc.bnez s1,.Lrecord_field_transitions_edge_b4d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_b50e\n");
    __builtin_unreachable();
}

/* Original0xB4D4..0xB4E0. */
REGION void tsl9_record_field_transitions_block_b4d4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB4E0..0xB4E4. */
REGION void tsl9_record_field_transitions_block_b4e0(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_b4e0:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_b4e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_f65c\n");
    __builtin_unreachable();
}

/* Original0xB4E4..0xB4E6. */
REGION void tsl9_record_field_transitions_block_b4e4(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_b4e4:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_field_transitions_edge_b4e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_b4ce\n");
    __builtin_unreachable();
}

/* Original0xB4E6..0xB4EA. */
REGION void tsl9_record_field_transitions_block_b4e6(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_b4e6:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_b4e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d3e8\n");
    __builtin_unreachable();
}

/* Original0xB4EA..0xB4EC. */
REGION void tsl9_record_field_transitions_block_b4ea(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_b4ea:\n.option push\n.option rvc\nc.bnez a0,.Lrecord_field_transitions_edge_b4ea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_b4ce\n");
    __builtin_unreachable();
}

/* Original0xB4EC..0xB4FC. */
REGION void tsl9_record_field_transitions_block_b4ec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x0000001c); LIVE;
    a4 = a4 + UINT32_C(0xfffffffc); LIVE;
    a4 = a4 & UINT32_C(0x000000f8); LIVE;
    PORT(".Lrecord_field_transitions_edge_b4fa:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_transitions_edge_b4fa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_b4ce\n");
    __builtin_unreachable();
}

/* Original0xB4FC..0xB50E. */
REGION void tsl9_record_field_transitions_block_b4fc(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffe3); LIVE;
    a4 = UINT32_C(0x00000065); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".option push\n.option norvc\nsb a4, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB50E..0xB51E. */
REGION void tsl9_record_field_transitions_block_b50e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_b51a:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_b51a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xB51E..0xB520. */
REGION void tsl9_record_field_transitions_block_b51e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC8A2..0xC8B4. */
REGION void tsl9_feature_external_c8a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000067f)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_c8b2:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_transitions_edge_c8b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_c8ce\n");
    __builtin_unreachable();
}

/* Original0xC8B4..0xC8BA. */
REGION void tsl9_record_field_transitions_block_c8b4(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    PORT(".Lrecord_field_transitions_edge_c8b8:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_transitions_edge_c8b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_c8c6\n");
    __builtin_unreachable();
}

/* Original0xC8BA..0xC8C6. */
REGION void tsl9_record_field_transitions_block_c8ba(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 + UINT32_C(0xffffff90); LIVE;
    a5 = (uint32_t)(a5 == UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0xC8C6..0xC8CE. */
REGION void tsl9_record_field_transitions_block_c8c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000661)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xC8CE..0xC8D8. */
REGION void tsl9_record_field_transitions_block_c8ce(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_field_transitions_edge_c8d4:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_transitions_edge_c8d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c8e4\n");
    __builtin_unreachable();
}

/* Original0xC8D8..0xC8E4. */
REGION void tsl9_record_field_transitions_block_c8d8(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffff7); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_c8e0:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_field_transitions_edge_c8e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c906\n");
    __builtin_unreachable();
}

/* Original0xC8E4..0xC8F6. */
REGION void tsl9_record_field_transitions_block_c8e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_field_transitions_edge_c8f2:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_field_transitions_edge_c8f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c946\n");
    __builtin_unreachable();
}

/* Original0xC8F6..0xC8FA. */
REGION void tsl9_record_field_transitions_block_c8f6(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_c8f6:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_c8f6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a658\n");
    __builtin_unreachable();
}

/* Original0xC8FA..0xC906. */
REGION void tsl9_record_field_transitions_block_c8fa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_c902:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_c902\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_fe6a\n");
    __builtin_unreachable();
}

/* Original0xC906..0xC922. */
REGION void tsl9_record_field_transitions_block_c906(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x1ffff\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000626); LIVE;
    a1 = UINT32_C(0x00000043); LIVE;
    a0 = a0 >> UINT32_C(0x00000004); LIVE;
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    a0 = a0 + UINT32_C(0x00000043); LIVE;
    PORT(".Lrecord_field_transitions_edge_c91e:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_c91e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_ebac\n");
    __builtin_unreachable();
}

/* Original0xC922..0xC92A. */
REGION void tsl9_record_field_transitions_block_c922(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lrecord_field_transitions_edge_c928:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_c928\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_c934\n");
    __builtin_unreachable();
}

/* Original0xC92A..0xC92E. */
REGION void tsl9_record_field_transitions_block_c92a(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_c92a:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_c92a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a658\n");
    __builtin_unreachable();
}

/* Original0xC92E..0xC934. */
REGION void tsl9_record_field_transitions_block_c92e(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_c930:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_c930\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_fe6a\n");
    __builtin_unreachable();
}

/* Original0xC934..0xC946. */
REGION void tsl9_record_field_transitions_block_c934(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 4(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000004); LIVE;
    a0 = a0 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_c942:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_c942\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_ed36\n");
    __builtin_unreachable();
}

/* Original0xC946..0xC94E. */
REGION void tsl9_record_field_transitions_block_c946(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC94E..0xC960. */
REGION void tsl9_feature_external_c94e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_c95c:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_transitions_edge_c95c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c96c\n");
    __builtin_unreachable();
}

/* Original0xC960..0xC96C. */
REGION void tsl9_record_field_transitions_block_c960(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffff7); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_c968:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_field_transitions_edge_c968\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_ca00\n");
    __builtin_unreachable();
}

/* Original0xC96C..0xC976. */
REGION void tsl9_record_field_transitions_block_c96c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1ffff\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x000005c0)); LIVE;
    PORT(".Lrecord_field_transitions_edge_c974:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_field_transitions_edge_c974\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_c9aa\n");
    __builtin_unreachable();
}

/* Original0xC976..0xC990. */
REGION void tsl9_record_field_transitions_block_c976(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000004); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005a7)); LIVE;
    PORT(".Lrecord_field_transitions_edge_c98c:\n.option push\n.option norvc\nbeq a4,a2,.Lrecord_field_transitions_edge_c98c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c9e2\n");
    __builtin_unreachable();
}

/* Original0xC990..0xC994. */
REGION void tsl9_record_field_transitions_block_c990(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_c990:\n.option push\n.option norvc\nbltu a2,a4,.Lrecord_field_transitions_edge_c990\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c9b2\n");
    __builtin_unreachable();
}

/* Original0xC994..0xC99A. */
REGION void tsl9_record_field_transitions_block_c994(void)
{
    REGS;
    a2 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_c996:\n.option push\n.option norvc\nbeq a4,a2,.Lrecord_field_transitions_edge_c996\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c9e2\n");
    __builtin_unreachable();
}

/* Original0xC99A..0xC9A4. */
REGION void tsl9_record_field_transitions_block_c99a(void)
{
    REGS;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000590)) = (uint8_t)a3; LIVE;
    __builtin_unreachable();
}

/* Original0xC9A4..0xC9AA. */
REGION void tsl9_record_field_transitions_block_c9a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_c9a6:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_c9a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xC9AA..0xC9B2. */
REGION void tsl9_record_field_transitions_block_c9aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC9B2..0xC9B8. */
REGION void tsl9_record_field_transitions_block_c9b2(void)
{
    REGS;
    a2 = UINT32_C(0x00000006); LIVE;
    PORT(".Lrecord_field_transitions_edge_c9b4:\n.option push\n.option norvc\nbeq a4,a2,.Lrecord_field_transitions_edge_c9b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c9be\n");
    __builtin_unreachable();
}

/* Original0xC9B8..0xC9BE. */
REGION void tsl9_record_field_transitions_block_c9b8(void)
{
    REGS;
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".Lrecord_field_transitions_edge_c9ba:\n.option push\n.option norvc\nbne a4,a2,.Lrecord_field_transitions_edge_c9ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c99a\n");
    __builtin_unreachable();
}

/* Original0xC9BE..0xC9DC. */
REGION void tsl9_record_field_transitions_block_c9be(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_literal_c9be:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_data_19eb8\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_c9be\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffffd6); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    a5 = UINT32_C(0x0000006d); LIVE;
    __builtin_unreachable();
}

/* Original0xC9DC..0xC9E2. */
REGION void tsl9_record_field_transitions_block_c9dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_c9e0:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_c9e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_c99a\n");
    __builtin_unreachable();
}

/* Original0xC9E2..0xCA00. */
REGION void tsl9_record_field_transitions_block_c9e2(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_literal_c9e2:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_data_19ec8\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_c9e2\n.option pop\n");
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0xffffffe2); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000072); LIVE;
    PORT(".Lrecord_field_transitions_edge_c9fe:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_c9fe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_c9dc\n");
    __builtin_unreachable();
}

/* Original0xCA00..0xCA0E. */
REGION void tsl9_record_field_transitions_block_ca00(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)0; LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lrecord_field_transitions_edge_ca0c:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_ca0c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_ca12\n");
    __builtin_unreachable();
}

/* Original0xCA0E..0xCA12. */
REGION void tsl9_record_field_transitions_block_ca0e(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_ca0e:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_ca0e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_action_support_entry_a02e\n");
    __builtin_unreachable();
}

/* Original0xCA12..0xCA1C. */
REGION void tsl9_record_field_transitions_block_ca12(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000518)); LIVE;
    PORT(".Lrecord_field_transitions_edge_ca1a:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_ca1a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_ca3c\n");
    __builtin_unreachable();
}

/* Original0xCA1C..0xCA3C. */
REGION void tsl9_record_field_transitions_block_ca1c(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004fc)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xCA3C..0xCA46. */
REGION void tsl9_record_field_transitions_block_ca3c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000004f0)); LIVE;
    PORT(".Lrecord_field_transitions_edge_ca44:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_transitions_edge_ca44\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_ca72\n");
    __builtin_unreachable();
}

/* Original0xCA46..0xCA72. */
REGION void tsl9_record_field_transitions_block_ca46(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = a5 + UINT32_C(0x000004de); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a3 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff0); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004c8)) = (uint8_t)a4; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xCA72..0xCA7A. */
REGION void tsl9_record_field_transitions_block_ca72(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, sp, 15\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_ca76:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_ca76\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_c7e8\n");
    __builtin_unreachable();
}

/* Original0xCA7A..0xCA7C. */
REGION void tsl9_record_field_transitions_block_ca7a(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_ca7a:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_transitions_edge_ca7a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cb38\n");
    __builtin_unreachable();
}

/* Original0xCA7C..0xCA92. */
REGION void tsl9_record_field_transitions_block_ca7c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000020); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_ca8e:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_field_transitions_edge_ca8e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cacc\n");
    __builtin_unreachable();
}

/* Original0xCA92..0xCAA2. */
REGION void tsl9_record_field_transitions_block_ca92(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_ca9e:\n.option push\n.option norvc\nbleu a5,a4,.Lrecord_field_transitions_edge_ca9e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cacc\n");
    __builtin_unreachable();
}

/* Original0xCAA2..0xCAB2. */
REGION void tsl9_record_field_transitions_block_caa2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000716); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000020)); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_cab0:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_cab0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cacc\n");
    __builtin_unreachable();
}

/* Original0xCAB2..0xCAC2. */
REGION void tsl9_record_field_transitions_block_cab2(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000ba)); LIVE;
    a4 = UINT32_C(0x00000030); LIVE;
    a5 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_cabe:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_field_transitions_edge_cabe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cacc\n");
    __builtin_unreachable();
}

/* Original0xCAC2..0xCAC4. */
REGION void tsl9_record_field_transitions_block_cac2(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    __builtin_unreachable();
}

/* Original0xCAC4..0xCAC8. */
REGION void tsl9_record_field_transitions_block_cac4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e3)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xCAC8..0xCACC. */
REGION void tsl9_record_field_transitions_block_cac8(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_caca:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_caca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cae4\n");
    __builtin_unreachable();
}

/* Original0xCACC..0xCAE2. */
REGION void tsl9_record_field_transitions_block_cacc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 << UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0xffffffcf); LIVE;
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option norvc\nsb a0, 4(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCAE2..0xCAE4. */
REGION void tsl9_record_field_transitions_block_cae2(void)
{
    REGS;
    a5 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0xCAE4..0xCAEE. */
REGION void tsl9_record_field_transitions_block_cae4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000440)); LIVE;
    PORT(".Lrecord_field_transitions_edge_caec:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_field_transitions_edge_caec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cbc0\n");
    __builtin_unreachable();
}

/* Original0xCAEE..0xCAF2. */
REGION void tsl9_record_field_transitions_block_caee(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_caee:\n.option push\n.option norvc\nbnez a5,.Lrecord_field_transitions_edge_caee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cc10\n");
    __builtin_unreachable();
}

/* Original0xCAF2..0xCAFA. */
REGION void tsl9_record_field_transitions_block_caf2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)); LIVE;
    PORT(".Lrecord_field_transitions_edge_caf6:\n.option push\n.option norvc\nbeqz a5,.Lrecord_field_transitions_edge_caf6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_c9aa\n");
    __builtin_unreachable();
}

/* Original0xCAFA..0xCB18. */
REGION void tsl9_record_field_transitions_block_cafa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a3 = a5 + UINT32_C(0x00000001); LIVE;
    a3 = a3 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 & UINT32_C(0xfffffff0); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x000000c0); LIVE;
    a2 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb14:\n.option push\n.option norvc\nbnez a4,.Lrecord_field_transitions_edge_cb14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cc3e\n");
    __builtin_unreachable();
}

/* Original0xCB18..0xCB1A. */
REGION void tsl9_record_field_transitions_block_cb18(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_cb18:\n.option push\n.option rvc\nc.beqz a2,.Lrecord_field_transitions_edge_cb18\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cb1c\n");
    __builtin_unreachable();
}

/* Original0xCB1A..0xCB1C. */
REGION void tsl9_record_field_transitions_block_cb1a(void)
{
    REGS;
    a4 = UINT32_C(0x0000000a); LIVE;
    __builtin_unreachable();
}

/* Original0xCB1C..0xCB2E. */
REGION void tsl9_record_field_transitions_block_cb1c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a4 = a4 + a5; LIVE;
    a4 = a4 << UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_transitions_literal_cb26:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_static_data_19ed8\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_cb26\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCB2E..0xCB38. */
REGION void tsl9_record_field_transitions_block_cb2e(void)
{
    REGS;
    a5 = a5 + a4; LIVE;
    a5 = a5 + a3; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb36:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cb36\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cc38\n");
    __builtin_unreachable();
}

/* Original0xCB38..0xCB4A. */
REGION void tsl9_record_field_transitions_block_cb38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 4(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000010); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e3)); LIVE;
    a4 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb46:\n.option push\n.option norvc\nbne a4,a3,.Lrecord_field_transitions_edge_cb46\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cba6\n");
    __builtin_unreachable();
}

/* Original0xCB4A..0xCB50. */
REGION void tsl9_record_field_transitions_block_cb4a(void)
{
    REGS;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb4c:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_field_transitions_edge_cb4c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cb9a\n");
    __builtin_unreachable();
}

/* Original0xCB50..0xCB66. */
REGION void tsl9_record_field_transitions_block_cb50(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000020); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb62:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_field_transitions_edge_cb62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCB66..0xCB76. */
REGION void tsl9_record_field_transitions_block_cb66(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb72:\n.option push\n.option norvc\nbleu a5,a4,.Lrecord_field_transitions_edge_cb72\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCB76..0xCB86. */
REGION void tsl9_record_field_transitions_block_cb76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = a4 + UINT32_C(0x00000642); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000020)); LIVE;
    a5 = a5 & UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb84:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_cb84\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCB86..0xCB96. */
REGION void tsl9_record_field_transitions_block_cb86(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000000ba)); LIVE;
    a4 = UINT32_C(0x00000030); LIVE;
    a5 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb92:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_field_transitions_edge_cb92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCB96..0xCB9A. */
REGION void tsl9_record_field_transitions_block_cb96(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb98:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cb98\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cac4\n");
    __builtin_unreachable();
}

/* Original0xCB9A..0xCBA0. */
REGION void tsl9_record_field_transitions_block_cb9a(void)
{
    REGS;
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".Lrecord_field_transitions_edge_cb9c:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_transitions_edge_cb9c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCBA0..0xCBA6. */
REGION void tsl9_record_field_transitions_block_cba0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e3)) = (uint8_t)a4; LIVE;
    PORT(".Lrecord_field_transitions_edge_cba4:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cba4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCBA6..0xCBA8. */
REGION void tsl9_record_field_transitions_block_cba6(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_cba6:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_cba6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCBA8..0xCBB4. */
REGION void tsl9_record_field_transitions_block_cba8(void)
{
    REGS;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lrecord_field_transitions_edge_cbb0:\n.option push\n.option norvc\nbltu a4,a5,.Lrecord_field_transitions_edge_cbb0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cbba\n");
    __builtin_unreachable();
}

/* Original0xCBB4..0xCBBA. */
REGION void tsl9_record_field_transitions_block_cbb4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e3)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_cbb8:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cbb8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cae2\n");
    __builtin_unreachable();
}

/* Original0xCBBA..0xCBC0. */
REGION void tsl9_record_field_transitions_block_cbba(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e3)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_field_transitions_edge_cbbe:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cbbe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cac8\n");
    __builtin_unreachable();
}

/* Original0xCBC0..0xCBDE. */
REGION void tsl9_record_field_transitions_block_cbc0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000364)) = (uint8_t)0; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = original_gp + UINT32_C(0x00000054); LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a3 = UINT32_C(0x00000020); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000007)); LIVE;
    a4 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_cbda:\n.option push\n.option norvc\nbne a4,a3,.Lrecord_field_transitions_edge_cbda\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_caee\n");
    __builtin_unreachable();
}

/* Original0xCBDE..0xCBEE. */
REGION void tsl9_record_field_transitions_block_cbde(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_cbea:\n.option push\n.option norvc\nbleu a4,a3,.Lrecord_field_transitions_edge_cbea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_caee\n");
    __builtin_unreachable();
}

/* Original0xCBEE..0xCC00. */
REGION void tsl9_record_field_transitions_block_cbee(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1ffff\n.option pop\n");
    a3 = a3 + UINT32_C(0x000005ca); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000020)); LIVE;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_cbfc:\n.option push\n.option norvc\nbeqz a4,.Lrecord_field_transitions_edge_cbfc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_caee\n");
    __builtin_unreachable();
}

/* Original0xCC00..0xCC10. */
REGION void tsl9_record_field_transitions_block_cc00(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x000000ba)); LIVE;
    a3 = UINT32_C(0x00000030); LIVE;
    a4 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".Lrecord_field_transitions_edge_cc0c:\n.option push\n.option norvc\nbne a4,a3,.Lrecord_field_transitions_edge_cc0c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_caee\n");
    __builtin_unreachable();
}

/* Original0xCC10..0xCC38. */
REGION void tsl9_record_field_transitions_block_cc10(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffcf); LIVE;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    a4 = a5 + UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 & UINT32_C(0xfffffff0); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".Lrecord_field_transitions_literal_cc2a:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_data_19ea8\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_cc2a\n.option pop\n");
    a4 = a4 + a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    __builtin_unreachable();
}

/* Original0xCC38..0xCC3E. */
REGION void tsl9_record_field_transitions_block_cc38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_cc3c:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cc3c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_c9a4\n");
    __builtin_unreachable();
}

/* Original0xCC3E..0xCC42. */
REGION void tsl9_record_field_transitions_block_cc3e(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_transitions_edge_cc40:\n.option push\n.option rvc\nc.beqz a2,.Lrecord_field_transitions_edge_cc40\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cc44\n");
    __builtin_unreachable();
}

/* Original0xCC42..0xCC44. */
REGION void tsl9_record_field_transitions_block_cc42(void)
{
    REGS;
    a4 = UINT32_C(0x00000003); LIVE;
    __builtin_unreachable();
}

/* Original0xCC44..0xCC54. */
REGION void tsl9_record_field_transitions_block_cc44(void)
{
    REGS;
    a5 = a5 >> UINT32_C(0x00000006); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 << UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_transitions_literal_cc4a:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_static_data_1a018\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_cc4a\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_cc52:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cc52\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cb2e\n");
    __builtin_unreachable();
}

/* Original0xCEC0..0xCEDC. */
REGION void tsl9_feature_external_cec0(void)
{
    REGS;
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x1ffff\n.option pop\n");
    a2 = a2 + UINT32_C(0x00000078); LIVE;
    a1 = UINT32_C(0x00000039); LIVE;
    a0 = a0 >> UINT32_C(0x00000004); LIVE;
    a0 = a0 & UINT32_C(0x00000007); LIVE;
    a0 = a0 + UINT32_C(0x00000039); LIVE;
    PORT(".Lrecord_field_transitions_edge_ced8:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_ced8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_ebac\n");
    __builtin_unreachable();
}

/* Original0xCEDC..0xCEE6. */
REGION void tsl9_feature_external_cedc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000005c)); LIVE;
    PORT(".Lrecord_field_transitions_edge_cee4:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_cee4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cf94\n");
    __builtin_unreachable();
}

/* Original0xCEE6..0xCEFA. */
REGION void tsl9_record_field_transitions_block_cee6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000054)); LIVE;
    a3 = UINT32_C(0x000000ff); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".Lrecord_field_transitions_edge_cef6:\n.option push\n.option norvc\nbne a4,a3,.Lrecord_field_transitions_edge_cef6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cf66\n");
    __builtin_unreachable();
}

/* Original0xCEFA..0xCF1E. */
REGION void tsl9_record_field_transitions_block_cefa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1ffff\n.option pop\n");
    a3 = a3 + UINT32_C(0x0000003e); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000033)); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000027)) = (uint8_t)a3; LIVE;
    PORT(".Lrecord_field_transitions_edge_cf1c:\n.option push\n.option rvc\nc.beqz a3,.Lrecord_field_transitions_edge_cf1c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cf8a\n");
    __builtin_unreachable();
}

/* Original0xCF1E..0xCF24. */
REGION void tsl9_record_field_transitions_block_cf1e(void)
{
    REGS;
    a3 = UINT32_C(0x00000005); LIVE;
    PORT(".Lrecord_field_transitions_edge_cf20:\n.option push\n.option norvc\nbne a4,a3,.Lrecord_field_transitions_edge_cf20\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_cf7c\n");
    __builtin_unreachable();
}

/* Original0xCF24..0xCF36. */
REGION void tsl9_record_field_transitions_block_cf24(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 & UINT32_C(0xffffff8f); LIVE;
    a3 = a3 & UINT32_C(0xfffffffc); LIVE;
    a3 = a3 | UINT32_C(0x00000001); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)) = (uint8_t)a3; LIVE;
    __builtin_unreachable();
}

/* Original0xCF36..0xCF66. */
REGION void tsl9_record_field_transitions_block_cf36(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 << UINT32_C(0x00000004); LIVE;
    a3 = a5 + UINT32_C(0x00000001); LIVE;
    a3 = a3 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 & UINT32_C(0xfffffff0); LIVE;
    a5 = a5 | a3; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_literal_cf4e:\n.option push\n.option norvc\nauipc a5,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_static_data_1a078\naddi a5,a5,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_cf4e\n.option pop\n");
    a4 = a4 + a5; LIVE;
    a4 = a4 + a3; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_cf62:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_cf62\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xCF66..0xCF7A. */
REGION void tsl9_record_field_transitions_block_cf66(void)
{
    REGS;
    a2 = UINT32_C(0x00000003); LIVE;
    a3 = a4 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nrem a3, a3, a2\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0xffffffca)) = (uint8_t)a3; LIVE;
    PORT(".Lrecord_field_transitions_edge_cf78:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_transitions_edge_cf78\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_cefa\n");
    __builtin_unreachable();
}

/* Original0xCF7A..0xCF7C. */
REGION void tsl9_record_field_transitions_block_cf7a(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0xCF7C..0xCF8A. */
REGION void tsl9_record_field_transitions_block_cf7c(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x00000007); LIVE;
    a3 = a3 << UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0xffffff8f); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".Lrecord_field_transitions_edge_cf88:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cf88\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cf36\n");
    __builtin_unreachable();
}

/* Original0xCF8A..0xCF94. */
REGION void tsl9_record_field_transitions_block_cf8a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xffffffae)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_field_transitions_edge_cf92:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_cf92\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_cf1e\n");
    __builtin_unreachable();
}

/* Original0xCF94..0xCF96. */
REGION void tsl9_record_field_transitions_block_cf94(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD14A..0xD162. */
REGION void tsl9_feature_external_d14a(void)
{
    REGS;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e8)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d15e:\n.option push\n.option norvc\nbne a1,a2,.Lrecord_field_transitions_edge_d15e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d17a\n");
    __builtin_unreachable();
}

/* Original0xD162..0xD16A. */
REGION void tsl9_record_field_transitions_block_d162(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e9)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d166:\n.option push\n.option norvc\nbne a1,a3,.Lrecord_field_transitions_edge_d166\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d17a\n");
    __builtin_unreachable();
}

/* Original0xD16A..0xD172. */
REGION void tsl9_record_field_transitions_block_d16a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ea)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d16e:\n.option push\n.option norvc\nbne a1,a4,.Lrecord_field_transitions_edge_d16e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d17a\n");
    __builtin_unreachable();
}

/* Original0xD172..0xD17A. */
REGION void tsl9_record_field_transitions_block_d172(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a1 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000eb)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d176:\n.option push\n.option norvc\nbeq a1,a5,.Lrecord_field_transitions_edge_d176\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d18e\n");
    __builtin_unreachable();
}

/* Original0xD17A..0xD18E. */
REGION void tsl9_record_field_transitions_block_d17a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e8)) = (uint8_t)a2; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000e9)) = (uint8_t)a3; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ea)) = (uint8_t)a4; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000eb)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_d18a:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_d18a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xD18E..0xD190. */
REGION void tsl9_record_field_transitions_block_d18e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD1B2..0xD1BC. */
REGION void tsl9_feature_external_d1b2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffd96)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d1ba:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_transitions_edge_d1ba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_d266\n");
    __builtin_unreachable();
}

/* Original0xD1BC..0xD1C2. */
REGION void tsl9_record_field_transitions_block_d1bc(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ec)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d1c0:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_transitions_edge_d1c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_d1ea\n");
    __builtin_unreachable();
}

/* Original0xD1C2..0xD1CC. */
REGION void tsl9_record_field_transitions_block_d1c2(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = UINT32_C(0x00000010); LIVE;
    PORT(".Lrecord_field_transitions_edge_d1c8:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_d1c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d26c\n");
    __builtin_unreachable();
}

/* Original0xD1CC..0xD1E8. */
REGION void tsl9_record_field_transitions_block_d1cc(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ec)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option norvc\nlw t1, 76(a5)\n.option pop\n");
    a1 = a0 + UINT32_C(0x00000008); LIVE;
    a2 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffd69); LIVE;
    __builtin_unreachable();
}

/* Original0xD1E8..0xD1EA. */
REGION void tsl9_record_field_transitions_block_d1e8(void)
{
    REGS;
    PORT(".option push\n.option rvc\njr t1\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD1EA..0xD1F6. */
REGION void tsl9_record_field_transitions_block_d1ea(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_d1f2:\n.option push\n.option norvc\nbne a5,s0,.Lrecord_field_transitions_edge_d1f2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d224\n");
    __builtin_unreachable();
}

/* Original0xD1F6..0xD200. */
REGION void tsl9_record_field_transitions_block_d1f6(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = UINT32_C(0x00000011); LIVE;
    PORT(".Lrecord_field_transitions_edge_d1fc:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_d1fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d260\n");
    __builtin_unreachable();
}

/* Original0xD200..0xD224. */
REGION void tsl9_record_field_transitions_block_d200(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ec)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00040000); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlw t1, 76(a5)\n.option pop\n");
    a1 = a0 + UINT32_C(0x00000004); LIVE;
    a2 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffd34); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_d222:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_d222\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_d1e8\n");
    __builtin_unreachable();
}

/* Original0xD224..0xD22A. */
REGION void tsl9_record_field_transitions_block_d224(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_d226:\n.option push\n.option norvc\nbne a5,a4,.Lrecord_field_transitions_edge_d226\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d260\n");
    __builtin_unreachable();
}

/* Original0xD22A..0xD234. */
REGION void tsl9_record_field_transitions_block_d22a(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = UINT32_C(0x00000012); LIVE;
    PORT(".Lrecord_field_transitions_edge_d230:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_d230\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d260\n");
    __builtin_unreachable();
}

/* Original0xD234..0xD250. */
REGION void tsl9_record_field_transitions_block_d234(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ec)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    a1 = a0 + UINT32_C(0x00000004); LIVE;
    a2 = UINT32_C(0x00000007); LIVE;
    PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = a0 + UINT32_C(0xfffffd0d); LIVE;
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD250..0xD258. */
REGION void tsl9_record_field_transitions_block_d250(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, -776(a5)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD258..0xD260. */
REGION void tsl9_record_field_transitions_block_d258(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD260..0xD266. */
REGION void tsl9_record_field_transitions_block_d260(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ec)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_field_transitions_edge_d264:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_d264\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_d258\n");
    __builtin_unreachable();
}

/* Original0xD266..0xD26C. */
REGION void tsl9_record_field_transitions_block_d266(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_d268:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_d268\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_12ad0\n");
    __builtin_unreachable();
}

/* Original0xD26C..0xD272. */
REGION void tsl9_record_field_transitions_block_d26c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000ec)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD288..0xD2A6. */
REGION void tsl9_feature_external_d288(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlhu s0, 2(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nc.srli s0,0xa\n.option pop\n");
    PORT(".option push\n.option rvc\nandi s0, s0, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffcc5)); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_d2a2:\n.option push\n.option norvc\nbeq a5,s0,.Lrecord_field_transitions_edge_d2a2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d2b4\n");
    __builtin_unreachable();
}

/* Original0xD2A6..0xD2B4. */
REGION void tsl9_record_field_transitions_block_d2a6(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s0, -843(a5)\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_d2b0:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_d2b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xD2B4..0xD2BE. */
REGION void tsl9_record_field_transitions_block_d2b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffca8)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d2bc:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_d2bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_d2e4\n");
    __builtin_unreachable();
}

/* Original0xD2BE..0xD2C0. */
REGION void tsl9_record_field_transitions_block_d2be(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_d2be:\n.option push\n.option rvc\nc.bnez s0,.Lrecord_field_transitions_edge_d2be\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_d2e4\n");
    __builtin_unreachable();
}

/* Original0xD2C0..0xD2D6. */
REGION void tsl9_record_field_transitions_block_d2c0(void)
{
    REGS;
    a5 = UINT32_C(0x00040000); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000004c)); LIVE;
    PORT(".option push\n.option norvc\naddi a0, s1, 3\n.option pop\n");
    a2 = UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_field_transitions_literal_d2cc:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_field_transitions_data_1a0d8\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lrecord_field_transitions_literal_d2cc\n.option pop\n");
    PORT(".option push\n.option rvc\njalr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD2D6..0xD2E4. */
REGION void tsl9_record_field_transitions_block_d2d6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_d2e0:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_d2e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xD2E4..0xD2EE. */
REGION void tsl9_record_field_transitions_block_d2e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD378..0xD382. */
REGION void tsl9_feature_external_d378(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffbe6)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d380:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_transitions_edge_d380\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_d3c4\n");
    __builtin_unreachable();
}

/* Original0xD382..0xD39E. */
REGION void tsl9_record_field_transitions_block_d382(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a3 = a4 & UINT32_C(0x00000003); LIVE;
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | a3; LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_d39a:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_d39a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d3aa\n");
    __builtin_unreachable();
}

/* Original0xD39E..0xD3AA. */
REGION void tsl9_record_field_transitions_block_d39e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xD3AA..0xD3B8. */
REGION void tsl9_record_field_transitions_block_d3aa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbb2)) = (uint8_t)0; LIVE;
    PORT(".Lrecord_field_transitions_edge_d3b4:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_d3b4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xD3B8..0xD3C4. */
REGION void tsl9_record_field_transitions_block_d3b8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_d3c0:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_d3c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xD3C4..0xD3C6. */
REGION void tsl9_record_field_transitions_block_d3c4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD3F6..0xD3FE. */
REGION void tsl9_feature_external_d3f6(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lrecord_field_transitions_edge_d3fc:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_d3fc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_d406\n");
    __builtin_unreachable();
}

/* Original0xD3FE..0xD404. */
REGION void tsl9_record_field_transitions_block_d3fe(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_d400:\n.option push\n.option norvc\nbeq a5,a4,.Lrecord_field_transitions_edge_d400\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d42a\n");
    __builtin_unreachable();
}

/* Original0xD404..0xD406. */
REGION void tsl9_record_field_transitions_block_d404(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD406..0xD41E. */
REGION void tsl9_record_field_transitions_block_d406(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb50)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d41a:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_d41a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d466\n");
    __builtin_unreachable();
}

/* Original0xD41E..0xD426. */
REGION void tsl9_record_field_transitions_block_d41e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb44)) = (uint16_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xD426..0xD42A. */
REGION void tsl9_record_field_transitions_block_d426(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_d426:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_d426\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xD42A..0xD45C. */
REGION void tsl9_record_field_transitions_block_d42a(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a3 = a4 >> UINT32_C(0x00000002); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a4 = a4 & UINT32_C(0x0000003f); LIVE;
    a4 = a4 << UINT32_C(0x00000006); LIVE;
    a4 = a4 | a3; LIVE;
    a5 = a5 + a4; LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb10)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d458:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_d458\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d466\n");
    __builtin_unreachable();
}

/* Original0xD45C..0xD466. */
REGION void tsl9_record_field_transitions_block_d45c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffb04)) = (uint16_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_d464:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_d464\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_d426\n");
    __builtin_unreachable();
}

/* Original0xD466..0xD468. */
REGION void tsl9_record_field_transitions_block_d466(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD47C..0xD488. */
REGION void tsl9_feature_external_d47c(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000008)); LIVE;
    a5 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lrecord_field_transitions_edge_d484:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_d484\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d4d4\n");
    __builtin_unreachable();
}

/* Original0xD488..0xD49A. */
REGION void tsl9_record_field_transitions_block_d488(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a4 = a5 >> UINT32_C(0x00000004); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 & UINT32_C(0x00000007); LIVE;
    a5 = a5 << UINT32_C(0x00000004); LIVE;
    a5 = a5 | a4; LIVE;
    __builtin_unreachable();
}

/* Original0xD49A..0xD4B4. */
REGION void tsl9_record_field_transitions_block_d49a(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a4 = a4 & UINT32_C(0x00000003); LIVE;
    a4 = a4 << UINT32_C(0x00000008); LIVE;
    a4 = a4 | a3; LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x1ffff\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xfffffabc)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d4b0:\n.option push\n.option norvc\nbne a3,a5,.Lrecord_field_transitions_edge_d4b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d4c0\n");
    __builtin_unreachable();
}

/* Original0xD4B4..0xD4C0. */
REGION void tsl9_record_field_transitions_block_d4b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1ffff\n.option pop\n");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffffab2)); LIVE;
    PORT(".Lrecord_field_transitions_edge_d4bc:\n.option push\n.option norvc\nbeq a3,a4,.Lrecord_field_transitions_edge_d4bc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_d4de\n");
    __builtin_unreachable();
}

/* Original0xD4C0..0xD4D4. */
REGION void tsl9_record_field_transitions_block_d4c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xfffffaa4)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1ffff\n.option pop\n");
    *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffffa9e)) = (uint16_t)a4; LIVE;
    PORT(".Lrecord_field_transitions_edge_d4d0:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_d4d0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xD4D4..0xD4DE. */
REGION void tsl9_record_field_transitions_block_d4d4(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)); LIVE;
    a5 = a5 & UINT32_C(0x0000007f); LIVE;
    PORT(".Lrecord_field_transitions_edge_d4dc:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_d4dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_d49a\n");
    __builtin_unreachable();
}

/* Original0xD4DE..0xD4E0. */
REGION void tsl9_record_field_transitions_block_d4de(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10288..0x102A8. */
REGION void tsl9_feature_external_10288(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s0, 7(a0)\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nandi s0, s0, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s0, s0, 0x8\n.option pop\n");
    PORT(".option push\n.option rvc\nor s0, s0, a5\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x000001ff); LIVE;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_102a4:\n.option push\n.option norvc\nbne s0,a5,.Lrecord_field_transitions_edge_102a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_102aa\n");
    __builtin_unreachable();
}

/* Original0x102A8..0x102AA. */
REGION void tsl9_record_field_transitions_block_102a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 0\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x102AA..0x102B2. */
REGION void tsl9_record_field_transitions_block_102aa(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000050)); LIVE;
    PORT(".Lrecord_field_transitions_edge_102ae:\n.option push\n.option norvc\nbeq a5,s0,.Lrecord_field_transitions_edge_102ae\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_103ca\n");
    __builtin_unreachable();
}

/* Original0x102B2..0x102C4. */
REGION void tsl9_record_field_transitions_block_102b2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsh s0, 80(gp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_transitions_edge_102c2:\n.option push\n.option rvc\nc.beqz a5,.Lrecord_field_transitions_edge_102c2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_1030a\n");
    __builtin_unreachable();
}

/* Original0x102C4..0x102CC. */
REGION void tsl9_record_field_transitions_block_102c4(void)
{
    REGS;
    a5 = UINT32_C(0x00000089); LIVE;
    PORT(".Lrecord_field_transitions_edge_102c8:\n.option push\n.option norvc\nbleu s0,a5,.Lrecord_field_transitions_edge_102c8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_10306\n");
    __builtin_unreachable();
}

/* Original0x102CC..0x102D2. */
REGION void tsl9_record_field_transitions_block_102cc(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000137)); LIVE;
    PORT(".Lrecord_field_transitions_edge_102d0:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_transitions_edge_102d0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_102ea\n");
    __builtin_unreachable();
}

/* Original0x102D2..0x102DC. */
REGION void tsl9_record_field_transitions_block_102d2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000137)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_102d8:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_102d8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0x102DC..0x102DE. */
REGION void tsl9_record_field_transitions_block_102dc(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_102dc:\n.option push\n.option rvc\nc.beqz a0,.Lrecord_field_transitions_edge_102dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_102ea\n");
    __builtin_unreachable();
}

/* Original0x102DE..0x102E4. */
REGION void tsl9_record_field_transitions_block_102de(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lrecord_field_transitions_edge_102e0:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_102e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_ac0a\n");
    __builtin_unreachable();
}

/* Original0x102E4..0x102EA. */
REGION void tsl9_record_field_transitions_block_102e4(void)
{
    REGS;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_transitions_edge_102e6:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_102e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b0b0\n");
    __builtin_unreachable();
}

/* Original0x102EA..0x102F0. */
REGION void tsl9_record_field_transitions_block_102ea(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000135)); LIVE;
    PORT(".Lrecord_field_transitions_edge_102ee:\n.option push\n.option rvc\nc.bnez a5,.Lrecord_field_transitions_edge_102ee\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_10318\n");
    __builtin_unreachable();
}

/* Original0x102F0..0x102FA. */
REGION void tsl9_record_field_transitions_block_102f0(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000135)) = (uint8_t)a5; LIVE;
    PORT(".Lrecord_field_transitions_edge_102f6:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_102f6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0x102FA..0x10300. */
REGION void tsl9_record_field_transitions_block_102fa(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lrecord_field_transitions_edge_102fc:\n.option push\n.option norvc\nbne a0,a5,.Lrecord_field_transitions_edge_102fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_10318\n");
    __builtin_unreachable();
}

/* Original0x10300..0x10306. */
REGION void tsl9_record_field_transitions_block_10300(void)
{
    REGS;
    a0 = UINT32_C(0x00000095); LIVE;
    PORT(".Lrecord_field_transitions_edge_10304:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_10304\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_10314\n");
    __builtin_unreachable();
}

/* Original0x10306..0x1030A. */
REGION void tsl9_record_field_transitions_block_10306(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000137)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0x1030A..0x1030C. */
REGION void tsl9_record_field_transitions_block_1030a(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_1030a:\n.option push\n.option rvc\nc.bnez s0,.Lrecord_field_transitions_edge_1030a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_102ea\n");
    __builtin_unreachable();
}

/* Original0x1030C..0x10314. */
REGION void tsl9_record_field_transitions_block_1030c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000135)) = (uint8_t)0; LIVE;
    a0 = UINT32_C(0x0000008a); LIVE;
    __builtin_unreachable();
}

/* Original0x10314..0x10318. */
REGION void tsl9_record_field_transitions_block_10314(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_10314:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10314\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0x10318..0x1032A. */
REGION void tsl9_record_field_transitions_block_10318(void)
{
    REGS;
    a4 = UINT32_C(0x0000008b); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = original_gp + UINT32_C(0x00000136); LIVE;
    a2 = UINT32_C(0x0000000a); LIVE;
    a1 = UINT32_C(0x00000005); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_10326:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10326\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_8248\n");
    __builtin_unreachable();
}

/* Original0x1032A..0x1033C. */
REGION void tsl9_record_field_transitions_block_1032a(void)
{
    REGS;
    a4 = UINT32_C(0x0000008c); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = original_gp + UINT32_C(0x00000138); LIVE;
    a2 = UINT32_C(0x00000014); LIVE;
    a1 = UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_10338:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10338\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_8248\n");
    __builtin_unreachable();
}

/* Original0x1033C..0x1034E. */
REGION void tsl9_record_field_transitions_block_1033c(void)
{
    REGS;
    a4 = UINT32_C(0x0000008d); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = original_gp + UINT32_C(0x00000139); LIVE;
    a2 = UINT32_C(0x0000001e); LIVE;
    a1 = UINT32_C(0x00000019); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_1034a:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_1034a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_8248\n");
    __builtin_unreachable();
}

/* Original0x1034E..0x10364. */
REGION void tsl9_record_field_transitions_block_1034e(void)
{
    REGS;
    a4 = UINT32_C(0x0000008e); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = original_gp + UINT32_C(0x0000013a); LIVE;
    a2 = UINT32_C(0x00000028); LIVE;
    a1 = UINT32_C(0x00000023); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_10360:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10360\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_8248\n");
    __builtin_unreachable();
}

/* Original0x10364..0x1037A. */
REGION void tsl9_record_field_transitions_block_10364(void)
{
    REGS;
    a4 = UINT32_C(0x0000008f); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = original_gp + UINT32_C(0x0000013b); LIVE;
    a2 = UINT32_C(0x00000032); LIVE;
    a1 = UINT32_C(0x0000002d); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_10376:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10376\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_8248\n");
    __builtin_unreachable();
}

/* Original0x1037A..0x10390. */
REGION void tsl9_record_field_transitions_block_1037a(void)
{
    REGS;
    a4 = UINT32_C(0x00000090); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = original_gp + UINT32_C(0x0000013c); LIVE;
    a2 = UINT32_C(0x0000003c); LIVE;
    a1 = UINT32_C(0x00000037); LIVE;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_1038c:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_1038c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_8248\n");
    __builtin_unreachable();
}

/* Original0x10390..0x10394. */
REGION void tsl9_record_field_transitions_block_10390(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_10390:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10390\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0x10394..0x10398. */
REGION void tsl9_record_field_transitions_block_10394(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_10394:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10394\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_ab68\n");
    __builtin_unreachable();
}

/* Original0x10398..0x103B0. */
REGION void tsl9_record_field_transitions_block_10398(void)
{
    REGS;
    a5 = UINT32_C(0x00000005); LIVE;
    a0 = a0 * a5; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000134)); LIVE;
    a0 = a0 + UINT32_C(0x0000000a); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    a5 = a0 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lrecord_field_transitions_edge_103ae:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_field_transitions_edge_103ae\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_103ea\n");
    __builtin_unreachable();
}

/* Original0x103B0..0x103B4. */
REGION void tsl9_record_field_transitions_block_103b0(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_103b0:\n.option push\n.option norvc\nbleu s0,a5,.Lrecord_field_transitions_edge_103b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_103ca\n");
    __builtin_unreachable();
}

/* Original0x103B4..0x103BC. */
REGION void tsl9_record_field_transitions_block_103b4(void)
{
    REGS;
    a5 = UINT32_C(0x0000003b); LIVE;
    PORT(".Lrecord_field_transitions_edge_103b8:\n.option push\n.option norvc\nbleu a0,a5,.Lrecord_field_transitions_edge_103b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_103ca\n");
    __builtin_unreachable();
}

/* Original0x103BC..0x103C6. */
REGION void tsl9_record_field_transitions_block_103bc(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000134)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x0000009f); LIVE;
    __builtin_unreachable();
}

/* Original0x103C6..0x103CA. */
REGION void tsl9_record_field_transitions_block_103c6(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_103c6:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_103c6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0x103CA..0x103DA. */
REGION void tsl9_record_field_transitions_block_103ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 7(s1)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000052)); LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_103d6:\n.option push\n.option norvc\nbeq a4,a5,.Lrecord_field_transitions_edge_103d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_103f8\n");
    __builtin_unreachable();
}

/* Original0x103DA..0x103EA. */
REGION void tsl9_record_field_transitions_block_103da(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000052)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_103e6:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_103e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0x103EA..0x103EE. */
REGION void tsl9_record_field_transitions_block_103ea(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_103ea:\n.option push\n.option norvc\nbltu a5,s0,.Lrecord_field_transitions_edge_103ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_103ca\n");
    __builtin_unreachable();
}

/* Original0x103EE..0x103F8. */
REGION void tsl9_record_field_transitions_block_103ee(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000134)) = (uint8_t)0; LIVE;
    a0 = UINT32_C(0x0000009e); LIVE;
    PORT(".Lrecord_field_transitions_edge_103f6:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_103f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_103c6\n");
    __builtin_unreachable();
}

/* Original0x103F8..0x10402. */
REGION void tsl9_record_field_transitions_block_103f8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x10440..0x10470. */
REGION void tsl9_feature_external_10440(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 << UINT32_C(0x00000008); LIVE;
    a5 = a5 | a4; LIVE;
    a4 = UINT32_C(0xffffe000); LIVE;
    a5 = a5 + a4; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint16_t *)(uintptr_t)(original_gp + UINT32_C(0x00000140)) = (uint16_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = *(volatile int8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    PORT(".option push\n.option norvc\naddi s0, gp, 320\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_1046c:\n.option push\n.option norvc\nbgez a5,.Lrecord_field_transitions_edge_1046c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_10492\n");
    __builtin_unreachable();
}

/* Original0x10470..0x10474. */
REGION void tsl9_record_field_transitions_block_10470(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_10470:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_10470\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0x10474..0x1047A. */
REGION void tsl9_record_field_transitions_block_10474(void)
{
    REGS;
    a5 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lrecord_field_transitions_edge_10476:\n.option push\n.option norvc\nbltu a5,a0,.Lrecord_field_transitions_edge_10476\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_10492\n");
    __builtin_unreachable();
}

/* Original0x1047A..0x1048E. */
REGION void tsl9_record_field_transitions_block_1047a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 0(s0)\n.option pop\n");
    a4 = UINT32_C(0x000001f2); LIVE;
    a5 = a5 + UINT32_C(0x000000f9); LIVE;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lrecord_field_transitions_edge_1048a:\n.option push\n.option norvc\nbleu a5,a4,.Lrecord_field_transitions_edge_1048a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_10492\n");
    __builtin_unreachable();
}

/* Original0x1048E..0x10492. */
REGION void tsl9_record_field_transitions_block_1048e(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_1048e:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_1048e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_f414\n");
    __builtin_unreachable();
}

/* Original0x10492..0x104AA. */
REGION void tsl9_record_field_transitions_block_10492(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlh a5, 0(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000078); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)); LIVE;
    a3 = a5 + UINT32_C(0x0000003c); LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a3 = a3 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lrecord_field_transitions_edge_104a6:\n.option push\n.option norvc\nbltu a2,a3,.Lrecord_field_transitions_edge_104a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_104e2\n");
    __builtin_unreachable();
}

/* Original0x104AA..0x104AC. */
REGION void tsl9_record_field_transitions_block_104aa(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_104aa:\n.option push\n.option rvc\nc.beqz a4,.Lrecord_field_transitions_edge_104aa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_1054e\n");
    __builtin_unreachable();
}

/* Original0x104AC..0x104B4. */
REGION void tsl9_record_field_transitions_block_104ac(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)) = (uint8_t)0; LIVE;
    a0 = UINT32_C(0x000000aa); LIVE;
    __builtin_unreachable();
}

/* Original0x104B4..0x104B8. */
REGION void tsl9_record_field_transitions_block_104b4(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_104b4:\n.option push\n.option norvc\njal ra,.Lrecord_field_transitions_edge_104b4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_1040e\n");
    __builtin_unreachable();
}

/* Original0x104B8..0x104C2. */
REGION void tsl9_record_field_transitions_block_104b8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lrecord_field_transitions_edge_104be:\n.option push\n.option norvc\nbne a4,a5,.Lrecord_field_transitions_edge_104be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_1054e\n");
    __builtin_unreachable();
}

/* Original0x104C2..0x104CE. */
REGION void tsl9_record_field_transitions_block_104c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlh a5, 0(s0)\n.option pop\n");
    a4 = UINT32_C(0xfffffc7c); LIVE;
    PORT(".Lrecord_field_transitions_edge_104ca:\n.option push\n.option norvc\nble a4,a5,.Lrecord_field_transitions_edge_104ca\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_1053a\n");
    __builtin_unreachable();
}

/* Original0x104CE..0x104D8. */
REGION void tsl9_record_field_transitions_block_104ce(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x000000ad); LIVE;
    __builtin_unreachable();
}

/* Original0x104D8..0x104E2. */
REGION void tsl9_record_field_transitions_block_104d8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lrecord_field_transitions_edge_104de:\n.option push\n.option norvc\njal zero,.Lrecord_field_transitions_edge_104de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_1040e\n");
    __builtin_unreachable();
}

/* Original0x104E2..0x104E4. */
REGION void tsl9_record_field_transitions_block_104e2(void)
{
    REGS;
    PORT(".Lrecord_field_transitions_edge_104e2:\n.option push\n.option rvc\nc.bnez a4,.Lrecord_field_transitions_edge_104e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_record_field_transitions_block_1050c\n");
    __builtin_unreachable();
}

/* Original0x104E4..0x104EC. */
REGION void tsl9_record_field_transitions_block_104e4(void)
{
    REGS;
    a4 = UINT32_C(0xffffff38); LIVE;
    PORT(".Lrecord_field_transitions_edge_104e8:\n.option push\n.option norvc\nble a4,a5,.Lrecord_field_transitions_edge_104e8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_104f8\n");
    __builtin_unreachable();
}

/* Original0x104EC..0x104F8. */
REGION void tsl9_record_field_transitions_block_104ec(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x000000ab); LIVE;
    PORT(".Lrecord_field_transitions_edge_104f6:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_104f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_104b4\n");
    __builtin_unreachable();
}

/* Original0x104F8..0x10500. */
REGION void tsl9_record_field_transitions_block_104f8(void)
{
    REGS;
    a4 = UINT32_C(0x000000c8); LIVE;
    PORT(".Lrecord_field_transitions_edge_104fc:\n.option push\n.option norvc\nble a5,a4,.Lrecord_field_transitions_edge_104fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_1054e\n");
    __builtin_unreachable();
}

/* Original0x10500..0x1050C. */
REGION void tsl9_record_field_transitions_block_10500(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x000000ae); LIVE;
    PORT(".Lrecord_field_transitions_edge_1050a:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_1050a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_104b4\n");
    __builtin_unreachable();
}

/* Original0x1050C..0x10512. */
REGION void tsl9_record_field_transitions_block_1050c(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lrecord_field_transitions_edge_1050e:\n.option push\n.option norvc\nbne a4,a3,.Lrecord_field_transitions_edge_1050e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_104b8\n");
    __builtin_unreachable();
}

/* Original0x10512..0x1051A. */
REGION void tsl9_record_field_transitions_block_10512(void)
{
    REGS;
    a4 = UINT32_C(0xfffffe3e); LIVE;
    PORT(".Lrecord_field_transitions_edge_10516:\n.option push\n.option norvc\nble a4,a5,.Lrecord_field_transitions_edge_10516\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_10526\n");
    __builtin_unreachable();
}

/* Original0x1051A..0x10526. */
REGION void tsl9_record_field_transitions_block_1051a(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x000000ac); LIVE;
    PORT(".Lrecord_field_transitions_edge_10524:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_10524\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_104b4\n");
    __builtin_unreachable();
}

/* Original0x10526..0x1052E. */
REGION void tsl9_record_field_transitions_block_10526(void)
{
    REGS;
    a4 = UINT32_C(0x000001c2); LIVE;
    PORT(".Lrecord_field_transitions_edge_1052a:\n.option push\n.option norvc\nble a5,a4,.Lrecord_field_transitions_edge_1052a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_1054e\n");
    __builtin_unreachable();
}

/* Original0x1052E..0x1053A. */
REGION void tsl9_record_field_transitions_block_1052e(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x000000af); LIVE;
    PORT(".Lrecord_field_transitions_edge_10538:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_10538\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_104b4\n");
    __builtin_unreachable();
}

/* Original0x1053A..0x10542. */
REGION void tsl9_record_field_transitions_block_1053a(void)
{
    REGS;
    a4 = UINT32_C(0x00000384); LIVE;
    PORT(".Lrecord_field_transitions_edge_1053e:\n.option push\n.option norvc\nble a5,a4,.Lrecord_field_transitions_edge_1053e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_record_field_transitions_block_1054e\n");
    __builtin_unreachable();
}

/* Original0x10542..0x1054E. */
REGION void tsl9_record_field_transitions_block_10542(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000013d)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x000000b0); LIVE;
    PORT(".Lrecord_field_transitions_edge_1054c:\n.option push\n.option rvc\nc.j .Lrecord_field_transitions_edge_1054c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_field_transitions_block_104d8\n");
    __builtin_unreachable();
}

/* Original0x1054E..0x10556. */
REGION void tsl9_record_field_transitions_block_1054e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
TABLE_DATA(".rodata.tsl9_record_field_transitions_data_19ea8") const uint8_t tsl9_record_field_transitions_data_19ea8[16] = {0x77, 0x04, 0xc6, 0x3f, 0x3f, 0x6f, 0xa0, 0xb2, 0xd3, 0xb2, 0x0e, 0xc4, 0xd6, 0xff, 0x43, 0x22};
TABLE_DATA(".rodata.tsl9_record_field_transitions_data_19eb8") const uint8_t tsl9_record_field_transitions_data_19eb8[16] = {0x04, 0x77, 0xb5, 0x4c, 0x4c, 0x1c, 0xd3, 0xc1, 0xa0, 0xc1, 0x7d, 0xb7, 0xa5, 0x8c, 0x30, 0x51};
TABLE_DATA(".rodata.tsl9_record_field_transitions_data_19ec8") const uint8_t tsl9_record_field_transitions_data_19ec8[16] = {0x52, 0x21, 0xe3, 0x1a, 0x1a, 0x4a, 0x85, 0x97, 0xf6, 0x97, 0x2b, 0xe1, 0xf3, 0xda, 0x00, 0x07};
TABLE_DATA(".rodata.tsl9_record_field_transitions_data_1a0d8") const uint8_t tsl9_record_field_transitions_data_1a0d8[3] = {0xbf, 0x50, 0xbe};
