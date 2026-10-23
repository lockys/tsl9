#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private record-dispatch regions only; never execute on a host or device.
#endif

/* Original [0x12A08,0x12A6E), including the post-RET tagged path.
 * C supplies constants, argument arithmetic and the fresh resident word load.
 * Physical S0/SP reads, record/stack operations, frame/call/branch/return ports
 * retain original ordering and unknown callee effects. No ordinary C ABI,
 * successful transmission or peripheral identity is inferred from these cuts.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define FRAME ENTRY __attribute__((naked, used, aligned(2)))

FRAME void tsl9_queue_external_12a08(void)
{
    __asm__ volatile("addi sp, sp, -48\nsw s0, 40(sp)\nsw ra, 44(sp)\nmv s0, a0\n"
                     ".Lrecord_status_call:\njal ra, .Lrecord_status_call\n"
                     ".reloc .-4, R_RISCV_JAL, tsl9_queue_external_81aa\n");
}

REGION void tsl9_dispatch_status_12a14(void)
{
    __asm__ volatile(".Lrecord_status_nonzero:\nc.bnez a0, .Lrecord_status_nonzero\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_dispatch_query_12a20\n"
                     : : : "memory");
    __builtin_unreachable();
}

REGION void tsl9_dispatch_ID_12a16(void)
{
    register uint32_t identifier __asm__("a4");
    __asm__ volatile("lhu a4, 0(s0)\n" : "=r"(identifier) : : "a5", "memory");
    register uint32_t one __asm__("a5") = 1;
    __asm__ volatile(".Lrecord_ID_rejected:\nbne a4, a5, .Lrecord_ID_rejected\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_dispatch_finish_12a5e\n"
                     : : "r"(identifier), "r"(one) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_dispatch_query_12a20(void)
{
    register uint32_t index __asm__("a0") = 0;
    __asm__ volatile(".Lrecord_query_call:\njal ra, .Lrecord_query_call\n"
                     ".reloc .-4, R_RISCV_JAL, tsl9_dispatch_external_821e\n"
                     : "+r"(index) : : "a1", "a2", "a3", "a4", "a5", "memory");
    __asm__ volatile(".Lrecord_query_zero:\nc.beqz a0, .Lrecord_query_zero\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_dispatch_finish_12a5e\n"
                     : : "r"(index) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_dispatch_tag_12a28(void)
{
    register uint32_t tag __asm__("a5");
    __asm__ volatile("lbu a5, 11(s0)\n" : "=r"(tag) : : "memory");
    __asm__ volatile(".Lrecord_tagged:\nc.bnez a5, .Lrecord_tagged\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_dispatch_tagged_12a66\n"
                     : : "r"(tag) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_dispatch_copy_12a2e(void)
{
    register uint32_t provider __asm__("a5");
    register uint32_t length __asm__("a2");
    __asm__ volatile("lhu a5, 0(s0)\nlbu a2, 2(s0)\n"
                     "sh zero, 20(sp)\nsw a5, 12(sp)\nsb a2, 22(sp)\n"
                     : "=r"(provider), "=r"(length) : : "memory");
    provider = 0x40000;
    __asm__ volatile("" : "+r"(provider) : "r"(length) : "memory");
    provider = *(volatile uint32_t *)(uintptr_t)(provider + 76);
    __asm__ volatile("addi a1, s0, 3\naddi a0, sp, 23\njalr a5\n"
                     : : "r"(provider), "r"(length)
                     : "a0", "a1", "a3", "a4", "memory");
    __builtin_unreachable();
}

REGION void tsl9_dispatch_peripheral_12a50(void)
{
    register uint32_t base __asm__("a0") = 0x40006000;
    register uint32_t record __asm__("a1");
    __asm__ volatile("addi a1, sp, 12\n" : "=r"(record), "+r"(base) : : "memory");
    base += 1024;
    __asm__ volatile(".Lrecord_peripheral_call:\njal ra, .Lrecord_peripheral_call\n"
                     ".reloc .-4, R_RISCV_JAL, tsl9_dispatch_external_18ca4\n"
                     : : "r"(base), "r"(record)
                     : "a2", "a3", "a4", "a5", "memory");
    __builtin_unreachable();
}

FRAME void tsl9_dispatch_finish_12a5e(void)
{
    __asm__ volatile("lw ra, 44(sp)\nlw s0, 40(sp)\naddi sp, sp, 48\nret\n");
}

FRAME void tsl9_dispatch_tagged_12a66(void)
{
    __asm__ volatile("mv a0, s0\n.Lrecord_tag_call:\njal ra, .Lrecord_tag_call\n"
                     ".reloc .-4, R_RISCV_JAL, tsl9_dispatch_external_16b7c\n"
                     ".Lrecord_tag_finish:\nc.j .Lrecord_tag_finish\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_dispatch_finish_12a5e\n");
}
