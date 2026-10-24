#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Offline RV32 architectural regions only; never run on a HOST or device.
#endif
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used,noinline,noreturn,aligned(2)))
#define FRAME ENTRY __attribute__((used,naked,aligned(2)))
#define INPUT(x) __asm__ volatile("" : "=r"(x) : : "memory")

/* Fixed source for original137C0-13CDC; existing81B0 is reused.
 * C owns free-bank arithmetic/constants and ordinary memory.
 * SP/GP/reserved-S/frame/PC/control effects remain explicit architecture ports.
 * Regions require original placement and adjacency, not independent C ABI.
 * Every opaque call ends a region; following regions resample live registers.
 * No installed ROM, time units, field identities, bounds or IRQ assumptions.
 * Static authoring only; native original-byte comparison is separate. */

/* Original0x137C0-0x137CC. */
REGION void tsl9_events_137c0(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    __asm__ volatile("auipc a5, 0x1fff9\n" : "=r"(a5) :  : "memory");
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xffffffd4));
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_137c8:\n.option push\n.option norvc\nbnez a5, .Levent_control_137c8\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13b4a\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x137CC-0x137D8. */
FRAME void tsl9_events_137cc(void)
{
    __asm__ volatile("addi sp, sp, -80\n");
    __asm__ volatile("sw s0, 72(sp)\n");
    __asm__ volatile("lui s0, 0x40\n");
    __asm__ volatile("lw a5, 72(s0)\n");
    __asm__ volatile("sw ra, 76(sp)\n");
}

/* Original0x137D8-0x137DE. */
REGION void tsl9_events_137d8(void)
{
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    register uint32_t a2 __asm__("a2"); INPUT(a2);
    a2 = UINT32_C(0x21);
    __asm__ volatile("" : "+r"(a1), "+r"(a2) :  : "memory");
    a1 = UINT32_C(0x0);
    __asm__ volatile("" : "+r"(a1), "+r"(a2) :  : "memory");
    __builtin_unreachable();
}

/* Original0x137DE-0x137E8. */
FRAME void tsl9_events_137de(void)
{
    __asm__ volatile("sw s1, 68(sp)\n");
    __asm__ volatile("sw s2, 64(sp)\n");
    __asm__ volatile("sw s3, 60(sp)\n");
    __asm__ volatile("addi a0, sp, 12\n");
    __asm__ volatile("jalr a5\n");
}

/* Original0x137E8-0x137EC. */
FRAME void tsl9_events_137e8(void)
{
    __asm__ volatile(".Levent_control_137e8:\n.option push\n.option norvc\njal ra, .Levent_control_137e8\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_10402\n");
}

/* Original0x137EC-0x137EE. */
FRAME void tsl9_events_137ec(void)
{
    __asm__ volatile("lw a5, 12(sp)\n");
}

/* Original0x137EE-0x137F2. */
REGION void tsl9_events_137ee(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0 = a0 & UINT32_C(0x1ff);
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __builtin_unreachable();
}

/* Original0x137F2-0x137FA. */
FRAME void tsl9_events_137f2(void)
{
    __asm__ volatile("auipc s3, 0x1fff9\n");
    __asm__ volatile("addi s3, s3, -94\n");
}

/* Original0x137FA-0x13800. */
REGION void tsl9_events_137fa(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 & UINT32_C(0xfffffe00);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 | a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13800-0x13806. */
FRAME void tsl9_events_13800(void)
{
    __asm__ volatile("sw a5, 12(sp)\n");
    __asm__ volatile(".Levent_control_13802:\n.option push\n.option norvc\njal ra, .Levent_control_13802\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d052\n");
}

/* Original0x13806-0x1380C. */
REGION void tsl9_events_13806(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x7);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 9u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1380C-0x1380E. */
FRAME void tsl9_events_1380c(void)
{
    __asm__ volatile("lw a0, 12(sp)\n");
}

/* Original0x1380E-0x13818. */
REGION void tsl9_events_1380e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0xfffff000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0x1ff);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13818-0x1381E. */
FRAME void tsl9_events_13818(void)
{
    __asm__ volatile("sw a0, 12(sp)\n");
    __asm__ volatile(".Levent_control_1381a:\n.option push\n.option norvc\njal ra, .Levent_control_1381a\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_a9bc\n");
}

/* Original0x1381E-0x13826. */
REGION void tsl9_events_1381e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x3);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 12u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = UINT32_C(0xffffd000);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13826-0x1382E. */
FRAME void tsl9_events_13826(void)
{
    __asm__ volatile("addi s1, a0, -1\n");
    __asm__ volatile("lw a0, 12(sp)\n");
    __asm__ volatile("and a0, a0, s1\n");
}

/* Original0x1382E-0x13830. */
REGION void tsl9_events_1382e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13830-0x13836. */
FRAME void tsl9_events_13830(void)
{
    __asm__ volatile("sw a0, 12(sp)\n");
    __asm__ volatile(".Levent_control_13832:\n.option push\n.option norvc\njal ra, .Levent_control_13832\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_b082\n");
}

/* Original0x13836-0x1383C. */
REGION void tsl9_events_13836(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x3);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 14u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1383C-0x1383E. */
FRAME void tsl9_events_1383c(void)
{
    __asm__ volatile("lw a0, 12(sp)\n");
}

/* Original0x1383E-0x13846. */
REGION void tsl9_events_1383e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0xffff4000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13846-0x1384C. */
FRAME void tsl9_events_13846(void)
{
    __asm__ volatile("sw a0, 12(sp)\n");
    __asm__ volatile(".Levent_control_13848:\n.option push\n.option norvc\njal ra, .Levent_control_13848\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_e058\n");
}

/* Original0x1384C-0x13852. */
REGION void tsl9_events_1384c(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0xf);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 16u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13852-0x13854. */
FRAME void tsl9_events_13852(void)
{
    __asm__ volatile("lw a0, 12(sp)\n");
}

/* Original0x13854-0x1385E. */
REGION void tsl9_events_13854(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0xfff10000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1385E-0x13864. */
FRAME void tsl9_events_1385e(void)
{
    __asm__ volatile("sw a0, 12(sp)\n");
    __asm__ volatile(".Levent_control_13860:\n.option push\n.option norvc\njal ra, .Levent_control_13860\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_a976\n");
}

/* Original0x13864-0x13868. */
FRAME void tsl9_events_13864(void)
{
    __asm__ volatile("lbu a5, 14(sp)\n");
}

/* Original0x13868-0x1386C. */
REGION void tsl9_events_13868(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 << 4u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1386C-0x13874. */
FRAME void tsl9_events_1386c(void)
{
    __asm__ volatile("sb a0, 14(sp)\n");
    __asm__ volatile(".Levent_control_13870:\n.option push\n.option norvc\njal ra, .Levent_control_13870\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d4e0\n");
}

/* Original0x13874-0x1387C. */
REGION void tsl9_events_13874(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x7f);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 24u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1387C-0x1387E. */
FRAME void tsl9_events_1387c(void)
{
    __asm__ volatile("lw a0, 12(sp)\n");
}

/* Original0x1387E-0x13888. */
REGION void tsl9_events_1387e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0x81000000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13888-0x1388E. */
FRAME void tsl9_events_13888(void)
{
    __asm__ volatile("sw a0, 12(sp)\n");
    __asm__ volatile(".Levent_control_1388a:\n.option push\n.option norvc\njal ra, .Levent_control_1388a\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_state_get_100f6\n");
}

/* Original0x1388E-0x13890. */
FRAME void tsl9_events_1388e(void)
{
    __asm__ volatile("lw a5, 12(sp)\n");
}

/* Original0x13890-0x13898. */
REGION void tsl9_events_13890(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 << 31u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 << 1u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 >> 1u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 | a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13898-0x1389E. */
FRAME void tsl9_events_13898(void)
{
    __asm__ volatile("sw a5, 12(sp)\n");
    __asm__ volatile(".Levent_control_1389a:\n.option push\n.option norvc\njal ra, .Levent_control_1389a\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_f65c\n");
}

/* Original0x1389E-0x138A0. */
FRAME void tsl9_events_1389e(void)
{
    __asm__ volatile("lw a5, 16(sp)\n");
}

/* Original0x138A0-0x138A8. */
REGION void tsl9_events_138a0(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = (a0 == 0u);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0xfffffffe);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 | a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138A8-0x138AE. */
FRAME void tsl9_events_138a8(void)
{
    __asm__ volatile("sw a5, 16(sp)\n");
    __asm__ volatile(".Levent_control_138aa:\n.option push\n.option norvc\njal ra, .Levent_control_138aa\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_dee2\n");
}

/* Original0x138AE-0x138BC. */
REGION void tsl9_events_138ae(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a0 << 1u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile("auipc a5, 0x1fff9\n" : "=r"(a5) :  : "memory");
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0xfffff998));
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138BC-0x138BE. */
FRAME void tsl9_events_138bc(void)
{
    __asm__ volatile("lw a0, 16(sp)\n");
}

/* Original0x138BE-0x138CE. */
REGION void tsl9_events_138be(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 >> 14u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 ^ UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & UINT32_C(0xfffffff9);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 << 2u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 | a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138CE-0x138D4. */
FRAME void tsl9_events_138ce(void)
{
    __asm__ volatile("sw a5, 16(sp)\n");
    __asm__ volatile(".Levent_control_138d0:\n.option push\n.option norvc\njal ra, .Levent_control_138d0\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_f992\n");
}

/* Original0x138D4-0x138DA. */
REGION void tsl9_events_138d4(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 3u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138DA-0x138DC. */
FRAME void tsl9_events_138da(void)
{
    __asm__ volatile("lw a0, 16(sp)\n");
}

/* Original0x138DC-0x138E0. */
REGION void tsl9_events_138dc(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0xfffffff7);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138E0-0x138E6. */
FRAME void tsl9_events_138e0(void)
{
    __asm__ volatile("sw a0, 16(sp)\n");
    __asm__ volatile(".Levent_control_138e2:\n.option push\n.option norvc\njal ra, .Levent_control_138e2\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_c462\n");
}

/* Original0x138E6-0x138EC. */
REGION void tsl9_events_138e6(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 4u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138EC-0x138EE. */
FRAME void tsl9_events_138ec(void)
{
    __asm__ volatile("lw a0, 16(sp)\n");
}

/* Original0x138EE-0x138F2. */
REGION void tsl9_events_138ee(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0xffffffef);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138F2-0x138F8. */
FRAME void tsl9_events_138f2(void)
{
    __asm__ volatile("sw a0, 16(sp)\n");
    __asm__ volatile(".Levent_control_138f4:\n.option push\n.option norvc\njal ra, .Levent_control_138f4\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_e038\n");
}

/* Original0x138F8-0x138FE. */
REGION void tsl9_events_138f8(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 5u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x138FE-0x13900. */
FRAME void tsl9_events_138fe(void)
{
    __asm__ volatile("lw a0, 16(sp)\n");
}

/* Original0x13900-0x13906. */
REGION void tsl9_events_13900(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0xffffffdf);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13906-0x1390C. */
FRAME void tsl9_events_13906(void)
{
    __asm__ volatile("sw a0, 16(sp)\n");
    __asm__ volatile(".Levent_control_13908:\n.option push\n.option norvc\njal ra, .Levent_control_13908\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_state_get_1008a\n");
}

/* Original0x1390C-0x1390E. */
FRAME void tsl9_events_1390c(void)
{
    __asm__ volatile("lw a5, 16(sp)\n");
}

/* Original0x1390E-0x13910. */
REGION void tsl9_events_1390e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0 = a0 << 6u;
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13910-0x13914. */
FRAME void tsl9_events_13910(void)
{
    __asm__ volatile("lw s2, 76(s0)\n");
}

/* Original0x13914-0x1391A. */
REGION void tsl9_events_13914(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 & UINT32_C(0x3f);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 | a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1391A-0x13920. */
FRAME void tsl9_events_1391a(void)
{
    __asm__ volatile("sw a5, 16(sp)\n");
    __asm__ volatile(".Levent_control_1391c:\n.option push\n.option norvc\njal ra, .Levent_control_1391c\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d190\n");
}

/* Original0x13920-0x13924. */
REGION void tsl9_events_13920(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    register uint32_t a2 __asm__("a2"); INPUT(a2);
    a1 = a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2) :  : "memory");
    a2 = UINT32_C(0x4);
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13924-0x13928. */
FRAME void tsl9_events_13924(void)
{
    __asm__ volatile("addi a0, sp, 20\n");
    __asm__ volatile("jalr s2\n");
}

/* Original0x13928-0x1392C. */
FRAME void tsl9_events_13928(void)
{
    __asm__ volatile(".Levent_control_13928:\n.option push\n.option norvc\njal ra, .Levent_control_13928\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d048\n");
}

/* Original0x1392C-0x13930. */
FRAME void tsl9_events_1392c(void)
{
    __asm__ volatile("sb a0, 24(sp)\n");
}

/* Original0x13930-0x13936. */
REGION void tsl9_events_13930(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0 = UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __asm__ volatile(".Levent_control_13932:\n.option push\n.option norvc\njal ra, .Levent_control_13932\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_state_get_10130\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13936-0x1393E. */
REGION void tsl9_events_13936(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x7ff);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 8u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1393E-0x13940. */
FRAME void tsl9_events_1393e(void)
{
    __asm__ volatile("lw a0, 24(sp)\n");
}

/* Original0x13940-0x1394C. */
REGION void tsl9_events_13940(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0xfff80000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xff);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1394C-0x1394E. */
FRAME void tsl9_events_1394c(void)
{
    __asm__ volatile("sw a0, 24(sp)\n");
}

/* Original0x1394E-0x13954. */
REGION void tsl9_events_1394e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0 = UINT32_C(0x0);
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __asm__ volatile(".Levent_control_13950:\n.option push\n.option norvc\njal ra, .Levent_control_13950\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_state_get_10130\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13954-0x1395C. */
REGION void tsl9_events_13954(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x7ff);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 19u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1395C-0x1395E. */
FRAME void tsl9_events_1395c(void)
{
    __asm__ volatile("lw a0, 24(sp)\n");
}

/* Original0x1395E-0x13968. */
REGION void tsl9_events_1395e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0xc0080000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13968-0x1396E. */
FRAME void tsl9_events_13968(void)
{
    __asm__ volatile("sw a0, 24(sp)\n");
    __asm__ volatile(".Levent_control_1396a:\n.option push\n.option norvc\njal ra, .Levent_control_1396a\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_state_get_100c8\n");
}

/* Original0x1396E-0x13970. */
FRAME void tsl9_events_1396e(void)
{
    __asm__ volatile("lw a5, 24(sp)\n");
}

/* Original0x13970-0x1397E. */
REGION void tsl9_events_13970(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 << 16u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 >> 16u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 << 2u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a0 << 30u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 >> 2u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 | a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1397E-0x13984. */
FRAME void tsl9_events_1397e(void)
{
    __asm__ volatile("sw a5, 24(sp)\n");
    __asm__ volatile("lhu a5, 28(sp)\n");
}

/* Original0x13984-0x1398E. */
REGION void tsl9_events_13984(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0xfffff000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 << 18u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 >> 20u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1398E-0x13996. */
FRAME void tsl9_events_1398e(void)
{
    __asm__ volatile("sh a0, 28(sp)\n");
    __asm__ volatile(".Levent_control_13992:\n.option push\n.option norvc\njal ra, .Levent_control_13992\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d322\n");
}

/* Original0x13996-0x1399C. */
REGION void tsl9_events_13996(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x3);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 12u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x1399C-0x139A4. */
FRAME void tsl9_events_1399c(void)
{
    __asm__ volatile("lhu a0, 28(sp)\n");
    __asm__ volatile("li s2, 1\n");
    __asm__ volatile("and a0, a0, s1\n");
}

/* Original0x139A4-0x139A6. */
REGION void tsl9_events_139a4(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x139A6-0x139AE. */
FRAME void tsl9_events_139a6(void)
{
    __asm__ volatile("sh a0, 28(sp)\n");
    __asm__ volatile(".Levent_control_139aa:\n.option push\n.option norvc\njal ra, .Levent_control_139aa\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_10408\n");
}

/* Original0x139AE-0x139B4. */
REGION void tsl9_events_139ae(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 & UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a0 << 14u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x139B4-0x139B8. */
FRAME void tsl9_events_139b4(void)
{
    __asm__ volatile("lhu a0, 28(sp)\n");
}

/* Original0x139B8-0x139C0. */
REGION void tsl9_events_139b8(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0xffffc000);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xffffffff);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x139C0-0x139C8. */
FRAME void tsl9_events_139c0(void)
{
    __asm__ volatile("sh a0, 28(sp)\n");
    __asm__ volatile(".Levent_control_139c4:\n.option push\n.option norvc\njal ra, .Levent_control_139c4\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_81f8\n");
}

/* Original0x139C8-0x139CC. */
FRAME void tsl9_events_139c8(void)
{
    __asm__ volatile("lhu a5, 28(sp)\n");
}

/* Original0x139CC-0x139CE. */
REGION void tsl9_events_139cc(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0 = a0 << 15u;
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __builtin_unreachable();
}

/* Original0x139CE-0x139D0. */
FRAME void tsl9_events_139ce(void)
{
    __asm__ volatile("lui s1, 0x10\n");
}

/* Original0x139D0-0x139D6. */
REGION void tsl9_events_139d0(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 << 17u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 >> 17u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 | a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x139D6-0x139E0. */
FRAME void tsl9_events_139d6(void)
{
    __asm__ volatile("sh a5, 28(sp)\n");
    __asm__ volatile("lw s0, 76(s0)\n");
    __asm__ volatile(".Levent_control_139dc:\n.option push\n.option norvc\njal ra, .Levent_control_139dc\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d754\n");
}

/* Original0x139E0-0x139E4. */
REGION void tsl9_events_139e0(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    register uint32_t a2 __asm__("a2"); INPUT(a2);
    a1 = a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2) :  : "memory");
    a2 = UINT32_C(0x5);
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2) :  : "memory");
    __builtin_unreachable();
}

/* Original0x139E4-0x139EA. */
FRAME void tsl9_events_139e4(void)
{
    __asm__ volatile("addi a0, sp, 30\n");
    __asm__ volatile("jalr s0\n");
}

/* Original0x139EA-0x139EE. */
FRAME void tsl9_events_139ea(void)
{
    __asm__ volatile(".Levent_control_139ea:\n.option push\n.option norvc\njal ra, .Levent_control_139ea\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_b3ee\n");
}

/* Original0x139EE-0x139F6. */
FRAME void tsl9_events_139ee(void)
{
    __asm__ volatile("lbu a5, 36(sp)\n");
    __asm__ volatile("sb a0, 35(sp)\n");
}

/* Original0x139F6-0x139FE. */
REGION void tsl9_events_139f6(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 >> 8u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0xfffffffc);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 & UINT32_C(0x3);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x139FE-0x13A06. */
FRAME void tsl9_events_139fe(void)
{
    __asm__ volatile("sb a0, 36(sp)\n");
    __asm__ volatile(".Levent_control_13a02:\n.option push\n.option norvc\njal ra, .Levent_control_13a02\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_b3f8\n");
}

/* Original0x13A06-0x13A0E. */
REGION void tsl9_events_13a06(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a0 & UINT32_C(0x3f);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a5 << 2u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A0E-0x13A12. */
FRAME void tsl9_events_13a0e(void)
{
    __asm__ volatile("lbu a5, 36(sp)\n");
}

/* Original0x13A12-0x13A1A. */
REGION void tsl9_events_13a12(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 >> 6u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & UINT32_C(0x1f);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0x3);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 | a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A1A-0x13A26. */
FRAME void tsl9_events_13a1a(void)
{
    __asm__ volatile("sb a5, 36(sp)\n");
    __asm__ volatile("lbu a5, 37(sp)\n");
    __asm__ volatile("li s0, 0\n");
    __asm__ volatile("addi s1, s1, -2\n");
}

/* Original0x13A26-0x13A2A. */
REGION void tsl9_events_13a26(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 & UINT32_C(0xffffffe0);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A2A-0x13A32. */
FRAME void tsl9_events_13a2a(void)
{
    __asm__ volatile("sb a0, 37(sp)\n");
    __asm__ volatile(".Levent_control_13a2e:\n.option push\n.option norvc\njal ra, .Levent_control_13a2e\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_b3da\n");
}

/* Original0x13A32-0x13A3A. */
REGION void tsl9_events_13a32(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a0 & UINT32_C(0x7);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a5 << 5u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A3A-0x13A3E. */
FRAME void tsl9_events_13a3a(void)
{
    __asm__ volatile("lbu a5, 37(sp)\n");
}

/* Original0x13A3E-0x13A40. */
REGION void tsl9_events_13a3e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0 = a0 >> 3u;
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A40-0x13A44. */
FRAME void tsl9_events_13a40(void)
{
    __asm__ volatile("sb a0, 38(sp)\n");
}

/* Original0x13A44-0x13A48. */
REGION void tsl9_events_13a44(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 & UINT32_C(0x1f);
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 | a4;
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A48-0x13A50. */
FRAME void tsl9_events_13a48(void)
{
    __asm__ volatile("sb a5, 37(sp)\n");
    __asm__ volatile(".Levent_control_13a4c:\n.option push\n.option norvc\njal ra, .Levent_control_13a4c\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_b3e4\n");
}

/* Original0x13A50-0x13A58. */
FRAME void tsl9_events_13a50(void)
{
    __asm__ volatile("sb a0, 39(sp)\n");
    __asm__ volatile(".Levent_control_13a54:\n.option push\n.option norvc\njal ra, .Levent_control_13a54\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d472\n");
}

/* Original0x13A58-0x13A60. */
REGION void tsl9_events_13a58(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a0 & UINT32_C(0x3);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a5 << 6u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A60-0x13A64. */
FRAME void tsl9_events_13a60(void)
{
    __asm__ volatile("lbu a5, 42(sp)\n");
}

/* Original0x13A64-0x13A70. */
REGION void tsl9_events_13a64(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 >> 2u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & UINT32_C(0x7f);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0x3f);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 | a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A70-0x13A78. */
FRAME void tsl9_events_13a70(void)
{
    __asm__ volatile("sb a5, 42(sp)\n");
    __asm__ volatile("lbu a5, 43(sp)\n");
}

/* Original0x13A78-0x13A7E. */
REGION void tsl9_events_13a78(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 & UINT32_C(0xffffff80);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A7E-0x13A86. */
FRAME void tsl9_events_13a7e(void)
{
    __asm__ volatile("sb a0, 43(sp)\n");
    __asm__ volatile(".Levent_control_13a82:\n.option push\n.option norvc\njal ra, .Levent_control_13a82\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d468\n");
}

/* Original0x13A86-0x13A8E. */
FRAME void tsl9_events_13a86(void)
{
    __asm__ volatile("lbu a5, 41(sp)\n");
    __asm__ volatile("sb a0, 40(sp)\n");
}

/* Original0x13A8E-0x13A96. */
REGION void tsl9_events_13a8e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 >> 8u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0xfffffff0);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 & UINT32_C(0xf);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13A96-0x13A9E. */
FRAME void tsl9_events_13a96(void)
{
    __asm__ volatile("sb a0, 41(sp)\n");
    __asm__ volatile(".Levent_control_13a9a:\n.option push\n.option norvc\njal ra, .Levent_control_13a9a\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_d4ea\n");
}

/* Original0x13A9E-0x13AA6. */
REGION void tsl9_events_13a9e(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a0 & UINT32_C(0xf);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a5 << 4u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13AA6-0x13AAA. */
FRAME void tsl9_events_13aa6(void)
{
    __asm__ volatile("lbu a5, 41(sp)\n");
}

/* Original0x13AAA-0x13AB4. */
REGION void tsl9_events_13aaa(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 >> 4u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & UINT32_C(0x3f);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0xf);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 | a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13AB4-0x13ABC. */
FRAME void tsl9_events_13ab4(void)
{
    __asm__ volatile("sb a5, 41(sp)\n");
    __asm__ volatile("lbu a5, 42(sp)\n");
}

/* Original0x13ABC-0x13AC2. */
REGION void tsl9_events_13abc(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 & UINT32_C(0xffffffc0);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13AC2-0x13ACA. */
FRAME void tsl9_events_13ac2(void)
{
    __asm__ volatile("sb a0, 42(sp)\n");
    __asm__ volatile(".Levent_control_13ac6:\n.option push\n.option norvc\njal ra, .Levent_control_13ac6\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_ab68\n");
}

/* Original0x13ACA-0x13AD2. */
REGION void tsl9_events_13aca(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a0 & UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a5 << 7u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13AD2-0x13AD6. */
FRAME void tsl9_events_13ad2(void)
{
    __asm__ volatile("lbu a5, 43(sp)\n");
}

/* Original0x13AD6-0x13AE0. */
REGION void tsl9_events_13ad6(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 >> 1u;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a0 = a0 & UINT32_C(0xf);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0x7f);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 | a4;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13AE0-0x13AE8. */
FRAME void tsl9_events_13ae0(void)
{
    __asm__ volatile("sb a5, 43(sp)\n");
    __asm__ volatile("lbu a5, 44(sp)\n");
}

/* Original0x13AE8-0x13AEC. */
REGION void tsl9_events_13ae8(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = a5 & UINT32_C(0xfffffff0);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a0 = a0 | a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13AEC-0x13AF4. */
FRAME void tsl9_events_13aec(void)
{
    __asm__ volatile("sb a0, 44(sp)\n");
    __asm__ volatile(".Levent_control_13af0:\n.option push\n.option norvc\njal ra, .Levent_control_13af0\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_external_ab72\n");
}

/* Original0x13AF4-0x13AF8. */
FRAME void tsl9_events_13af4(void)
{
    __asm__ volatile("lbu a5, 44(sp)\n");
}

/* Original0x13AF8-0x13AFE. */
REGION void tsl9_events_13af8(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = a0 << 4u;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0xf);
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    a5 = a5 | a0;
    __asm__ volatile("" : "+r"(a0), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13AFE-0x13B02. */
FRAME void tsl9_events_13afe(void)
{
    __asm__ volatile("sb a5, 44(sp)\n");
}

/* Original0x13B02-0x13B08. */
FRAME void tsl9_events_13b02(void)
{
    __asm__ volatile("slli a5, s0, 0x2\n");
    __asm__ volatile("add a5, a5, s3\n");
}

/* Original0x13B08-0x13B10. */
REGION void tsl9_events_13b08(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x2));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13b0c:\n.option push\n.option norvc\nbeq s1, a4, .Levent_control_13b0c\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13b34\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13B10-0x13B18. */
REGION void tsl9_events_13b10(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x5));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13b14:\n.option push\n.option norvc\nbne s2, a4, .Levent_control_13b14\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13b34\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13B18-0x13B22. */
REGION void tsl9_events_13b18(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & UINT32_C(0xff);
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13b20:\n.option push\n.option rvc\nbeqz a4, .Levent_control_13b20\n.option pop\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_events_13b34\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13B22-0x13B2A. */
REGION void tsl9_events_13b22(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x2));
    __asm__ volatile("" : "+r"(a0), "+r"(a3), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x21);
    __asm__ volatile("" : "+r"(a0), "+r"(a3), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13B2A-0x13B2C. */
FRAME void tsl9_events_13b2a(void)
{
    __asm__ volatile("addi a2, sp, 12\n");
}

/* Original0x13B2C-0x13B34. */
REGION void tsl9_events_13b2c(void)
{
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    a1 = UINT32_C(0xb0);
    __asm__ volatile("" : "+r"(a1) :  : "memory");
    __asm__ volatile(".Levent_control_13b30:\n.option push\n.option norvc\njal ra, .Levent_control_13b30\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_filter_external_8a56\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13B34-0x13B38. */
FRAME void tsl9_events_13b34(void)
{
    __asm__ volatile(".Levent_control_13b34:\n.option push\n.option norvc\nbne s0, s2, .Levent_control_13b34\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13b46\n");
}

/* Original0x13B38-0x13B46. */
FRAME void tsl9_events_13b38(void)
{
    __asm__ volatile("lw ra, 76(sp)\n");
    __asm__ volatile("lw s0, 72(sp)\n");
    __asm__ volatile("lw s1, 68(sp)\n");
    __asm__ volatile("lw s2, 64(sp)\n");
    __asm__ volatile("lw s3, 60(sp)\n");
    __asm__ volatile("addi sp, sp, 80\n");
    __asm__ volatile("ret\n");
}

/* Original0x13B46-0x13B4A. */
FRAME void tsl9_events_13b46(void)
{
    __asm__ volatile("li s0, 1\n");
    __asm__ volatile(".Levent_control_13b48:\n.option push\n.option rvc\nc.j .Levent_control_13b48\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_events_13b02\n");
}

/* Original0x13B4A-0x13B4C. */
FRAME void tsl9_events_13b4a(void)
{
    __asm__ volatile("ret\n");
}

/* Original0x13B4C-0x13B60. */
FRAME void tsl9_events_13b4c(void)
{
    __asm__ volatile("addi sp, sp, -48\n");
    __asm__ volatile("sw s1, 36(sp)\n");
    __asm__ volatile("lui s1, 0x40\n");
    __asm__ volatile("lw a5, 112(s1)\n");
    __asm__ volatile("sw s2, 32(sp)\n");
    __asm__ volatile("sw s3, 28(sp)\n");
    __asm__ volatile("sw ra, 44(sp)\n");
    __asm__ volatile("sw s0, 40(sp)\n");
    __asm__ volatile("mv s2, a0\n");
}

/* Original0x13B60-0x13B62. */
REGION void tsl9_events_13b60(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    a0 = a3;
    __asm__ volatile("" : "+r"(a0), "+r"(a3) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13B62-0x13B6A. */
FRAME void tsl9_events_13b62(void)
{
    __asm__ volatile("mv s3, a1\n");
    __asm__ volatile("sw a2, 12(sp)\n");
    __asm__ volatile("sw a3, 8(sp)\n");
    __asm__ volatile("jalr a5\n");
}

/* Original0x13B6A-0x13B6C. */
FRAME void tsl9_events_13b6a(void)
{
    __asm__ volatile(".Levent_control_13b6a:\n.option push\n.option rvc\nbeqz a0, .Levent_control_13b6a\n.option pop\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_events_13b98\n");
}

/* Original0x13B6C-0x13B72. */
FRAME void tsl9_events_13b6c(void)
{
    __asm__ volatile("lw a3, 8(sp)\n");
    __asm__ volatile("lw a5, 76(s1)\n");
    __asm__ volatile("lw a1, 12(sp)\n");
}

/* Original0x13B72-0x13B74. */
REGION void tsl9_events_13b72(void)
{
    register uint32_t a2 __asm__("a2"); INPUT(a2);
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    a2 = a3;
    __asm__ volatile("" : "+r"(a2), "+r"(a3) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13B74-0x13B78. */
FRAME void tsl9_events_13b74(void)
{
    __asm__ volatile("mv s0, a0\n");
    __asm__ volatile("jalr a5\n");
}

/* Original0x13B78-0x13B84. */
FRAME void tsl9_events_13b78(void)
{
    __asm__ volatile("lw a3, 8(sp)\n");
    __asm__ volatile("mv a0, s2\n");
    __asm__ volatile("mv a2, s0\n");
    __asm__ volatile("mv a1, s3\n");
    __asm__ volatile(".Levent_control_13b80:\n.option push\n.option norvc\njal ra, .Levent_control_13b80\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_filter_external_8a56\n");
}

/* Original0x13B84-0x13B98. */
FRAME void tsl9_events_13b84(void)
{
    __asm__ volatile("mv a0, s0\n");
    __asm__ volatile("lw s0, 40(sp)\n");
    __asm__ volatile("lw t1, 104(s1)\n");
    __asm__ volatile("lw ra, 44(sp)\n");
    __asm__ volatile("lw s1, 36(sp)\n");
    __asm__ volatile("lw s2, 32(sp)\n");
    __asm__ volatile("lw s3, 28(sp)\n");
    __asm__ volatile("addi sp, sp, 48\n");
    __asm__ volatile("jr t1\n");
}

/* Original0x13B98-0x13BA6. */
FRAME void tsl9_events_13b98(void)
{
    __asm__ volatile("lw ra, 44(sp)\n");
    __asm__ volatile("lw s0, 40(sp)\n");
    __asm__ volatile("lw s1, 36(sp)\n");
    __asm__ volatile("lw s2, 32(sp)\n");
    __asm__ volatile("lw s3, 28(sp)\n");
    __asm__ volatile("addi sp, sp, 48\n");
    __asm__ volatile("ret\n");
}

/* Original0x13BA6-0x13BBA. */
REGION void tsl9_events_13ba6(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    __asm__ volatile("auipc a4, 0x1fff9\n" : "=r"(a4) :  : "memory");
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a4 = *(volatile uint16_t *)(uintptr_t)(a4 + UINT32_C(0xfffffbf0));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile("auipc a5, 0x1fff9\n" : "=r"(a5) :  : "memory");
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 + UINT32_C(0xfffffbe6);
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13bb6:\n.option push\n.option norvc\nbeq a0, a4, .Levent_control_13bb6\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13bce\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13BBA-0x13BC2. */
REGION void tsl9_events_13bba(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x6));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13bbe:\n.option push\n.option norvc\nbne a0, a4, .Levent_control_13bbe\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13bcc\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13BC2-0x13BC4. */
REGION void tsl9_events_13bc2(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    a4 = UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a4) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13BC4-0x13BCC. */
REGION void tsl9_events_13bc4(void)
{
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = a4 << 2u;
    __asm__ volatile("" : "+r"(a1), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 + a4;
    __asm__ volatile("" : "+r"(a1), "+r"(a4), "+r"(a5) :  : "memory");
    *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x5)) = (uint8_t)a1;
    __asm__ volatile("" : "+r"(a1), "+r"(a4), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13BCC-0x13BCE. */
FRAME void tsl9_events_13bcc(void)
{
    __asm__ volatile("ret\n");
}

/* Original0x13BCE-0x13BD2. */
REGION void tsl9_events_13bce(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    a4 = UINT32_C(0x0);
    __asm__ volatile("" : "+r"(a4) :  : "memory");
    __asm__ volatile(".Levent_control_13bd0:\n.option push\n.option rvc\nc.j .Levent_control_13bd0\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_events_13bc4\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13BD2-0x13BDC. */
REGION void tsl9_feature_external_13bd2(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    __asm__ volatile("auipc a5, 0x1fff9\n" : "=r"(a5) :  : "memory");
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0xfffffbc2));
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13bda:\n.option push\n.option rvc\nbnez a5, .Levent_control_13bda\n.option pop\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_events_13c4c\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13BDC-0x13C02. */
FRAME void tsl9_events_13bdc(void)
{
    __asm__ volatile("addi sp, sp, -32\n");
    __asm__ volatile("sw s2, 16(sp)\n");
    __asm__ volatile("lui s2, 0x10\n");
    __asm__ volatile("sw s0, 24(sp)\n");
    __asm__ volatile("sw s1, 20(sp)\n");
    __asm__ volatile("sw s3, 12(sp)\n");
    __asm__ volatile("sw s4, 8(sp)\n");
    __asm__ volatile("sw s5, 4(sp)\n");
    __asm__ volatile("sw ra, 28(sp)\n");
    __asm__ volatile("li s1, 0\n");
    __asm__ volatile("auipc s4, 0x1fff9\n");
    __asm__ volatile("addi s4, s4, -1116\n");
    __asm__ volatile("addi s2, s2, -2\n");
    __asm__ volatile("li s5, 4\n");
    __asm__ volatile("addi s0, a0, 3\n");
    __asm__ volatile("li s3, 1\n");
}

/* Original0x13C02-0x13C08. */
FRAME void tsl9_events_13c02(void)
{
    __asm__ volatile("slli a5, s1, 0x2\n");
    __asm__ volatile("add a5, a5, s4\n");
}

/* Original0x13C08-0x13C10. */
REGION void tsl9_events_13c08(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x2));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c0c:\n.option push\n.option norvc\nbeq s2, a4, .Levent_control_13c0c\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13c32\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C10-0x13C18. */
REGION void tsl9_events_13c10(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x5));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c14:\n.option push\n.option norvc\nbne s5, a4, .Levent_control_13c14\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13c32\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C18-0x13C22. */
REGION void tsl9_events_13c18(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & UINT32_C(0xff);
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c20:\n.option push\n.option rvc\nbeqz a4, .Levent_control_13c20\n.option pop\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_events_13c32\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C22-0x13C28. */
REGION void tsl9_events_13c22(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a0 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x2));
    __asm__ volatile("" : "+r"(a0), "+r"(a3), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x8);
    __asm__ volatile("" : "+r"(a0), "+r"(a3), "+r"(a5) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C28-0x13C2A. */
FRAME void tsl9_events_13c28(void)
{
    __asm__ volatile("mv a2, s0\n");
}

/* Original0x13C2A-0x13C32. */
REGION void tsl9_events_13c2a(void)
{
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    a1 = UINT32_C(0xd1);
    __asm__ volatile("" : "+r"(a1) :  : "memory");
    __asm__ volatile(".Levent_control_13c2e:\n.option push\n.option norvc\njal ra, .Levent_control_13c2e\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_filter_external_8a56\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C32-0x13C36. */
FRAME void tsl9_events_13c32(void)
{
    __asm__ volatile(".Levent_control_13c32:\n.option push\n.option norvc\nbne s1, s3, .Levent_control_13c32\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13c48\n");
}

/* Original0x13C36-0x13C48. */
FRAME void tsl9_events_13c36(void)
{
    __asm__ volatile("lw ra, 28(sp)\n");
    __asm__ volatile("lw s0, 24(sp)\n");
    __asm__ volatile("lw s1, 20(sp)\n");
    __asm__ volatile("lw s2, 16(sp)\n");
    __asm__ volatile("lw s3, 12(sp)\n");
    __asm__ volatile("lw s4, 8(sp)\n");
    __asm__ volatile("lw s5, 4(sp)\n");
    __asm__ volatile("addi sp, sp, 32\n");
    __asm__ volatile("ret\n");
}

/* Original0x13C48-0x13C4C. */
FRAME void tsl9_events_13c48(void)
{
    __asm__ volatile("li s1, 1\n");
    __asm__ volatile(".Levent_control_13c4a:\n.option push\n.option rvc\nc.j .Levent_control_13c4a\n.option pop\n.reloc .-2, R_RISCV_RVC_JUMP, tsl9_events_13c02\n");
}

/* Original0x13C4C-0x13C4E. */
FRAME void tsl9_events_13c4c(void)
{
    __asm__ volatile("ret\n");
}

/* Original0x13C4E-0x13C66. */
REGION void tsl9_state_external_13c4e(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = UINT32_C(0x10000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile("auipc a3, 0x1fff9\n" : "=r"(a3) :  : "memory");
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = *(volatile uint16_t *)(uintptr_t)(a3 + UINT32_C(0xfffffb46));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xfffffffe);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile("auipc a5, 0x1fff9\n" : "=r"(a5) :  : "memory");
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a5 + UINT32_C(0xfffffb3a);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c62:\n.option push\n.option norvc\nbeq a3, a4, .Levent_control_13c62\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13c7a\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C66-0x13C70. */
REGION void tsl9_events_13c66(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x5));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c6c:\n.option push\n.option norvc\nbne a3, a4, .Levent_control_13c6c\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13c7a\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C70-0x13C7A. */
REGION void tsl9_events_13c70(void)
{
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x4));
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 & UINT32_C(0xff);
    __asm__ volatile("" : "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c78:\n.option push\n.option rvc\nbnez a4, .Levent_control_13c78\n.option pop\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_events_13c9a\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C7A-0x13C86. */
REGION void tsl9_events_13c7a(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a3 = *(volatile uint16_t *)(uintptr_t)(a5 + UINT32_C(0x6));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = UINT32_C(0x10000);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = a4 + UINT32_C(0xfffffffe);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c82:\n.option push\n.option norvc\nbeq a4, a3, .Levent_control_13c82\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13cda\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C86-0x13C90. */
REGION void tsl9_events_13c86(void)
{
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a4 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x9));
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    a3 = UINT32_C(0x1);
    __asm__ volatile("" : "+r"(a3), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c8c:\n.option push\n.option norvc\nbne a3, a4, .Levent_control_13c8c\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13cda\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C90-0x13C9A. */
REGION void tsl9_events_13c90(void)
{
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = *(volatile uint8_t *)(uintptr_t)(a5 + UINT32_C(0x8));
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    a5 = a5 & UINT32_C(0xff);
    __asm__ volatile("" : "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13c98:\n.option push\n.option rvc\nbeqz a5, .Levent_control_13c98\n.option pop\n.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_events_13cda\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13C9A-0x13CA2. */
FRAME void tsl9_events_13c9a(void)
{
    __asm__ volatile("addi sp, sp, -16\n");
    __asm__ volatile("sw ra, 12(sp)\n");
    __asm__ volatile(".Levent_control_13c9e:\n.option push\n.option norvc\njal ra, .Levent_control_13c9e\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_channel_external_81b0\n");
}

/* Original0x13CA2-0x13CA6. */
FRAME void tsl9_events_13ca2(void)
{
    __asm__ volatile("addi a5, gp, 340\n");
}

/* Original0x13CA6-0x13CB4. */
REGION void tsl9_events_13ca6(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a4 __asm__("a4"); INPUT(a4);
    register uint32_t a5 __asm__("a5"); INPUT(a5);
    a5 = *(volatile uint32_t *)(uintptr_t)(a5 + UINT32_C(0x0));
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a4 = UINT32_C(0x22);
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    a5 = a0 - a5;
    __asm__ volatile("" : "+r"(a0), "+r"(a4), "+r"(a5) :  : "memory");
    __asm__ volatile(".Levent_control_13cb0:\n.option push\n.option norvc\nbleu a5, a4, .Levent_control_13cb0\n.option pop\n.reloc .-4, R_RISCV_BRANCH, tsl9_events_13cc2\n" :  :  : "memory");
    __builtin_unreachable();
}

/* Original0x13CB4-0x13CBA. */
FRAME void tsl9_events_13cb4(void)
{
    __asm__ volatile("lw ra, 12(sp)\n");
    __asm__ volatile("sw a0, 340(gp)\n");
}

/* Original0x13CBA-0x13CBC. */
REGION void tsl9_events_13cba(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    a0 = UINT32_C(0x0);
    __asm__ volatile("" : "+r"(a0) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13CBC-0x13CC2. */
FRAME void tsl9_events_13cbc(void)
{
    __asm__ volatile("addi sp, sp, 16\n");
    __asm__ volatile(".Levent_control_13cbe:\n.option push\n.option norvc\njal zero, .Levent_control_13cbe\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_events_137c0\n");
}

/* Original0x13CC2-0x13CC4. */
FRAME void tsl9_events_13cc2(void)
{
    __asm__ volatile("lw ra, 12(sp)\n");
}

/* Original0x13CC4-0x13CD4. */
REGION void tsl9_events_13cc4(void)
{
    register uint32_t a0 __asm__("a0"); INPUT(a0);
    register uint32_t a1 __asm__("a1"); INPUT(a1);
    register uint32_t a2 __asm__("a2"); INPUT(a2);
    register uint32_t a3 __asm__("a3"); INPUT(a3);
    a3 = UINT32_C(0x0);
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3) :  : "memory");
    a2 = UINT32_C(0x23);
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3) :  : "memory");
    a1 = UINT32_C(0x0);
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3) :  : "memory");
    __asm__ volatile(".Levent_hi_13ccc:\nauipc a0, 0\n.reloc .-4, R_RISCV_PCREL_HI20, tsl9_events_137c0\n" : "=r"(a0) :  : "memory");
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3) :  : "memory");
    __asm__ volatile(".option push\n.option norvc\naddi a0, a0, 0\n.option pop\n.reloc .-4, R_RISCV_PCREL_LO12_I, .Levent_hi_13ccc\n" : "+r"(a0) :  : "memory");
    __asm__ volatile("" : "+r"(a0), "+r"(a1), "+r"(a2), "+r"(a3) :  : "memory");
    __builtin_unreachable();
}

/* Original0x13CD4-0x13CDA. */
FRAME void tsl9_events_13cd4(void)
{
    __asm__ volatile("addi sp, sp, 16\n");
    __asm__ volatile(".Levent_control_13cd6:\n.option push\n.option norvc\njal zero, .Levent_control_13cd6\n.option pop\n.reloc .-4, R_RISCV_JAL, tsl9_callback_external_9124\n");
}

/* Original0x13CDA-0x13CDC. */
FRAME void tsl9_events_13cda(void)
{
    __asm__ volatile("ret\n");
}
