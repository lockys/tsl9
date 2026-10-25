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

/* Thirty-eight complete remaining dispatch entries:6022B/1926i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xB584..0xB594. */
REGION void tsl9_record_dispatch_provider_b584(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff969)); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB5F6..0xB604. */
REGION void tsl9_remaining_record_dispatch_entry_b5f6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\naddi a2, sp, 4\n.option pop\n");
    a1 = UINT32_C(0x0000000a); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b600:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b600\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_external_82a8\n");
    __builtin_unreachable();
}

/* Original0xB604..0xB60A. */
REGION void tsl9_remaining_record_dispatch_block_b604(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000006)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b608:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_b608\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b642\n");
    __builtin_unreachable();
}

/* Original0xB60A..0xB616. */
REGION void tsl9_remaining_record_dispatch_block_b60a(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, sp, 3\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x00000003)) = (uint8_t)0; LIVE;
    PORT(".Lremaining_record_dispatch_edge_b612:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b612\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_c7e8\n");
    __builtin_unreachable();
}

/* Original0xB616..0xB618. */
REGION void tsl9_remaining_record_dispatch_block_b616(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_b616:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_b616\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b642\n");
    __builtin_unreachable();
}

/* Original0xB618..0xB628. */
REGION void tsl9_remaining_record_dispatch_block_b618(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b624:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_b624\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b648\n");
    __builtin_unreachable();
}

/* Original0xB628..0xB63C. */
REGION void tsl9_remaining_record_dispatch_block_b628(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)); LIVE;
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 << UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    a0 = a0 | a5; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000d)) = (uint8_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0xB63C..0xB642. */
REGION void tsl9_remaining_record_dispatch_block_b63c(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a0, sp, 4\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b63e:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b63e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xB642..0xB648. */
REGION void tsl9_remaining_record_dispatch_block_b642(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB648..0xB64E. */
REGION void tsl9_remaining_record_dispatch_block_b648(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b64a:\n.option push\n.option norvc\nbeq a0,a4,.Lremaining_record_dispatch_edge_b64a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b650\n");
    __builtin_unreachable();
}

/* Original0xB64E..0xB650. */
REGION void tsl9_remaining_record_dispatch_block_b64e(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xB650..0xB664. */
REGION void tsl9_remaining_record_dispatch_block_b650(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000006); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | a4; LIVE;
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_b662:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b662\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b63c\n");
    __builtin_unreachable();
}

/* Original0xB67A..0xB680. */
REGION void tsl9_remaining_record_dispatch_entry_b67a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b67e:\n.option push\n.option rvc\nc.jal .Lremaining_record_dispatch_edge_b67e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xB680..0xB68A. */
REGION void tsl9_remaining_record_dispatch_block_b680(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff880)) = (uint8_t)a0; LIVE;
    PORT(".Lremaining_record_dispatch_edge_b688:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_b688\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b6a2\n");
    __builtin_unreachable();
}

/* Original0xB68A..0xB6A2. */
REGION void tsl9_remaining_record_dispatch_block_b68a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_literal_b694:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_entry_b67a\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_b694\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b69e:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_b69e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xB6A2..0xB6A8. */
REGION void tsl9_remaining_record_dispatch_block_b6a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB6BC..0xB6C2. */
REGION void tsl9_remaining_record_dispatch_entry_b6bc(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b6c0:\n.option push\n.option rvc\nc.jal .Lremaining_record_dispatch_edge_b6c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_provider_b6a8\n");
    __builtin_unreachable();
}

/* Original0xB6C2..0xB6CC. */
REGION void tsl9_remaining_record_dispatch_block_b6c2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffff83f)) = (uint8_t)a0; LIVE;
    PORT(".Lremaining_record_dispatch_edge_b6ca:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_b6ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b6e4\n");
    __builtin_unreachable();
}

/* Original0xB6CC..0xB6E4. */
REGION void tsl9_remaining_record_dispatch_block_b6cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000064); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_literal_b6d6:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_entry_b6bc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_b6d6\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b6e0:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_b6e0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xB6E4..0xB6EA. */
REGION void tsl9_remaining_record_dispatch_block_b6e4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xB730..0xB744. */
REGION void tsl9_feature_external_b730(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b742:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_b742\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b756\n");
    __builtin_unreachable();
}

/* Original0xB744..0xB74A. */
REGION void tsl9_remaining_record_dispatch_block_b744(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b746:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_b746\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b9ce\n");
    __builtin_unreachable();
}

/* Original0xB74A..0xB756. */
REGION void tsl9_remaining_record_dispatch_block_b74a(void)
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

/* Original0xB756..0xB76A. */
REGION void tsl9_remaining_record_dispatch_block_b756(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000007a2)); LIVE;
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b766:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_b766\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b776\n");
    __builtin_unreachable();
}

/* Original0xB76A..0xB776. */
REGION void tsl9_remaining_record_dispatch_block_b76a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000792)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_b772:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b772\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_state_controls_entry_d53c\n");
    __builtin_unreachable();
}

/* Original0xB776..0xB790. */
REGION void tsl9_remaining_record_dispatch_block_b776(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 9(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a3 = UINT32_C(0x00000077); LIVE;
    a2 = UINT32_C(0x00000076); LIVE;
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000c9); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b78c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b78c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xB790..0xB7AC. */
REGION void tsl9_remaining_record_dispatch_block_b790(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 9(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a1 = a1 >> UINT32_C(0x00000004); LIVE;
    a3 = UINT32_C(0x00000085); LIVE;
    a2 = UINT32_C(0x00000084); LIVE;
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000ca); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b7a8:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b7a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xB7AC..0xB7C6. */
REGION void tsl9_remaining_record_dispatch_block_b7ac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 10(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a3 = UINT32_C(0x00000087); LIVE;
    a2 = UINT32_C(0x00000086); LIVE;
    a1 = a1 >> UINT32_C(0x00000006); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000cb); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b7c2:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b7c2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xB7C6..0xB7E2. */
REGION void tsl9_remaining_record_dispatch_block_b7c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 9(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a1 = a1 >> UINT32_C(0x00000002); LIVE;
    a3 = UINT32_C(0x0000007f); LIVE;
    a2 = UINT32_C(0x0000007e); LIVE;
    a1 = a1 & UINT32_C(0x00000003); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000cc); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b7de:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b7de\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xB7E2..0xB7F0. */
REGION void tsl9_remaining_record_dispatch_block_b7e2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 10(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    a4 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b7ec:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_b7ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b898\n");
    __builtin_unreachable();
}

/* Original0xB7F0..0xB800. */
REGION void tsl9_remaining_record_dispatch_block_b7f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 9(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000040); LIVE;
    a4 = a4 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b7fc:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_b7fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b89e\n");
    __builtin_unreachable();
}

/* Original0xB800..0xB808. */
REGION void tsl9_remaining_record_dispatch_block_b800(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x0000000c); LIVE;
    a3 = UINT32_C(0x00000004); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xB808..0xB80C. */
REGION void tsl9_remaining_record_dispatch_block_b808(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_b808:\n.option push\n.option norvc\nbeq a4,a3,.Lremaining_record_dispatch_edge_b808\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b818\n");
    __builtin_unreachable();
}

/* Original0xB80C..0xB816. */
REGION void tsl9_remaining_record_dispatch_block_b80c(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x0000000c); LIVE;
    a4 = UINT32_C(0x00000008); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b812:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_b812\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b818\n");
    __builtin_unreachable();
}

/* Original0xB816..0xB818. */
REGION void tsl9_remaining_record_dispatch_block_b816(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0xB818..0xB82C. */
REGION void tsl9_remaining_record_dispatch_block_b818(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    a3 = UINT32_C(0x00000083); LIVE;
    a2 = UINT32_C(0x00000082); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x000000cd); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b828:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b828\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xB82C..0xB838. */
REGION void tsl9_remaining_record_dispatch_block_b82c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 3(s0)\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000002); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b834:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b834\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_helpers_block_eda6\n");
    __builtin_unreachable();
}

/* Original0xB838..0xB846. */
REGION void tsl9_remaining_record_dispatch_block_b838(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c8)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b844:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_b844\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8ae\n");
    __builtin_unreachable();
}

/* Original0xB846..0xB84A. */
REGION void tsl9_remaining_record_dispatch_block_b846(void)
{
    REGS;
    a5 = UINT32_C(0x00000037); LIVE;
    __builtin_unreachable();
}

/* Original0xB84A..0xB84E. */
REGION void tsl9_remaining_record_dispatch_block_b84a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c8)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xB84E..0xB85E. */
REGION void tsl9_remaining_record_dispatch_block_b84e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b85a:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_b85a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b910\n");
    __builtin_unreachable();
}

/* Original0xB85E..0xB86E. */
REGION void tsl9_remaining_record_dispatch_block_b85e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000080); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b86a:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_b86a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b74a\n");
    __builtin_unreachable();
}

/* Original0xB86E..0xB872. */
REGION void tsl9_remaining_record_dispatch_block_b86e(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_b86e:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b86e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xB872..0xB878. */
REGION void tsl9_remaining_record_dispatch_block_b872(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b874:\n.option push\n.option norvc\nbeq a0,a5,.Lremaining_record_dispatch_edge_b874\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b890\n");
    __builtin_unreachable();
}

/* Original0xB878..0xB890. */
REGION void tsl9_remaining_record_dispatch_block_b878(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, a5, 1668\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000675)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xB890..0xB892. */
REGION void tsl9_remaining_record_dispatch_block_b890(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    __builtin_unreachable();
}

/* Original0xB892..0xB898. */
REGION void tsl9_remaining_record_dispatch_block_b892(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x000000c8)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_b896:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b896\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b74a\n");
    __builtin_unreachable();
}

/* Original0xB898..0xB89E. */
REGION void tsl9_remaining_record_dispatch_block_b898(void)
{
    REGS;
    a1 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b89a:\n.option push\n.option norvc\nbeq a4,a1,.Lremaining_record_dispatch_edge_b89a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b818\n");
    __builtin_unreachable();
}

/* Original0xB89E..0xB8AE. */
REGION void tsl9_remaining_record_dispatch_block_b89e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 9(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000080); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a4 = a4 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8ac:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8ac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b808\n");
    __builtin_unreachable();
}

/* Original0xB8AE..0xB8B2. */
REGION void tsl9_remaining_record_dispatch_block_b8ae(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8b0:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_b8b0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8b8\n");
    __builtin_unreachable();
}

/* Original0xB8B2..0xB8B8. */
REGION void tsl9_remaining_record_dispatch_block_b8b2(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8b6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8b6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB8B8..0xB8C2. */
REGION void tsl9_remaining_record_dispatch_block_b8b8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 7(s0)\n.option pop\n");
    a5 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8c0:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_b8c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8c6\n");
    __builtin_unreachable();
}

/* Original0xB8C2..0xB8C6. */
REGION void tsl9_remaining_record_dispatch_block_b8c2(void)
{
    REGS;
    a5 = UINT32_C(0x00000013); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8c4:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8c4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB8C6..0xB8CC. */
REGION void tsl9_remaining_record_dispatch_block_b8c6(void)
{
    REGS;
    a5 = a4 & UINT32_C(0x0000000c); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8ca:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_b8ca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8d0\n");
    __builtin_unreachable();
}

/* Original0xB8CC..0xB8D0. */
REGION void tsl9_remaining_record_dispatch_block_b8cc(void)
{
    REGS;
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8ce:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8ce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB8D0..0xB8DA. */
REGION void tsl9_remaining_record_dispatch_block_b8d0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a3 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8d8:\n.option push\n.option rvc\nc.beqz a3,.Lremaining_record_dispatch_edge_b8d8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8de\n");
    __builtin_unreachable();
}

/* Original0xB8DA..0xB8DE. */
REGION void tsl9_remaining_record_dispatch_block_b8da(void)
{
    REGS;
    a5 = UINT32_C(0x00000015); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8dc:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB8DE..0xB8E4. */
REGION void tsl9_remaining_record_dispatch_block_b8de(void)
{
    REGS;
    a3 = a5 & UINT32_C(0x0000000c); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8e2:\n.option push\n.option rvc\nc.beqz a3,.Lremaining_record_dispatch_edge_b8e2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8e8\n");
    __builtin_unreachable();
}

/* Original0xB8E4..0xB8E8. */
REGION void tsl9_remaining_record_dispatch_block_b8e4(void)
{
    REGS;
    a5 = UINT32_C(0x00000016); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8e6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8e6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB8E8..0xB8EE. */
REGION void tsl9_remaining_record_dispatch_block_b8e8(void)
{
    REGS;
    a3 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8ec:\n.option push\n.option rvc\nc.beqz a3,.Lremaining_record_dispatch_edge_b8ec\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8f2\n");
    __builtin_unreachable();
}

/* Original0xB8EE..0xB8F2. */
REGION void tsl9_remaining_record_dispatch_block_b8ee(void)
{
    REGS;
    a5 = UINT32_C(0x00000017); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8f0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8f0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB8F2..0xB8F8. */
REGION void tsl9_remaining_record_dispatch_block_b8f2(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8f6:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_b8f6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b8fc\n");
    __builtin_unreachable();
}

/* Original0xB8F8..0xB8FC. */
REGION void tsl9_remaining_record_dispatch_block_b8f8(void)
{
    REGS;
    a5 = UINT32_C(0x00000018); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b8fa:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b8fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB8FC..0xB902. */
REGION void tsl9_remaining_record_dispatch_block_b8fc(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b900:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_b900\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b906\n");
    __builtin_unreachable();
}

/* Original0xB902..0xB906. */
REGION void tsl9_remaining_record_dispatch_block_b902(void)
{
    REGS;
    a5 = UINT32_C(0x00000019); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b904:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b904\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB906..0xB90C. */
REGION void tsl9_remaining_record_dispatch_block_b906(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b90a:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_b90a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_b84e\n");
    __builtin_unreachable();
}

/* Original0xB90C..0xB910. */
REGION void tsl9_remaining_record_dispatch_block_b90c(void)
{
    REGS;
    a5 = UINT32_C(0x0000001a); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b90e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b90e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b84a\n");
    __builtin_unreachable();
}

/* Original0xB910..0xB91E. */
REGION void tsl9_remaining_record_dispatch_block_b910(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a1 = UINT32_C(0x00000002); LIVE;
    a4 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b91a:\n.option push\n.option norvc\nbne a4,a1,.Lremaining_record_dispatch_edge_b91a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b924\n");
    __builtin_unreachable();
}

/* Original0xB91E..0xB924. */
REGION void tsl9_remaining_record_dispatch_block_b91e(void)
{
    REGS;
    a5 = UINT32_C(0x00000023); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b922:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b922\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB924..0xB92E. */
REGION void tsl9_remaining_record_dispatch_block_b924(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x0000000c); LIVE;
    a2 = UINT32_C(0x00000008); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b92a:\n.option push\n.option norvc\nbne a4,a2,.Lremaining_record_dispatch_edge_b92a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b934\n");
    __builtin_unreachable();
}

/* Original0xB92E..0xB934. */
REGION void tsl9_remaining_record_dispatch_block_b92e(void)
{
    REGS;
    a5 = UINT32_C(0x00000024); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b932:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b932\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB934..0xB940. */
REGION void tsl9_remaining_record_dispatch_block_b934(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000030); LIVE;
    a3 = UINT32_C(0x00000020); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b93c:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_b93c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b946\n");
    __builtin_unreachable();
}

/* Original0xB940..0xB946. */
REGION void tsl9_remaining_record_dispatch_block_b940(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b944:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b944\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB946..0xB952. */
REGION void tsl9_remaining_record_dispatch_block_b946(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    a4 = UINT32_C(0x00000080); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b94e:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_b94e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b958\n");
    __builtin_unreachable();
}

/* Original0xB952..0xB958. */
REGION void tsl9_remaining_record_dispatch_block_b952(void)
{
    REGS;
    a5 = UINT32_C(0x00000026); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b956:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b956\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB958..0xB964. */
REGION void tsl9_remaining_record_dispatch_block_b958(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a0 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b960:\n.option push\n.option norvc\nbne a0,a1,.Lremaining_record_dispatch_edge_b960\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b96a\n");
    __builtin_unreachable();
}

/* Original0xB964..0xB96A. */
REGION void tsl9_remaining_record_dispatch_block_b964(void)
{
    REGS;
    a5 = UINT32_C(0x00000027); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b968:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b968\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB96A..0xB972. */
REGION void tsl9_remaining_record_dispatch_block_b96a(void)
{
    REGS;
    a1 = a5 & UINT32_C(0x0000000c); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b96e:\n.option push\n.option norvc\nbne a1,a2,.Lremaining_record_dispatch_edge_b96e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b978\n");
    __builtin_unreachable();
}

/* Original0xB972..0xB978. */
REGION void tsl9_remaining_record_dispatch_block_b972(void)
{
    REGS;
    a5 = UINT32_C(0x00000028); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b976:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b976\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB978..0xB980. */
REGION void tsl9_remaining_record_dispatch_block_b978(void)
{
    REGS;
    a2 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b97c:\n.option push\n.option norvc\nbne a2,a3,.Lremaining_record_dispatch_edge_b97c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b986\n");
    __builtin_unreachable();
}

/* Original0xB980..0xB986. */
REGION void tsl9_remaining_record_dispatch_block_b980(void)
{
    REGS;
    a5 = UINT32_C(0x00000029); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b984:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b984\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB986..0xB98E. */
REGION void tsl9_remaining_record_dispatch_block_b986(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b98a:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_b98a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b994\n");
    __builtin_unreachable();
}

/* Original0xB98E..0xB994. */
REGION void tsl9_remaining_record_dispatch_block_b98e(void)
{
    REGS;
    a5 = UINT32_C(0x0000002a); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b992:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b992\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB994..0xB9A0. */
REGION void tsl9_remaining_record_dispatch_block_b994(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a3 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b99c:\n.option push\n.option norvc\nbne a3,a4,.Lremaining_record_dispatch_edge_b99c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b9a4\n");
    __builtin_unreachable();
}

/* Original0xB9A0..0xB9A4. */
REGION void tsl9_remaining_record_dispatch_block_b9a0(void)
{
    REGS;
    a5 = UINT32_C(0x0000001b); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9a2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b9a2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB9A4..0xB9B0. */
REGION void tsl9_remaining_record_dispatch_block_b9a4(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000030); LIVE;
    a3 = UINT32_C(0x00000020); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9ac:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_b9ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b9b4\n");
    __builtin_unreachable();
}

/* Original0xB9B0..0xB9B4. */
REGION void tsl9_remaining_record_dispatch_block_b9b0(void)
{
    REGS;
    a5 = UINT32_C(0x0000001c); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9b2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b9b2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB9B4..0xB9BE. */
REGION void tsl9_remaining_record_dispatch_block_b9b4(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x0000000c); LIVE;
    a3 = UINT32_C(0x00000008); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9ba:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_b9ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b9c2\n");
    __builtin_unreachable();
}

/* Original0xB9BE..0xB9C2. */
REGION void tsl9_remaining_record_dispatch_block_b9be(void)
{
    REGS;
    a5 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9c0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b9c0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB9C2..0xB9CA. */
REGION void tsl9_remaining_record_dispatch_block_b9c2(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9c6:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_b9c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_b74a\n");
    __builtin_unreachable();
}

/* Original0xB9CA..0xB9CE. */
REGION void tsl9_remaining_record_dispatch_block_b9ca(void)
{
    REGS;
    a5 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9cc:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_b9cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_b892\n");
    __builtin_unreachable();
}

/* Original0xB9CE..0xB9D4. */
REGION void tsl9_remaining_record_dispatch_block_b9ce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu s1, 200(gp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b9d2:\n.option push\n.option rvc\nc.bnez s1,.Lremaining_record_dispatch_edge_b9d2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_baa4\n");
    __builtin_unreachable();
}

/* Original0xB9D4..0xB9E4. */
REGION void tsl9_remaining_record_dispatch_block_b9d4(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = UINT32_C(0x00000080); LIVE;
    a3 = a4 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9e0:\n.option push\n.option norvc\nbeq a3,a5,.Lremaining_record_dispatch_edge_b9e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bb9c\n");
    __builtin_unreachable();
}

/* Original0xB9E4..0xB9F2. */
REGION void tsl9_remaining_record_dispatch_block_b9e4(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = UINT32_C(0x00000010); LIVE;
    a2 = a3 & UINT32_C(0x00000018); LIVE;
    PORT(".Lremaining_record_dispatch_edge_b9ee:\n.option push\n.option norvc\nbeq a2,a5,.Lremaining_record_dispatch_edge_b9ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bba0\n");
    __builtin_unreachable();
}

/* Original0xB9F2..0xB9FE. */
REGION void tsl9_remaining_record_dispatch_block_b9f2(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 << UINT32_C(0x0000001a); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x1a\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_b9fa:\n.option push\n.option norvc\nbgez a5,.Lremaining_record_dispatch_edge_b9fa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_babe\n");
    __builtin_unreachable();
}

/* Original0xB9FE..0xBA02. */
REGION void tsl9_remaining_record_dispatch_block_b9fe(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_b9fe:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_b9fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_action_support_entry_a04a\n");
    __builtin_unreachable();
}

/* Original0xBA02..0xBA08. */
REGION void tsl9_remaining_record_dispatch_block_ba02(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba04:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ba04\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_dependencies_provider_9f7a\n");
    __builtin_unreachable();
}

/* Original0xBA08..0xBA14. */
REGION void tsl9_remaining_record_dispatch_block_ba08(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000004f8)); LIVE;
    PORT(".option push\n.option rvc\nli s1, 3\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_ba12:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_ba12\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBA14..0xBA18. */
REGION void tsl9_remaining_record_dispatch_block_ba14(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ba14:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ba14\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xBA18..0xBA1A. */
REGION void tsl9_remaining_record_dispatch_block_ba18(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ba18:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_ba18\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBA1A..0xBA20. */
REGION void tsl9_remaining_record_dispatch_block_ba1a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba1c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ba1c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_b67a\n");
    __builtin_unreachable();
}

/* Original0xBA20..0xBA24. */
REGION void tsl9_remaining_record_dispatch_block_ba20(void)
{
    REGS;
    a0 = UINT32_C(0x0000002c); LIVE;
    __builtin_unreachable();
}

/* Original0xBA24..0xBA28. */
REGION void tsl9_remaining_record_dispatch_block_ba24(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ba24:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ba24\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xBA28..0xBA3A. */
REGION void tsl9_remaining_record_dispatch_block_ba28(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = a5 + UINT32_C(0xfffffff9); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba36:\n.option push\n.option norvc\nbltu a3,a4,.Lremaining_record_dispatch_edge_ba36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bbea\n");
    __builtin_unreachable();
}

/* Original0xBA3A..0xBA46. */
REGION void tsl9_remaining_record_dispatch_block_ba3a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a5, 8(s0)\n.option pop\n");
    a4 = a5 & UINT32_C(0x00000500); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba42:\n.option push\n.option norvc\nbeqz a4,.Lremaining_record_dispatch_edge_ba42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bbc4\n");
    __builtin_unreachable();
}

/* Original0xBA46..0xBA4A. */
REGION void tsl9_remaining_record_dispatch_block_ba46(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ba46:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ba46\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a658\n");
    __builtin_unreachable();
}

/* Original0xBA4A..0xBA50. */
REGION void tsl9_remaining_record_dispatch_block_ba4a(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba4c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ba4c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_fe6a\n");
    __builtin_unreachable();
}

/* Original0xBA50..0xBA58. */
REGION void tsl9_remaining_record_dispatch_block_ba50(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 9(s0)\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000004); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xBA58..0xBA5C. */
REGION void tsl9_remaining_record_dispatch_block_ba58(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ba58:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ba58\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_ed36\n");
    __builtin_unreachable();
}

/* Original0xBA5C..0xBA70. */
REGION void tsl9_remaining_record_dispatch_block_ba5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000049e)); LIVE;
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba6c:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_ba6c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ba80\n");
    __builtin_unreachable();
}

/* Original0xBA70..0xBA7E. */
REGION void tsl9_remaining_record_dispatch_block_ba70(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000048e)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba7a:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_ba7a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ba80\n");
    __builtin_unreachable();
}

/* Original0xBA7E..0xBA80. */
REGION void tsl9_remaining_record_dispatch_block_ba7e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBA80..0xBA94. */
REGION void tsl9_remaining_record_dispatch_block_ba80(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000047b)); LIVE;
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba90:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_ba90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_baa4\n");
    __builtin_unreachable();
}

/* Original0xBA94..0xBAA2. */
REGION void tsl9_remaining_record_dispatch_block_ba94(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000046b)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ba9e:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_ba9e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_baa4\n");
    __builtin_unreachable();
}

/* Original0xBAA2..0xBAA4. */
REGION void tsl9_remaining_record_dispatch_block_baa2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 13\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBAA4..0xBABE. */
REGION void tsl9_remaining_record_dispatch_block_baa4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s1\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, a2, 1110\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_baba:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_baba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_feature_state_records_provider_ebac\n");
    __builtin_unreachable();
}

/* Original0xBABE..0xBAC0. */
REGION void tsl9_remaining_record_dispatch_block_babe(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_babe:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_babe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bae8\n");
    __builtin_unreachable();
}

/* Original0xBAC0..0xBAC4. */
REGION void tsl9_remaining_record_dispatch_block_bac0(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bac0:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bac0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_action_support_entry_a04a\n");
    __builtin_unreachable();
}

/* Original0xBAC4..0xBACA. */
REGION void tsl9_remaining_record_dispatch_block_bac4(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bac6:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bac6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_dependencies_provider_9f7a\n");
    __builtin_unreachable();
}

/* Original0xBACA..0xBAD6. */
REGION void tsl9_remaining_record_dispatch_block_baca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000436)); LIVE;
    PORT(".option push\n.option rvc\nli s1, 1\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bad4:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bad4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBAD6..0xBADA. */
REGION void tsl9_remaining_record_dispatch_block_bad6(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bad6:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bad6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xBADA..0xBADC. */
REGION void tsl9_remaining_record_dispatch_block_bada(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bada:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_bada\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBADC..0xBAE2. */
REGION void tsl9_remaining_record_dispatch_block_badc(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bade:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bade\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_b67a\n");
    __builtin_unreachable();
}

/* Original0xBAE2..0xBAE8. */
REGION void tsl9_remaining_record_dispatch_block_bae2(void)
{
    REGS;
    a0 = UINT32_C(0x0000002b); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bae6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bae6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba24\n");
    __builtin_unreachable();
}

/* Original0xBAE8..0xBAF2. */
REGION void tsl9_remaining_record_dispatch_block_bae8(void)
{
    REGS;
    a5 = a4 & UINT32_C(0x00000003); LIVE;
    a2 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_baee:\n.option push\n.option norvc\nbeq a5,a2,.Lremaining_record_dispatch_edge_baee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bba4\n");
    __builtin_unreachable();
}

/* Original0xBAF2..0xBAFA. */
REGION void tsl9_remaining_record_dispatch_block_baf2(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x0000000c); LIVE;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lremaining_record_dispatch_edge_baf6:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_baf6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bba8\n");
    __builtin_unreachable();
}

/* Original0xBAFA..0xBB06. */
REGION void tsl9_remaining_record_dispatch_block_bafa(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 << UINT32_C(0x0000001a); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x1a\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bb02:\n.option push\n.option norvc\nbgez a5,.Lremaining_record_dispatch_edge_bb02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bb40\n");
    __builtin_unreachable();
}

/* Original0xBB06..0xBB0A. */
REGION void tsl9_remaining_record_dispatch_block_bb06(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb06:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb06\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_9fc8\n");
    __builtin_unreachable();
}

/* Original0xBB0A..0xBB14. */
REGION void tsl9_remaining_record_dispatch_block_bb0a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003f7)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb12:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bb12\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bb28\n");
    __builtin_unreachable();
}

/* Original0xBB14..0xBB18. */
REGION void tsl9_remaining_record_dispatch_block_bb14(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb14:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb14\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b6a8\n");
    __builtin_unreachable();
}

/* Original0xBB18..0xBB1A. */
REGION void tsl9_remaining_record_dispatch_block_bb18(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb18:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_bb18\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bb28\n");
    __builtin_unreachable();
}

/* Original0xBB1A..0xBB20. */
REGION void tsl9_remaining_record_dispatch_block_bb1a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb1c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb1c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_b6bc\n");
    __builtin_unreachable();
}

/* Original0xBB20..0xBB28. */
REGION void tsl9_remaining_record_dispatch_block_bb20(void)
{
    REGS;
    a0 = UINT32_C(0x0000002e); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb24:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb24\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xBB28..0xBB2C. */
REGION void tsl9_remaining_record_dispatch_block_bb28(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb28:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb28\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xBB2C..0xBB2E. */
REGION void tsl9_remaining_record_dispatch_block_bb2c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 11\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBB2E..0xBB32. */
REGION void tsl9_remaining_record_dispatch_block_bb2e(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb2e:\n.option push\n.option norvc\nbeqz a0,.Lremaining_record_dispatch_edge_bb2e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBB32..0xBB3E. */
REGION void tsl9_remaining_record_dispatch_block_bb32(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 6(s0)\n.option pop\n");
    a0 = a0 << UINT32_C(0x0000001a); LIVE;
    PORT(".option push\n.option rvc\nsrai a0, a0, 0x1a\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bb3a:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb3a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_181ce\n");
    __builtin_unreachable();
}

/* Original0xBB3E..0xBB40. */
REGION void tsl9_remaining_record_dispatch_block_bb3e(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb3e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bb3e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBB40..0xBB42. */
REGION void tsl9_remaining_record_dispatch_block_bb40(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb40:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bb40\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bb68\n");
    __builtin_unreachable();
}

/* Original0xBB42..0xBB4C. */
REGION void tsl9_remaining_record_dispatch_block_bb42(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000003bf)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb4a:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bb4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bb60\n");
    __builtin_unreachable();
}

/* Original0xBB4C..0xBB50. */
REGION void tsl9_remaining_record_dispatch_block_bb4c(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb4c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb4c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b6a8\n");
    __builtin_unreachable();
}

/* Original0xBB50..0xBB52. */
REGION void tsl9_remaining_record_dispatch_block_bb50(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb50:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_bb50\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bb60\n");
    __builtin_unreachable();
}

/* Original0xBB52..0xBB58. */
REGION void tsl9_remaining_record_dispatch_block_bb52(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb54:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb54\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_b6bc\n");
    __builtin_unreachable();
}

/* Original0xBB58..0xBB60. */
REGION void tsl9_remaining_record_dispatch_block_bb58(void)
{
    REGS;
    a0 = UINT32_C(0x0000002d); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb5c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb5c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xBB60..0xBB64. */
REGION void tsl9_remaining_record_dispatch_block_bb60(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb60:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb60\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xBB64..0xBB68. */
REGION void tsl9_remaining_record_dispatch_block_bb64(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 9\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bb66:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bb66\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bb2e\n");
    __builtin_unreachable();
}

/* Original0xBB68..0xBB72. */
REGION void tsl9_remaining_record_dispatch_block_bb68(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000007)); LIVE;
    a4 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb70:\n.option push\n.option rvc\nc.bnez a4,.Lremaining_record_dispatch_edge_bb70\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bbac\n");
    __builtin_unreachable();
}

/* Original0xBB72..0xBB7C. */
REGION void tsl9_remaining_record_dispatch_block_bb72(void)
{
    REGS;
    a4 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a4, a4, 0x18\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bb78:\n.option push\n.option norvc\nbltz a4,.Lremaining_record_dispatch_edge_bb78\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bbb2\n");
    __builtin_unreachable();
}

/* Original0xBB7C..0xBB82. */
REGION void tsl9_remaining_record_dispatch_block_bb7c(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb80:\n.option push\n.option rvc\nc.bnez a4,.Lremaining_record_dispatch_edge_bb80\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bbb8\n");
    __builtin_unreachable();
}

/* Original0xBB82..0xBB88. */
REGION void tsl9_remaining_record_dispatch_block_bb82(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb86:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bb86\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bbbe\n");
    __builtin_unreachable();
}

/* Original0xBB88..0xBB94. */
REGION void tsl9_remaining_record_dispatch_block_bb88(void)
{
    REGS;
    a3 = a3 & UINT32_C(0x00000060); LIVE;
    a5 = UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb90:\n.option push\n.option norvc\nbne a3,a5,.Lremaining_record_dispatch_edge_bb90\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBB94..0xBB9A. */
REGION void tsl9_remaining_record_dispatch_block_bb94(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bb96:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bb96\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_action_support_entry_9fb2\n");
    __builtin_unreachable();
}

/* Original0xBB9A..0xBB9C. */
REGION void tsl9_remaining_record_dispatch_block_bb9a(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bb9a:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bb9a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBB9C..0xBBA0. */
REGION void tsl9_remaining_record_dispatch_block_bb9c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 4\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bb9e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bb9e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBA0..0xBBA4. */
REGION void tsl9_remaining_record_dispatch_block_bba0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 2\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bba2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bba2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBA4..0xBBA8. */
REGION void tsl9_remaining_record_dispatch_block_bba4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 12\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bba6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bba6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBA8..0xBBAC. */
REGION void tsl9_remaining_record_dispatch_block_bba8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 10\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bbaa:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbaa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBAC..0xBBB2. */
REGION void tsl9_remaining_record_dispatch_block_bbac(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s1, 51\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bbb0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbb0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBB2..0xBBB8. */
REGION void tsl9_remaining_record_dispatch_block_bbb2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s1, 52\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bbb6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbb6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBB8..0xBBBE. */
REGION void tsl9_remaining_record_dispatch_block_bbb8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s1, 53\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bbbc:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbbc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBBE..0xBBC4. */
REGION void tsl9_remaining_record_dispatch_block_bbbe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s1, 54\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bbc2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbc2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba28\n");
    __builtin_unreachable();
}

/* Original0xBBC4..0xBBCE. */
REGION void tsl9_remaining_record_dispatch_block_bbc4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 9(s0)\n.option pop\n");
    a3 = a4 & UINT32_C(0x00000010); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bbcc:\n.option push\n.option rvc\nc.bnez a3,.Lremaining_record_dispatch_edge_bbcc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bbe2\n");
    __builtin_unreachable();
}

/* Original0xBBCE..0xBBD4. */
REGION void tsl9_remaining_record_dispatch_block_bbce(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bbd2:\n.option push\n.option rvc\nc.bnez a4,.Lremaining_record_dispatch_edge_bbd2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bbe6\n");
    __builtin_unreachable();
}

/* Original0xBBD4..0xBBDC. */
REGION void tsl9_remaining_record_dispatch_block_bbd4(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bbd8:\n.option push\n.option norvc\nbeqz a5,.Lremaining_record_dispatch_edge_bbd8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ba50\n");
    __builtin_unreachable();
}

/* Original0xBBDC..0xBBE0. */
REGION void tsl9_remaining_record_dispatch_block_bbdc(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bbdc:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bbdc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_action_support_entry_a02e\n");
    __builtin_unreachable();
}

/* Original0xBBE0..0xBBE2. */
REGION void tsl9_remaining_record_dispatch_block_bbe0(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bbe0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbe0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba50\n");
    __builtin_unreachable();
}

/* Original0xBBE2..0xBBE6. */
REGION void tsl9_remaining_record_dispatch_block_bbe2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 8\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bbe4:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbe4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba50\n");
    __builtin_unreachable();
}

/* Original0xBBE6..0xBBEA. */
REGION void tsl9_remaining_record_dispatch_block_bbe6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 14\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bbe8:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bbe8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba50\n");
    __builtin_unreachable();
}

/* Original0xBBEA..0xBBF2. */
REGION void tsl9_remaining_record_dispatch_block_bbea(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffb); LIVE;
    a5 = a5 & UINT32_C(0x000000fa); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bbf0:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bbf0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bc32\n");
    __builtin_unreachable();
}

/* Original0xBBF2..0xBC06. */
REGION void tsl9_remaining_record_dispatch_block_bbf2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000308)); LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc02:\n.option push\n.option norvc\nbne a4,a5,.Lremaining_record_dispatch_edge_bc02\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bcca\n");
    __builtin_unreachable();
}

/* Original0xBC06..0xBC1A. */
REGION void tsl9_remaining_record_dispatch_block_bc06(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000002f5)); LIVE;
    a5 = a5 >> UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc16:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_bc16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_baa4\n");
    __builtin_unreachable();
}

/* Original0xBC1A..0xBC26. */
REGION void tsl9_remaining_record_dispatch_block_bc1a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000002e5)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc22:\n.option push\n.option norvc\nbeqz a5,.Lremaining_record_dispatch_edge_bc22\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_baa4\n");
    __builtin_unreachable();
}

/* Original0xBC26..0xBC30. */
REGION void tsl9_remaining_record_dispatch_block_bc26(void)
{
    REGS;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc2c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bc2c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xBC30..0xBC32. */
REGION void tsl9_remaining_record_dispatch_block_bc30(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bc30:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bc30\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_baa4\n");
    __builtin_unreachable();
}

/* Original0xBC32..0xBC42. */
REGION void tsl9_remaining_record_dispatch_block_bc32(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a4 = UINT32_C(0x00000080); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc3e:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_bc3e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bc52\n");
    __builtin_unreachable();
}

/* Original0xBC42..0xBC52. */
REGION void tsl9_remaining_record_dispatch_block_bc42(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000020); LIVE;
    a2 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc4e:\n.option push\n.option norvc\nbne a2,a3,.Lremaining_record_dispatch_edge_bc4e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bc6e\n");
    __builtin_unreachable();
}

/* Original0xBC52..0xBC56. */
REGION void tsl9_remaining_record_dispatch_block_bc52(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bc52:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bc52\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_a658\n");
    __builtin_unreachable();
}

/* Original0xBC56..0xBC5C. */
REGION void tsl9_remaining_record_dispatch_block_bc56(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc58:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bc58\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_control_gates_provider_fe6a\n");
    __builtin_unreachable();
}

/* Original0xBC5C..0xBC6E. */
REGION void tsl9_remaining_record_dispatch_block_bc5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a0, 8(s0)\n.option pop\n");
    a0 = a0 & UINT32_C(0x000000c0); LIVE;
    a0 = a0 + UINT32_C(0xffffff80); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc6c:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bc6c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ba58\n");
    __builtin_unreachable();
}

/* Original0xBC6E..0xBC76. */
REGION void tsl9_remaining_record_dispatch_block_bc6e(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc72:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_bc72\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bcc2\n");
    __builtin_unreachable();
}

/* Original0xBC76..0xBC84. */
REGION void tsl9_remaining_record_dispatch_block_bc76(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s2, 2\n.option pop\n");
    a3 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc80:\n.option push\n.option norvc\nbeq a3,s2,.Lremaining_record_dispatch_edge_bc80\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bcc6\n");
    __builtin_unreachable();
}

/* Original0xBC84..0xBC8C. */
REGION void tsl9_remaining_record_dispatch_block_bc84(void)
{
    REGS;
    a5 = a5 & UINT32_C(0x0000000c); LIVE;
    a3 = UINT32_C(0x00000008); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bc88:\n.option push\n.option norvc\nbne a5,a3,.Lremaining_record_dispatch_edge_bc88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bcb0\n");
    __builtin_unreachable();
}

/* Original0xBC8C..0xBC90. */
REGION void tsl9_remaining_record_dispatch_block_bc8c(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bc8c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bc8c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xBC90..0xBC96. */
REGION void tsl9_remaining_record_dispatch_block_bc90(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 15\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bc92:\n.option push\n.option norvc\nbeq a0,s2,.Lremaining_record_dispatch_edge_bc92\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bc5c\n");
    __builtin_unreachable();
}

/* Original0xBC96..0xBCB0. */
REGION void tsl9_remaining_record_dispatch_block_bc96(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a5, a5, 614\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000257)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_bcae:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bcae\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bc5c\n");
    __builtin_unreachable();
}

/* Original0xBCB0..0xBCBC. */
REGION void tsl9_remaining_record_dispatch_block_bcb0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bcb8:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_bcb8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bc5c\n");
    __builtin_unreachable();
}

/* Original0xBCBC..0xBCC0. */
REGION void tsl9_remaining_record_dispatch_block_bcbc(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bcbc:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bcbc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_action_support_entry_a02e\n");
    __builtin_unreachable();
}

/* Original0xBCC0..0xBCC2. */
REGION void tsl9_remaining_record_dispatch_block_bcc0(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bcc0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bcc0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bc5c\n");
    __builtin_unreachable();
}

/* Original0xBCC2..0xBCC6. */
REGION void tsl9_remaining_record_dispatch_block_bcc2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 8\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bcc4:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bcc4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bc5c\n");
    __builtin_unreachable();
}

/* Original0xBCC6..0xBCCA. */
REGION void tsl9_remaining_record_dispatch_block_bcc6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 14\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bcc8:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bcc8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bc5c\n");
    __builtin_unreachable();
}

/* Original0xBCCA..0xBCD4. */
REGION void tsl9_remaining_record_dispatch_block_bcca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000234)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_bcd2:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bcd2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bc06\n");
    __builtin_unreachable();
}

/* Original0xBCD4..0xBCDE. */
REGION void tsl9_remaining_record_dispatch_block_bcd4(void)
{
    REGS;
    a2 = UINT32_C(0x00000002); LIVE;
    a1 = UINT32_C(0x00000002); LIVE;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bcda:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bcda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_storage_provider_e220\n");
    __builtin_unreachable();
}

/* Original0xBCDE..0xBCE0. */
REGION void tsl9_remaining_record_dispatch_block_bcde(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bcde:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bcde\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bc06\n");
    __builtin_unreachable();
}

/* Original0xBD3A..0xBD46. */
REGION void tsl9_record_dispatch_provider_bd3a(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000001d1)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBD88..0xBDA4. */
REGION void tsl9_feature_external_bd88(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 3(a0)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s4, 24(sp)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nandi s1, s1, 3\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bda2:\n.option push\n.option rvc\nc.beqz s1,.Lremaining_record_dispatch_edge_bda2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bdc6\n");
    __builtin_unreachable();
}

/* Original0xBDA4..0xBDAA. */
REGION void tsl9_remaining_record_dispatch_block_bda4(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bda6:\n.option push\n.option norvc\nbeq s1,a5,.Lremaining_record_dispatch_edge_bda6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bfe6\n");
    __builtin_unreachable();
}

/* Original0xBDAA..0xBDB0. */
REGION void tsl9_remaining_record_dispatch_block_bdaa(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bdae:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bdae\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bdb6\n");
    __builtin_unreachable();
}

/* Original0xBDB0..0xBDB6. */
REGION void tsl9_remaining_record_dispatch_block_bdb0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bdb2:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bdb2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xBDB6..0xBDC6. */
REGION void tsl9_remaining_record_dispatch_block_bdb6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s4, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBDC6..0xBDD8. */
REGION void tsl9_remaining_record_dispatch_block_bdc6(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s3, gp, 84\n.option pop\n");
    PORT(".option push\n.option norvc\nlw a3, 0(s3)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s2, 10(a3)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi a5, s2, 2\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bdd6:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bdd6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bdf6\n");
    __builtin_unreachable();
}

/* Original0xBDD8..0xBDE6. */
REGION void tsl9_remaining_record_dispatch_block_bdd8(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)); LIVE;
    a4 = UINT32_C(0x00000009); LIVE;
    a2 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bde2:\n.option push\n.option norvc\nbne a2,a4,.Lremaining_record_dispatch_edge_bde2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bdf6\n");
    __builtin_unreachable();
}

/* Original0xBDE6..0xBDF6. */
REGION void tsl9_remaining_record_dispatch_block_bde6(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000009)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xBDF6..0xBDFC. */
REGION void tsl9_remaining_record_dispatch_block_bdf6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi a5, s2, 8\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bdfa:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bdfa\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_be5c\n");
    __builtin_unreachable();
}

/* Original0xBDFC..0xBE0A. */
REGION void tsl9_remaining_record_dispatch_block_bdfc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 10(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a2 = a4 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_be06:\n.option push\n.option norvc\nbne a2,a5,.Lremaining_record_dispatch_edge_be06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_be2a\n");
    __builtin_unreachable();
}

/* Original0xBE0A..0xBE18. */
REGION void tsl9_remaining_record_dispatch_block_be0a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000010); LIVE;
    a1 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_be14:\n.option push\n.option norvc\nbne a1,a2,.Lremaining_record_dispatch_edge_be14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_be2a\n");
    __builtin_unreachable();
}

/* Original0xBE18..0xBE2A. */
REGION void tsl9_remaining_record_dispatch_block_be18(void)
{
    REGS;
    a5 = a5 & UINT32_C(0xffffffcf); LIVE;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xBE2A..0xBE3A. */
REGION void tsl9_remaining_record_dispatch_block_be2a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a2 = UINT32_C(0x00000080); LIVE;
    a5 = a5 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_be36:\n.option push\n.option norvc\nbne a5,a2,.Lremaining_record_dispatch_edge_be36\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_be5c\n");
    __builtin_unreachable();
}

/* Original0xBE3A..0xBE46. */
REGION void tsl9_remaining_record_dispatch_block_be3a(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x000000c0); LIVE;
    a5 = UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_be42:\n.option push\n.option norvc\nbne a4,a5,.Lremaining_record_dispatch_edge_be42\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_be5c\n");
    __builtin_unreachable();
}

/* Original0xBE46..0xBE5C. */
REGION void tsl9_remaining_record_dispatch_block_be46(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 10(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 10(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xBE5C..0xBE70. */
REGION void tsl9_remaining_record_dispatch_block_be5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000000b3)); LIVE;
    PORT(".option push\n.option norvc\nauipc s1, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s1, s1, 152\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_be6c:\n.option push\n.option norvc\nbeqz a5,.Lremaining_record_dispatch_edge_be6c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bf5a\n");
    __builtin_unreachable();
}

/* Original0xBE70..0xBE78. */
REGION void tsl9_remaining_record_dispatch_block_be70(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_be76:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_be76\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bf42\n");
    __builtin_unreachable();
}

/* Original0xBE78..0xBE82. */
REGION void tsl9_remaining_record_dispatch_block_be78(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 19(s1)\n.option pop\n");
    a4 = UINT32_C(0x00000005); LIVE;
    PORT(".Lremaining_record_dispatch_edge_be7e:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_be7e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bf1a\n");
    __builtin_unreachable();
}

/* Original0xBE82..0xBE98. */
REGION void tsl9_remaining_record_dispatch_block_be82(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 19(s1)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nauipc a2, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000083)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_be94:\n.option push\n.option norvc\nbleu a5,a4,.Lremaining_record_dispatch_edge_be94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_beec\n");
    __builtin_unreachable();
}

/* Original0xBE98..0xBEA4. */
REGION void tsl9_remaining_record_dispatch_block_be98(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x00000003)); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000020); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bea2:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bea2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bf56\n");
    __builtin_unreachable();
}

/* Original0xBEA4..0xBEAE. */
REGION void tsl9_remaining_record_dispatch_block_bea4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 16(s1)\n.option pop\n");
    a4 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_beaa:\n.option push\n.option norvc\nbne a4,a5,.Lremaining_record_dispatch_edge_beaa\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bdaa\n");
    __builtin_unreachable();
}

/* Original0xBEAE..0xBEBE. */
REGION void tsl9_remaining_record_dispatch_block_beae(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_beba:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_beba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bdaa\n");
    __builtin_unreachable();
}

/* Original0xBEBE..0xBEEC. */
REGION void tsl9_remaining_record_dispatch_block_bebe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000004e)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 1(s1)\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a4; LIVE;
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x0000002b)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_beea:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_beea\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bdaa\n");
    __builtin_unreachable();
}

/* Original0xBEEC..0xBEF4. */
REGION void tsl9_remaining_record_dispatch_block_beec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nandi s2, s2, 48\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bef0:\n.option push\n.option norvc\nbeqz s2,.Lremaining_record_dispatch_edge_bef0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBEF4..0xBEF8. */
REGION void tsl9_remaining_record_dispatch_block_bef4(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bef4:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bef4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xBEF8..0xBF0E. */
REGION void tsl9_remaining_record_dispatch_block_bef8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s3)\n.option pop\n");
    a4 = UINT32_C(0x0000000a); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000a)); LIVE;
    a5 = a5 >> UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    a5 = a5 * a4; LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf0a:\n.option push\n.option norvc\nblt a5,a0,.Lremaining_record_dispatch_edge_bf0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBF0E..0xBF14. */
REGION void tsl9_remaining_record_dispatch_block_bf0e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffb); LIVE;
    __builtin_unreachable();
}

/* Original0xBF14..0xBF1A. */
REGION void tsl9_remaining_record_dispatch_block_bf14(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bf18:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bf18\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bf3a\n");
    __builtin_unreachable();
}

/* Original0xBF1A..0xBF24. */
REGION void tsl9_remaining_record_dispatch_block_bf1a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 22(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf22:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bf22\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBF24..0xBF28. */
REGION void tsl9_remaining_record_dispatch_block_bf24(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bf24:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bf24\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_continuations_provider_ef6c\n");
    __builtin_unreachable();
}

/* Original0xBF28..0xBF3A. */
REGION void tsl9_remaining_record_dispatch_block_bf28(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    a5 = a0 << UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nlbu a0, 3(s0)\n.option pop\n");
    a0 = a0 & UINT32_C(0xfffffffb); LIVE;
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option norvc\nsb a0, 3(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xBF3A..0xBF42. */
REGION void tsl9_remaining_record_dispatch_block_bf3a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf40:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bf40\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBF42..0xBF54. */
REGION void tsl9_remaining_record_dispatch_block_bf42(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffcd)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 22(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf52:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bf52\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBF54..0xBF56. */
REGION void tsl9_remaining_record_dispatch_block_bf54(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0xBF56..0xBF58. */
REGION void tsl9_remaining_record_dispatch_block_bf56(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bf56:\n.option push\n.option rvc\nc.jal .Lremaining_record_dispatch_edge_bf56\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_provider_bd6e\n");
    __builtin_unreachable();
}

/* Original0xBF58..0xBF5A. */
REGION void tsl9_remaining_record_dispatch_block_bf58(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bf58:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bf58\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBF5A..0xBF64. */
REGION void tsl9_remaining_record_dispatch_block_bf5a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 21(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf62:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bf62\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bf24\n");
    __builtin_unreachable();
}

/* Original0xBF64..0xBF6E. */
REGION void tsl9_remaining_record_dispatch_block_bf64(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 20(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf6c:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bf6c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bf24\n");
    __builtin_unreachable();
}

/* Original0xBF6E..0xBF78. */
REGION void tsl9_remaining_record_dispatch_block_bf6e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 22(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf76:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_bf76\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bf24\n");
    __builtin_unreachable();
}

/* Original0xBF78..0xBF80. */
REGION void tsl9_remaining_record_dispatch_block_bf78(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bf7e:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bf7e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bfd0\n");
    __builtin_unreachable();
}

/* Original0xBF80..0xBF84. */
REGION void tsl9_remaining_record_dispatch_block_bf80(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bf80:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bf80\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b6a8\n");
    __builtin_unreachable();
}

/* Original0xBF84..0xBF86. */
REGION void tsl9_remaining_record_dispatch_block_bf84(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bf84:\n.option push\n.option rvc\nc.bnez a0,.Lremaining_record_dispatch_edge_bf84\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_bfd0\n");
    __builtin_unreachable();
}

/* Original0xBF86..0xBF98. */
REGION void tsl9_remaining_record_dispatch_block_bf86(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s4, 1\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s4, -121(a5)\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s2, s2, 48\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bf94:\n.option push\n.option norvc\nbeqz s2,.Lremaining_record_dispatch_edge_bf94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBF98..0xBF9C. */
REGION void tsl9_remaining_record_dispatch_block_bf98(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_bf98:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bf98\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xBF9C..0xBFB4. */
REGION void tsl9_remaining_record_dispatch_block_bf9c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s3)\n.option pop\n");
    a3 = UINT32_C(0x0000000a); LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x0000000a)); LIVE;
    a5 = a4 >> UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    a5 = a5 * a3; LIVE;
    PORT(".Lremaining_record_dispatch_edge_bfb0:\n.option push\n.option norvc\nblt a5,a0,.Lremaining_record_dispatch_edge_bfb0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBFB4..0xBFC0. */
REGION void tsl9_remaining_record_dispatch_block_bfb4(void)
{
    REGS;
    a0 = a4 >> UINT32_C(0x00000006); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bfbc:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_bfbc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_f016\n");
    __builtin_unreachable();
}

/* Original0xBFC0..0xBFD0. */
REGION void tsl9_remaining_record_dispatch_block_bfc0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s4, 15(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffb); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bfce:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bfce\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBFD0..0xBFDC. */
REGION void tsl9_remaining_record_dispatch_block_bfd0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 23(s1)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bfd8:\n.option push\n.option norvc\nbeqz a5,.Lremaining_record_dispatch_edge_bfd8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_bea4\n");
    __builtin_unreachable();
}

/* Original0xBFDC..0xBFE6. */
REGION void tsl9_remaining_record_dispatch_block_bfdc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_bfe4:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_bfe4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bf14\n");
    __builtin_unreachable();
}

/* Original0xBFE6..0xBFF8. */
REGION void tsl9_remaining_record_dispatch_block_bfe6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffff27)); LIVE;
    PORT(".option push\n.option norvc\nauipc s2, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, s2, -242\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_bff6:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_bff6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c01a\n");
    __builtin_unreachable();
}

/* Original0xBFF8..0xC01A. */
REGION void tsl9_remaining_record_dispatch_block_bff8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 17(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, 15(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xffffff0b)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0xffffff9f); LIVE;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xC01A..0xC024. */
REGION void tsl9_remaining_record_dispatch_block_c01a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 18(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c022:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_c022\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c058\n");
    __builtin_unreachable();
}

/* Original0xC024..0xC058. */
REGION void tsl9_remaining_record_dispatch_block_c024(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 18(s2)\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffffee4)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffff9f); LIVE;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffcf); LIVE;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xC058..0xC05E. */
REGION void tsl9_remaining_record_dispatch_block_c058(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c05c:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_c05c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c120\n");
    __builtin_unreachable();
}

/* Original0xC05E..0xC066. */
REGION void tsl9_remaining_record_dispatch_block_c05e(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a0, sp, 15\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c062:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_c062\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_field_transitions_provider_c7e8\n");
    __builtin_unreachable();
}

/* Original0xC066..0xC068. */
REGION void tsl9_remaining_record_dispatch_block_c066(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_c066:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_c066\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c0aa\n");
    __builtin_unreachable();
}

/* Original0xC068..0xC07C. */
REGION void tsl9_remaining_record_dispatch_block_c068(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000160); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c078:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_c078\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c15a\n");
    __builtin_unreachable();
}

/* Original0xC07C..0xC090. */
REGION void tsl9_remaining_record_dispatch_block_c07c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a0 = a0 + UINT32_C(0xffffffff); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 << UINT32_C(0x00000004); LIVE;
    a5 = a5 & UINT32_C(0xffffffef); LIVE;
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option norvc\nsb a0, 9(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC090..0xC094. */
REGION void tsl9_remaining_record_dispatch_block_c090(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_c090:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_c090\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_cd44\n");
    __builtin_unreachable();
}

/* Original0xC094..0xC096. */
REGION void tsl9_remaining_record_dispatch_block_c094(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_c094:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_c094\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c0aa\n");
    __builtin_unreachable();
}

/* Original0xC096..0xC0AA. */
REGION void tsl9_remaining_record_dispatch_block_c096(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x00000032); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_literal_c09e:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_entry_b5f6\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_c09e\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c0a6:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_c0a6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xC0AA..0xC0B4. */
REGION void tsl9_remaining_record_dispatch_block_c0aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffe6a)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c0b2:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_c0b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c120\n");
    __builtin_unreachable();
}

/* Original0xC0B4..0xC0D2. */
REGION void tsl9_remaining_record_dispatch_block_c0b4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffe60)) = (uint8_t)0; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000020); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c0ce:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_c0ce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c120\n");
    __builtin_unreachable();
}

/* Original0xC0D2..0xC0E4. */
REGION void tsl9_remaining_record_dispatch_block_c0d2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = a5 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c0e0:\n.option push\n.option norvc\nbleu a4,a3,.Lremaining_record_dispatch_edge_c0e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c120\n");
    __builtin_unreachable();
}

/* Original0xC0E4..0xC0F4. */
REGION void tsl9_remaining_record_dispatch_block_c0e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a2, 0x20000\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, a2, 212\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000020)); LIVE;
    a4 = a4 & UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c0f2:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_c0f2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c120\n");
    __builtin_unreachable();
}

/* Original0xC0F4..0xC104. */
REGION void tsl9_remaining_record_dispatch_block_c0f4(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x000000ba)); LIVE;
    a2 = UINT32_C(0x00000030); LIVE;
    a4 = a4 & UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c100:\n.option push\n.option norvc\nbne a4,a2,.Lremaining_record_dispatch_edge_c100\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c120\n");
    __builtin_unreachable();
}

/* Original0xC104..0xC10E. */
REGION void tsl9_remaining_record_dispatch_block_c104(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c10a:\n.option push\n.option norvc\nbltu a3,a5,.Lremaining_record_dispatch_edge_c10a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c172\n");
    __builtin_unreachable();
}

/* Original0xC10E..0xC11A. */
REGION void tsl9_remaining_record_dispatch_block_c10e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC11A..0xC120. */
REGION void tsl9_remaining_record_dispatch_block_c11a(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xC120..0xC12C. */
REGION void tsl9_remaining_record_dispatch_block_c120(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 16(s2)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c128:\n.option push\n.option norvc\nbeqz a5,.Lremaining_record_dispatch_edge_c128\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c2b8\n");
    __builtin_unreachable();
}

/* Original0xC12C..0xC148. */
REGION void tsl9_remaining_record_dispatch_block_c12c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 16(s2)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a3 = a4 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a2 = UINT32_C(0x00000011); LIVE;
    a3 = a3 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c144:\n.option push\n.option norvc\nbltu a2,a5,.Lremaining_record_dispatch_edge_c144\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c194\n");
    __builtin_unreachable();
}

/* Original0xC148..0xC15A. */
REGION void tsl9_remaining_record_dispatch_block_c148(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_c148:\n.option push\n.option norvc\nauipc a2,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_static_data_19e08\naddi a2,a2,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_c148\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a2; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 + a2; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC15A..0xC15E. */
REGION void tsl9_remaining_record_dispatch_block_c15a(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_c15a:\n.option push\n.option norvc\nbne a0,a4,.Lremaining_record_dispatch_edge_c15a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c160\n");
    __builtin_unreachable();
}

/* Original0xC15E..0xC160. */
REGION void tsl9_remaining_record_dispatch_block_c15e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s1, 2\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC160..0xC172. */
REGION void tsl9_remaining_record_dispatch_block_c160(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s1, s1, 0x6\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    PORT(".option push\n.option rvc\nor s1, s1, a5\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s1, 8(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c170:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c170\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c090\n");
    __builtin_unreachable();
}

/* Original0xC172..0xC184. */
REGION void tsl9_remaining_record_dispatch_block_c172(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 8(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c182:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c182\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c11a\n");
    __builtin_unreachable();
}

/* Original0xC184..0xC190. */
REGION void tsl9_remaining_record_dispatch_block_c184(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffc0); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC190..0xC194. */
REGION void tsl9_remaining_record_dispatch_block_c190(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC194..0xC19A. */
REGION void tsl9_remaining_record_dispatch_block_c194(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c196:\n.option push\n.option norvc\nbltu a5,a3,.Lremaining_record_dispatch_edge_c196\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c27a\n");
    __builtin_unreachable();
}

/* Original0xC19A..0xC19C. */
REGION void tsl9_remaining_record_dispatch_block_c19a(void)
{
    REGS;
    a4 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC19C..0xC1AC. */
REGION void tsl9_remaining_record_dispatch_block_c19c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 16(s2)\n.option pop\n");
    a3 = UINT32_C(0x0000000a); LIVE;
    a5 = a5 + UINT32_C(0xfffffffa); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c1a8:\n.option push\n.option norvc\nbltu a3,a5,.Lremaining_record_dispatch_edge_c1a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c2b6\n");
    __builtin_unreachable();
}

/* Original0xC1AC..0xC1BE. */
REGION void tsl9_remaining_record_dispatch_block_c1ac(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_c1ac:\n.option push\n.option norvc\nauipc a3,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_static_data_19e50\naddi a3,a3,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_c1ac\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a3; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 + a3; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC1BE..0xC1C8. */
REGION void tsl9_remaining_record_dispatch_block_c1be(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffe7); LIVE;
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0xC1C8..0xC1CE. */
REGION void tsl9_remaining_record_dispatch_block_c1c8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c1cc:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c1cc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c194\n");
    __builtin_unreachable();
}

/* Original0xC1CE..0xC1D8. */
REGION void tsl9_remaining_record_dispatch_block_c1ce(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x0000003f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c1d6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c1d6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c190\n");
    __builtin_unreachable();
}

/* Original0xC1D8..0xC1E4. */
REGION void tsl9_remaining_record_dispatch_block_c1d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    __builtin_unreachable();
}

/* Original0xC1E4..0xC1EA. */
REGION void tsl9_remaining_record_dispatch_block_c1e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c1e8:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c1e8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c194\n");
    __builtin_unreachable();
}

/* Original0xC1EA..0xC1F8. */
REGION void tsl9_remaining_record_dispatch_block_c1ea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffff9f); LIVE;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c1f6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c1f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c1c8\n");
    __builtin_unreachable();
}

/* Original0xC1F8..0xC204. */
REGION void tsl9_remaining_record_dispatch_block_c1f8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffc0); LIVE;
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC204..0xC20A. */
REGION void tsl9_remaining_record_dispatch_block_c204(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c208:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c208\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c194\n");
    __builtin_unreachable();
}

/* Original0xC20A..0xC216. */
REGION void tsl9_remaining_record_dispatch_block_c20a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff3); LIVE;
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c214:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c214\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c1e4\n");
    __builtin_unreachable();
}

/* Original0xC216..0xC220. */
REGION void tsl9_remaining_record_dispatch_block_c216(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x0000003f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c21e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c21e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c204\n");
    __builtin_unreachable();
}

/* Original0xC220..0xC22C. */
REGION void tsl9_remaining_record_dispatch_block_c220(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c22a:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c22a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c1e4\n");
    __builtin_unreachable();
}

/* Original0xC22C..0xC23A. */
REGION void tsl9_remaining_record_dispatch_block_c22c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffcf); LIVE;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c238:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c238\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c1e4\n");
    __builtin_unreachable();
}

/* Original0xC23A..0xC248. */
REGION void tsl9_remaining_record_dispatch_block_c23a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffc0); LIVE;
    a5 = a5 | UINT32_C(0x00000005); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c246:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c246\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c204\n");
    __builtin_unreachable();
}

/* Original0xC248..0xC256. */
REGION void tsl9_remaining_record_dispatch_block_c248(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffc0); LIVE;
    a5 = a5 | UINT32_C(0x0000003b); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c254:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c254\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c204\n");
    __builtin_unreachable();
}

/* Original0xC256..0xC25C. */
REGION void tsl9_remaining_record_dispatch_block_c256(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c258:\n.option push\n.option norvc\nbleu a3,a5,.Lremaining_record_dispatch_edge_c258\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c2a6\n");
    __builtin_unreachable();
}

/* Original0xC25C..0xC27A. */
REGION void tsl9_remaining_record_dispatch_block_c25c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 1(s2)\n.option pop\n");
    a5 = a5 ^ UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a3, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0xfffffc99)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffff3); LIVE;
    a5 = a5 | UINT32_C(0x00000008); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC27A..0xC284. */
REGION void tsl9_remaining_record_dispatch_block_c27a(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xfffffffb); LIVE;
    a5 = a5 & UINT32_C(0x000000fa); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c282:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_c282\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c308\n");
    __builtin_unreachable();
}

/* Original0xC284..0xC294. */
REGION void tsl9_remaining_record_dispatch_block_c284(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 16(s2)\n.option pop\n");
    a4 = UINT32_C(0x0000000a); LIVE;
    a5 = a5 + UINT32_C(0xfffffffa); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c290:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_c290\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_c308\n");
    __builtin_unreachable();
}

/* Original0xC294..0xC2A6. */
REGION void tsl9_remaining_record_dispatch_block_c294(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_c294:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_static_data_19e7c\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_c294\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC2A6..0xC2AA. */
REGION void tsl9_remaining_record_dispatch_block_c2a6(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c2a8:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c2a8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c19c\n");
    __builtin_unreachable();
}

/* Original0xC2AA..0xC2B2. */
REGION void tsl9_remaining_record_dispatch_block_c2aa(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xC2B2..0xC2B6. */
REGION void tsl9_remaining_record_dispatch_block_c2b2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC2B6..0xC2B8. */
REGION void tsl9_remaining_record_dispatch_block_c2b6(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_c2b6:\n.option push\n.option rvc\nc.bnez a4,.Lremaining_record_dispatch_edge_c2b6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_c308\n");
    __builtin_unreachable();
}

/* Original0xC2B8..0xC2BE. */
REGION void tsl9_remaining_record_dispatch_block_c2b8(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c2ba:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_c2ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_entry_a204\n");
    __builtin_unreachable();
}

/* Original0xC2BE..0xC2C0. */
REGION void tsl9_remaining_record_dispatch_block_c2be(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_c2be:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c2be\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_bdaa\n");
    __builtin_unreachable();
}

/* Original0xC2C0..0xC2CA. */
REGION void tsl9_remaining_record_dispatch_block_c2c0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c2c8:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c2c8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c2b2\n");
    __builtin_unreachable();
}

/* Original0xC2CA..0xC2D4. */
REGION void tsl9_remaining_record_dispatch_block_c2ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c2d2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c2d2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c2b2\n");
    __builtin_unreachable();
}

/* Original0xC2D4..0xC2DE. */
REGION void tsl9_remaining_record_dispatch_block_c2d4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c2dc:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c2dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c2b2\n");
    __builtin_unreachable();
}

/* Original0xC2DE..0xC2F8. */
REGION void tsl9_remaining_record_dispatch_block_c2de(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 8(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 10(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000060); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 10(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c2f6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c2f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c2b6\n");
    __builtin_unreachable();
}

/* Original0xC2F8..0xC308. */
REGION void tsl9_remaining_record_dispatch_block_c2f8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xC308..0xC318. */
REGION void tsl9_remaining_record_dispatch_block_c308(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x20000\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffc04)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000f)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_c316:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c316\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c2b8\n");
    __builtin_unreachable();
}

/* Original0xC318..0xC324. */
REGION void tsl9_remaining_record_dispatch_block_c318(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xffffffcf); LIVE;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    __builtin_unreachable();
}

/* Original0xC324..0xC32A. */
REGION void tsl9_remaining_record_dispatch_block_c324(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 8(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c328:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c328\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c308\n");
    __builtin_unreachable();
}

/* Original0xC32A..0xC338. */
REGION void tsl9_remaining_record_dispatch_block_c32a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 8(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".Lremaining_record_dispatch_edge_c336:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c336\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c324\n");
    __builtin_unreachable();
}

/* Original0xC338..0xC348. */
REGION void tsl9_remaining_record_dispatch_block_c338(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffc); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c346:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c346\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c308\n");
    __builtin_unreachable();
}

/* Original0xC348..0xC35A. */
REGION void tsl9_remaining_record_dispatch_block_c348(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_c358:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_c358\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_c308\n");
    __builtin_unreachable();
}

/* Original0xCE88..0xCE98. */
REGION void tsl9_record_dispatch_provider_ce88(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ce94:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_ce94\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_cea4\n");
    __builtin_unreachable();
}

/* Original0xCE98..0xCEA4. */
REGION void tsl9_remaining_record_dispatch_block_ce98(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1ffff\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000090)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xCEA4..0xCEAA. */
REGION void tsl9_remaining_record_dispatch_block_cea4(void)
{
    REGS;
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".Lremaining_record_dispatch_edge_cea6:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_cea6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_b6f4\n");
    __builtin_unreachable();
}

/* Original0xD868..0xD86A. */
REGION void tsl9_remaining_record_dispatch_entry_d868(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d868:\n.option push\n.option rvc\nc.bnez a0,.Lremaining_record_dispatch_edge_d868\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d870\n");
    __builtin_unreachable();
}

/* Original0xD86A..0xD870. */
REGION void tsl9_remaining_record_dispatch_block_d86a(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD870..0xD88A. */
REGION void tsl9_remaining_record_dispatch_block_d870(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -48\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nli s3, 1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a2\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s2, a3\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d886:\n.option push\n.option norvc\nbeq a5,s3,.Lremaining_record_dispatch_edge_d886\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d8a6\n");
    __builtin_unreachable();
}

/* Original0xD88A..0xD88C. */
REGION void tsl9_remaining_record_dispatch_block_d88a(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d88a:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_d88a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d896\n");
    __builtin_unreachable();
}

/* Original0xD88C..0xD892. */
REGION void tsl9_remaining_record_dispatch_block_d88c(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d88e:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_d88e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d8da\n");
    __builtin_unreachable();
}

/* Original0xD892..0xD896. */
REGION void tsl9_remaining_record_dispatch_block_d892(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d894:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_d894\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_d8ca\n");
    __builtin_unreachable();
}

/* Original0xD896..0xD898. */
REGION void tsl9_remaining_record_dispatch_block_d896(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d896:\n.option push\n.option rvc\nc.beqz a1,.Lremaining_record_dispatch_edge_d896\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d892\n");
    __builtin_unreachable();
}

/* Original0xD898..0xD89C. */
REGION void tsl9_remaining_record_dispatch_block_d898(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d898:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d898\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xD89C..0xD8A6. */
REGION void tsl9_remaining_record_dispatch_block_d89c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsw a0, 0(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nsb s3, 0(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d8a4:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_d8a4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_d892\n");
    __builtin_unreachable();
}

/* Original0xD8A6..0xD8A8. */
REGION void tsl9_remaining_record_dispatch_block_d8a6(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d8a6:\n.option push\n.option rvc\nc.beqz a1,.Lremaining_record_dispatch_edge_d8a6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d8dc\n");
    __builtin_unreachable();
}

/* Original0xD8A8..0xD8B0. */
REGION void tsl9_remaining_record_dispatch_block_d8a8(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv s1, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lremaining_record_dispatch_edge_d8ac:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d8ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_channel_external_81b0\n");
    __builtin_unreachable();
}

/* Original0xD8B0..0xD8C2. */
REGION void tsl9_remaining_record_dispatch_block_d8b0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlw a5, 0(s2)\n.option pop\n");
    a0 = a0 - a5; LIVE;
    a5 = UINT32_C(0x000003e8); LIVE;
    PORT(".option push\n.option norvc\nmul s1, s1, a5\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d8be:\n.option push\n.option norvc\nbltu a0,s1,.Lremaining_record_dispatch_edge_d8be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d892\n");
    __builtin_unreachable();
}

/* Original0xD8C2..0xD8CA. */
REGION void tsl9_remaining_record_dispatch_block_d8c2(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 0(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD8CA..0xD8DA. */
REGION void tsl9_remaining_record_dispatch_block_d8ca(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 44(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 40(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 36(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 32(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s3, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 48\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD8DA..0xD8DC. */
REGION void tsl9_remaining_record_dispatch_block_d8da(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d8da:\n.option push\n.option rvc\nc.bnez a1,.Lremaining_record_dispatch_edge_d8da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d892\n");
    __builtin_unreachable();
}

/* Original0xD8DC..0xD8E2. */
REGION void tsl9_remaining_record_dispatch_block_d8dc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb zero, 0(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d8e0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_d8e0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_d892\n");
    __builtin_unreachable();
}

/* Original0xD8E2..0xD8F2. */
REGION void tsl9_remaining_record_dispatch_entry_d8e2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d8ee:\n.option push\n.option norvc\nbleu a5,a4,.Lremaining_record_dispatch_edge_d8ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d90a\n");
    __builtin_unreachable();
}

/* Original0xD8F2..0xD902. */
REGION void tsl9_remaining_record_dispatch_block_d8f2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000000fa); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d8fe:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d8fe\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xD902..0xD90A. */
REGION void tsl9_remaining_record_dispatch_block_d902(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD90A..0xD90E. */
REGION void tsl9_remaining_record_dispatch_block_d90a(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD90E..0xD91E. */
REGION void tsl9_remaining_record_dispatch_entry_d90e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = a4 + UINT32_C(0xfffffff9); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d91a:\n.option push\n.option norvc\nbltu a3,a4,.Lremaining_record_dispatch_edge_d91a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d93a\n");
    __builtin_unreachable();
}

/* Original0xD91E..0xD926. */
REGION void tsl9_remaining_record_dispatch_block_d91e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d922:\n.option push\n.option norvc\nbeq a5,a3,.Lremaining_record_dispatch_edge_d922\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d954\n");
    __builtin_unreachable();
}

/* Original0xD926..0xD92A. */
REGION void tsl9_remaining_record_dispatch_block_d926(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d928:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_d928\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d954\n");
    __builtin_unreachable();
}

/* Original0xD92A..0xD93A. */
REGION void tsl9_remaining_record_dispatch_block_d92a(void)
{
    REGS;
    a0 = a5 + UINT32_C(0xfffffffd); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsltu a0, a3, a0\n.option pop\n");
    a0 = a0 + UINT32_C(0x00000002); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD93A..0xD94C. */
REGION void tsl9_remaining_record_dispatch_block_d93a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, a1\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000000fa); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d948:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d948\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xD94C..0xD954. */
REGION void tsl9_remaining_record_dispatch_block_d94c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD954..0xD956. */
REGION void tsl9_remaining_record_dispatch_block_d954(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xD956..0xD95E. */
REGION void tsl9_remaining_record_dispatch_entry_d956(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d95a:\n.option push\n.option norvc\nbeq a5,a2,.Lremaining_record_dispatch_edge_d95a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d962\n");
    __builtin_unreachable();
}

/* Original0xD95E..0xD962. */
REGION void tsl9_remaining_record_dispatch_block_d95e(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint8_t)a2; LIVE;
    __builtin_unreachable();
}

/* Original0xD962..0xD970. */
REGION void tsl9_remaining_record_dispatch_block_d962(void)
{
    REGS;
    a5 = a2 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d96c:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_d96c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_da34\n");
    __builtin_unreachable();
}

/* Original0xD970..0xD97C. */
REGION void tsl9_remaining_record_dispatch_block_d970(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d978:\n.option push\n.option norvc\nbeq a5,a2,.Lremaining_record_dispatch_edge_d978\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d984\n");
    __builtin_unreachable();
}

/* Original0xD97C..0xD984. */
REGION void tsl9_remaining_record_dispatch_block_d97c(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)) = (uint8_t)a2; LIVE;
    PORT(".Lremaining_record_dispatch_edge_d980:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d980\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xD984..0xD988. */
REGION void tsl9_remaining_record_dispatch_block_d984(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d984:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d984\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_request_records_provider_d76c\n");
    __builtin_unreachable();
}

/* Original0xD988..0xD98A. */
REGION void tsl9_remaining_record_dispatch_block_d988(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d988:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_d988\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d9ca\n");
    __builtin_unreachable();
}

/* Original0xD98A..0xD990. */
REGION void tsl9_remaining_record_dispatch_block_d98a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000101)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d98e:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_d98e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_da2e\n");
    __builtin_unreachable();
}

/* Original0xD990..0xD9A4. */
REGION void tsl9_remaining_record_dispatch_block_d990(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000101)) = (uint8_t)0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a4 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d9a2:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_d9a2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_d9b2\n");
    __builtin_unreachable();
}

/* Original0xD9A4..0xD9AC. */
REGION void tsl9_remaining_record_dispatch_block_d9a4(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000018); LIVE;
    PORT(".option push\n.option rvc\nsrai a5, a5, 0x18\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d9a8:\n.option push\n.option norvc\nbltz a5,.Lremaining_record_dispatch_edge_d9a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d9be\n");
    __builtin_unreachable();
}

/* Original0xD9AC..0xD9B2. */
REGION void tsl9_remaining_record_dispatch_block_d9ac(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d9ae:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d9ae\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_request_records_entry_fe1c\n");
    __builtin_unreachable();
}

/* Original0xD9B2..0xD9BE. */
REGION void tsl9_remaining_record_dispatch_block_d9b2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000069); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_d9ba:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_d9ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xD9BE..0xD9C2. */
REGION void tsl9_remaining_record_dispatch_block_d9be(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d9be:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_d9be\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xD9C2..0xD9C8. */
REGION void tsl9_remaining_record_dispatch_block_d9c2(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d9c4:\n.option push\n.option norvc\nbne a0,a5,.Lremaining_record_dispatch_edge_d9c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d9ac\n");
    __builtin_unreachable();
}

/* Original0xD9C8..0xD9CA. */
REGION void tsl9_remaining_record_dispatch_block_d9c8(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_d9c8:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_d9c8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_d9b2\n");
    __builtin_unreachable();
}

/* Original0xD9CA..0xD9D8. */
REGION void tsl9_remaining_record_dispatch_block_d9ca(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000005a0)); LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d9d4:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_d9d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d9fc\n");
    __builtin_unreachable();
}

/* Original0xD9D8..0xD9E4. */
REGION void tsl9_remaining_record_dispatch_block_d9d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000594)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d9e0:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_d9e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d9fc\n");
    __builtin_unreachable();
}

/* Original0xD9E4..0xD9F0. */
REGION void tsl9_remaining_record_dispatch_block_d9e4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000587)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d9ec:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_d9ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_d9fc\n");
    __builtin_unreachable();
}

/* Original0xD9F0..0xD9FC. */
REGION void tsl9_remaining_record_dispatch_block_d9f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000057d)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_d9f8:\n.option push\n.option norvc\nbne a4,a5,.Lremaining_record_dispatch_edge_d9f8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_da2e\n");
    __builtin_unreachable();
}

/* Original0xD9FC..0xDA02. */
REGION void tsl9_remaining_record_dispatch_block_d9fc(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000101)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_da00:\n.option push\n.option rvc\nc.bnez a5,.Lremaining_record_dispatch_edge_da00\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_da2e\n");
    __builtin_unreachable();
}

/* Original0xDA02..0xDA16. */
REGION void tsl9_remaining_record_dispatch_block_da02(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000101)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lremaining_record_dispatch_edge_da14:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_da14\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_da1c\n");
    __builtin_unreachable();
}

/* Original0xDA16..0xDA1C. */
REGION void tsl9_remaining_record_dispatch_block_da16(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_da18:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_da18\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_request_records_entry_fe1c\n");
    __builtin_unreachable();
}

/* Original0xDA1C..0xDA24. */
REGION void tsl9_remaining_record_dispatch_block_da1c(void)
{
    REGS;
    a0 = UINT32_C(0x00000068); LIVE;
    PORT(".Lremaining_record_dispatch_edge_da20:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_da20\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xDA24..0xDA2E. */
REGION void tsl9_remaining_record_dispatch_block_da24(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_da2a:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_da2a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_settings_state_inputs_entry_b254\n");
    __builtin_unreachable();
}

/* Original0xDA2E..0xDA34. */
REGION void tsl9_remaining_record_dispatch_block_da2e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDA34..0xDA36. */
REGION void tsl9_remaining_record_dispatch_block_da34(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDA74..0xDA7E. */
REGION void tsl9_feature_external_da74(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a4 = a5 & UINT32_C(0x00000007); LIVE;
    PORT(".Lremaining_record_dispatch_edge_da7c:\n.option push\n.option rvc\nc.bnez a4,.Lremaining_record_dispatch_edge_da7c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_dac6\n");
    __builtin_unreachable();
}

/* Original0xDA7E..0xDA8C. */
REGION void tsl9_remaining_record_dispatch_block_da7e(void)
{
    REGS;
    a5 = a5 >> UINT32_C(0x00000003); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    a3 = a5 + UINT32_C(0xffffffff); LIVE;
    a4 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_da88:\n.option push\n.option norvc\nbltu a4,a3,.Lremaining_record_dispatch_edge_da88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dac6\n");
    __builtin_unreachable();
}

/* Original0xDA8C..0xDA9E. */
REGION void tsl9_remaining_record_dispatch_block_da8c(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    a5 = (uint32_t)(a5 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000004d6)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_da9a:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_da9a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dac6\n");
    __builtin_unreachable();
}

/* Original0xDA9E..0xDAAE. */
REGION void tsl9_remaining_record_dispatch_block_da9e(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000004c6)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_daaa:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_daaa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xDAAE..0xDAC6. */
REGION void tsl9_remaining_record_dispatch_block_daae(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000004ba)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x000000c4); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dac2:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_dac2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xDAC6..0xDAC8. */
REGION void tsl9_remaining_record_dispatch_block_dac6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDAC8..0xDAEA. */
REGION void tsl9_feature_external_dac8(void)
{
    REGS;
    a2 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a2 = a2 & UINT32_C(0x0000000f); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a1, a1, 1175\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, a0, 1172\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dae6:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dae6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d956\n");
    __builtin_unreachable();
}

/* Original0xDAEA..0xDB04. */
REGION void tsl9_remaining_record_dispatch_block_daea(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a1, a1, 1151\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, a0, 1148\n.option pop\n");
    a2 = a2 >> UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db00:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_db00\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d956\n");
    __builtin_unreachable();
}

/* Original0xDB04..0xDB1E. */
REGION void tsl9_remaining_record_dispatch_block_db04(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x00000075); LIVE;
    a2 = UINT32_C(0x00000074); LIVE;
    a1 = a1 & UINT32_C(0x0000000f); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000104); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db1a:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_db1a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xDB1E..0xDB20. */
REGION void tsl9_remaining_record_dispatch_block_db1e(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_db1e:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_db1e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_db42\n");
    __builtin_unreachable();
}

/* Original0xDB20..0xDB32. */
REGION void tsl9_remaining_record_dispatch_block_db20(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = UINT32_C(0x00000010); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    a5 = a5 & UINT32_C(0x00000018); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db2e:\n.option push\n.option norvc\nbne a5,a4,.Lremaining_record_dispatch_edge_db2e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_db42\n");
    __builtin_unreachable();
}

/* Original0xDB32..0xDB3C. */
REGION void tsl9_remaining_record_dispatch_block_db32(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000104)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db38:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_db38\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dbb8\n");
    __builtin_unreachable();
}

/* Original0xDB3C..0xDB42. */
REGION void tsl9_remaining_record_dispatch_block_db3c(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db3e:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_db3e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dbc0\n");
    __builtin_unreachable();
}

/* Original0xDB42..0xDB5C. */
REGION void tsl9_remaining_record_dispatch_block_db42(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x0000007d); LIVE;
    a2 = UINT32_C(0x0000007c); LIVE;
    a1 = a1 >> UINT32_C(0x00000004); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000105); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db58:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_db58\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xDB5C..0xDB6E. */
REGION void tsl9_remaining_record_dispatch_block_db5c(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 10(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000413)); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db6a:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_db6a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_db76\n");
    __builtin_unreachable();
}

/* Original0xDB6E..0xDB76. */
REGION void tsl9_remaining_record_dispatch_block_db6e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000405)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xDB76..0xDB80. */
REGION void tsl9_remaining_record_dispatch_block_db76(void)
{
    REGS;
    a4 = a5 + UINT32_C(0xffffffff); LIVE;
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db7c:\n.option push\n.option norvc\nbltu a3,a4,.Lremaining_record_dispatch_edge_db7c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dbc4\n");
    __builtin_unreachable();
}

/* Original0xDB80..0xDB92. */
REGION void tsl9_remaining_record_dispatch_block_db80(void)
{
    REGS;
    a5 = a5 + UINT32_C(0xfffffffe); LIVE;
    a5 = (uint32_t)(a5 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000003e3)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_db8e:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_db8e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dbc4\n");
    __builtin_unreachable();
}

/* Original0xDB92..0xDB9E. */
REGION void tsl9_remaining_record_dispatch_block_db92(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x000003d7)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_db9a:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_db9a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xDB9E..0xDBB8. */
REGION void tsl9_remaining_record_dispatch_block_db9e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000003c9)); LIVE;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x000000c6); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dbb4:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_dbb4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xDBB8..0xDBBA. */
REGION void tsl9_remaining_record_dispatch_block_dbb8(void)
{
    REGS;
    a0 = UINT32_C(0x00000005); LIVE;
    __builtin_unreachable();
}

/* Original0xDBBA..0xDBBE. */
REGION void tsl9_remaining_record_dispatch_block_dbba(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_dbba:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dbba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_18232\n");
    __builtin_unreachable();
}

/* Original0xDBBE..0xDBC0. */
REGION void tsl9_remaining_record_dispatch_block_dbbe(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_dbbe:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dbbe\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_db42\n");
    __builtin_unreachable();
}

/* Original0xDBC0..0xDBC4. */
REGION void tsl9_remaining_record_dispatch_block_dbc0(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dbc2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dbc2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dbba\n");
    __builtin_unreachable();
}

/* Original0xDBC4..0xDBCC. */
REGION void tsl9_remaining_record_dispatch_block_dbc4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDBCC..0xDBD8. */
REGION void tsl9_feature_external_dbcc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffe\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 + UINT32_C(0x000003a2)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dbd4:\n.option push\n.option norvc\nbeqz a3,.Lremaining_record_dispatch_edge_dbd4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_de80\n");
    __builtin_unreachable();
}

/* Original0xDBD8..0xDBEE. */
REGION void tsl9_remaining_record_dispatch_block_dbd8(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    a5 = a3 + UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000017); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dbea:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_dbea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dc22\n");
    __builtin_unreachable();
}

/* Original0xDBEE..0xDC00. */
REGION void tsl9_remaining_record_dispatch_block_dbee(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dbee:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_static_data_1a0dc\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dbee\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDC00..0xDC14. */
REGION void tsl9_remaining_record_dispatch_block_dc00(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dc00:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7a4\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dc00\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000367)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dc10:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dc10\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d90e\n");
    __builtin_unreachable();
}

/* Original0xDC14..0xDC1E. */
REGION void tsl9_remaining_record_dispatch_block_dc14(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 3(s0)\n.option pop\n");
    a0 = a0 << UINT32_C(0x00000005); LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a5 = a5 | a0; LIVE;
    __builtin_unreachable();
}

/* Original0xDC1E..0xDC22. */
REGION void tsl9_remaining_record_dispatch_block_dc1e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDC22..0xDC36. */
REGION void tsl9_remaining_record_dispatch_block_dc22(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000346)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dc32:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_dc32\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xDC36..0xDC42. */
REGION void tsl9_remaining_record_dispatch_block_dc36(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dc36:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7a4\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dc36\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dc3e:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dc3e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d8e2\n");
    __builtin_unreachable();
}

/* Original0xDC42..0xDC44. */
REGION void tsl9_remaining_record_dispatch_block_dc42(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_dc42:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dc42\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc14\n");
    __builtin_unreachable();
}

/* Original0xDC44..0xDC50. */
REGION void tsl9_remaining_record_dispatch_block_dc44(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a5 = a5 | UINT32_C(0xffffffc0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dc4e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dc4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc1e\n");
    __builtin_unreachable();
}

/* Original0xDC50..0xDC64. */
REGION void tsl9_remaining_record_dispatch_block_dc50(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dc50:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7b0\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dc50\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000318)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dc60:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dc60\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d90e\n");
    __builtin_unreachable();
}

/* Original0xDC64..0xDC6E. */
REGION void tsl9_remaining_record_dispatch_block_dc64(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000007); LIVE;
    a5 = a5 & UINT32_C(0xfffffff8); LIVE;
    a5 = a5 | a0; LIVE;
    __builtin_unreachable();
}

/* Original0xDC6E..0xDC74. */
REGION void tsl9_remaining_record_dispatch_block_dc6e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dc72:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dc72\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc22\n");
    __builtin_unreachable();
}

/* Original0xDC74..0xDC80. */
REGION void tsl9_remaining_record_dispatch_block_dc74(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dc74:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7b0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dc74\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dc7c:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dc7c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d8e2\n");
    __builtin_unreachable();
}

/* Original0xDC80..0xDC82. */
REGION void tsl9_remaining_record_dispatch_block_dc80(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_dc80:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dc80\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc64\n");
    __builtin_unreachable();
}

/* Original0xDC82..0xDC8E. */
REGION void tsl9_remaining_record_dispatch_block_dc82(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xfffffff8); LIVE;
    a5 = a5 | UINT32_C(0x00000006); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dc8c:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dc8c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc6e\n");
    __builtin_unreachable();
}

/* Original0xDC8E..0xDCA2. */
REGION void tsl9_remaining_record_dispatch_block_dc8e(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dc8e:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7bc\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dc8e\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x000002db)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dc9e:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dc9e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d90e\n");
    __builtin_unreachable();
}

/* Original0xDCA2..0xDCB8. */
REGION void tsl9_remaining_record_dispatch_block_dca2(void)
{
    REGS;
    a0 = a0 & UINT32_C(0x00000007); LIVE;
    a5 = a0 << UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nlbu a0, 4(s0)\n.option pop\n");
    a0 = a0 & UINT32_C(0xffffffc7); LIVE;
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option norvc\nsb a0, 4(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dcb6:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dcb6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc22\n");
    __builtin_unreachable();
}

/* Original0xDCB8..0xDCC4. */
REGION void tsl9_remaining_record_dispatch_block_dcb8(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dcb8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7bc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dcb8\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dcc0:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dcc0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d8e2\n");
    __builtin_unreachable();
}

/* Original0xDCC4..0xDCC6. */
REGION void tsl9_remaining_record_dispatch_block_dcc4(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_dcc4:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dcc4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dca2\n");
    __builtin_unreachable();
}

/* Original0xDCC6..0xDCD4. */
REGION void tsl9_remaining_record_dispatch_block_dcc6(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xffffffc7); LIVE;
    a5 = a5 | UINT32_C(0x00000030); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dcd2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dcd2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc6e\n");
    __builtin_unreachable();
}

/* Original0xDCD4..0xDCE8. */
REGION void tsl9_remaining_record_dispatch_block_dcd4(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dcd4:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7c8\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dcd4\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000296)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dce4:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dce4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d90e\n");
    __builtin_unreachable();
}

/* Original0xDCE8..0xDD10. */
REGION void tsl9_remaining_record_dispatch_block_dce8(void)
{
    REGS;
    a5 = a0 & UINT32_C(0x00000003); LIVE;
    a4 = a5 << UINT32_C(0x00000006); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 4(s0)\n.option pop\n");
    a0 = a0 >> UINT32_C(0x00000002); LIVE;
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    a0 = a0 | a5; LIVE;
    PORT(".option push\n.option norvc\nsb a0, 5(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dd0e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dd0e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc22\n");
    __builtin_unreachable();
}

/* Original0xDD10..0xDD1C. */
REGION void tsl9_remaining_record_dispatch_block_dd10(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_dd10:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_input_state_decoders_entry_d7c8\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_dd10\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dd18:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dd18\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d8e2\n");
    __builtin_unreachable();
}

/* Original0xDD1C..0xDD1E. */
REGION void tsl9_remaining_record_dispatch_block_dd1c(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_dd1c:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dd1c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dce8\n");
    __builtin_unreachable();
}

/* Original0xDD1E..0xDD2A. */
REGION void tsl9_remaining_record_dispatch_block_dd1e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x0000003f); LIVE;
    a5 = a5 | UINT32_C(0xffffff80); LIVE;
    __builtin_unreachable();
}

/* Original0xDD2A..0xDD38. */
REGION void tsl9_remaining_record_dispatch_block_dd2a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dd36:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dd36\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd86\n");
    __builtin_unreachable();
}

/* Original0xDD38..0xDD48. */
REGION void tsl9_remaining_record_dispatch_block_dd38(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x0000023b)); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dd44:\n.option push\n.option norvc\nbeq a4,a3,.Lremaining_record_dispatch_edge_dd44\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_dd5a\n");
    __builtin_unreachable();
}

/* Original0xDD48..0xDD4C. */
REGION void tsl9_remaining_record_dispatch_block_dd48(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dd4a:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_dd4a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_dd5a\n");
    __builtin_unreachable();
}

/* Original0xDD4C..0xDD5A. */
REGION void tsl9_remaining_record_dispatch_block_dd4c(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xfffffffd); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a3, a5\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0xDD5A..0xDD62. */
REGION void tsl9_remaining_record_dispatch_block_dd5a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 5(s0)\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000001); LIVE;
    a4 = a4 & UINT32_C(0xfffffff1); LIVE;
    __builtin_unreachable();
}

/* Original0xDD62..0xDD66. */
REGION void tsl9_remaining_record_dispatch_block_dd62(void)
{
    REGS;
    a5 = a5 | a4; LIVE;
    PORT(".Lremaining_record_dispatch_edge_dd64:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dd64\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd86\n");
    __builtin_unreachable();
}

/* Original0xDD66..0xDD86. */
REGION void tsl9_remaining_record_dispatch_block_dd66(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a5 = a5 | UINT32_C(0xffffffc0); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0xffffffb6); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 & UINT32_C(0xfffffff0); LIVE;
    a5 = a5 | UINT32_C(0x0000000d); LIVE;
    __builtin_unreachable();
}

/* Original0xDD86..0xDD8C. */
REGION void tsl9_remaining_record_dispatch_block_dd86(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_dd8a:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dd8a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc22\n");
    __builtin_unreachable();
}

/* Original0xDD8C..0xDD9E. */
REGION void tsl9_remaining_record_dispatch_block_dd8c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a5 = a5 | UINT32_C(0x00000060); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0xffffffdb); LIVE;
    __builtin_unreachable();
}

/* Original0xDD9E..0xDDAA. */
REGION void tsl9_remaining_record_dispatch_block_dd9e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dda8:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_dda8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd86\n");
    __builtin_unreachable();
}

/* Original0xDDAA..0xDDCC. */
REGION void tsl9_remaining_record_dispatch_block_ddaa(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0xffffff92); LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 & UINT32_C(0xfffffff0); LIVE;
    a5 = a5 | UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ddca:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_ddca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd86\n");
    __builtin_unreachable();
}

/* Original0xDDCC..0xDDDE. */
REGION void tsl9_remaining_record_dispatch_block_ddcc(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000165)); LIVE;
    a4 = a4 + UINT32_C(0xfffffff9); LIVE;
    a4 = a4 & UINT32_C(0x000000ff); LIVE;
    a2 = UINT32_C(0x00000001); LIVE;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ddda:\n.option push\n.option norvc\nbltu a2,a4,.Lremaining_record_dispatch_edge_ddda\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ddfa\n");
    __builtin_unreachable();
}

/* Original0xDDDE..0xDDEA. */
REGION void tsl9_remaining_record_dispatch_block_ddde(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000193)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dde6:\n.option push\n.option norvc\nbeq a4,a2,.Lremaining_record_dispatch_edge_dde6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_de32\n");
    __builtin_unreachable();
}

/* Original0xDDEA..0xDDEC. */
REGION void tsl9_remaining_record_dispatch_block_ddea(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ddea:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_ddea\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_ddfa\n");
    __builtin_unreachable();
}

/* Original0xDDEC..0xDDFA. */
REGION void tsl9_remaining_record_dispatch_block_ddec(void)
{
    REGS;
    a5 = a4 + UINT32_C(0xfffffffd); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option norvc\nsltu a5, a2, a5\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0xDDFA..0xDE04. */
REGION void tsl9_remaining_record_dispatch_block_ddfa(void)
{
    REGS;
    a2 = UINT32_C(0x00000010); LIVE;
    a4 = a5 & UINT32_C(0x00000007); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de00:\n.option push\n.option norvc\nbne a3,a2,.Lremaining_record_dispatch_edge_de00\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_de10\n");
    __builtin_unreachable();
}

/* Original0xDE04..0xDE10. */
REGION void tsl9_remaining_record_dispatch_block_de04(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a3, 4(s0)\n.option pop\n");
    a3 = a3 & UINT32_C(0xfffffff8); LIVE;
    a3 = a3 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a3, 4(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDE10..0xDE32. */
REGION void tsl9_remaining_record_dispatch_block_de10(void)
{
    REGS;
    a3 = a4 << UINT32_C(0x00000003); LIVE;
    PORT(".option push\n.option norvc\nlbu a4, 4(s0)\n.option pop\n");
    a2 = a5 & UINT32_C(0x00000003); LIVE;
    a2 = a2 << UINT32_C(0x00000006); LIVE;
    a4 = a4 & UINT32_C(0x00000007); LIVE;
    a4 = a4 | a3; LIVE;
    a4 = a4 | a2; LIVE;
    PORT(".option push\n.option norvc\nsb a4, 4(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 5(s0)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x00000002); LIVE;
    a4 = a4 & UINT32_C(0xfffffffe); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de30:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de30\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd62\n");
    __builtin_unreachable();
}

/* Original0xDE32..0xDE36. */
REGION void tsl9_remaining_record_dispatch_block_de32(void)
{
    REGS;
    a5 = UINT32_C(0x00000006); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de34:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de34\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ddfa\n");
    __builtin_unreachable();
}

/* Original0xDE36..0xDE44. */
REGION void tsl9_remaining_record_dispatch_block_de36(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xffffffc7); LIVE;
    a5 = a5 | UINT32_C(0xffffffd8); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de42:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de42\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd9e\n");
    __builtin_unreachable();
}

/* Original0xDE44..0xDE50. */
REGION void tsl9_remaining_record_dispatch_block_de44(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0x00000007); LIVE;
    a5 = a5 | UINT32_C(0xffffffb0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de4e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de4e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd2a\n");
    __builtin_unreachable();
}

/* Original0xDE50..0xDE5C. */
REGION void tsl9_remaining_record_dispatch_block_de50(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    a5 = a5 & UINT32_C(0x0000001f); LIVE;
    a5 = a5 | UINT32_C(0x00000060); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de5a:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de5a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc1e\n");
    __builtin_unreachable();
}

/* Original0xDE5C..0xDE68. */
REGION void tsl9_remaining_record_dispatch_block_de5c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xfffffff8); LIVE;
    a5 = a5 | UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de66:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de66\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc6e\n");
    __builtin_unreachable();
}

/* Original0xDE68..0xDE76. */
REGION void tsl9_remaining_record_dispatch_block_de68(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xffffffc7); LIVE;
    a5 = a5 | UINT32_C(0x00000018); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de74:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de74\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dc6e\n");
    __builtin_unreachable();
}

/* Original0xDE76..0xDE80. */
REGION void tsl9_remaining_record_dispatch_block_de76(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 | UINT32_C(0xffffffc0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_de7e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_de7e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_dd9e\n");
    __builtin_unreachable();
}

/* Original0xDE80..0xDE82. */
REGION void tsl9_remaining_record_dispatch_block_de80(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xDEEC..0xDEF2. */
REGION void tsl9_record_dispatch_provider_deec(void)
{
    REGS;
    a0 = UINT32_C(0x00000019); LIVE;
    PORT(".Lremaining_record_dispatch_edge_deee:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_deee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0xDEF2..0xDF1A. */
REGION void tsl9_feature_external_def2(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\naddi s2, gp, 352\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a5, 5(s2)\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000003)); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    a4 = a4 & UINT32_C(0x0000000f); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_df16:\n.option push\n.option norvc\nbltu a3,a5,.Lremaining_record_dispatch_edge_df16\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_e016\n");
    __builtin_unreachable();
}

/* Original0xDF1A..0xDF1E. */
REGION void tsl9_remaining_record_dispatch_block_df1a(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_df1a:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_df1a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_df26\n");
    __builtin_unreachable();
}

/* Original0xDF1E..0xDF26. */
REGION void tsl9_remaining_record_dispatch_block_df1e(void)
{
    REGS;
    a1 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a1 = a1 >> UINT32_C(0x00000004); LIVE;
    a1 = a1 & UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xDF26..0xDF48. */
REGION void tsl9_remaining_record_dispatch_block_df26(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s1, gp, 84\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a3, a3, 76\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, a2, 64\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a0 = a0 >> UINT32_C(0x00000002); LIVE;
    a0 = a0 & UINT32_C(0x00000007); LIVE;
    PORT(".Lremaining_record_dispatch_edge_df44:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_df44\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d868\n");
    __builtin_unreachable();
}

/* Original0xDF48..0xDF4A. */
REGION void tsl9_remaining_record_dispatch_block_df48(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_df48:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_df48\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_df4e\n");
    __builtin_unreachable();
}

/* Original0xDF4A..0xDF4E. */
REGION void tsl9_remaining_record_dispatch_block_df4a(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_df4a:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_df4a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_deec\n");
    __builtin_unreachable();
}

/* Original0xDF4E..0xDF66. */
REGION void tsl9_remaining_record_dispatch_block_df4e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 5(s2)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu a4, 3(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    a5 = a5 + UINT32_C(0xfffffff9); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = a4 & UINT32_C(0x000000f0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_df62:\n.option push\n.option norvc\nbltu a3,a5,.Lremaining_record_dispatch_edge_df62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_e028\n");
    __builtin_unreachable();
}

/* Original0xDF66..0xDF6E. */
REGION void tsl9_remaining_record_dispatch_block_df66(void)
{
    REGS;
    a5 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_df6a:\n.option push\n.option norvc\nbne a4,a5,.Lremaining_record_dispatch_edge_df6a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_df76\n");
    __builtin_unreachable();
}

/* Original0xDF6E..0xDF74. */
REGION void tsl9_remaining_record_dispatch_block_df6e(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a1, 4(s0)\n.option pop\n");
    a1 = a1 >> UINT32_C(0x00000005); LIVE;
    __builtin_unreachable();
}

/* Original0xDF74..0xDF76. */
REGION void tsl9_remaining_record_dispatch_block_df74(void)
{
    REGS;
    a1 = a1 & UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xDF76..0xDF92. */
REGION void tsl9_remaining_record_dispatch_block_df76(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a3, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a3, a3, 4\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a2, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a2, a2, -11\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a0 = a0 >> UINT32_C(0x00000005); LIVE;
    PORT(".Lremaining_record_dispatch_edge_df8e:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_df8e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d868\n");
    __builtin_unreachable();
}

/* Original0xDF92..0xDF94. */
REGION void tsl9_remaining_record_dispatch_block_df92(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_df92:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_df92\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_dfa4\n");
    __builtin_unreachable();
}

/* Original0xDF94..0xDF98. */
REGION void tsl9_remaining_record_dispatch_block_df94(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_df94:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_df94\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_d3e8\n");
    __builtin_unreachable();
}

/* Original0xDF98..0xDFA4. */
REGION void tsl9_remaining_record_dispatch_block_df98(void)
{
    REGS;
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dfa0:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dfa0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d3c6\n");
    __builtin_unreachable();
}

/* Original0xDFA4..0xDFBE. */
REGION void tsl9_remaining_record_dispatch_block_dfa4(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a1, a1, -62\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, a0, -65\n.option pop\n");
    a2 = a2 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dfba:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dfba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d956\n");
    __builtin_unreachable();
}

/* Original0xDFBE..0xDFD8. */
REGION void tsl9_remaining_record_dispatch_block_dfbe(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a2, 3(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a1, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a1, a1, -86\n.option pop\n");
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    PORT(".option push\n.option norvc\naddi a0, a0, -89\n.option pop\n");
    a2 = a2 >> UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dfd4:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dfd4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_entry_d956\n");
    __builtin_unreachable();
}

/* Original0xDFD8..0xDFF2. */
REGION void tsl9_remaining_record_dispatch_block_dfd8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 3(s0)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x00000073); LIVE;
    a2 = UINT32_C(0x00000072); LIVE;
    a1 = a1 & UINT32_C(0x0000000f); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000102); LIVE;
    PORT(".Lremaining_record_dispatch_edge_dfee:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_dfee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xDFF2..0xE016. */
REGION void tsl9_remaining_record_dispatch_block_dff2(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a1, 3(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000002); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x0000007b); LIVE;
    a2 = UINT32_C(0x0000007a); LIVE;
    a1 = a1 >> UINT32_C(0x00000004); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = original_gp + UINT32_C(0x00000103); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_e012:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_e012\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_input_state_decoders_provider_eca8\n");
    __builtin_unreachable();
}

/* Original0xE016..0xE01A. */
REGION void tsl9_remaining_record_dispatch_block_e016(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_e016:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_e016\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_df26\n");
    __builtin_unreachable();
}

/* Original0xE01A..0xE028. */
REGION void tsl9_remaining_record_dispatch_block_e01a(void)
{
    REGS;
    a1 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a1 = a1 & UINT32_C(0x00000104); LIVE;
    a1 = (uint32_t)(a1 != UINT32_C(0)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_e026:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_e026\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_df26\n");
    __builtin_unreachable();
}

/* Original0xE028..0xE030. */
REGION void tsl9_remaining_record_dispatch_block_e028(void)
{
    REGS;
    a5 = UINT32_C(0x00000010); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_e02c:\n.option push\n.option norvc\nbne a4,a5,.Lremaining_record_dispatch_edge_e02c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_df76\n");
    __builtin_unreachable();
}

/* Original0xE030..0xE038. */
REGION void tsl9_remaining_record_dispatch_block_e030(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlhu a1, 4(s0)\n.option pop\n");
    a1 = a1 >> UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_e036:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_e036\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_df74\n");
    __builtin_unreachable();
}

/* Original0xE042..0xE048. */
REGION void tsl9_record_dispatch_provider_e042(void)
{
    REGS;
    a0 = UINT32_C(0x00000018); LIVE;
    PORT(".Lremaining_record_dispatch_edge_e044:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_e044\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_dea0\n");
    __builtin_unreachable();
}

/* Original0xE048..0xE058. */
REGION void tsl9_record_dispatch_provider_e048(void)
{
    REGS;
    a5 = UINT32_C(0x0000001a); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffe\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xffffff36)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_e054:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_e054\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_d810\n");
    __builtin_unreachable();
}

/* Original0xF0C6..0xF0D0. */
REGION void tsl9_record_dispatch_provider_f0c6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffed0)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF630..0xF63C. */
REGION void tsl9_record_dispatch_provider_f630(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff964)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF63C..0xF65C. */
REGION void tsl9_record_dispatch_provider_f63c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a2 = UINT32_C(0x00002000); LIVE;
    PORT(".option push\n.option norvc\nauipc a4, 0x1fffd\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0xfffff956)) = (uint8_t)a5; LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = a2 + UINT32_C(0x00000710); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_literal_f650:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_f0c6\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_f650\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_f658:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_f658\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xF7DC..0xF7EC. */
REGION void tsl9_record_dispatch_provider_f7dc(void)
{
    REGS;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffc\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x000007b0)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF7EC..0xF800. */
REGION void tsl9_record_dispatch_provider_f7ec(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0xfffff9d5)); LIVE;
    a0 = a0 & UINT32_C(0x00000070); LIVE;
    a0 = a0 + UINT32_C(0xffffffe0); LIVE;
    a0 = (uint32_t)(a0 == UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF800..0xF80A. */
REGION void tsl9_record_dispatch_provider_f800(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a5, 0x1fffc\n.option pop\n");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000794)) = (uint8_t)a0; LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF80A..0xF818. */
REGION void tsl9_record_dispatch_provider_f80a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nauipc a0, 0x1fffc\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x0000078a)); LIVE;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF860..0xF87A. */
REGION void tsl9_feature_external_f860(void)
{
    REGS;
    a5 = *(volatile uint16_t *)(uintptr_t)(a0 + UINT32_C(0x00000002)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    a5 = a5 >> UINT32_C(0x0000000d); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 20(sp)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000114)); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_f876:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_f876\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_f88c\n");
    __builtin_unreachable();
}

/* Original0xF87A..0xF888. */
REGION void tsl9_remaining_record_dispatch_block_f87a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000114)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000115)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_f884:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_f884\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xF888..0xF88C. */
REGION void tsl9_remaining_record_dispatch_block_f888(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_f888:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_f888\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_external_13c4e\n");
    __builtin_unreachable();
}

/* Original0xF88C..0xF89A. */
REGION void tsl9_remaining_record_dispatch_block_f88c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000115)); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000114)); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f896:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_f896\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_f8ae\n");
    __builtin_unreachable();
}

/* Original0xF89A..0xF8AE. */
REGION void tsl9_remaining_record_dispatch_block_f89a(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 3(s0)\n.option pop\n");
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    a5 = a5 << UINT32_C(0x00000005); LIVE;
    a4 = a4 & UINT32_C(0xffffffdf); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 3(s0)\n.option pop\n");
    a3 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xF8AE..0xF8BE. */
REGION void tsl9_remaining_record_dispatch_block_f8ae(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a2 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0x000000e0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f8bc:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_f8bc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f8e2\n");
    __builtin_unreachable();
}

/* Original0xF8BE..0xF8E2. */
REGION void tsl9_remaining_record_dispatch_block_f8be(void)
{
    REGS;
    a4 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option norvc\nlbu a5, 5(s0)\n.option pop\n");
    a3 = a4 >> UINT32_C(0x00000005); LIVE;
    PORT(".Lremaining_record_dispatch_literal_f8ca:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_static_data_1ab50\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_f8ca\n.option pop\n");
    a4 = a4 + a3; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0xffffffe0); LIVE;
    a3 = UINT32_C(0x00000001); LIVE;
    a5 = a5 | a4; LIVE;
    PORT(".option push\n.option norvc\nsb a5, 5(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF8E2..0xF8E8. */
REGION void tsl9_remaining_record_dispatch_block_f8e2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000116)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f8e6:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_f8e6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f94c\n");
    __builtin_unreachable();
}

/* Original0xF8E8..0xF8F0. */
REGION void tsl9_remaining_record_dispatch_block_f8e8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0xF8F0..0xF8F6. */
REGION void tsl9_remaining_record_dispatch_block_f8f0(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb a5, 6(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a3, a4\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF8F6..0xF90A. */
REGION void tsl9_remaining_record_dispatch_block_f8f6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a4, 6(s0)\n.option pop\n");
    a5 = UINT32_C(0x00408000); LIVE;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a5; LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000118)); LIVE;
    a1 = a4 & UINT32_C(0x000000c0); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f908:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_f908\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f95c\n");
    __builtin_unreachable();
}

/* Original0xF90A..0xF916. */
REGION void tsl9_remaining_record_dispatch_block_f90a(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi a2, sp, 16\n.option pop\n");
    a5 = a5 + a2; LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffffc)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f912:\n.option push\n.option norvc\nbeq a5,a1,.Lremaining_record_dispatch_edge_f912\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_f970\n");
    __builtin_unreachable();
}

/* Original0xF916..0xF920. */
REGION void tsl9_remaining_record_dispatch_block_f916(void)
{
    REGS;
    a4 = a4 & UINT32_C(0x0000003f); LIVE;
    a4 = a4 | a5; LIVE;
    PORT(".option push\n.option norvc\nsb a4, 6(s0)\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF920..0xF938. */
REGION void tsl9_remaining_record_dispatch_block_f920(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 9(s0)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s1, 2(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000010); LIVE;
    PORT(".option push\n.option norvc\nsb a5, 9(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    a1 = UINT32_C(0x00000007); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f934:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_f934\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_checksum_ed00\n");
    __builtin_unreachable();
}

/* Original0xF938..0xF94C. */
REGION void tsl9_remaining_record_dispatch_block_f938(void)
{
    REGS;
    PORT(".option push\n.option rvc\nadd s1, s1, s0\n.option pop\n");
    PORT(".option push\n.option norvc\nsb a0, 3(s1)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_f948:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_f948\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xF94C..0xF952. */
REGION void tsl9_remaining_record_dispatch_block_f94c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000117)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f950:\n.option push\n.option rvc\nc.beqz a4,.Lremaining_record_dispatch_edge_f950\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f8f6\n");
    __builtin_unreachable();
}

/* Original0xF952..0xF95C. */
REGION void tsl9_remaining_record_dispatch_block_f952(void)
{
    REGS;
    PORT(".option push\n.option norvc\nlbu a5, 6(s0)\n.option pop\n");
    a5 = a5 | UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f95a:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_f95a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_f8f0\n");
    __builtin_unreachable();
}

/* Original0xF95C..0xF966. */
REGION void tsl9_remaining_record_dispatch_block_f95c(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000001)); LIVE;
    a5 = a5 & UINT32_C(0x00000060); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f964:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_f964\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f970\n");
    __builtin_unreachable();
}

/* Original0xF966..0xF970. */
REGION void tsl9_remaining_record_dispatch_block_f966(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a2 + UINT32_C(0x00000001)); LIVE;
    a5 = a5 >> UINT32_C(0x00000005); LIVE;
    a5 = a5 & UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f96e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_f96e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_f90a\n");
    __builtin_unreachable();
}

/* Original0xF970..0xF972. */
REGION void tsl9_remaining_record_dispatch_block_f970(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_f970:\n.option push\n.option rvc\nc.bnez a3,.Lremaining_record_dispatch_edge_f970\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f920\n");
    __builtin_unreachable();
}

/* Original0xF972..0xF97C. */
REGION void tsl9_remaining_record_dispatch_block_f972(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 20(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF998..0xF99E. */
REGION void tsl9_record_dispatch_provider_f998(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f99a:\n.option push\n.option norvc\nbltu a5,a0,.Lremaining_record_dispatch_edge_f99a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_f9a2\n");
    __builtin_unreachable();
}

/* Original0xF99E..0xF9A2. */
REGION void tsl9_remaining_record_dispatch_block_f99e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000118)) = (uint8_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0xF9A2..0xF9A4. */
REGION void tsl9_remaining_record_dispatch_block_f9a2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xF9A4..0xF9B2. */
REGION void tsl9_remaining_record_dispatch_block_f9a4(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -32\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 28(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)) = (uint32_t)a1; LIVE;
    PORT(".Lremaining_record_dispatch_edge_f9ae:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_f9ae\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xF9B2..0xF9B8. */
REGION void tsl9_remaining_record_dispatch_block_f9b2(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f9b4:\n.option push\n.option norvc\nbne a0,a5,.Lremaining_record_dispatch_edge_f9b4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_f9e4\n");
    __builtin_unreachable();
}

/* Original0xF9B8..0xF9BC. */
REGION void tsl9_remaining_record_dispatch_block_f9b8(void)
{
    REGS;
    register uintptr_t original_sp __asm__("sp");
    __asm__ volatile("":"=r"(original_sp)::"memory");
    a1 = *(volatile uint32_t *)(uintptr_t)(original_sp + UINT32_C(0x0000000c)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f9ba:\n.option push\n.option rvc\nc.beqz a1,.Lremaining_record_dispatch_edge_f9ba\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f9d8\n");
    __builtin_unreachable();
}

/* Original0xF9BC..0xF9C2. */
REGION void tsl9_remaining_record_dispatch_block_f9bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 278(gp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_f9c0:\n.option push\n.option rvc\nc.beqz s0,.Lremaining_record_dispatch_edge_f9c0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f9c6\n");
    __builtin_unreachable();
}

/* Original0xF9C2..0xF9C6. */
REGION void tsl9_remaining_record_dispatch_block_f9c2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000117)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xF9C6..0xF9CC. */
REGION void tsl9_remaining_record_dispatch_block_f9c6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_f9c8:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_f9c8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xF9CC..0xF9D8. */
REGION void tsl9_remaining_record_dispatch_block_f9cc(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 24(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 28(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 32\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_f9d4:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_f9d4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_provider_entry_13d48\n");
    __builtin_unreachable();
}

/* Original0xF9D8..0xF9DE. */
REGION void tsl9_remaining_record_dispatch_block_f9d8(void)
{
    REGS;
    PORT(".option push\n.option norvc\nsb s0, 279(gp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_f9dc:\n.option push\n.option rvc\nc.beqz s0,.Lremaining_record_dispatch_edge_f9dc\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_f9c6\n");
    __builtin_unreachable();
}

/* Original0xF9DE..0xF9E4. */
REGION void tsl9_remaining_record_dispatch_block_f9de(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000116)) = (uint8_t)0; LIVE;
    PORT(".Lremaining_record_dispatch_edge_f9e2:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_f9e2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_f9c6\n");
    __builtin_unreachable();
}

/* Original0xF9E4..0xF9EA. */
REGION void tsl9_remaining_record_dispatch_block_f9e4(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_f9e6:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_f9e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_9508\n");
    __builtin_unreachable();
}

/* Original0xF9EA..0xF9EC. */
REGION void tsl9_remaining_record_dispatch_block_f9ea(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_f9ea:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_f9ea\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_f9cc\n");
    __builtin_unreachable();
}

/* Original0xFA24..0xFA2A. */
REGION void tsl9_record_dispatch_provider_fa24(void)
{
    REGS;
    a1 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fa26:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_fa26\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_block_f9a4\n");
    __builtin_unreachable();
}

/* Original0xFA30..0xFA36. */
REGION void tsl9_record_dispatch_provider_fa30(void)
{
    REGS;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fa32:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_fa32\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_remaining_record_dispatch_block_f9a4\n");
    __builtin_unreachable();
}

/* Original0xFA62..0xFA72. */
REGION void tsl9_feature_external_fa62(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000119)); LIVE;
    a5 = a5 >> UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x00000007); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fa6e:\n.option push\n.option norvc\nbeq a4,a5,.Lremaining_record_dispatch_edge_fa6e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_fa7a\n");
    __builtin_unreachable();
}

/* Original0xFA72..0xFA7A. */
REGION void tsl9_remaining_record_dispatch_block_fa72(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000119)) = (uint8_t)a5; LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fa78:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_fa78\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_record_dispatch_provider_fd6a\n");
    __builtin_unreachable();
}

/* Original0xFA7A..0xFA7C. */
REGION void tsl9_remaining_record_dispatch_block_fa7a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFA7C..0xFA86. */
REGION void tsl9_feature_external_fa7c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011c)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fa82:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_fa82\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_fac4\n");
    __builtin_unreachable();
}

/* Original0xFA86..0xFA8C. */
REGION void tsl9_remaining_record_dispatch_block_fa86(void)
{
    REGS;
    a4 = UINT32_C(0x00000002); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fa88:\n.option push\n.option norvc\nbeq a5,a4,.Lremaining_record_dispatch_edge_fa88\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_fad6\n");
    __builtin_unreachable();
}

/* Original0xFA8C..0xFA8E. */
REGION void tsl9_remaining_record_dispatch_block_fa8c(void)
{
    REGS;
    a4 = UINT32_C(0x00000000); LIVE;
    __builtin_unreachable();
}

/* Original0xFA8E..0xFA9C. */
REGION void tsl9_remaining_record_dispatch_block_fa8e(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011d)); LIVE;
    a5 = a5 & UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fa98:\n.option push\n.option norvc\nbeq a3,a5,.Lremaining_record_dispatch_edge_fa98\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_faa4\n");
    __builtin_unreachable();
}

/* Original0xFA9C..0xFAA4. */
REGION void tsl9_remaining_record_dispatch_block_fa9c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011d)) = (uint8_t)a5; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011e)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xFAA4..0xFAB0. */
REGION void tsl9_remaining_record_dispatch_block_faa4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011e)); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a3 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011d)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_faac:\n.option push\n.option norvc\nbeq a3,a5,.Lremaining_record_dispatch_edge_faac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_fae2\n");
    __builtin_unreachable();
}

/* Original0xFAB0..0xFAC0. */
REGION void tsl9_remaining_record_dispatch_block_fab0(void)
{
    REGS;
    a4 = a5 & UINT32_C(0x00000001); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xfffffffe); LIVE;
    a5 = a5 | a4; LIVE;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xFAC0..0xFAC4. */
REGION void tsl9_remaining_record_dispatch_block_fac0(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_fac0:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_fac0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xFAC4..0xFACE. */
REGION void tsl9_remaining_record_dispatch_block_fac4(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xfffffff1); LIVE;
    a5 = a5 | UINT32_C(0x00000002); LIVE;
    __builtin_unreachable();
}

/* Original0xFACE..0xFAD6. */
REGION void tsl9_remaining_record_dispatch_block_face(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fad4:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_fad4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_fa8e\n");
    __builtin_unreachable();
}

/* Original0xFAD6..0xFAE2. */
REGION void tsl9_remaining_record_dispatch_block_fad6(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a5 = a5 & UINT32_C(0xfffffff1); LIVE;
    a5 = a5 | UINT32_C(0x00000006); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fae0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_fae0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_face\n");
    __builtin_unreachable();
}

/* Original0xFAE2..0xFAE4. */
REGION void tsl9_remaining_record_dispatch_block_fae2(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_fae2:\n.option push\n.option rvc\nc.bnez a4,.Lremaining_record_dispatch_edge_fae2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_fac0\n");
    __builtin_unreachable();
}

/* Original0xFAE4..0xFAE6. */
REGION void tsl9_remaining_record_dispatch_block_fae4(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFAE6..0xFAF2. */
REGION void tsl9_record_dispatch_provider_fae6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011e)) = (uint8_t)a0; LIVE;
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_faee:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_faee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_external_9792\n");
    __builtin_unreachable();
}

/* Original0xFAF2..0xFAF8. */
REGION void tsl9_record_dispatch_provider_faf2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000011e)); LIVE;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFF56..0xFF5C. */
REGION void tsl9_feature_external_ff56(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ff5a:\n.option push\n.option rvc\nc.bnez a4,.Lremaining_record_dispatch_edge_ff5a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_ffa2\n");
    __builtin_unreachable();
}

/* Original0xFF5C..0xFF66. */
REGION void tsl9_remaining_record_dispatch_block_ff5c(void)
{
    REGS;
    a3 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    a4 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ff62:\n.option push\n.option norvc\nbltu a4,a3,.Lremaining_record_dispatch_edge_ff62\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ffa2\n");
    __builtin_unreachable();
}

/* Original0xFF66..0xFF76. */
REGION void tsl9_remaining_record_dispatch_block_ff66(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option norvc\nlbu s0, 3(a0)\n.option pop\n");
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_ff72:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ff72\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_checksum_ed00\n");
    __builtin_unreachable();
}

/* Original0xFF76..0xFF7A. */
REGION void tsl9_remaining_record_dispatch_block_ff76(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ff76:\n.option push\n.option norvc\nbne s0,a0,.Lremaining_record_dispatch_edge_ff76\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ff8e\n");
    __builtin_unreachable();
}

/* Original0xFF7A..0xFF8A. */
REGION void tsl9_remaining_record_dispatch_block_ff7a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012e)); LIVE;
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ff86:\n.option push\n.option norvc\nbltu a4,a5,.Lremaining_record_dispatch_edge_ff86\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ff96\n");
    __builtin_unreachable();
}

/* Original0xFF8A..0xFF8E. */
REGION void tsl9_remaining_record_dispatch_block_ff8a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012e)) = (uint8_t)a5; LIVE;
    __builtin_unreachable();
}

/* Original0xFF8E..0xFF96. */
REGION void tsl9_remaining_record_dispatch_block_ff8e(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFF96..0xFFA2. */
REGION void tsl9_remaining_record_dispatch_block_ff96(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012e)) = (uint8_t)0; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)) = (uint8_t)a5; LIVE;
    PORT(".Lremaining_record_dispatch_edge_ffa0:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_ffa0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ff8e\n");
    __builtin_unreachable();
}

/* Original0xFFA2..0xFFA4. */
REGION void tsl9_remaining_record_dispatch_block_ffa2(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xFFA4..0xFFAA. */
REGION void tsl9_feature_external_ffa4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012d)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ffa8:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_ffa8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_10020\n");
    __builtin_unreachable();
}

/* Original0xFFAA..0xFFB0. */
REGION void tsl9_remaining_record_dispatch_block_ffaa(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ffae:\n.option push\n.option rvc\nc.beqz a5,.Lremaining_record_dispatch_edge_ffae\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_10020\n");
    __builtin_unreachable();
}

/* Original0xFFB0..0xFFC8. */
REGION void tsl9_remaining_record_dispatch_block_ffb0(void)
{
    REGS;
    a5 = *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a4 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012c)); LIVE;
    a3 = UINT32_C(0x00000002); LIVE;
    a5 = a5 & UINT32_C(0x0000000f); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ffc4:\n.option push\n.option norvc\nbeq a4,a3,.Lremaining_record_dispatch_edge_ffc4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_10014\n");
    __builtin_unreachable();
}

/* Original0xFFC8..0xFFCC. */
REGION void tsl9_remaining_record_dispatch_block_ffc8(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_ffc8:\n.option push\n.option norvc\nbltu a3,a4,.Lremaining_record_dispatch_edge_ffc8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_fffc\n");
    __builtin_unreachable();
}

/* Original0xFFCC..0xFFD2. */
REGION void tsl9_remaining_record_dispatch_block_ffcc(void)
{
    REGS;
    a3 = UINT32_C(0x00000001); LIVE;
    PORT(".Lremaining_record_dispatch_edge_ffce:\n.option push\n.option norvc\nbeq a4,a3,.Lremaining_record_dispatch_edge_ffce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_1000e\n");
    __builtin_unreachable();
}

/* Original0xFFD2..0xFFDE. */
REGION void tsl9_remaining_record_dispatch_block_ffd2(void)
{
    REGS;
    *(volatile uint8_t *)(uintptr_t)(a0 + UINT32_C(0x00000004)) = (uint8_t)a5; LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_ffda:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_ffda\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_checksum_ed00\n");
    __builtin_unreachable();
}

/* Original0xFFDE..0xFFFC. */
REGION void tsl9_remaining_record_dispatch_block_ffde(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x0000012c); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000001)); LIVE;
    PORT(".option push\n.option norvc\nsb a0, 3(s0)\n.option pop\n");
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000012d)) = (uint8_t)a5; LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_fff8:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_fff8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_queue_external_12a08\n");
    __builtin_unreachable();
}

/* Original0xFFFC..0x10002. */
REGION void tsl9_remaining_record_dispatch_block_fffc(void)
{
    REGS;
    a3 = UINT32_C(0x00000003); LIVE;
    PORT(".Lremaining_record_dispatch_edge_fffe:\n.option push\n.option norvc\nbeq a4,a3,.Lremaining_record_dispatch_edge_fffe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_1001a\n");
    __builtin_unreachable();
}

/* Original0x10002..0x10008. */
REGION void tsl9_remaining_record_dispatch_block_10002(void)
{
    REGS;
    a3 = UINT32_C(0x00000004); LIVE;
    PORT(".Lremaining_record_dispatch_edge_10004:\n.option push\n.option norvc\nbne a4,a3,.Lremaining_record_dispatch_edge_10004\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_ffd2\n");
    __builtin_unreachable();
}

/* Original0x10008..0x1000E. */
REGION void tsl9_remaining_record_dispatch_block_10008(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000040); LIVE;
    PORT(".Lremaining_record_dispatch_edge_1000c:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_1000c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ffd2\n");
    __builtin_unreachable();
}

/* Original0x1000E..0x10014. */
REGION void tsl9_remaining_record_dispatch_block_1000e(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000010); LIVE;
    PORT(".Lremaining_record_dispatch_edge_10012:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_10012\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ffd2\n");
    __builtin_unreachable();
}

/* Original0x10014..0x1001A. */
REGION void tsl9_remaining_record_dispatch_block_10014(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000020); LIVE;
    PORT(".Lremaining_record_dispatch_edge_10018:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_10018\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ffd2\n");
    __builtin_unreachable();
}

/* Original0x1001A..0x10020. */
REGION void tsl9_remaining_record_dispatch_block_1001a(void)
{
    REGS;
    a5 = a5 | UINT32_C(0x00000080); LIVE;
    PORT(".Lremaining_record_dispatch_edge_1001e:\n.option push\n.option rvc\nc.j .Lremaining_record_dispatch_edge_1001e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_remaining_record_dispatch_block_ffd2\n");
    __builtin_unreachable();
}

/* Original0x10020..0x10022. */
REGION void tsl9_remaining_record_dispatch_block_10020(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x181A0..0x181A8. */
REGION void tsl9_remaining_record_dispatch_entry_181a0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_181a4:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_181a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0x181A8..0x181AA. */
REGION void tsl9_remaining_record_dispatch_block_181a8(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_181a8:\n.option push\n.option rvc\nc.bnez a0,.Lremaining_record_dispatch_edge_181a8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_181be\n");
    __builtin_unreachable();
}

/* Original0x181AA..0x181B6. */
REGION void tsl9_remaining_record_dispatch_block_181aa(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_literal_181aa:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_entry_181a0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_181aa\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_181b2:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_181b2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_table_entry_90b0\n");
    __builtin_unreachable();
}

/* Original0x181B6..0x181BE. */
REGION void tsl9_remaining_record_dispatch_block_181b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_181ba:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_181ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_18110\n");
    __builtin_unreachable();
}

/* Original0x181BE..0x181C4. */
REGION void tsl9_remaining_record_dispatch_block_181be(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x181CE..0x181D0. */
REGION void tsl9_remaining_record_dispatch_entry_181ce(void)
{
    REGS;
    PORT(".Lremaining_record_dispatch_edge_181ce:\n.option push\n.option rvc\nc.beqz a0,.Lremaining_record_dispatch_edge_181ce\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_remaining_record_dispatch_block_18216\n");
    __builtin_unreachable();
}

/* Original0x181D0..0x181DE. */
REGION void tsl9_remaining_record_dispatch_block_181d0(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\nli s0, 1\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_181da:\n.option push\n.option norvc\nbeq a0,a5,.Lremaining_record_dispatch_edge_181da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_181f0\n");
    __builtin_unreachable();
}

/* Original0x181DE..0x181E6. */
REGION void tsl9_remaining_record_dispatch_block_181de(void)
{
    REGS;
    a4 = UINT32_C(0xffffffff); LIVE;
    PORT(".option push\n.option rvc\nli s0, 2\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_181e2:\n.option push\n.option norvc\nbeq a0,a4,.Lremaining_record_dispatch_edge_181e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_181f0\n");
    __builtin_unreachable();
}

/* Original0x181E6..0x181EE. */
REGION void tsl9_remaining_record_dispatch_block_181e6(void)
{
    REGS;
    PORT(".option push\n.option norvc\nli s0, 32\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_181ea:\n.option push\n.option norvc\nblt a5,a0,.Lremaining_record_dispatch_edge_181ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_remaining_record_dispatch_block_181f0\n");
    __builtin_unreachable();
}

/* Original0x181EE..0x181F0. */
REGION void tsl9_remaining_record_dispatch_block_181ee(void)
{
    REGS;
    PORT(".option push\n.option rvc\nli s0, 16\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x181F0..0x18204. */
REGION void tsl9_remaining_record_dispatch_block_181f0(void)
{
    REGS;
    a2 = UINT32_C(0x00000032); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a3 = UINT32_C(0x00000000); LIVE;
    PORT(".Lremaining_record_dispatch_literal_181f8:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_remaining_record_dispatch_entry_181a0\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lremaining_record_dispatch_literal_181f8\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_18200:\n.option push\n.option norvc\njal ra,.Lremaining_record_dispatch_edge_18200\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0x18204..0x18216. */
REGION void tsl9_remaining_record_dispatch_block_18204(void)
{
    REGS;
    PORT(".option push\n.option rvc\nmv a0, s0\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    a2 = UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x000000c8); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lremaining_record_dispatch_edge_18212:\n.option push\n.option norvc\njal zero,.Lremaining_record_dispatch_edge_18212\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_registered_callbacks_provider_1802e\n");
    __builtin_unreachable();
}

/* Original0x18216..0x18218. */
REGION void tsl9_remaining_record_dispatch_block_18216(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(1)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(1)))
#endif
