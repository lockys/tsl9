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

/* One selector notification dispatcher and five guarded relative-offset tables functions:2444B/789i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original0xE220..0xE226. */
REGION void tsl9_selector_storage_provider_e220(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lselector_notifications_edge_e222:\n.option push\n.option norvc\nbltu a5,a2,.Lselector_notifications_edge_e222\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ebaa\n");
    __builtin_unreachable();
}

/* Original0xE226..0xE246. */
REGION void tsl9_selector_notifications_block_e226(void)
{
    REGS;
    PORT(".Lselector_notifications_literal_e226:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_selector_notifications_table_1a13c\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_e226\n.option pop\n");
    a2 = a2 << UINT32_C(0x00000002); LIVE;
    a2 = a2 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a2 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, -16\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nsw s2, 0(sp)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\nmv s1, a1\n.option pop\n");
    PORT(".option push\n.option rvc\nmv s0, a0\n.option pop\n");
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xE246..0xE24A. */
REGION void tsl9_selector_notifications_block_e246(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e246:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e246\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_8202\n");
    __builtin_unreachable();
}

/* Original0xE24A..0xE252. */
REGION void tsl9_selector_notifications_block_e24a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000106)) = (uint8_t)a0; LIVE;
    PORT(".Lselector_notifications_edge_e24e:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e24e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xE252..0xE254. */
REGION void tsl9_selector_notifications_block_e252(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e252:\n.option push\n.option rvc\nc.beqz a0,.Lselector_notifications_edge_e252\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e288\n");
    __builtin_unreachable();
}

/* Original0xE254..0xE260. */
REGION void tsl9_selector_notifications_block_e254(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010d)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e25c:\n.option push\n.option norvc\nbne s1,a5,.Lselector_notifications_edge_e25c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e288\n");
    __builtin_unreachable();
}

/* Original0xE260..0xE26E. */
REGION void tsl9_selector_notifications_block_e260(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s0, -43\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lselector_notifications_edge_e26a:\n.option push\n.option norvc\nbltu a4,a5,.Lselector_notifications_edge_e26a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e288\n");
    __builtin_unreachable();
}

/* Original0xE26E..0xE280. */
REGION void tsl9_selector_notifications_block_e26e(void)
{
    REGS;
    PORT(".Lselector_notifications_literal_e26e:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_selector_notifications_table_1a150\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_e26e\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xE280..0xE284. */
REGION void tsl9_selector_notifications_block_e280(void)
{
    REGS;
    a0 = UINT32_C(0x00000028); LIVE;
    __builtin_unreachable();
}

/* Original0xE284..0xE288. */
REGION void tsl9_selector_notifications_block_e284(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e284:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e284\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE288..0xE28C. */
REGION void tsl9_selector_notifications_block_e288(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e288:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e288\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b6a8\n");
    __builtin_unreachable();
}

/* Original0xE28C..0xE290. */
REGION void tsl9_selector_notifications_block_e28c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e28c:\n.option push\n.option norvc\nbeqz a0,.Lselector_notifications_edge_e28c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e432\n");
    __builtin_unreachable();
}

/* Original0xE290..0xE29C. */
REGION void tsl9_selector_notifications_block_e290(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010e)) = (uint8_t)a5; LIVE;
    a5 = UINT32_C(0x0000001a); LIVE;
    PORT(".Lselector_notifications_edge_e298:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e298\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e410\n");
    __builtin_unreachable();
}

/* Original0xE29C..0xE2A0. */
REGION void tsl9_selector_notifications_block_e29c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e29c:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e29c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e380\n");
    __builtin_unreachable();
}

/* Original0xE2A0..0xE2A6. */
REGION void tsl9_selector_notifications_block_e2a0(void)
{
    REGS;
    a5 = UINT32_C(0x00000014); LIVE;
    PORT(".Lselector_notifications_edge_e2a2:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e2a2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3f8\n");
    __builtin_unreachable();
}

/* Original0xE2A6..0xE2AA. */
REGION void tsl9_selector_notifications_block_e2a6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e2a6:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e2a6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e352\n");
    __builtin_unreachable();
}

/* Original0xE2AA..0xE2B0. */
REGION void tsl9_selector_notifications_block_e2aa(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lselector_notifications_edge_e2ac:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e2ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e42e\n");
    __builtin_unreachable();
}

/* Original0xE2B0..0xE2B4. */
REGION void tsl9_selector_notifications_block_e2b0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e2b0:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e2b0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e33c\n");
    __builtin_unreachable();
}

/* Original0xE2B4..0xE2BC. */
REGION void tsl9_selector_notifications_block_e2b4(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_e2b8:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e2b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3f2\n");
    __builtin_unreachable();
}

/* Original0xE2BC..0xE2CA. */
REGION void tsl9_selector_notifications_block_e2bc(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s0, -35\n.option pop\n");
    a4 = a5 & UINT32_C(0x000000ff); LIVE;
    a5 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lselector_notifications_edge_e2c6:\n.option push\n.option norvc\nbltu a5,a4,.Lselector_notifications_edge_e2c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e592\n");
    __builtin_unreachable();
}

/* Original0xE2CA..0xE2DA. */
REGION void tsl9_selector_notifications_block_e2ca(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option norvc\nsll a5, a5, a4\n.option pop\n");
    a4 = UINT32_C(0x76000000); LIVE;
    a4 = a4 & a5; LIVE;
    PORT(".Lselector_notifications_edge_e2d6:\n.option push\n.option norvc\nbnez a4,.Lselector_notifications_edge_e2d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e506\n");
    __builtin_unreachable();
}

/* Original0xE2DA..0xE2E2. */
REGION void tsl9_selector_notifications_block_e2da(void)
{
    REGS;
    a5 = a5 << UINT32_C(0x00000010); LIVE;
    a5 = a5 >> UINT32_C(0x00000010); LIVE;
    PORT(".Lselector_notifications_edge_e2de:\n.option push\n.option norvc\nbeqz a5,.Lselector_notifications_edge_e2de\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e50e\n");
    __builtin_unreachable();
}

/* Original0xE2E2..0xE2E8. */
REGION void tsl9_selector_notifications_block_e2e2(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lselector_notifications_edge_e2e4:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e2e4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_profiles_provider_18430\n");
    __builtin_unreachable();
}

/* Original0xE2E8..0xE2EA. */
REGION void tsl9_selector_notifications_block_e2e8(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e2e8:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e2e8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e50e\n");
    __builtin_unreachable();
}

/* Original0xE2EA..0xE2F0. */
REGION void tsl9_selector_notifications_block_e2ea(void)
{
    REGS;
    a0 = UINT32_C(0x00000029); LIVE;
    PORT(".Lselector_notifications_edge_e2ee:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e2ee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e284\n");
    __builtin_unreachable();
}

/* Original0xE2F0..0xE2F8. */
REGION void tsl9_selector_notifications_block_e2f0(void)
{
    REGS;
    a0 = UINT32_C(0x0000002a); LIVE;
    PORT(".Lselector_notifications_edge_e2f4:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e2f4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE2F8..0xE30C. */
REGION void tsl9_selector_notifications_block_e2f8(void)
{
    REGS;
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000001f4); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_literal_e300:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_fe08\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_e300\n.option pop\n");
    PORT(".Lselector_notifications_edge_e308:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e308\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xE30C..0xE30E. */
REGION void tsl9_selector_notifications_block_e30c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e30c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e30c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e288\n");
    __builtin_unreachable();
}

/* Original0xE30E..0xE310. */
REGION void tsl9_selector_notifications_block_e30e(void)
{
    REGS;
    a0 = UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0xE310..0xE314. */
REGION void tsl9_selector_notifications_block_e310(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e310:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e310\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_180f0\n");
    __builtin_unreachable();
}

/* Original0xE314..0xE316. */
REGION void tsl9_selector_notifications_block_e314(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e314:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e314\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e288\n");
    __builtin_unreachable();
}

/* Original0xE316..0xE31A. */
REGION void tsl9_selector_notifications_block_e316(void)
{
    REGS;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lselector_notifications_edge_e318:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e318\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e310\n");
    __builtin_unreachable();
}

/* Original0xE31A..0xE322. */
REGION void tsl9_selector_notifications_block_e31a(void)
{
    REGS;
    a0 = UINT32_C(0x00001000); LIVE;
    a0 = a0 + UINT32_C(0xfffff800); LIVE;
    PORT(".Lselector_notifications_edge_e320:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e320\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e310\n");
    __builtin_unreachable();
}

/* Original0xE322..0xE328. */
REGION void tsl9_selector_notifications_block_e322(void)
{
    REGS;
    a0 = UINT32_C(0x00000400); LIVE;
    PORT(".Lselector_notifications_edge_e326:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e326\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e310\n");
    __builtin_unreachable();
}

/* Original0xE328..0xE32C. */
REGION void tsl9_selector_notifications_block_e328(void)
{
    REGS;
    a0 = UINT32_C(0x00008000); LIVE;
    PORT(".Lselector_notifications_edge_e32a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e32a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e310\n");
    __builtin_unreachable();
}

/* Original0xE32C..0xE330. */
REGION void tsl9_selector_notifications_block_e32c(void)
{
    REGS;
    a0 = UINT32_C(0x00004000); LIVE;
    PORT(".Lselector_notifications_edge_e32e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e32e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e310\n");
    __builtin_unreachable();
}

/* Original0xE330..0xE336. */
REGION void tsl9_selector_notifications_block_e330(void)
{
    REGS;
    a0 = UINT32_C(0x00000040); LIVE;
    PORT(".Lselector_notifications_edge_e334:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e334\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e310\n");
    __builtin_unreachable();
}

/* Original0xE336..0xE33C. */
REGION void tsl9_selector_notifications_block_e336(void)
{
    REGS;
    a0 = UINT32_C(0x00000080); LIVE;
    PORT(".Lselector_notifications_edge_e33a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e33a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e310\n");
    __builtin_unreachable();
}

/* Original0xE33C..0xE342. */
REGION void tsl9_selector_notifications_block_e33c(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lselector_notifications_edge_e33e:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e33e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3f0\n");
    __builtin_unreachable();
}

/* Original0xE342..0xE34C. */
REGION void tsl9_selector_notifications_block_e342(void)
{
    REGS;
    a5 = UINT32_C(0x00000013); LIVE;
    a0 = UINT32_C(0x00000032); LIVE;
    PORT(".Lselector_notifications_edge_e348:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e348\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE34C..0xE350. */
REGION void tsl9_selector_notifications_block_e34c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e34c:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e34c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE350..0xE352. */
REGION void tsl9_selector_notifications_block_e350(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e350:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e350\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE352..0xE358. */
REGION void tsl9_selector_notifications_block_e352(void)
{
    REGS;
    a5 = UINT32_C(0x00000017); LIVE;
    PORT(".Lselector_notifications_edge_e354:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e354\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e404\n");
    __builtin_unreachable();
}

/* Original0xE358..0xE35C. */
REGION void tsl9_selector_notifications_block_e358(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e358:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e358\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e36e\n");
    __builtin_unreachable();
}

/* Original0xE35C..0xE362. */
REGION void tsl9_selector_notifications_block_e35c(void)
{
    REGS;
    a5 = UINT32_C(0x00000015); LIVE;
    PORT(".Lselector_notifications_edge_e35e:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e35e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3fe\n");
    __builtin_unreachable();
}

/* Original0xE362..0xE36C. */
REGION void tsl9_selector_notifications_block_e362(void)
{
    REGS;
    a5 = UINT32_C(0x00000016); LIVE;
    a0 = UINT32_C(0x00000035); LIVE;
    PORT(".Lselector_notifications_edge_e368:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e368\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE36C..0xE36E. */
REGION void tsl9_selector_notifications_block_e36c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e36c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e36c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE36E..0xE374. */
REGION void tsl9_selector_notifications_block_e36e(void)
{
    REGS;
    a5 = UINT32_C(0x00000018); LIVE;
    PORT(".Lselector_notifications_edge_e370:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e370\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e40a\n");
    __builtin_unreachable();
}

/* Original0xE374..0xE37E. */
REGION void tsl9_selector_notifications_block_e374(void)
{
    REGS;
    a5 = UINT32_C(0x00000019); LIVE;
    a0 = UINT32_C(0x00000038); LIVE;
    PORT(".Lselector_notifications_edge_e37a:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e37a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE37E..0xE380. */
REGION void tsl9_selector_notifications_block_e37e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e37e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e37e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE380..0xE388. */
REGION void tsl9_selector_notifications_block_e380(void)
{
    REGS;
    a5 = UINT32_C(0x00000027); LIVE;
    PORT(".Lselector_notifications_edge_e384:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e384\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e420\n");
    __builtin_unreachable();
}

/* Original0xE388..0xE38C. */
REGION void tsl9_selector_notifications_block_e388(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e388:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e388\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3be\n");
    __builtin_unreachable();
}

/* Original0xE38C..0xE394. */
REGION void tsl9_selector_notifications_block_e38c(void)
{
    REGS;
    a5 = UINT32_C(0x00000024); LIVE;
    PORT(".Lselector_notifications_edge_e390:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e390\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e416\n");
    __builtin_unreachable();
}

/* Original0xE394..0xE398. */
REGION void tsl9_selector_notifications_block_e394(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e394:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e394\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3a8\n");
    __builtin_unreachable();
}

/* Original0xE398..0xE3A2. */
REGION void tsl9_selector_notifications_block_e398(void)
{
    REGS;
    a5 = UINT32_C(0x00000023); LIVE;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_e39e:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e39e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE3A2..0xE3A6. */
REGION void tsl9_selector_notifications_block_e3a2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e3a2:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e3a2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_action_primitives_provider_180f0\n");
    __builtin_unreachable();
}

/* Original0xE3A6..0xE3A8. */
REGION void tsl9_selector_notifications_block_e3a6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e3a6:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e3a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE3A8..0xE3B0. */
REGION void tsl9_selector_notifications_block_e3a8(void)
{
    REGS;
    a5 = UINT32_C(0x00000025); LIVE;
    PORT(".Lselector_notifications_edge_e3ac:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e3ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e41a\n");
    __builtin_unreachable();
}

/* Original0xE3B0..0xE3BC. */
REGION void tsl9_selector_notifications_block_e3b0(void)
{
    REGS;
    a5 = UINT32_C(0x00000026); LIVE;
    a0 = UINT32_C(0x00000100); LIVE;
    PORT(".Lselector_notifications_edge_e3b8:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e3b8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3a2\n");
    __builtin_unreachable();
}

/* Original0xE3BC..0xE3BE. */
REGION void tsl9_selector_notifications_block_e3bc(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e3bc:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e3bc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE3BE..0xE3C6. */
REGION void tsl9_selector_notifications_block_e3be(void)
{
    REGS;
    a5 = UINT32_C(0x0000002a); LIVE;
    PORT(".Lselector_notifications_edge_e3c2:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e3c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e428\n");
    __builtin_unreachable();
}

/* Original0xE3C6..0xE3CA. */
REGION void tsl9_selector_notifications_block_e3c6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e3c6:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e3c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3de\n");
    __builtin_unreachable();
}

/* Original0xE3CA..0xE3D2. */
REGION void tsl9_selector_notifications_block_e3ca(void)
{
    REGS;
    a5 = UINT32_C(0x00000028); LIVE;
    PORT(".Lselector_notifications_edge_e3ce:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e3ce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e424\n");
    __builtin_unreachable();
}

/* Original0xE3D2..0xE3DC. */
REGION void tsl9_selector_notifications_block_e3d2(void)
{
    REGS;
    a5 = UINT32_C(0x00000029); LIVE;
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".Lselector_notifications_edge_e3d8:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e3d8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3a2\n");
    __builtin_unreachable();
}

/* Original0xE3DC..0xE3DE. */
REGION void tsl9_selector_notifications_block_e3dc(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e3dc:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e3dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE3DE..0xE3E8. */
REGION void tsl9_selector_notifications_block_e3de(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_edge_e3e4:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e3e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e3f2\n");
    __builtin_unreachable();
}

/* Original0xE3E8..0xE3F0. */
REGION void tsl9_selector_notifications_block_e3e8(void)
{
    REGS;
    a5 = UINT32_C(0x00000044); LIVE;
    PORT(".Lselector_notifications_edge_e3ec:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e3ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE3F0..0xE3F2. */
REGION void tsl9_selector_notifications_block_e3f0(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0xE3F2..0xE3F6. */
REGION void tsl9_selector_notifications_block_e3f2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e3f2:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e3f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_101de\n");
    __builtin_unreachable();
}

/* Original0xE3F6..0xE3F8. */
REGION void tsl9_selector_notifications_block_e3f6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e3f6:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e3f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE3F8..0xE3FE. */
REGION void tsl9_selector_notifications_block_e3f8(void)
{
    REGS;
    a0 = UINT32_C(0x00000033); LIVE;
    PORT(".Lselector_notifications_edge_e3fc:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e3fc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE3FE..0xE404. */
REGION void tsl9_selector_notifications_block_e3fe(void)
{
    REGS;
    a0 = UINT32_C(0x00000034); LIVE;
    PORT(".Lselector_notifications_edge_e402:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e402\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE404..0xE40A. */
REGION void tsl9_selector_notifications_block_e404(void)
{
    REGS;
    a0 = UINT32_C(0x00000036); LIVE;
    PORT(".Lselector_notifications_edge_e408:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e408\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE40A..0xE410. */
REGION void tsl9_selector_notifications_block_e40a(void)
{
    REGS;
    a0 = UINT32_C(0x00000037); LIVE;
    PORT(".Lselector_notifications_edge_e40e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e40e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE410..0xE416. */
REGION void tsl9_selector_notifications_block_e410(void)
{
    REGS;
    a0 = UINT32_C(0x00000039); LIVE;
    PORT(".Lselector_notifications_edge_e414:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e414\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE416..0xE41A. */
REGION void tsl9_selector_notifications_block_e416(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e418:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e418\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e3a2\n");
    __builtin_unreachable();
}

/* Original0xE41A..0xE420. */
REGION void tsl9_selector_notifications_block_e41a(void)
{
    REGS;
    a0 = UINT32_C(0x00000200); LIVE;
    PORT(".Lselector_notifications_edge_e41e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e41e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e3a2\n");
    __builtin_unreachable();
}

/* Original0xE420..0xE424. */
REGION void tsl9_selector_notifications_block_e420(void)
{
    REGS;
    a0 = UINT32_C(0x00002000); LIVE;
    PORT(".Lselector_notifications_edge_e422:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e422\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e3a2\n");
    __builtin_unreachable();
}

/* Original0xE424..0xE428. */
REGION void tsl9_selector_notifications_block_e424(void)
{
    REGS;
    a0 = UINT32_C(0x00001000); LIVE;
    PORT(".Lselector_notifications_edge_e426:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e426\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e3a2\n");
    __builtin_unreachable();
}

/* Original0xE428..0xE42E. */
REGION void tsl9_selector_notifications_block_e428(void)
{
    REGS;
    a0 = UINT32_C(0x00000020); LIVE;
    PORT(".Lselector_notifications_edge_e42c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e42c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e3a2\n");
    __builtin_unreachable();
}

/* Original0xE42E..0xE432. */
REGION void tsl9_selector_notifications_block_e42e(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lselector_notifications_edge_e430:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e430\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e3f2\n");
    __builtin_unreachable();
}

/* Original0xE432..0xE438. */
REGION void tsl9_selector_notifications_block_e432(void)
{
    REGS;
    a5 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lselector_notifications_edge_e434:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e434\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e4de\n");
    __builtin_unreachable();
}

/* Original0xE438..0xE43C. */
REGION void tsl9_selector_notifications_block_e438(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e438:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e438\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e486\n");
    __builtin_unreachable();
}

/* Original0xE43C..0xE442. */
REGION void tsl9_selector_notifications_block_e43c(void)
{
    REGS;
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lselector_notifications_edge_e43e:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e43e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e4ca\n");
    __builtin_unreachable();
}

/* Original0xE442..0xE446. */
REGION void tsl9_selector_notifications_block_e442(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e442:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e442\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e466\n");
    __builtin_unreachable();
}

/* Original0xE446..0xE44C. */
REGION void tsl9_selector_notifications_block_e446(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lselector_notifications_edge_e448:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e448\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE44C..0xE450. */
REGION void tsl9_selector_notifications_block_e44c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e44c:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e44c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_cd44\n");
    __builtin_unreachable();
}

/* Original0xE450..0xE454. */
REGION void tsl9_selector_notifications_block_e450(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e452:\n.option push\n.option rvc\nc.bnez a0,.Lselector_notifications_edge_e452\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e45c\n");
    __builtin_unreachable();
}

/* Original0xE454..0xE458. */
REGION void tsl9_selector_notifications_block_e454(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e454:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e454\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_a9e8\n");
    __builtin_unreachable();
}

/* Original0xE458..0xE45C. */
REGION void tsl9_selector_notifications_block_e458(void)
{
    REGS;
    a5 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    __builtin_unreachable();
}

/* Original0xE45C..0xE464. */
REGION void tsl9_selector_notifications_block_e45c(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010c)) = (uint8_t)a5; LIVE;
    PORT(".Lselector_notifications_edge_e460:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e460\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_ccc2\n");
    __builtin_unreachable();
}

/* Original0xE464..0xE466. */
REGION void tsl9_selector_notifications_block_e464(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e464:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e464\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE466..0xE46C. */
REGION void tsl9_selector_notifications_block_e466(void)
{
    REGS;
    a5 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lselector_notifications_edge_e468:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e468\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e4f2\n");
    __builtin_unreachable();
}

/* Original0xE46C..0xE472. */
REGION void tsl9_selector_notifications_block_e46c(void)
{
    REGS;
    a5 = UINT32_C(0x0000000b); LIVE;
    PORT(".Lselector_notifications_edge_e46e:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e46e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE472..0xE47A. */
REGION void tsl9_selector_notifications_block_e472(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000106)); LIVE;
    PORT(".Lselector_notifications_edge_e476:\n.option push\n.option norvc\nbnez a5,.Lselector_notifications_edge_e476\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE47A..0xE47E. */
REGION void tsl9_selector_notifications_block_e47a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e47a:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e47a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xE47E..0xE482. */
REGION void tsl9_selector_notifications_block_e47e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e47e:\n.option push\n.option norvc\nbnez a0,.Lselector_notifications_edge_e47e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE482..0xE486. */
REGION void tsl9_selector_notifications_block_e482(void)
{
    REGS;
    a0 = UINT32_C(0x00000005); LIVE;
    PORT(".Lselector_notifications_edge_e484:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e484\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE486..0xE48E. */
REGION void tsl9_selector_notifications_block_e486(void)
{
    REGS;
    a5 = UINT32_C(0x0000003d); LIVE;
    PORT(".Lselector_notifications_edge_e48a:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e48a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e4b6\n");
    __builtin_unreachable();
}

/* Original0xE48E..0xE492. */
REGION void tsl9_selector_notifications_block_e48e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e48e:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e48e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e4a0\n");
    __builtin_unreachable();
}

/* Original0xE492..0xE49A. */
REGION void tsl9_selector_notifications_block_e492(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lselector_notifications_edge_e496:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e496\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE49A..0xE49E. */
REGION void tsl9_selector_notifications_block_e49a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e49a:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e49a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_c364\n");
    __builtin_unreachable();
}

/* Original0xE49E..0xE4A0. */
REGION void tsl9_selector_notifications_block_e49e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e49e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e49e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4A0..0xE4A8. */
REGION void tsl9_selector_notifications_block_e4a0(void)
{
    REGS;
    a5 = UINT32_C(0x00000044); LIVE;
    PORT(".Lselector_notifications_edge_e4a4:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e4a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e44c\n");
    __builtin_unreachable();
}

/* Original0xE4A8..0xE4B0. */
REGION void tsl9_selector_notifications_block_e4a8(void)
{
    REGS;
    a5 = UINT32_C(0x00000045); LIVE;
    PORT(".Lselector_notifications_edge_e4ac:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e4ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4B0..0xE4B4. */
REGION void tsl9_selector_notifications_block_e4b0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4b0:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e4b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_ccf6\n");
    __builtin_unreachable();
}

/* Original0xE4B4..0xE4B6. */
REGION void tsl9_selector_notifications_block_e4b4(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4b4:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e4b4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4B6..0xE4C2. */
REGION void tsl9_selector_notifications_block_e4b6(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e4be:\n.option push\n.option norvc\nbltu a5,s1,.Lselector_notifications_edge_e4be\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4C2..0xE4C8. */
REGION void tsl9_selector_notifications_block_e4c2(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_e4c4:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e4c4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_ac78\n");
    __builtin_unreachable();
}

/* Original0xE4C8..0xE4CA. */
REGION void tsl9_selector_notifications_block_e4c8(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4c8:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e4c8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4CA..0xE4D2. */
REGION void tsl9_selector_notifications_block_e4ca(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000106)); LIVE;
    PORT(".Lselector_notifications_edge_e4ce:\n.option push\n.option norvc\nbnez a5,.Lselector_notifications_edge_e4ce\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4D2..0xE4D6. */
REGION void tsl9_selector_notifications_block_e4d2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4d2:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e4d2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xE4D6..0xE4DA. */
REGION void tsl9_selector_notifications_block_e4d6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4d6:\n.option push\n.option norvc\nbnez a0,.Lselector_notifications_edge_e4d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4DA..0xE4DE. */
REGION void tsl9_selector_notifications_block_e4da(void)
{
    REGS;
    a0 = UINT32_C(0x00000004); LIVE;
    PORT(".Lselector_notifications_edge_e4dc:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e4dc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE4DE..0xE4E6. */
REGION void tsl9_selector_notifications_block_e4de(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000106)); LIVE;
    PORT(".Lselector_notifications_edge_e4e2:\n.option push\n.option norvc\nbnez a5,.Lselector_notifications_edge_e4e2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4E6..0xE4EA. */
REGION void tsl9_selector_notifications_block_e4e6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4e6:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e4e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xE4EA..0xE4EE. */
REGION void tsl9_selector_notifications_block_e4ea(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4ea:\n.option push\n.option norvc\nbnez a0,.Lselector_notifications_edge_e4ea\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4EE..0xE4F2. */
REGION void tsl9_selector_notifications_block_e4ee(void)
{
    REGS;
    a0 = UINT32_C(0x00000012); LIVE;
    PORT(".Lselector_notifications_edge_e4f0:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e4f0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE4F2..0xE4FA. */
REGION void tsl9_selector_notifications_block_e4f2(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000106)); LIVE;
    PORT(".Lselector_notifications_edge_e4f6:\n.option push\n.option norvc\nbnez a5,.Lselector_notifications_edge_e4f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE4FA..0xE4FE. */
REGION void tsl9_selector_notifications_block_e4fa(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4fa:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e4fa\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xE4FE..0xE502. */
REGION void tsl9_selector_notifications_block_e4fe(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e4fe:\n.option push\n.option norvc\nbnez a0,.Lselector_notifications_edge_e4fe\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e2bc\n");
    __builtin_unreachable();
}

/* Original0xE502..0xE506. */
REGION void tsl9_selector_notifications_block_e502(void)
{
    REGS;
    a0 = UINT32_C(0x00000013); LIVE;
    PORT(".Lselector_notifications_edge_e504:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e504\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e34c\n");
    __builtin_unreachable();
}

/* Original0xE506..0xE50A. */
REGION void tsl9_selector_notifications_block_e506(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e506:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e506\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xE50A..0xE50E. */
REGION void tsl9_selector_notifications_block_e50a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010b)) = (uint8_t)a0; LIVE;
    __builtin_unreachable();
}

/* Original0xE50E..0xE516. */
REGION void tsl9_selector_notifications_block_e50e(void)
{
    REGS;
    a5 = UINT32_C(0x0000003f); LIVE;
    PORT(".Lselector_notifications_edge_e512:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e512\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5a2\n");
    __builtin_unreachable();
}

/* Original0xE516..0xE51A. */
REGION void tsl9_selector_notifications_block_e516(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e516:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e516\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5b2\n");
    __builtin_unreachable();
}

/* Original0xE51A..0xE520. */
REGION void tsl9_selector_notifications_block_e51a(void)
{
    REGS;
    a5 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lselector_notifications_edge_e51c:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e51c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5a2\n");
    __builtin_unreachable();
}

/* Original0xE520..0xE524. */
REGION void tsl9_selector_notifications_block_e520(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e520:\n.option push\n.option norvc\nbltu s0,a5,.Lselector_notifications_edge_e520\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e532\n");
    __builtin_unreachable();
}

/* Original0xE524..0xE532. */
REGION void tsl9_selector_notifications_block_e524(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s0, -58\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e52e:\n.option push\n.option norvc\nbleu a5,a4,.Lselector_notifications_edge_e52e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5a2\n");
    __builtin_unreachable();
}

/* Original0xE532..0xE53A. */
REGION void tsl9_selector_notifications_block_e532(void)
{
    REGS;
    a5 = UINT32_C(0x00000040); LIVE;
    PORT(".Lselector_notifications_edge_e536:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e536\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e642\n");
    __builtin_unreachable();
}

/* Original0xE53A..0xE53E. */
REGION void tsl9_selector_notifications_block_e53a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e53a:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e53a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5fe\n");
    __builtin_unreachable();
}

/* Original0xE53E..0xE546. */
REGION void tsl9_selector_notifications_block_e53e(void)
{
    REGS;
    a5 = UINT32_C(0x0000003f); LIVE;
    PORT(".Lselector_notifications_edge_e542:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e542\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e606\n");
    __builtin_unreachable();
}

/* Original0xE546..0xE554. */
REGION void tsl9_selector_notifications_block_e546(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 & UINT32_C(0x00000010); LIVE;
    PORT(".Lselector_notifications_edge_e552:\n.option push\n.option rvc\nc.beqz a5,.Lselector_notifications_edge_e552\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e568\n");
    __builtin_unreachable();
}

/* Original0xE554..0xE55C. */
REGION void tsl9_selector_notifications_block_e554(void)
{
    REGS;
    a5 = UINT32_C(0x0000003f); LIVE;
    PORT(".Lselector_notifications_edge_e558:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e558\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e65a\n");
    __builtin_unreachable();
}

/* Original0xE55C..0xE560. */
REGION void tsl9_selector_notifications_block_e55c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e55c:\n.option push\n.option norvc\nbltu s0,a5,.Lselector_notifications_edge_e55c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e568\n");
    __builtin_unreachable();
}

/* Original0xE560..0xE568. */
REGION void tsl9_selector_notifications_block_e560(void)
{
    REGS;
    a5 = UINT32_C(0x00000042); LIVE;
    PORT(".Lselector_notifications_edge_e564:\n.option push\n.option norvc\nbleu s0,a5,.Lselector_notifications_edge_e564\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e66a\n");
    __builtin_unreachable();
}

/* Original0xE568..0xE570. */
REGION void tsl9_selector_notifications_block_e568(void)
{
    REGS;
    a5 = UINT32_C(0x0000003d); LIVE;
    PORT(".Lselector_notifications_edge_e56c:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e56c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e672\n");
    __builtin_unreachable();
}

/* Original0xE570..0xE578. */
REGION void tsl9_selector_notifications_block_e570(void)
{
    REGS;
    a5 = UINT32_C(0x0000003c); LIVE;
    PORT(".Lselector_notifications_edge_e574:\n.option push\n.option norvc\nbleu a5,s0,.Lselector_notifications_edge_e574\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e584\n");
    __builtin_unreachable();
}

/* Original0xE578..0xE580. */
REGION void tsl9_selector_notifications_block_e578(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    a5 = UINT32_C(0x0000000f); LIVE;
    __builtin_unreachable();
}

/* Original0xE580..0xE584. */
REGION void tsl9_selector_notifications_block_e580(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e580:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e580\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e736\n");
    __builtin_unreachable();
}

/* Original0xE584..0xE592. */
REGION void tsl9_selector_notifications_block_e584(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lselector_notifications_edge_e58e:\n.option push\n.option norvc\njal zero,.Lselector_notifications_edge_e58e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_171de\n");
    __builtin_unreachable();
}

/* Original0xE592..0xE59A. */
REGION void tsl9_selector_notifications_block_e592(void)
{
    REGS;
    a5 = UINT32_C(0x0000004c); LIVE;
    PORT(".Lselector_notifications_edge_e596:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e596\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e50e\n");
    __builtin_unreachable();
}

/* Original0xE59A..0xE5A2. */
REGION void tsl9_selector_notifications_block_e59a(void)
{
    REGS;
    a0 = UINT32_C(0x0000005a); LIVE;
    PORT(".Lselector_notifications_edge_e59e:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e59e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE5A2..0xE5A8. */
REGION void tsl9_selector_notifications_block_e5a2(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_edge_e5a4:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e5a4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_adb8\n");
    __builtin_unreachable();
}

/* Original0xE5A8..0xE5AC. */
REGION void tsl9_selector_notifications_block_e5a8(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e5a8:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e5a8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_a6aa\n");
    __builtin_unreachable();
}

/* Original0xE5AC..0xE5B0. */
REGION void tsl9_selector_notifications_block_e5ac(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e5ac:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e5ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_aaa0\n");
    __builtin_unreachable();
}

/* Original0xE5B0..0xE5B2. */
REGION void tsl9_selector_notifications_block_e5b0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e5b0:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e5b0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e532\n");
    __builtin_unreachable();
}

/* Original0xE5B2..0xE5BA. */
REGION void tsl9_selector_notifications_block_e5b2(void)
{
    REGS;
    a5 = UINT32_C(0x0000004d); LIVE;
    PORT(".Lselector_notifications_edge_e5b6:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e5b6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5ee\n");
    __builtin_unreachable();
}

/* Original0xE5BA..0xE5BE. */
REGION void tsl9_selector_notifications_block_e5ba(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e5ba:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e5ba\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5c8\n");
    __builtin_unreachable();
}

/* Original0xE5BE..0xE5C6. */
REGION void tsl9_selector_notifications_block_e5be(void)
{
    REGS;
    a5 = UINT32_C(0x0000004c); LIVE;
    PORT(".Lselector_notifications_edge_e5c2:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e5c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e532\n");
    __builtin_unreachable();
}

/* Original0xE5C6..0xE5C8. */
REGION void tsl9_selector_notifications_block_e5c6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e5c6:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e5c6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e5a2\n");
    __builtin_unreachable();
}

/* Original0xE5C8..0xE5D0. */
REGION void tsl9_selector_notifications_block_e5c8(void)
{
    REGS;
    a5 = UINT32_C(0x0000004e); LIVE;
    PORT(".Lselector_notifications_edge_e5cc:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e5cc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5f8\n");
    __builtin_unreachable();
}

/* Original0xE5D0..0xE5D8. */
REGION void tsl9_selector_notifications_block_e5d0(void)
{
    REGS;
    a5 = UINT32_C(0x0000004f); LIVE;
    PORT(".Lselector_notifications_edge_e5d4:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e5d4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e532\n");
    __builtin_unreachable();
}

/* Original0xE5D8..0xE5E8. */
REGION void tsl9_selector_notifications_block_e5d8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a0 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000106)); LIVE;
    a0 = (uint32_t)(a0 != UINT32_C(0)); LIVE;
    a0 = a0 + UINT32_C(0x00000062); LIVE;
    PORT(".Lselector_notifications_edge_e5e4:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e5e4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE5E8..0xE5EE. */
REGION void tsl9_selector_notifications_block_e5e8(void)
{
    REGS;
    a0 = UINT32_C(0x00000065); LIVE;
    PORT(".Lselector_notifications_edge_e5ec:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e5ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e5f2\n");
    __builtin_unreachable();
}

/* Original0xE5EE..0xE5F2. */
REGION void tsl9_selector_notifications_block_e5ee(void)
{
    REGS;
    a0 = UINT32_C(0x0000005b); LIVE;
    __builtin_unreachable();
}

/* Original0xE5F2..0xE5F6. */
REGION void tsl9_selector_notifications_block_e5f2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e5f2:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e5f2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE5F6..0xE5F8. */
REGION void tsl9_selector_notifications_block_e5f6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e5f6:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e5f6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e546\n");
    __builtin_unreachable();
}

/* Original0xE5F8..0xE5FE. */
REGION void tsl9_selector_notifications_block_e5f8(void)
{
    REGS;
    a0 = UINT32_C(0x00000064); LIVE;
    PORT(".Lselector_notifications_edge_e5fc:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e5fc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e5f2\n");
    __builtin_unreachable();
}

/* Original0xE5FE..0xE606. */
REGION void tsl9_selector_notifications_block_e5fe(void)
{
    REGS;
    a5 = UINT32_C(0x00000042); LIVE;
    PORT(".Lselector_notifications_edge_e602:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e602\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e546\n");
    __builtin_unreachable();
}

/* Original0xE606..0xE60C. */
REGION void tsl9_selector_notifications_block_e606(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000107)); LIVE;
    PORT(".Lselector_notifications_edge_e60a:\n.option push\n.option rvc\nc.beqz a5,.Lselector_notifications_edge_e60a\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e616\n");
    __builtin_unreachable();
}

/* Original0xE60C..0xE616. */
REGION void tsl9_selector_notifications_block_e60c(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000107)) = (uint8_t)0; LIVE;
    PORT(".Lselector_notifications_edge_e612:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e612\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_bd00\n");
    __builtin_unreachable();
}

/* Original0xE616..0xE61C. */
REGION void tsl9_selector_notifications_block_e616(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_edge_e618:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e618\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_da36\n");
    __builtin_unreachable();
}

/* Original0xE61C..0xE628. */
REGION void tsl9_selector_notifications_block_e61c(void)
{
    REGS;
    a5 = UINT32_C(0x00000041); LIVE;
    a0 = UINT32_C(0x00000070); LIVE;
    PORT(".Lselector_notifications_edge_e624:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e624\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5f2\n");
    __builtin_unreachable();
}

/* Original0xE628..0xE634. */
REGION void tsl9_selector_notifications_block_e628(void)
{
    REGS;
    a5 = UINT32_C(0x00000042); LIVE;
    a0 = UINT32_C(0x00000071); LIVE;
    PORT(".Lselector_notifications_edge_e630:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e630\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5f2\n");
    __builtin_unreachable();
}

/* Original0xE634..0xE640. */
REGION void tsl9_selector_notifications_block_e634(void)
{
    REGS;
    a5 = UINT32_C(0x00000040); LIVE;
    a0 = UINT32_C(0x0000006e); LIVE;
    PORT(".Lselector_notifications_edge_e63c:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e63c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e5f2\n");
    __builtin_unreachable();
}

/* Original0xE640..0xE642. */
REGION void tsl9_selector_notifications_block_e640(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e640:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e640\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e654\n");
    __builtin_unreachable();
}

/* Original0xE642..0xE64E. */
REGION void tsl9_selector_notifications_block_e642(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000001); LIVE;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000107)) = (uint8_t)a5; LIVE;
    PORT(".Lselector_notifications_edge_e64a:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e64a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_bd00\n");
    __builtin_unreachable();
}

/* Original0xE64E..0xE654. */
REGION void tsl9_selector_notifications_block_e64e(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e650:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e650\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_da36\n");
    __builtin_unreachable();
}

/* Original0xE654..0xE65A. */
REGION void tsl9_selector_notifications_block_e654(void)
{
    REGS;
    a0 = UINT32_C(0x0000006f); LIVE;
    PORT(".Lselector_notifications_edge_e658:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e658\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e5f2\n");
    __builtin_unreachable();
}

/* Original0xE65A..0xE66A. */
REGION void tsl9_selector_notifications_block_e65a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lselector_notifications_edge_e666:\n.option push\n.option norvc\njal zero,.Lselector_notifications_edge_e666\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d668\n");
    __builtin_unreachable();
}

/* Original0xE66A..0xE670. */
REGION void tsl9_selector_notifications_block_e66a(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_edge_e66c:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e66c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_d668\n");
    __builtin_unreachable();
}

/* Original0xE670..0xE672. */
REGION void tsl9_selector_notifications_block_e670(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e670:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e670\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e568\n");
    __builtin_unreachable();
}

/* Original0xE672..0xE67E. */
REGION void tsl9_selector_notifications_block_e672(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi s0, s0, -68\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e67c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e67c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e580\n");
    __builtin_unreachable();
}

/* Original0xE67E..0xE684. */
REGION void tsl9_selector_notifications_block_e67e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000162)); LIVE;
    PORT(".Lselector_notifications_edge_e682:\n.option push\n.option rvc\nc.bnez a5,.Lselector_notifications_edge_e682\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e742\n");
    __builtin_unreachable();
}

/* Original0xE684..0xE692. */
REGION void tsl9_selector_notifications_block_e684(void)
{
    REGS;
    a5 = a0 + UINT32_C(0xffffffc4); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\nli s2, 1\n.option pop\n");
    PORT(".Lselector_notifications_edge_e68e:\n.option push\n.option norvc\nbltu s2,a5,.Lselector_notifications_edge_e68e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE692..0xE69E. */
REGION void tsl9_selector_notifications_block_e692(void)
{
    REGS;
    a5 = a1 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lselector_notifications_edge_e69a:\n.option push\n.option norvc\nbltu s2,a5,.Lselector_notifications_edge_e69a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE69E..0xE6A2. */
REGION void tsl9_selector_notifications_block_e69e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e69e:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e69e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_d052\n");
    __builtin_unreachable();
}

/* Original0xE6A2..0xE6A8. */
REGION void tsl9_selector_notifications_block_e6a2(void)
{
    REGS;
    a5 = UINT32_C(0x00000004); LIVE;
    PORT(".Lselector_notifications_edge_e6a4:\n.option push\n.option norvc\nbne a0,a5,.Lselector_notifications_edge_e6a4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE6A8..0xE6B0. */
REGION void tsl9_selector_notifications_block_e6a8(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010b)); LIVE;
    PORT(".Lselector_notifications_edge_e6ac:\n.option push\n.option norvc\nbne a5,a0,.Lselector_notifications_edge_e6ac\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE6B0..0xE6B4. */
REGION void tsl9_selector_notifications_block_e6b0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6b0:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e6b0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_d662\n");
    __builtin_unreachable();
}

/* Original0xE6B4..0xE6B6. */
REGION void tsl9_selector_notifications_block_e6b4(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6b4:\n.option push\n.option rvc\nc.bnez a0,.Lselector_notifications_edge_e6b4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE6B6..0xE6C8. */
REGION void tsl9_selector_notifications_block_e6b6(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000160); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000005)); LIVE;
    a5 = a5 + UINT32_C(0xffffffff); LIVE;
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lselector_notifications_edge_e6c4:\n.option push\n.option norvc\nbleu a5,s2,.Lselector_notifications_edge_e6c4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e6ee\n");
    __builtin_unreachable();
}

/* Original0xE6C8..0xE6CE. */
REGION void tsl9_selector_notifications_block_e6c8(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e6ca:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e6ca\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_adb8\n");
    __builtin_unreachable();
}

/* Original0xE6CE..0xE6DC. */
REGION void tsl9_selector_notifications_block_e6ce(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lselector_notifications_edge_e6da:\n.option push\n.option rvc\nc.beqz a5,.Lselector_notifications_edge_e6da\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE6DC..0xE6E0. */
REGION void tsl9_selector_notifications_block_e6dc(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6dc:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e6dc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_abfc\n");
    __builtin_unreachable();
}

/* Original0xE6E0..0xE6E2. */
REGION void tsl9_selector_notifications_block_e6e0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6e0:\n.option push\n.option rvc\nc.beqz a0,.Lselector_notifications_edge_e6e0\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE6E2..0xE6EC. */
REGION void tsl9_selector_notifications_block_e6e2(void)
{
    REGS;
    a2 = UINT32_C(0x00000000); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lselector_notifications_edge_e6e8:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e6e8\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_dependency_external_d05c\n");
    __builtin_unreachable();
}

/* Original0xE6EC..0xE6EE. */
REGION void tsl9_selector_notifications_block_e6ec(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6ec:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e6ec\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE6EE..0xE6F2. */
REGION void tsl9_selector_notifications_block_e6ee(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6ee:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e6ee\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_leaf_entry_10402\n");
    __builtin_unreachable();
}

/* Original0xE6F2..0xE6F4. */
REGION void tsl9_selector_notifications_block_e6f2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6f2:\n.option push\n.option rvc\nc.bnez a0,.Lselector_notifications_edge_e6f2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e6c8\n");
    __builtin_unreachable();
}

/* Original0xE6F4..0xE6F8. */
REGION void tsl9_selector_notifications_block_e6f4(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6f4:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e6f4\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b6a8\n");
    __builtin_unreachable();
}

/* Original0xE6F8..0xE6FA. */
REGION void tsl9_selector_notifications_block_e6f8(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e6f8:\n.option push\n.option rvc\nc.bnez a0,.Lselector_notifications_edge_e6f8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE6FA..0xE700. */
REGION void tsl9_selector_notifications_block_e6fa(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010e)); LIVE;
    PORT(".Lselector_notifications_edge_e6fe:\n.option push\n.option rvc\nc.bnez a5,.Lselector_notifications_edge_e6fe\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE700..0xE706. */
REGION void tsl9_selector_notifications_block_e700(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_e702:\n.option push\n.option norvc\nbeq s1,a5,.Lselector_notifications_edge_e702\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e808\n");
    __builtin_unreachable();
}

/* Original0xE706..0xE70C. */
REGION void tsl9_selector_notifications_block_e706(void)
{
    REGS;
    a5 = UINT32_C(0x00000003); LIVE;
    PORT(".Lselector_notifications_edge_e708:\n.option push\n.option norvc\nbeq s1,a5,.Lselector_notifications_edge_e708\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e8d4\n");
    __builtin_unreachable();
}

/* Original0xE70C..0xE712. */
REGION void tsl9_selector_notifications_block_e70c(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e70e:\n.option push\n.option norvc\nbne s1,a5,.Lselector_notifications_edge_e70e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE712..0xE71A. */
REGION void tsl9_selector_notifications_block_e712(void)
{
    REGS;
    a5 = UINT32_C(0x00000034); LIVE;
    PORT(".Lselector_notifications_edge_e716:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e716\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e7f6\n");
    __builtin_unreachable();
}

/* Original0xE71A..0xE71E. */
REGION void tsl9_selector_notifications_block_e71a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e71a:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e71a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e788\n");
    __builtin_unreachable();
}

/* Original0xE71E..0xE724. */
REGION void tsl9_selector_notifications_block_e71e(void)
{
    REGS;
    a5 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lselector_notifications_edge_e720:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e720\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e7c4\n");
    __builtin_unreachable();
}

/* Original0xE724..0xE728. */
REGION void tsl9_selector_notifications_block_e724(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e724:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e724\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e770\n");
    __builtin_unreachable();
}

/* Original0xE728..0xE72E. */
REGION void tsl9_selector_notifications_block_e728(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lselector_notifications_edge_e72a:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e72a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e7cc\n");
    __builtin_unreachable();
}

/* Original0xE72E..0xE736. */
REGION void tsl9_selector_notifications_block_e72e(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010d)) = (uint8_t)0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010e)) = (uint8_t)0; LIVE;
    __builtin_unreachable();
}

/* Original0xE736..0xE742. */
REGION void tsl9_selector_notifications_block_e736(void)
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

/* Original0xE742..0xE750. */
REGION void tsl9_selector_notifications_block_e742(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000007)); LIVE;
    a5 = a5 & UINT32_C(0x00000008); LIVE;
    PORT(".Lselector_notifications_edge_e74e:\n.option push\n.option rvc\nc.beqz a5,.Lselector_notifications_edge_e74e\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE750..0xE756. */
REGION void tsl9_selector_notifications_block_e750(void)
{
    REGS;
    a5 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lselector_notifications_edge_e752:\n.option push\n.option norvc\nbne a0,a5,.Lselector_notifications_edge_e752\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE756..0xE75C. */
REGION void tsl9_selector_notifications_block_e756(void)
{
    REGS;
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e758:\n.option push\n.option norvc\nbne a1,a5,.Lselector_notifications_edge_e758\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE75C..0xE760. */
REGION void tsl9_selector_notifications_block_e75c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e75c:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e75c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_abfc\n");
    __builtin_unreachable();
}

/* Original0xE760..0xE762. */
REGION void tsl9_selector_notifications_block_e760(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e760:\n.option push\n.option rvc\nc.beqz a0,.Lselector_notifications_edge_e760\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE762..0xE768. */
REGION void tsl9_selector_notifications_block_e762(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x00000106)); LIVE;
    PORT(".Lselector_notifications_edge_e766:\n.option push\n.option rvc\nc.bnez a5,.Lselector_notifications_edge_e766\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE768..0xE76E. */
REGION void tsl9_selector_notifications_block_e768(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_edge_e76a:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e76a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_ab02\n");
    __builtin_unreachable();
}

/* Original0xE76E..0xE770. */
REGION void tsl9_selector_notifications_block_e76e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e76e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e76e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e6f4\n");
    __builtin_unreachable();
}

/* Original0xE770..0xE776. */
REGION void tsl9_selector_notifications_block_e770(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lselector_notifications_edge_e772:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e772\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e7c8\n");
    __builtin_unreachable();
}

/* Original0xE776..0xE782. */
REGION void tsl9_selector_notifications_block_e776(void)
{
    REGS;
    a5 = UINT32_C(0x00000033); LIVE;
    a0 = UINT32_C(0x000000b4); LIVE;
    PORT(".Lselector_notifications_edge_e77e:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e77e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE782..0xE786. */
REGION void tsl9_selector_notifications_block_e782(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e782:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e782\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE786..0xE788. */
REGION void tsl9_selector_notifications_block_e786(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e786:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e786\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE788..0xE790. */
REGION void tsl9_selector_notifications_block_e788(void)
{
    REGS;
    a5 = UINT32_C(0x00000036); LIVE;
    PORT(".Lselector_notifications_edge_e78c:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e78c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e802\n");
    __builtin_unreachable();
}

/* Original0xE790..0xE794. */
REGION void tsl9_selector_notifications_block_e790(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e790:\n.option push\n.option norvc\nbltu s0,a5,.Lselector_notifications_edge_e790\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e7fc\n");
    __builtin_unreachable();
}

/* Original0xE794..0xE79C. */
REGION void tsl9_selector_notifications_block_e794(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lselector_notifications_edge_e798:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e798\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e7f0\n");
    __builtin_unreachable();
}

/* Original0xE79C..0xE7A4. */
REGION void tsl9_selector_notifications_block_e79c(void)
{
    REGS;
    a5 = UINT32_C(0x00000044); LIVE;
    PORT(".Lselector_notifications_edge_e7a0:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e7a0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE7A4..0xE7B4. */
REGION void tsl9_selector_notifications_block_e7a4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lselector_notifications_edge_e7b2:\n.option push\n.option rvc\nc.beqz a5,.Lselector_notifications_edge_e7b2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e7be\n");
    __builtin_unreachable();
}

/* Original0xE7B4..0xE7BA. */
REGION void tsl9_selector_notifications_block_e7b4(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010c)); LIVE;
    PORT(".Lselector_notifications_edge_e7b8:\n.option push\n.option rvc\nc.bnez a5,.Lselector_notifications_edge_e7b8\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e7be\n");
    __builtin_unreachable();
}

/* Original0xE7BA..0xE7BE. */
REGION void tsl9_selector_notifications_block_e7ba(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e7ba:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e7ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc60\n");
    __builtin_unreachable();
}

/* Original0xE7BE..0xE7C4. */
REGION void tsl9_selector_notifications_block_e7be(void)
{
    REGS;
    a0 = UINT32_C(0x00000046); LIVE;
    PORT(".Lselector_notifications_edge_e7c2:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e7c2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE7C4..0xE7C8. */
REGION void tsl9_selector_notifications_block_e7c4(void)
{
    REGS;
    a0 = UINT32_C(0x0000001a); LIVE;
    PORT(".Lselector_notifications_edge_e7c6:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e7c6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE7C8..0xE7CC. */
REGION void tsl9_selector_notifications_block_e7c8(void)
{
    REGS;
    a0 = UINT32_C(0x00000015); LIVE;
    PORT(".Lselector_notifications_edge_e7ca:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e7ca\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE7CC..0xE7D0. */
REGION void tsl9_selector_notifications_block_e7cc(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e7cc:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e7cc\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_ccc2\n");
    __builtin_unreachable();
}

/* Original0xE7D0..0xE7E0. */
REGION void tsl9_selector_notifications_block_e7d0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = original_gp + UINT32_C(0x00000054); LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x00000006)); LIVE;
    a5 = a5 & UINT32_C(0x00000040); LIVE;
    PORT(".Lselector_notifications_edge_e7de:\n.option push\n.option rvc\nc.beqz a5,.Lselector_notifications_edge_e7de\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e7ea\n");
    __builtin_unreachable();
}

/* Original0xE7E0..0xE7E6. */
REGION void tsl9_selector_notifications_block_e7e0(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010c)); LIVE;
    PORT(".Lselector_notifications_edge_e7e4:\n.option push\n.option rvc\nc.bnez a5,.Lselector_notifications_edge_e7e4\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e7ea\n");
    __builtin_unreachable();
}

/* Original0xE7E6..0xE7EA. */
REGION void tsl9_selector_notifications_block_e7e6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e7e6:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e7e6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_cc60\n");
    __builtin_unreachable();
}

/* Original0xE7EA..0xE7F0. */
REGION void tsl9_selector_notifications_block_e7ea(void)
{
    REGS;
    a0 = UINT32_C(0x0000004c); LIVE;
    PORT(".Lselector_notifications_edge_e7ee:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e7ee\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE7F0..0xE7F6. */
REGION void tsl9_selector_notifications_block_e7f0(void)
{
    REGS;
    a0 = UINT32_C(0x0000003c); LIVE;
    PORT(".Lselector_notifications_edge_e7f4:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e7f4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE7F6..0xE7FC. */
REGION void tsl9_selector_notifications_block_e7f6(void)
{
    REGS;
    a0 = UINT32_C(0x000000b8); LIVE;
    PORT(".Lselector_notifications_edge_e7fa:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e7fa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE7FC..0xE802. */
REGION void tsl9_selector_notifications_block_e7fc(void)
{
    REGS;
    a0 = UINT32_C(0x000000bc); LIVE;
    PORT(".Lselector_notifications_edge_e800:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e800\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE802..0xE808. */
REGION void tsl9_selector_notifications_block_e802(void)
{
    REGS;
    a0 = UINT32_C(0x000000c0); LIVE;
    PORT(".Lselector_notifications_edge_e806:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e806\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE808..0xE816. */
REGION void tsl9_selector_notifications_block_e808(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s0, s0, -5\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s0, s0, 255\n.option pop\n");
    a5 = UINT32_C(0x00000052); LIVE;
    PORT(".Lselector_notifications_edge_e812:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e812\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE816..0xE828. */
REGION void tsl9_selector_notifications_block_e816(void)
{
    REGS;
    PORT(".Lselector_notifications_literal_e816:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_selector_notifications_table_1a1c8\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_e816\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s0, s0, 0x2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s0, s0, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 0(s0)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xE828..0xE82C. */
REGION void tsl9_selector_notifications_block_e828(void)
{
    REGS;
    a0 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_e82a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e82a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE82C..0xE832. */
REGION void tsl9_selector_notifications_block_e82c(void)
{
    REGS;
    a0 = UINT32_C(0x00000003); LIVE;
    PORT(".Lselector_notifications_edge_e82e:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e82e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE832..0xE838. */
REGION void tsl9_selector_notifications_block_e832(void)
{
    REGS;
    a0 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e834:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e834\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_ac78\n");
    __builtin_unreachable();
}

/* Original0xE838..0xE83A. */
REGION void tsl9_selector_notifications_block_e838(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e838:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e838\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE83A..0xE83E. */
REGION void tsl9_selector_notifications_block_e83a(void)
{
    REGS;
    a0 = UINT32_C(0x0000001b); LIVE;
    PORT(".Lselector_notifications_edge_e83c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e83c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE83E..0xE842. */
REGION void tsl9_selector_notifications_block_e83e(void)
{
    REGS;
    a0 = UINT32_C(0x00000016); LIVE;
    PORT(".Lselector_notifications_edge_e840:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e840\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE842..0xE848. */
REGION void tsl9_selector_notifications_block_e842(void)
{
    REGS;
    a0 = UINT32_C(0x0000004d); LIVE;
    PORT(".Lselector_notifications_edge_e846:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e846\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE848..0xE84E. */
REGION void tsl9_selector_notifications_block_e848(void)
{
    REGS;
    a0 = UINT32_C(0x00000047); LIVE;
    PORT(".Lselector_notifications_edge_e84c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e84c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE84E..0xE854. */
REGION void tsl9_selector_notifications_block_e84e(void)
{
    REGS;
    a0 = UINT32_C(0x0000003d); LIVE;
    PORT(".Lselector_notifications_edge_e852:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e852\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE854..0xE858. */
REGION void tsl9_selector_notifications_block_e854(void)
{
    REGS;
    a0 = UINT32_C(0x0000001e); LIVE;
    PORT(".Lselector_notifications_edge_e856:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e856\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE858..0xE85C. */
REGION void tsl9_selector_notifications_block_e858(void)
{
    REGS;
    a0 = UINT32_C(0x0000001f); LIVE;
    PORT(".Lselector_notifications_edge_e85a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e85a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE85C..0xE862. */
REGION void tsl9_selector_notifications_block_e85c(void)
{
    REGS;
    a0 = UINT32_C(0x00000020); LIVE;
    PORT(".Lselector_notifications_edge_e860:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e860\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE862..0xE868. */
REGION void tsl9_selector_notifications_block_e862(void)
{
    REGS;
    a0 = UINT32_C(0x00000021); LIVE;
    PORT(".Lselector_notifications_edge_e866:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e866\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE868..0xE86E. */
REGION void tsl9_selector_notifications_block_e868(void)
{
    REGS;
    a0 = UINT32_C(0x000000c8); LIVE;
    PORT(".Lselector_notifications_edge_e86c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e86c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE86E..0xE874. */
REGION void tsl9_selector_notifications_block_e86e(void)
{
    REGS;
    a0 = UINT32_C(0x000000c9); LIVE;
    PORT(".Lselector_notifications_edge_e872:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e872\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE874..0xE87A. */
REGION void tsl9_selector_notifications_block_e874(void)
{
    REGS;
    a0 = UINT32_C(0x000000ca); LIVE;
    PORT(".Lselector_notifications_edge_e878:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e878\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE87A..0xE880. */
REGION void tsl9_selector_notifications_block_e87a(void)
{
    REGS;
    a0 = UINT32_C(0x000000cb); LIVE;
    PORT(".Lselector_notifications_edge_e87e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e87e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE880..0xE884. */
REGION void tsl9_selector_notifications_block_e880(void)
{
    REGS;
    a0 = UINT32_C(0x00000009); LIVE;
    PORT(".Lselector_notifications_edge_e882:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e882\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE884..0xE888. */
REGION void tsl9_selector_notifications_block_e884(void)
{
    REGS;
    a0 = UINT32_C(0x00000008); LIVE;
    PORT(".Lselector_notifications_edge_e886:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e886\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE888..0xE88C. */
REGION void tsl9_selector_notifications_block_e888(void)
{
    REGS;
    a0 = UINT32_C(0x00000007); LIVE;
    PORT(".Lselector_notifications_edge_e88a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e88a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE88C..0xE890. */
REGION void tsl9_selector_notifications_block_e88c(void)
{
    REGS;
    a0 = UINT32_C(0x00000006); LIVE;
    PORT(".Lselector_notifications_edge_e88e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e88e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE890..0xE896. */
REGION void tsl9_selector_notifications_block_e890(void)
{
    REGS;
    a0 = UINT32_C(0x000000b5); LIVE;
    PORT(".Lselector_notifications_edge_e894:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e894\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE896..0xE89C. */
REGION void tsl9_selector_notifications_block_e896(void)
{
    REGS;
    a0 = UINT32_C(0x000000b9); LIVE;
    PORT(".Lselector_notifications_edge_e89a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e89a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE89C..0xE8A2. */
REGION void tsl9_selector_notifications_block_e89c(void)
{
    REGS;
    a0 = UINT32_C(0x000000bd); LIVE;
    PORT(".Lselector_notifications_edge_e8a0:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8a0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE8A2..0xE8A8. */
REGION void tsl9_selector_notifications_block_e8a2(void)
{
    REGS;
    a0 = UINT32_C(0x000000c1); LIVE;
    PORT(".Lselector_notifications_edge_e8a6:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8a6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE8A8..0xE8AE. */
REGION void tsl9_selector_notifications_block_e8a8(void)
{
    REGS;
    a0 = UINT32_C(0x00000026); LIVE;
    PORT(".Lselector_notifications_edge_e8ac:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8ac\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE8AE..0xE8B4. */
REGION void tsl9_selector_notifications_block_e8ae(void)
{
    REGS;
    a0 = UINT32_C(0x00000027); LIVE;
    PORT(".Lselector_notifications_edge_e8b2:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8b2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE8B4..0xE8BA. */
REGION void tsl9_selector_notifications_block_e8b4(void)
{
    REGS;
    a0 = UINT32_C(0x0000003a); LIVE;
    PORT(".Lselector_notifications_edge_e8b8:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8b8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE8BA..0xE8C0. */
REGION void tsl9_selector_notifications_block_e8ba(void)
{
    REGS;
    a0 = UINT32_C(0x0000003b); LIVE;
    PORT(".Lselector_notifications_edge_e8be:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8be\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE8C0..0xE8C4. */
REGION void tsl9_selector_notifications_block_e8c0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e8c0:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e8c0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_flow_external_8440\n");
    __builtin_unreachable();
}

/* Original0xE8C4..0xE8D2. */
REGION void tsl9_selector_notifications_block_e8c4(void)
{
    REGS;
    a0 = a0 ^ UINT32_C(0x00000001); LIVE;
    a1 = UINT32_C(0x00000001); LIVE;
    a0 = a0 & UINT32_C(0x000000ff); LIVE;
    PORT(".Lselector_notifications_edge_e8ce:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e8ce\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_17344\n");
    __builtin_unreachable();
}

/* Original0xE8D2..0xE8D4. */
REGION void tsl9_selector_notifications_block_e8d2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e8d2:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8d2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE8D4..0xE8DA. */
REGION void tsl9_selector_notifications_block_e8d4(void)
{
    REGS;
    a5 = UINT32_C(0x00000015); LIVE;
    PORT(".Lselector_notifications_edge_e8d6:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e8d6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e940\n");
    __builtin_unreachable();
}

/* Original0xE8DA..0xE8DE. */
REGION void tsl9_selector_notifications_block_e8da(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e8da:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e8da\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e906\n");
    __builtin_unreachable();
}

/* Original0xE8DE..0xE8E4. */
REGION void tsl9_selector_notifications_block_e8de(void)
{
    REGS;
    a5 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lselector_notifications_edge_e8e0:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e8e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e932\n");
    __builtin_unreachable();
}

/* Original0xE8E4..0xE8E8. */
REGION void tsl9_selector_notifications_block_e8e4(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e8e4:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e8e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e8f4\n");
    __builtin_unreachable();
}

/* Original0xE8E8..0xE8F2. */
REGION void tsl9_selector_notifications_block_e8e8(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    a0 = UINT32_C(0x0000004e); LIVE;
    PORT(".Lselector_notifications_edge_e8ee:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e8ee\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE8F2..0xE8F4. */
REGION void tsl9_selector_notifications_block_e8f2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e8f2:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e8f2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE8F4..0xE8FA. */
REGION void tsl9_selector_notifications_block_e8f4(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lselector_notifications_edge_e8f6:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e8f6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e936\n");
    __builtin_unreachable();
}

/* Original0xE8FA..0xE904. */
REGION void tsl9_selector_notifications_block_e8fa(void)
{
    REGS;
    a5 = UINT32_C(0x00000013); LIVE;
    a0 = UINT32_C(0x00000042); LIVE;
    PORT(".Lselector_notifications_edge_e900:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e900\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE904..0xE906. */
REGION void tsl9_selector_notifications_block_e904(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e904:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e904\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE906..0xE90C. */
REGION void tsl9_selector_notifications_block_e906(void)
{
    REGS;
    a5 = UINT32_C(0x00000019); LIVE;
    PORT(".Lselector_notifications_edge_e908:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e908\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e946\n");
    __builtin_unreachable();
}

/* Original0xE90C..0xE910. */
REGION void tsl9_selector_notifications_block_e90c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e90c:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e90c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e91c\n");
    __builtin_unreachable();
}

/* Original0xE910..0xE91A. */
REGION void tsl9_selector_notifications_block_e910(void)
{
    REGS;
    a5 = UINT32_C(0x00000017); LIVE;
    a0 = UINT32_C(0x00000044); LIVE;
    PORT(".Lselector_notifications_edge_e916:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e916\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE91A..0xE91C. */
REGION void tsl9_selector_notifications_block_e91a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e91a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e91a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE91C..0xE924. */
REGION void tsl9_selector_notifications_block_e91c(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lselector_notifications_edge_e920:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e920\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e93a\n");
    __builtin_unreachable();
}

/* Original0xE924..0xE930. */
REGION void tsl9_selector_notifications_block_e924(void)
{
    REGS;
    a5 = UINT32_C(0x00000044); LIVE;
    a0 = UINT32_C(0x00000048); LIVE;
    PORT(".Lselector_notifications_edge_e92c:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e92c\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE930..0xE932. */
REGION void tsl9_selector_notifications_block_e930(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e930:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e930\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e72e\n");
    __builtin_unreachable();
}

/* Original0xE932..0xE936. */
REGION void tsl9_selector_notifications_block_e932(void)
{
    REGS;
    a0 = UINT32_C(0x0000001c); LIVE;
    PORT(".Lselector_notifications_edge_e934:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e934\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE936..0xE93A. */
REGION void tsl9_selector_notifications_block_e936(void)
{
    REGS;
    a0 = UINT32_C(0x00000017); LIVE;
    PORT(".Lselector_notifications_edge_e938:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e938\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE93A..0xE940. */
REGION void tsl9_selector_notifications_block_e93a(void)
{
    REGS;
    a0 = UINT32_C(0x0000003e); LIVE;
    PORT(".Lselector_notifications_edge_e93e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e93e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE940..0xE946. */
REGION void tsl9_selector_notifications_block_e940(void)
{
    REGS;
    a0 = UINT32_C(0x00000043); LIVE;
    PORT(".Lselector_notifications_edge_e944:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e944\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE946..0xE94C. */
REGION void tsl9_selector_notifications_block_e946(void)
{
    REGS;
    a0 = UINT32_C(0x00000045); LIVE;
    PORT(".Lselector_notifications_edge_e94a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e94a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e782\n");
    __builtin_unreachable();
}

/* Original0xE94C..0xE950. */
REGION void tsl9_selector_notifications_block_e94c(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e94c:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e94c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_b664\n");
    __builtin_unreachable();
}

/* Original0xE950..0xE952. */
REGION void tsl9_selector_notifications_block_e950(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e950:\n.option push\n.option rvc\nc.bnez a0,.Lselector_notifications_edge_e950\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xE952..0xE958. */
REGION void tsl9_selector_notifications_block_e952(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010d)); LIVE;
    PORT(".Lselector_notifications_edge_e956:\n.option push\n.option rvc\nc.bnez a5,.Lselector_notifications_edge_e956\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xE958..0xE964. */
REGION void tsl9_selector_notifications_block_e958(void)
{
    REGS;
    PORT(".option push\n.option rvc\naddi s1, s1, -1\n.option pop\n");
    PORT(".option push\n.option norvc\nandi s1, s1, 255\n.option pop\n");
    a5 = UINT32_C(0x00000009); LIVE;
    PORT(".Lselector_notifications_edge_e960:\n.option push\n.option norvc\nbltu a5,s1,.Lselector_notifications_edge_e960\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xE964..0xE976. */
REGION void tsl9_selector_notifications_block_e964(void)
{
    REGS;
    PORT(".Lselector_notifications_literal_e964:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_selector_notifications_table_1a314\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_e964\n.option pop\n");
    PORT(".option push\n.option rvc\nslli s1, s1, 0x2\n.option pop\n");
    PORT(".option push\n.option rvc\nadd s1, s1, a4\n.option pop\n");
    PORT(".option push\n.option rvc\nlw a5, 0(s1)\n.option pop\n");
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xE976..0xE97E. */
REGION void tsl9_selector_notifications_block_e976(void)
{
    REGS;
    a5 = UINT32_C(0x00000036); LIVE;
    PORT(".Lselector_notifications_edge_e97a:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e97a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea46\n");
    __builtin_unreachable();
}

/* Original0xE97E..0xE982. */
REGION void tsl9_selector_notifications_block_e97e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e97e:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e97e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e9dc\n");
    __builtin_unreachable();
}

/* Original0xE982..0xE988. */
REGION void tsl9_selector_notifications_block_e982(void)
{
    REGS;
    a5 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lselector_notifications_edge_e984:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e984\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea1a\n");
    __builtin_unreachable();
}

/* Original0xE988..0xE98C. */
REGION void tsl9_selector_notifications_block_e988(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e988:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e988\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e9be\n");
    __builtin_unreachable();
}

/* Original0xE98C..0xE992. */
REGION void tsl9_selector_notifications_block_e98c(void)
{
    REGS;
    a5 = UINT32_C(0x00000008); LIVE;
    PORT(".Lselector_notifications_edge_e98e:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e98e\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea1e\n");
    __builtin_unreachable();
}

/* Original0xE992..0xE99A. */
REGION void tsl9_selector_notifications_block_e992(void)
{
    REGS;
    a5 = UINT32_C(0x0000000e); LIVE;
    a0 = UINT32_C(0x0000001d); LIVE;
    PORT(".Lselector_notifications_edge_e996:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e996\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xE99A..0xE9AC. */
REGION void tsl9_selector_notifications_block_e99a(void)
{
    REGS;
    register uintptr_t original_gp __asm__("gp");
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010d)) = (uint8_t)0; LIVE;
    __asm__ volatile("":"=r"(original_gp)::"memory");
    *(volatile uint8_t *)(uintptr_t)(original_gp + UINT32_C(0x0000010e)) = (uint8_t)0; LIVE;
    PORT(".option push\n.option norvc\naddi s0, s0, -60\n.option pop\n");
    a5 = UINT32_C(0x00000001); LIVE;
    PORT(".Lselector_notifications_edge_e9a8:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e9a8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e736\n");
    __builtin_unreachable();
}

/* Original0xE9AC..0xE9B0. */
REGION void tsl9_selector_notifications_block_e9ac(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e9ac:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e9ac\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_rom_driver_entry_171de\n");
    __builtin_unreachable();
}

/* Original0xE9B0..0xE9BE. */
REGION void tsl9_selector_notifications_block_e9b0(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lselector_notifications_edge_e9ba:\n.option push\n.option norvc\njal zero,.Lselector_notifications_edge_e9ba\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_output_builder_provider_9fc8\n");
    __builtin_unreachable();
}

/* Original0xE9BE..0xE9C6. */
REGION void tsl9_selector_notifications_block_e9be(void)
{
    REGS;
    a5 = UINT32_C(0x00000034); LIVE;
    PORT(".Lselector_notifications_edge_e9c2:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e9c2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea3a\n");
    __builtin_unreachable();
}

/* Original0xE9C6..0xE9CA. */
REGION void tsl9_selector_notifications_block_e9c6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e9c6:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e9c6\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea40\n");
    __builtin_unreachable();
}

/* Original0xE9CA..0xE9D6. */
REGION void tsl9_selector_notifications_block_e9ca(void)
{
    REGS;
    a5 = UINT32_C(0x00000033); LIVE;
    a0 = UINT32_C(0x000000b6); LIVE;
    PORT(".Lselector_notifications_edge_e9d2:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_e9d2\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xE9D6..0xE9DA. */
REGION void tsl9_selector_notifications_block_e9d6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e9d6:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_e9d6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xE9DA..0xE9DC. */
REGION void tsl9_selector_notifications_block_e9da(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e9da:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_e9da\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xE9DC..0xE9E4. */
REGION void tsl9_selector_notifications_block_e9dc(void)
{
    REGS;
    a5 = UINT32_C(0x00000047); LIVE;
    PORT(".Lselector_notifications_edge_e9e0:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e9e0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea2a\n");
    __builtin_unreachable();
}

/* Original0xE9E4..0xE9E8. */
REGION void tsl9_selector_notifications_block_e9e4(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e9e4:\n.option push\n.option norvc\nbltu a5,s0,.Lselector_notifications_edge_e9e4\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea02\n");
    __builtin_unreachable();
}

/* Original0xE9E8..0xE9F0. */
REGION void tsl9_selector_notifications_block_e9e8(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lselector_notifications_edge_e9ec:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e9ec\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea24\n");
    __builtin_unreachable();
}

/* Original0xE9F0..0xE9F4. */
REGION void tsl9_selector_notifications_block_e9f0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_e9f0:\n.option push\n.option norvc\nbltu s0,a5,.Lselector_notifications_edge_e9f0\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea36\n");
    __builtin_unreachable();
}

/* Original0xE9F4..0xEA00. */
REGION void tsl9_selector_notifications_block_e9f4(void)
{
    REGS;
    a5 = UINT32_C(0x00000044); LIVE;
    a0 = UINT32_C(0x00000049); LIVE;
    PORT(".Lselector_notifications_edge_e9fc:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_e9fc\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA00..0xEA02. */
REGION void tsl9_selector_notifications_block_ea00(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_ea00:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea00\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEA02..0xEA0A. */
REGION void tsl9_selector_notifications_block_ea02(void)
{
    REGS;
    a5 = UINT32_C(0x00000049); LIVE;
    PORT(".Lselector_notifications_edge_ea06:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_ea06\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea32\n");
    __builtin_unreachable();
}

/* Original0xEA0A..0xEA0E. */
REGION void tsl9_selector_notifications_block_ea0a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_ea0a:\n.option push\n.option norvc\nbltu s0,a5,.Lselector_notifications_edge_ea0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_ea2e\n");
    __builtin_unreachable();
}

/* Original0xEA0E..0xEA18. */
REGION void tsl9_selector_notifications_block_ea0e(void)
{
    REGS;
    a5 = UINT32_C(0x0000004a); LIVE;
    a0 = UINT32_C(0x00000010); LIVE;
    PORT(".Lselector_notifications_edge_ea14:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_ea14\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA18..0xEA1A. */
REGION void tsl9_selector_notifications_block_ea18(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_ea18:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea18\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEA1A..0xEA1E. */
REGION void tsl9_selector_notifications_block_ea1a(void)
{
    REGS;
    a0 = UINT32_C(0x00000018); LIVE;
    PORT(".Lselector_notifications_edge_ea1c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea1c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA1E..0xEA22. */
REGION void tsl9_selector_notifications_block_ea1e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_ea1e:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_ea1e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_ccf6\n");
    __builtin_unreachable();
}

/* Original0xEA22..0xEA24. */
REGION void tsl9_selector_notifications_block_ea22(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_ea22:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea22\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEA24..0xEA2A. */
REGION void tsl9_selector_notifications_block_ea24(void)
{
    REGS;
    a0 = UINT32_C(0x0000003f); LIVE;
    PORT(".Lselector_notifications_edge_ea28:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea28\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA2A..0xEA2E. */
REGION void tsl9_selector_notifications_block_ea2a(void)
{
    REGS;
    a0 = UINT32_C(0x0000000a); LIVE;
    PORT(".Lselector_notifications_edge_ea2c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea2c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA2E..0xEA32. */
REGION void tsl9_selector_notifications_block_ea2e(void)
{
    REGS;
    a0 = UINT32_C(0x0000000c); LIVE;
    PORT(".Lselector_notifications_edge_ea30:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea30\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA32..0xEA36. */
REGION void tsl9_selector_notifications_block_ea32(void)
{
    REGS;
    a0 = UINT32_C(0x0000000e); LIVE;
    PORT(".Lselector_notifications_edge_ea34:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea34\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA36..0xEA3A. */
REGION void tsl9_selector_notifications_block_ea36(void)
{
    REGS;
    a0 = UINT32_C(0x00000014); LIVE;
    PORT(".Lselector_notifications_edge_ea38:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea38\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA3A..0xEA40. */
REGION void tsl9_selector_notifications_block_ea3a(void)
{
    REGS;
    a0 = UINT32_C(0x000000ba); LIVE;
    PORT(".Lselector_notifications_edge_ea3e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea3e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA40..0xEA46. */
REGION void tsl9_selector_notifications_block_ea40(void)
{
    REGS;
    a0 = UINT32_C(0x000000be); LIVE;
    PORT(".Lselector_notifications_edge_ea44:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea44\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA46..0xEA4C. */
REGION void tsl9_selector_notifications_block_ea46(void)
{
    REGS;
    a0 = UINT32_C(0x000000c2); LIVE;
    PORT(".Lselector_notifications_edge_ea4a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea4a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA4C..0xEA5C. */
REGION void tsl9_selector_notifications_block_ea4c(void)
{
    REGS;
    PORT(".option push\n.option norvc\naddi a5, s0, -14\n.option pop\n");
    a5 = a5 & UINT32_C(0x000000ff); LIVE;
    a4 = UINT32_C(0x0000003c); LIVE;
    PORT(".Lselector_notifications_edge_ea58:\n.option push\n.option norvc\nbltu a4,a5,.Lselector_notifications_edge_ea58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEA5C..0xEA6E. */
REGION void tsl9_selector_notifications_block_ea5c(void)
{
    REGS;
    PORT(".Lselector_notifications_literal_ea5c:\n.option push\n.option norvc\nauipc a4,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_selector_notifications_table_1a33c\naddi a4,a4,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_ea5c\n.option pop\n");
    a5 = a5 << UINT32_C(0x00000002); LIVE;
    a5 = a5 + a4; LIVE;
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a5 = a5 + a4; LIVE;
    PORT(".option push\n.option rvc\njr a5\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEA6E..0xEA74. */
REGION void tsl9_selector_notifications_block_ea6e(void)
{
    REGS;
    a0 = UINT32_C(0x0000004f); LIVE;
    PORT(".Lselector_notifications_edge_ea72:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea72\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA74..0xEA78. */
REGION void tsl9_selector_notifications_block_ea74(void)
{
    REGS;
    a0 = UINT32_C(0x00000019); LIVE;
    PORT(".Lselector_notifications_edge_ea76:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea76\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA78..0xEA7E. */
REGION void tsl9_selector_notifications_block_ea78(void)
{
    REGS;
    a0 = UINT32_C(0x00000041); LIVE;
    PORT(".Lselector_notifications_edge_ea7c:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea7c\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA7E..0xEA84. */
REGION void tsl9_selector_notifications_block_ea7e(void)
{
    REGS;
    a0 = UINT32_C(0x0000004b); LIVE;
    PORT(".Lselector_notifications_edge_ea82:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea82\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA84..0xEA88. */
REGION void tsl9_selector_notifications_block_ea84(void)
{
    REGS;
    a0 = UINT32_C(0x0000000b); LIVE;
    PORT(".Lselector_notifications_edge_ea86:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea86\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA88..0xEA8C. */
REGION void tsl9_selector_notifications_block_ea88(void)
{
    REGS;
    a0 = UINT32_C(0x0000000d); LIVE;
    PORT(".Lselector_notifications_edge_ea8a:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea8a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA8C..0xEA90. */
REGION void tsl9_selector_notifications_block_ea8c(void)
{
    REGS;
    a0 = UINT32_C(0x0000000f); LIVE;
    PORT(".Lselector_notifications_edge_ea8e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea8e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA90..0xEA94. */
REGION void tsl9_selector_notifications_block_ea90(void)
{
    REGS;
    a0 = UINT32_C(0x00000011); LIVE;
    PORT(".Lselector_notifications_edge_ea92:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea92\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA94..0xEA9A. */
REGION void tsl9_selector_notifications_block_ea94(void)
{
    REGS;
    a0 = UINT32_C(0x00000022); LIVE;
    PORT(".Lselector_notifications_edge_ea98:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea98\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEA9A..0xEAA0. */
REGION void tsl9_selector_notifications_block_ea9a(void)
{
    REGS;
    a0 = UINT32_C(0x00000023); LIVE;
    PORT(".Lselector_notifications_edge_ea9e:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ea9e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAA0..0xEAA6. */
REGION void tsl9_selector_notifications_block_eaa0(void)
{
    REGS;
    a0 = UINT32_C(0x00000024); LIVE;
    PORT(".Lselector_notifications_edge_eaa4:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eaa4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAA6..0xEAAC. */
REGION void tsl9_selector_notifications_block_eaa6(void)
{
    REGS;
    a0 = UINT32_C(0x00000025); LIVE;
    PORT(".Lselector_notifications_edge_eaaa:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eaaa\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAAC..0xEAB2. */
REGION void tsl9_selector_notifications_block_eaac(void)
{
    REGS;
    a0 = UINT32_C(0x000000cc); LIVE;
    PORT(".Lselector_notifications_edge_eab0:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eab0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAB2..0xEAB8. */
REGION void tsl9_selector_notifications_block_eab2(void)
{
    REGS;
    a0 = UINT32_C(0x000000cd); LIVE;
    PORT(".Lselector_notifications_edge_eab6:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eab6\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAB8..0xEABE. */
REGION void tsl9_selector_notifications_block_eab8(void)
{
    REGS;
    a0 = UINT32_C(0x000000ce); LIVE;
    PORT(".Lselector_notifications_edge_eabc:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eabc\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEABE..0xEAC4. */
REGION void tsl9_selector_notifications_block_eabe(void)
{
    REGS;
    a0 = UINT32_C(0x000000cf); LIVE;
    PORT(".Lselector_notifications_edge_eac2:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eac2\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAC4..0xEACA. */
REGION void tsl9_selector_notifications_block_eac4(void)
{
    REGS;
    a0 = UINT32_C(0x000000b7); LIVE;
    PORT(".Lselector_notifications_edge_eac8:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eac8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEACA..0xEAD0. */
REGION void tsl9_selector_notifications_block_eaca(void)
{
    REGS;
    a0 = UINT32_C(0x000000bb); LIVE;
    PORT(".Lselector_notifications_edge_eace:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eace\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAD0..0xEAD6. */
REGION void tsl9_selector_notifications_block_ead0(void)
{
    REGS;
    a0 = UINT32_C(0x000000bf); LIVE;
    PORT(".Lselector_notifications_edge_ead4:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_ead4\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEAD6..0xEADC. */
REGION void tsl9_selector_notifications_block_ead6(void)
{
    REGS;
    a0 = UINT32_C(0x000000c3); LIVE;
    PORT(".Lselector_notifications_edge_eada:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eada\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e9d6\n");
    __builtin_unreachable();
}

/* Original0xEADC..0xEAE2. */
REGION void tsl9_selector_notifications_block_eadc(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_eade:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_eade\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEAE2..0xEAE6. */
REGION void tsl9_selector_notifications_block_eae2(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eae2:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eae2\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_1316a\n");
    __builtin_unreachable();
}

/* Original0xEAE6..0xEAEA. */
REGION void tsl9_selector_notifications_block_eae6(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eae6:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eae6\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12e86\n");
    __builtin_unreachable();
}

/* Original0xEAEA..0xEAEE. */
REGION void tsl9_selector_notifications_block_eaea(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eaea:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eaea\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_init_external_12f18\n");
    __builtin_unreachable();
}

/* Original0xEAEE..0xEB02. */
REGION void tsl9_selector_notifications_block_eaee(void)
{
    REGS;
    a2 = UINT32_C(0x00000064); LIVE;
    PORT(".Lselector_notifications_literal_eaf2:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_99e8\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_eaf2\n.option pop\n");
    PORT(".Lselector_notifications_literal_eafa:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_954e\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_eafa\n.option pop\n");
    __builtin_unreachable();
}

/* Original0xEB02..0xEB06. */
REGION void tsl9_selector_notifications_block_eb02(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eb02:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eb02\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_94ee\n");
    __builtin_unreachable();
}

/* Original0xEB06..0xEB08. */
REGION void tsl9_selector_notifications_block_eb06(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eb06:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eb06\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEB08..0xEB0E. */
REGION void tsl9_selector_notifications_block_eb08(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_eb0a:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_eb0a\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEB0E..0xEB24. */
REGION void tsl9_selector_notifications_block_eb0e(void)
{
    REGS;
    a2 = UINT32_C(0x000003e8); LIVE;
    PORT(".Lselector_notifications_literal_eb12:\n.option push\n.option norvc\nauipc a1,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_ota_external_99e8\naddi a1,a1,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_eb12\n.option pop\n");
    PORT(".Lselector_notifications_literal_eb1a:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_95bc\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_eb1a\n.option pop\n");
    PORT(".Lselector_notifications_edge_eb22:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eb22\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_eb02\n");
    __builtin_unreachable();
}

/* Original0xEB24..0xEB2A. */
REGION void tsl9_selector_notifications_block_eb24(void)
{
    REGS;
    a5 = UINT32_C(0x00000002); LIVE;
    PORT(".Lselector_notifications_edge_eb26:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_eb26\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEB2A..0xEB2E. */
REGION void tsl9_selector_notifications_block_eb2a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eb2a:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eb2a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_main_runtime_external_9334\n");
    __builtin_unreachable();
}

/* Original0xEB2E..0xEB32. */
REGION void tsl9_selector_notifications_block_eb2e(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eb2e:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eb2e\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_9ef0\n");
    __builtin_unreachable();
}

/* Original0xEB32..0xEB38. */
REGION void tsl9_selector_notifications_block_eb32(void)
{
    REGS;
    a0 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_edge_eb34:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eb34\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_record_dispatch_provider_96a2\n");
    __builtin_unreachable();
}

/* Original0xEB38..0xEB3A. */
REGION void tsl9_selector_notifications_block_eb38(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eb38:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eb38\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_e99a\n");
    __builtin_unreachable();
}

/* Original0xEB3A..0xEB4C. */
REGION void tsl9_selector_notifications_block_eb3a(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a0 = UINT32_C(0x000000ff); LIVE;
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lselector_notifications_edge_eb48:\n.option push\n.option norvc\njal zero,.Lselector_notifications_edge_eb48\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_dependencies_provider_155d0\n");
    __builtin_unreachable();
}

/* Original0xEB4C..0xEB54. */
REGION void tsl9_selector_notifications_block_eb4c(void)
{
    REGS;
    a0 = UINT32_C(0x000000ff); LIVE;
    PORT(".Lselector_notifications_edge_eb50:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eb50\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_dependencies_provider_155d0\n");
    __builtin_unreachable();
}

/* Original0xEB54..0xEB5C. */
REGION void tsl9_selector_notifications_block_eb54(void)
{
    REGS;
    a5 = UINT32_C(0x00000038); LIVE;
    PORT(".Lselector_notifications_edge_eb58:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_eb58\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_eba0\n");
    __builtin_unreachable();
}

/* Original0xEB5C..0xEB64. */
REGION void tsl9_selector_notifications_block_eb5c(void)
{
    REGS;
    a5 = UINT32_C(0x00000044); LIVE;
    PORT(".Lselector_notifications_edge_eb60:\n.option push\n.option norvc\nbeq s0,a5,.Lselector_notifications_edge_eb60\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_eb8a\n");
    __builtin_unreachable();
}

/* Original0xEB64..0xEB6C. */
REGION void tsl9_selector_notifications_block_eb64(void)
{
    REGS;
    a5 = UINT32_C(0x00000037); LIVE;
    PORT(".Lselector_notifications_edge_eb68:\n.option push\n.option norvc\nbne s0,a5,.Lselector_notifications_edge_eb68\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_selector_notifications_block_e736\n");
    __builtin_unreachable();
}

/* Original0xEB6C..0xEB8A. */
REGION void tsl9_selector_notifications_block_eb6c(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    a3 = UINT32_C(0x00000000); LIVE;
    a2 = UINT32_C(0x000000c8); LIVE;
    a1 = UINT32_C(0x00000000); LIVE;
    PORT(".Lselector_notifications_literal_eb7c:\n.option push\n.option norvc\nauipc a0,0\n.reloc .-4,R_RISCV_PCREL_HI20,tsl9_record_dispatch_provider_fe08\naddi a0,a0,0\n.reloc .-4,R_RISCV_PCREL_LO12_I,.Lselector_notifications_literal_eb7c\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lselector_notifications_edge_eb86:\n.option push\n.option norvc\njal zero,.Lselector_notifications_edge_eb86\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_callback_external_9124\n");
    __builtin_unreachable();
}

/* Original0xEB8A..0xEB8E. */
REGION void tsl9_selector_notifications_block_eb8a(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eb8a:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eb8a\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_ccc2\n");
    __builtin_unreachable();
}

/* Original0xEB8E..0xEB92. */
REGION void tsl9_selector_notifications_block_eb8e(void)
{
    REGS;
    a0 = UINT32_C(0x0000004a); LIVE;
    __builtin_unreachable();
}

/* Original0xEB92..0xEBA0. */
REGION void tsl9_selector_notifications_block_eb92(void)
{
    REGS;
    PORT(".option push\n.option rvc\nlw s0, 8(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw ra, 12(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s1, 4(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\nlw s2, 0(sp)\n.option pop\n");
    PORT(".option push\n.option rvc\naddi sp, sp, 16\n.option pop\n");
    PORT(".Lselector_notifications_edge_eb9c:\n.option push\n.option norvc\njal zero,.Lselector_notifications_edge_eb9c\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_state_controls_provider_167a6\n");
    __builtin_unreachable();
}

/* Original0xEBA0..0xEBA4. */
REGION void tsl9_selector_notifications_block_eba0(void)
{
    REGS;
    PORT(".Lselector_notifications_edge_eba0:\n.option push\n.option norvc\njal ra,.Lselector_notifications_edge_eba0\n.option pop\n.reloc .-4,R_RISCV_JAL,tsl9_selector_notifications_provider_c364\n");
    __builtin_unreachable();
}

/* Original0xEBA4..0xEBAA. */
REGION void tsl9_selector_notifications_block_eba4(void)
{
    REGS;
    a0 = UINT32_C(0x00000040); LIVE;
    PORT(".Lselector_notifications_edge_eba8:\n.option push\n.option rvc\nc.j .Lselector_notifications_edge_eba8\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_selector_notifications_block_eb92\n");
    __builtin_unreachable();
}

/* Original0xEBAA..0xEBAC. */
REGION void tsl9_selector_notifications_block_ebaa(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

#if defined(__cplusplus)
#define TABLE_DATA(section_name) extern "C" __attribute__((used,section(section_name),aligned(4)))
#else
#define TABLE_DATA(section_name) __attribute__((used,section(section_name),aligned(4)))
#endif
TABLE_DATA(".rodata.tsl9_selector_notifications_table_1a13c") const uint8_t tsl9_selector_notifications_table_1a13c[20] = {0x0a, 0x41, 0xff, 0xff, 0xfe, 0x49, 0xff, 0xff, 0x42, 0x45, 0xff, 0xff, 0x10, 0x48, 0xff, 0xff, 0x10, 0x4a, 0xff, 0xff};
TABLE_DATA(".rodata.tsl9_selector_notifications_table_1a150") const uint8_t tsl9_selector_notifications_table_1a150[120] = {0xbe, 0x41, 0xff, 0xff, 0xc6, 0x41, 0xff, 0xff, 0xca, 0x41, 0xff, 0xff, 0xd2, 0x41, 0xff, 0xff, 0xd8, 0x41, 0xff, 0xff, 0xdc, 0x41, 0xff, 0xff, 0xe0, 0x41, 0xff, 0xff, 0xe6, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0xa0, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x38, 0x41, 0xff, 0xff, 0x30, 0x41, 0xff, 0xff, 0x9a, 0x41, 0xff, 0xff};
TABLE_DATA(".rodata.tsl9_selector_notifications_table_1a1c8") const uint8_t tsl9_selector_notifications_table_1a1c8[332] = {0x60, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x7a, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x64, 0x46, 0xff, 0xff, 0x72, 0x46, 0xff, 0xff, 0x76, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0xe0, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0xe6, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0xec, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0xf2, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x8c, 0x46, 0xff, 0xff, 0x90, 0x46, 0xff, 0xff, 0x94, 0x46, 0xff, 0xff, 0x9a, 0x46, 0xff, 0xff, 0xa0, 0x46, 0xff, 0xff, 0xa6, 0x46, 0xff, 0xff, 0xac, 0x46, 0xff, 0xff, 0xb2, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0xc8, 0x46, 0xff, 0xff, 0xce, 0x46, 0xff, 0xff, 0xd4, 0x46, 0xff, 0xff, 0xda, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x86, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x80, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0xb8, 0x46, 0xff, 0xff, 0xbc, 0x46, 0xff, 0xff, 0xc0, 0x46, 0xff, 0xff, 0xc4, 0x46, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0x66, 0x45, 0xff, 0xff, 0xf8, 0x46, 0xff, 0xff};
TABLE_DATA(".rodata.tsl9_selector_notifications_table_1a314") const uint8_t tsl9_selector_notifications_table_1a314[40] = {0x62, 0x46, 0xff, 0xff, 0x38, 0x47, 0xff, 0xff, 0x86, 0x46, 0xff, 0xff, 0xc8, 0x47, 0xff, 0xff, 0x86, 0x46, 0xff, 0xff, 0xf4, 0x47, 0xff, 0xff, 0x86, 0x46, 0xff, 0xff, 0x86, 0x46, 0xff, 0xff, 0x86, 0x46, 0xff, 0xff, 0x10, 0x48, 0xff, 0xff};
TABLE_DATA(".rodata.tsl9_selector_notifications_table_1a33c") const uint8_t tsl9_selector_notifications_table_1a33c[244] = {0x32, 0x47, 0xff, 0xff, 0x38, 0x47, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x58, 0x47, 0xff, 0xff, 0x5e, 0x47, 0xff, 0xff, 0x64, 0x47, 0xff, 0xff, 0x6a, 0x47, 0xff, 0xff, 0x70, 0x47, 0xff, 0xff, 0x76, 0x47, 0xff, 0xff, 0x7c, 0x47, 0xff, 0xff, 0x82, 0x47, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x88, 0x47, 0xff, 0xff, 0x8e, 0x47, 0xff, 0xff, 0x94, 0x47, 0xff, 0xff, 0x9a, 0x47, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x3c, 0x47, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x42, 0x47, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x5e, 0x46, 0xff, 0xff, 0x48, 0x47, 0xff, 0xff, 0x4c, 0x47, 0xff, 0xff, 0x50, 0x47, 0xff, 0xff, 0x54, 0x47, 0xff, 0xff};
