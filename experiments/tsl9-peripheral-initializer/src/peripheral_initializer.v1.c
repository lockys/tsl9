#include <stdint.h>
#include <stddef.h>
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

/* One complete original peripheral initializer:242B/99i. Register-bound C
 * unsigned arithmetic and fresh volatile accesses retain original data flow.
 * Explicit ports preserve stack/RA/S registers,indirect calls,ISA DIVU/REMU
 * and original branch/call/literal roles. All regions require original layout.
 * ROM slot semantics,units,physical RAM/IRQ/radio/OTA remain unproved. */

/* Original descriptor reads are typed here; this is a compile-time RV32
 * layout assertion, not proof of installed hardware or ROM ABI. */
typedef struct {
    uint16_t divider;
    uint8_t timing_shift30;
    uint8_t timing_shift24;
    uint8_t timing_shift16;
    uint8_t timing_shift20;
    uint8_t unread_reserved[2];
    uint32_t control_bits_7_to_2[6];
} tsl9_original_peripheral_descriptor;
#ifdef __cplusplus
#define DESCRIPTOR_ASSERT static_assert
#else
#define DESCRIPTOR_ASSERT _Static_assert
#endif
DESCRIPTOR_ASSERT(sizeof(tsl9_original_peripheral_descriptor)==32,"Original descriptor extent");
DESCRIPTOR_ASSERT(offsetof(tsl9_original_peripheral_descriptor,divider)==0,"Original halfword");
DESCRIPTOR_ASSERT(offsetof(tsl9_original_peripheral_descriptor,timing_shift30)==2,"Original byte2");
DESCRIPTOR_ASSERT(offsetof(tsl9_original_peripheral_descriptor,timing_shift24)==3,"Original byte3");
DESCRIPTOR_ASSERT(offsetof(tsl9_original_peripheral_descriptor,timing_shift16)==4,"Original byte4");
DESCRIPTOR_ASSERT(offsetof(tsl9_original_peripheral_descriptor,timing_shift20)==5,"Original byte5");
DESCRIPTOR_ASSERT(offsetof(tsl9_original_peripheral_descriptor,control_bits_7_to_2)==8,"Original word flags");
#undef DESCRIPTOR_ASSERT

/* Original0x18AB0..0x18AC2. */
REGION void tsl9_main_init_external_18ab0(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    PORT(".option push\n.option rvc\nmv a5, a0\n.option pop\n");
    a4 = a4 & UINT32_C(0xfffffffd); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000001); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a0 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00010000); LIVE;
    __builtin_unreachable();
}

/* Original0x18AC2..0x18AC8. */
REGION void tsl9_peripheral_initializer_block_18ac2(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a3 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18ac6:\n.option push\n.option rvc\nc.bnez a3,.Lperipheral_initializer_edge_18ac6\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_initializer_block_18acc\n");
    __builtin_unreachable();
}

/* Original0x18AC8..0x18ACC. */
REGION void tsl9_peripheral_initializer_block_18ac8(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lperipheral_initializer_edge_18aca:\n.option push\n.option rvc\nc.bnez a4,.Lperipheral_initializer_edge_18aca\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_initializer_block_18ac2\n");
    __builtin_unreachable();
}

/* Original0x18ACC..0x18AD4. */
REGION void tsl9_peripheral_initializer_block_18acc(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a0 = UINT32_C(0x00000000); LIVE;
    a4 = a4 & UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18ad2:\n.option push\n.option rvc\nc.beqz a4,.Lperipheral_initializer_edge_18ad2\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_initializer_block_18b76\n");
    __builtin_unreachable();
}

/* Original0x18AD4..0x18ADC. */
REGION void tsl9_peripheral_initializer_block_18ad4(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000008)); LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18ad8:\n.option push\n.option norvc\nbne a3,a4,.Lperipheral_initializer_edge_18ad8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_initializer_block_18b78\n");
    __builtin_unreachable();
}

/* Original0x18ADC..0x18AE2. */
REGION void tsl9_peripheral_initializer_block_18adc(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000080); LIVE;
    __builtin_unreachable();
}

/* Original0x18AE2..0x18AEC. */
REGION void tsl9_peripheral_initializer_block_18ae2(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000000c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18ae8:\n.option push\n.option norvc\nbne a3,a4,.Lperipheral_initializer_edge_18ae8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_initializer_block_18b80\n");
    __builtin_unreachable();
}

/* Original0x18AEC..0x18AF2. */
REGION void tsl9_peripheral_initializer_block_18aec(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000040); LIVE;
    __builtin_unreachable();
}

/* Original0x18AF2..0x18AFC. */
REGION void tsl9_peripheral_initializer_block_18af2(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000010)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18af8:\n.option push\n.option norvc\nbne a3,a4,.Lperipheral_initializer_edge_18af8\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_initializer_block_18b88\n");
    __builtin_unreachable();
}

/* Original0x18AFC..0x18B02. */
REGION void tsl9_peripheral_initializer_block_18afc(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000020); LIVE;
    __builtin_unreachable();
}

/* Original0x18B02..0x18B0C. */
REGION void tsl9_peripheral_initializer_block_18b02(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000014)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18b08:\n.option push\n.option norvc\nbne a3,a4,.Lperipheral_initializer_edge_18b08\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_initializer_block_18b90\n");
    __builtin_unreachable();
}

/* Original0x18B0C..0x18B12. */
REGION void tsl9_peripheral_initializer_block_18b0c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000010); LIVE;
    __builtin_unreachable();
}

/* Original0x18B12..0x18B1C. */
REGION void tsl9_peripheral_initializer_block_18b12(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x00000018)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18b18:\n.option push\n.option norvc\nbne a3,a4,.Lperipheral_initializer_edge_18b18\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_initializer_block_18b96\n");
    __builtin_unreachable();
}

/* Original0x18B1C..0x18B22. */
REGION void tsl9_peripheral_initializer_block_18b1c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000008); LIVE;
    __builtin_unreachable();
}

/* Original0x18B22..0x18B2C. */
REGION void tsl9_peripheral_initializer_block_18b22(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a1 + UINT32_C(0x0000001c)); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18b28:\n.option push\n.option norvc\nbne a3,a4,.Lperipheral_initializer_edge_18b28\n.option pop\n.reloc .-4,R_RISCV_BRANCH,tsl9_peripheral_initializer_block_18b9c\n");
    __builtin_unreachable();
}

/* Original0x18B2C..0x18B32. */
REGION void tsl9_peripheral_initializer_block_18b2c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 | UINT32_C(0x00000004); LIVE;
    __builtin_unreachable();
}

/* Original0x18B32..0x18B64. */
REGION void tsl9_peripheral_initializer_block_18b32(void)
{
    REGS;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000002)); LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000003)); LIVE;
    a4 = a4 << UINT32_C(0x0000001e); LIVE;
    a3 = a3 << UINT32_C(0x00000018); LIVE;
    a4 = a4 | a3; LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000004)); LIVE;
    a3 = a3 << UINT32_C(0x00000010); LIVE;
    a4 = a4 | a3; LIVE;
    a3 = *(volatile uint8_t *)(uintptr_t)(a1 + UINT32_C(0x00000005)); LIVE;
    a3 = a3 << UINT32_C(0x00000014); LIVE;
    a4 = a4 | a3; LIVE;
    a3 = *(volatile uint16_t *)(uintptr_t)(a1 + UINT32_C(0x00000000)); LIVE;
    a3 = a3 + UINT32_C(0xffffffff); LIVE;
    a4 = a4 | a3; LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0000001c)) = (uint32_t)a4; LIVE;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffe); LIVE;
    *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)) = (uint32_t)a4; LIVE;
    a4 = UINT32_C(0x00010000); LIVE;
    __builtin_unreachable();
}

/* Original0x18B64..0x18B6A. */
REGION void tsl9_peripheral_initializer_block_18b64(void)
{
    REGS;
    a3 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    a3 = a3 & UINT32_C(0x00000001); LIVE;
    PORT(".Lperipheral_initializer_edge_18b68:\n.option push\n.option rvc\nc.beqz a3,.Lperipheral_initializer_edge_18b68\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_initializer_block_18b6e\n");
    __builtin_unreachable();
}

/* Original0x18B6A..0x18B6E. */
REGION void tsl9_peripheral_initializer_block_18b6a(void)
{
    REGS;
    a4 = a4 + UINT32_C(0xffffffff); LIVE;
    PORT(".Lperipheral_initializer_edge_18b6c:\n.option push\n.option rvc\nc.bnez a4,.Lperipheral_initializer_edge_18b6c\n.option pop\n.reloc .-2,R_RISCV_RVC_BRANCH,tsl9_peripheral_initializer_block_18b64\n");
    __builtin_unreachable();
}

/* Original0x18B6E..0x18B76. */
REGION void tsl9_peripheral_initializer_block_18b6e(void)
{
    REGS;
    a0 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000004)); LIVE;
    PORT(".option push\n.option norvc\nnot a0, a0\n.option pop\n");
    a0 = a0 & UINT32_C(0x00000001); LIVE;
    __builtin_unreachable();
}

/* Original0x18B76..0x18B78. */
REGION void tsl9_peripheral_initializer_block_18b76(void)
{
    REGS;
    PORT(".option push\n.option rvc\nret\n.option pop\n");
    __builtin_unreachable();
}

/* Original0x18B78..0x18B80. */
REGION void tsl9_peripheral_initializer_block_18b78(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffff7f); LIVE;
    PORT(".Lperipheral_initializer_edge_18b7e:\n.option push\n.option rvc\nc.j .Lperipheral_initializer_edge_18b7e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_initializer_block_18ae2\n");
    __builtin_unreachable();
}

/* Original0x18B80..0x18B88. */
REGION void tsl9_peripheral_initializer_block_18b80(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffffbf); LIVE;
    PORT(".Lperipheral_initializer_edge_18b86:\n.option push\n.option rvc\nc.j .Lperipheral_initializer_edge_18b86\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_initializer_block_18af2\n");
    __builtin_unreachable();
}

/* Original0x18B88..0x18B90. */
REGION void tsl9_peripheral_initializer_block_18b88(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffffdf); LIVE;
    PORT(".Lperipheral_initializer_edge_18b8e:\n.option push\n.option rvc\nc.j .Lperipheral_initializer_edge_18b8e\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_initializer_block_18b02\n");
    __builtin_unreachable();
}

/* Original0x18B90..0x18B96. */
REGION void tsl9_peripheral_initializer_block_18b90(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xffffffef); LIVE;
    PORT(".Lperipheral_initializer_edge_18b94:\n.option push\n.option rvc\nc.j .Lperipheral_initializer_edge_18b94\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_initializer_block_18b12\n");
    __builtin_unreachable();
}

/* Original0x18B96..0x18B9C. */
REGION void tsl9_peripheral_initializer_block_18b96(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffff7); LIVE;
    PORT(".Lperipheral_initializer_edge_18b9a:\n.option push\n.option rvc\nc.j .Lperipheral_initializer_edge_18b9a\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_initializer_block_18b22\n");
    __builtin_unreachable();
}

/* Original0x18B9C..0x18BA2. */
REGION void tsl9_peripheral_initializer_block_18b9c(void)
{
    REGS;
    a4 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x00000000)); LIVE;
    a4 = a4 & UINT32_C(0xfffffffb); LIVE;
    PORT(".Lperipheral_initializer_edge_18ba0:\n.option push\n.option rvc\nc.j .Lperipheral_initializer_edge_18ba0\n.option pop\n.reloc .-2,R_RISCV_RVC_JUMP,tsl9_peripheral_initializer_block_18b32\n");
    __builtin_unreachable();
}
