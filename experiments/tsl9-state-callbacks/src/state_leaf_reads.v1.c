#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 private regions only; never execute this experiment.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define REGS register uint32_t a0 __asm__("a0"),a1 __asm__("a1"),a2 __asm__("a2"),a3 __asm__("a3"),a4 __asm__("a4"),a5 __asm__("a5"); __asm__ volatile("":"=r"(a0),"=r"(a1),"=r"(a2),"=r"(a3),"=r"(a4),"=r"(a5)::"memory")
#define LIVE __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")
#define CALL_PORT(code) __asm__ volatile(code:"+r"(a0),"+r"(a1),"+r"(a2),"+r"(a3),"+r"(a4),"+r"(a5)::"memory")

/* Original 29 selected state read/helper functions only. Architectural basic blocks have deliberate
 * fallthrough adjacency. They are not ordinary independently callable C.
 * C unsigned arithmetic/volatile memory use fixed A-register ports.
 * Straight-line reads, conditional packed reads and one 16B framed helper remain separate entries.
 * Fresh full-word source reads and original stack save/restore remain exact.
 * Memory read side effects, caller bounds and physical purpose remain unproved.
 * Both direct helper calls, branches, RA/SP effects and returns remain explicit.
 * No target execution, standard IRQ ABI or original-PC placement claim. */

/* Original 81F8..8202 */
REGION void tsl9_state_leaf_entry_81f8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20004\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 782u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 8202..820C */
REGION void tsl9_state_leaf_entry_8202(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20004\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 801u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original A968..A976 */
REGION void tsl9_state_leaf_entry_a968(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 1385u); LIVE;
    CALL_PORT(".option push\n.option norvc\nsnez a0, a0\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original A976..A99A */
REGION void tsl9_state_leaf_entry_a976(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 1379u); LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 1370u); LIVE;
    a0 = a0 + 0xffffffffu; LIVE;
    a5 = a4 << 1u; LIVE;
    CALL_PORT(".option push\n.option norvc\nsltiu a0, a0, 2\n.option pop\n");
    a0 = a0 | a5; LIVE;
    a0 = a0 << 24u; LIVE;
    CALL_PORT("srai a0, a0, 0x18");
    a5 = UINT32_C(4); LIVE;
    CALL_PORT(".Lstate_leaf_edge_a998:\nc.bnez a4,.Lstate_leaf_edge_a998\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_leaf_block_a9a8\n");
    __builtin_unreachable();
}

/* Original A99A..A9A8 */
REGION void tsl9_state_leaf_block_a99a(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x20001\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + 1345u); LIVE;
    a5 = a5 << 2u; LIVE;
    a5 = a5 << 24u; LIVE;
    CALL_PORT("srai a5, a5, 0x18");
    __builtin_unreachable();
}

/* Original A9A8..A9BC */
REGION void tsl9_state_leaf_block_a9a8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 1330u); LIVE;
    a4 = a4 << 3u; LIVE;
    a0 = a0 | a4; LIVE;
    a0 = a0 | a5; LIVE;
    a0 = a0 & 0xffu; LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original A9BC..A9D8 */
REGION void tsl9_state_leaf_entry_a9bc(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 1306u); LIVE;
    a0 = a0 + 0xfffffffeu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a4, 0x20001\n.option pop\n");
    a4 = *(volatile uint8_t *)(uintptr_t)(a4 + 1297u); LIVE;
    a5 = UINT32_C(2); LIVE;
    CALL_PORT(".option push\n.option norvc\nseqz a0, a0\n.option pop\n");
    CALL_PORT(".Lstate_leaf_edge_a9d4:\n.option push\n.option norvc\nbne a4,a5,.Lstate_leaf_edge_a9d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_leaf_block_a9dc\n");
    __builtin_unreachable();
}

/* Original A9D8..A9DC */
REGION void tsl9_state_leaf_block_a9d8(void)
{
    REGS;
    a0 = a0 | 0x2u; LIVE;
    __builtin_unreachable();
}

/* Original A9DC..A9DE */
REGION void tsl9_state_leaf_block_a9dc(void)
{
    REGS;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original AB68..AB72 */
REGION void tsl9_state_leaf_entry_ab68(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 896u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original AB72..AB7C */
REGION void tsl9_state_leaf_entry_ab72(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 885u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original B082..B08A */
REGION void tsl9_state_leaf_entry_b082(void)
{
    REGS;
    CALL_PORT("addi sp, sp, -16");
    CALL_PORT("sw ra, 12(sp)");
    CALL_PORT(".Lstate_leaf_edge_b086:\n.option push\n.option norvc\njal ra,.Lstate_leaf_edge_b086\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_a968\n");
    __builtin_unreachable();
}

/* Original B08A..B08E */
REGION void tsl9_state_leaf_block_b08a(void)
{
    REGS;
    a5 = UINT32_C(2); LIVE;
    CALL_PORT(".Lstate_leaf_edge_b08c:\nc.bnez a0,.Lstate_leaf_edge_b08c\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_leaf_block_b0a8\n");
    __builtin_unreachable();
}

/* Original B08E..B092 */
REGION void tsl9_state_leaf_block_b08e(void)
{
    REGS;
    CALL_PORT(".Lstate_leaf_edge_b08e:\n.option push\n.option norvc\njal ra,.Lstate_leaf_edge_b08e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original B092..B096 */
REGION void tsl9_state_leaf_block_b092(void)
{
    REGS;
    a5 = UINT32_C(1); LIVE;
    CALL_PORT(".Lstate_leaf_edge_b094:\nc.bnez a0,.Lstate_leaf_edge_b094\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_state_leaf_block_b0a8\n");
    __builtin_unreachable();
}

/* Original B096..B0A6 */
REGION void tsl9_state_leaf_block_b096(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x20001\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 - 429u); LIVE;
    a4 = UINT32_C(2); LIVE;
    a5 = UINT32_C(0); LIVE;
    CALL_PORT(".Lstate_leaf_edge_b0a2:\n.option push\n.option norvc\nbne a3,a4,.Lstate_leaf_edge_b0a2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_leaf_block_b0a8\n");
    __builtin_unreachable();
}

/* Original B0A6..B0A8 */
REGION void tsl9_state_leaf_block_b0a6(void)
{
    REGS;
    a5 = UINT32_C(3); LIVE;
    __builtin_unreachable();
}

/* Original B0A8..B0B0 */
REGION void tsl9_state_leaf_block_b0a8(void)
{
    REGS;
    CALL_PORT("lw ra, 12(sp)");
    CALL_PORT("mv a0, a5");
    CALL_PORT("addi sp, sp, 16");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original B3DA..B3E4 */
REGION void tsl9_state_leaf_entry_b3da(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 - 1252u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original B3E4..B3EE */
REGION void tsl9_state_leaf_entry_b3e4(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 1264u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original B3EE..B3F8 */
REGION void tsl9_state_leaf_entry_b3ee(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 - 1268u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original B3F8..B402 */
REGION void tsl9_state_leaf_entry_b3f8(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20001\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 - 1280u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original C462..C472 */
REGION void tsl9_state_leaf_entry_c462(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x20000\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 1354u); LIVE;
    a0 = a0 + 0xffffffffu; LIVE;
    CALL_PORT(".option push\n.option norvc\nseqz a0, a0\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D048..D052 */
REGION void tsl9_state_leaf_entry_d048(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 259u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D052..D05C */
REGION void tsl9_state_leaf_entry_d052(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 270u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D190..D196 */
REGION void tsl9_state_leaf_entry_d190(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a0, gp, 232\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D322..D332 */
REGION void tsl9_state_leaf_entry_d322(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 - 966u); LIVE;
    CALL_PORT(".option push\n.option norvc\nsnez a0, a0\n.option pop\n");
    a0 = a0 << 1u; LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D468..D472 */
REGION void tsl9_state_leaf_entry_d468(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 - 1288u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D472..D47C */
REGION void tsl9_state_leaf_entry_d472(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 - 1296u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D4E0..D4EA */
REGION void tsl9_state_leaf_entry_d4e0(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 1404u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D4EA..D4F4 */
REGION void tsl9_state_leaf_entry_d4ea(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1ffff\n.option pop\n");
    a0 = *(volatile uint16_t *)(uintptr_t)(a0 - 1412u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original D754..D75A */
REGION void tsl9_state_leaf_entry_d754(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\naddi a0, gp, 252\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original DEE2..DEEC */
REGION void tsl9_state_leaf_entry_dee2(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 + 134u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original E038..E042 */
REGION void tsl9_state_leaf_entry_e038(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fffe\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 207u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original E058..E076 */
REGION void tsl9_state_leaf_entry_e058(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a5, 0x1fffe\n.option pop\n");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 - 238u); LIVE;
    a5 = a5 + 0xffffffffu; LIVE;
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x1fffe\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 - 246u); LIVE;
    a4 = UINT32_C(1); LIVE;
    CALL_PORT(".option push\n.option norvc\nseqz a5, a5\n.option pop\n");
    a0 = UINT32_C(2); LIVE;
    CALL_PORT(".Lstate_leaf_edge_e072:\n.option push\n.option norvc\nbeq a3,a4,.Lstate_leaf_edge_e072\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_leaf_block_e078\n");
    __builtin_unreachable();
}

/* Original E076..E078 */
REGION void tsl9_state_leaf_block_e076(void)
{
    REGS;
    a0 = UINT32_C(0); LIVE;
    __builtin_unreachable();
}

/* Original E078..E08A */
REGION void tsl9_state_leaf_block_e078(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x1fffe\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 - 269u); LIVE;
    a4 = UINT32_C(1); LIVE;
    a5 = a5 | a0; LIVE;
    a0 = UINT32_C(4); LIVE;
    CALL_PORT(".Lstate_leaf_edge_e086:\n.option push\n.option norvc\nbeq a3,a4,.Lstate_leaf_edge_e086\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_leaf_block_e08c\n");
    __builtin_unreachable();
}

/* Original E08A..E08C */
REGION void tsl9_state_leaf_block_e08a(void)
{
    REGS;
    a0 = UINT32_C(0); LIVE;
    __builtin_unreachable();
}

/* Original E08C..E09E */
REGION void tsl9_state_leaf_block_e08c(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a3, 0x1fffe\n.option pop\n");
    a3 = *(volatile uint8_t *)(uintptr_t)(a3 - 287u); LIVE;
    a4 = UINT32_C(1); LIVE;
    a5 = a5 | a0; LIVE;
    a0 = UINT32_C(8); LIVE;
    CALL_PORT(".Lstate_leaf_edge_e09a:\n.option push\n.option norvc\nbeq a3,a4,.Lstate_leaf_edge_e09a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_state_leaf_block_e0a0\n");
    __builtin_unreachable();
}

/* Original E09E..E0A0 */
REGION void tsl9_state_leaf_block_e09e(void)
{
    REGS;
    a0 = UINT32_C(0); LIVE;
    __builtin_unreachable();
}

/* Original E0A0..E0A4 */
REGION void tsl9_state_leaf_block_e0a0(void)
{
    REGS;
    a0 = a0 | a5; LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original F65C..F666 */
REGION void tsl9_state_leaf_entry_f65c(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nauipc a0, 0x1fffd\n.option pop\n");
    a0 = *(volatile uint8_t *)(uintptr_t)(a0 - 1735u); LIVE;
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original F992..F998 */
REGION void tsl9_state_leaf_entry_f992(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a0, 277(gp)\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 10402..10408 */
REGION void tsl9_state_leaf_entry_10402(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlhu a0, 80(gp)\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}

/* Original 10408..1040E */
REGION void tsl9_state_leaf_entry_10408(void)
{
    REGS;
    CALL_PORT(".option push\n.option norvc\nlbu a0, 82(gp)\n.option pop\n");
    CALL_PORT("ret");
    __builtin_unreachable();
}
