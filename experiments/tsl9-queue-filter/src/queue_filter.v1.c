#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private filter regions only; never execute on a host or device.
#endif

/* Original [0x82D2,0x838E), including the reachable post-RET cold block.
 * C owns masks, shifts, OR, length arithmetic and constants. Explicit ports
 * preserve physical frame/S0..S9/SP state, fresh reads and opaque calls.
 * These seven private regions are not ordinary independent C ABI entries.
 * S4 is set before the length rejection: nonzero does not prove forwarding.
 */
#ifdef __cplusplus
#define ENTRY extern "C"
#else
#define ENTRY
#endif
#define REGION ENTRY __attribute__((used, noinline, noreturn, aligned(2)))
#define FRAME ENTRY __attribute__((naked, used, aligned(2)))

FRAME void tsl9_queue_external_82d2(void)
{
    __asm__ volatile("addi sp, sp, -64\nsw s3, 44(sp)\nlui s3, 0x10\n"
                     "sw s1, 52(sp)\nsw s2, 48(sp)\nsw s4, 40(sp)\n"
                     "sw s5, 36(sp)\nsw s6, 32(sp)\nsw s7, 28(sp)\n"
                     "sw s8, 24(sp)\nsw s9, 20(sp)\nsw ra, 60(sp)\n"
                     "sw s0, 56(sp)\nmv s1, a0\nli s2, 0\nli s4, 0\n"
                     /* PC=0x82F2. Original placement is a separate obligation. */
                     "auipc s5, 0x20004\naddi s5, s5, 1186\n"
                     "addi s3, s3, -2\nli s6, 2\nli s7, 8\n"
                     "addi s8, a0, 3\nlui s9, 0x40\n");
}

REGION void tsl9_filter_scan_8308(void)
{
    register uint32_t value __asm__("a5");
    __asm__ volatile("slli s0, s2, 2\nadd s0, s0, s5\nlhu a5, 2(s0)\n"
                     : "=r"(value) : : "memory");
    __asm__ volatile(".Lfilter_sentinel:\nbeq s3, a5, .Lfilter_sentinel\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_filter_test_836a\n"
                     : : "r"(value) : "memory");
    __asm__ volatile("lbu a5, 5(s0)\n" : "=r"(value) : : "memory");
    __asm__ volatile(".Lfilter_kind:\nbne s6, a5, .Lfilter_kind\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_filter_test_836a\n"
                     : : "r"(value) : "memory");
    __asm__ volatile("lbu a5, 4(s0)\n" : "=r"(value) : : "memory");
    value &= 255u;
    __asm__ volatile(".Lfilter_disabled:\nc.beqz a5, .Lfilter_disabled\n"
                     ".reloc .-2, R_RISCV_RVC_BRANCH, tsl9_filter_test_836a\n"
                     : : "r"(value) : "memory");
    __builtin_unreachable();
}

REGION void tsl9_filter_pack_8328(void)
{
    register uint32_t selected __asm__("a5");
    register uint32_t length __asm__("a2");
    __asm__ volatile("" : "=r"(selected) : : "memory");
    __asm__ volatile("lbu a2, 2(s1)\nmv s4, a5\n"
                     : "=r"(length) : "r"(selected) : "memory");
    __asm__ volatile(".Lfilter_long:\nbltu s7, a2, .Lfilter_long\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_filter_test_836a\n"
                     : : "r"(length) : "memory");
    register uint32_t identifier __asm__("a3");
    __asm__ volatile("lhu a3, 0(s1)\nlbu a5, 11(s1)\nmv a1, s8\n"
                     "sb a3, 5(sp)\n"
                     : "=r"(identifier), "=r"(selected) : "r"(length) : "a1", "memory");
    register uint32_t channel_bits __asm__("a4") = selected << 4;
    __asm__ volatile("" : "+r"(channel_bits), "+r"(selected), "+r"(identifier)
                     : "r"(length) : "memory");
    selected = identifier >> 8;
    __asm__ volatile("" : "+r"(selected), "+r"(channel_bits), "+r"(identifier)
                     : "r"(length) : "memory");
    selected |= channel_bits;
    __asm__ volatile("sb a5, 4(sp)\nlw a5, 76(s9)\naddi a0, sp, 6\n"
                     : "+r"(selected) : "r"(length), "r"(identifier), "r"(channel_bits)
                     : "a0", "memory");
    __asm__ volatile("jalr a5\n" : : "r"(selected), "r"(length)
                     : "a0", "a1", "a3", "a4", "memory");
    __builtin_unreachable();
}

REGION void tsl9_filter_emit_8358(void)
{
    register uint32_t length __asm__("a3");
    __asm__ volatile("lbu a3, 2(s1)\nlhu a0, 2(s0)\naddi a2, sp, 4\n"
                     : "=r"(length) : : "a0", "a2", "memory");
    length += 2;
    __asm__ volatile("" : "+r"(length) : : "memory");
    register uint32_t command __asm__("a1") = 192;
    __asm__ volatile(".Lfilter_emit:\nc.jal .Lfilter_emit\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_filter_external_8a56\n"
                     : : "r"(command), "r"(length)
                     : "a0", "a2", "a4", "a5", "memory");
    __builtin_unreachable();
}

REGION void tsl9_filter_test_836a(void)
{
    __asm__ volatile(".Lfilter_second:\nbeq s2, zero, .Lfilter_second\n"
                     ".reloc .-4, R_RISCV_BRANCH, tsl9_filter_second_838a\n"
                     : : : "memory");
    __builtin_unreachable();
}

FRAME void tsl9_filter_finish_836e(void)
{
    __asm__ volatile("lw ra, 60(sp)\nlw s0, 56(sp)\nmv a0, s4\n"
                     "lw s1, 52(sp)\nlw s2, 48(sp)\nlw s3, 44(sp)\n"
                     "lw s4, 40(sp)\nlw s5, 36(sp)\nlw s6, 32(sp)\n"
                     "lw s7, 28(sp)\nlw s8, 24(sp)\nlw s9, 20(sp)\n"
                     "addi sp, sp, 64\nret\n");
}

FRAME void tsl9_filter_second_838a(void)
{
    __asm__ volatile("li s2, 1\n.Lfilter_scan:\nc.j .Lfilter_scan\n"
                     ".reloc .-2, R_RISCV_RVC_JUMP, tsl9_filter_scan_8308\n");
}
