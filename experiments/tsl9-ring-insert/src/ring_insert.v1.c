#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private ring regions only; never execute on the host.
#endif

/* C owns index/stride arithmetic, volatile memory widths and value truncation.
 * Physical frame, PC-derived base and cross-region/control boundaries remain
 * explicit architecture ports. These regions are not ordinary C ABI functions.
 * The resident pointer's identity and full preservation contract remain unknown.
 */
#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_ring_insert_entry_12bc8(void)
{
    __asm__ volatile("addi sp, sp, -16\nsw ra, 12(sp)\nsw s0, 8(sp)\nsw s1, 4(sp)\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_ring_init_12bd0(void)
{
    register uint32_t index __asm__("a5") = 0;
    __asm__ volatile("" : "+r"(index) : : "memory");
    register uintptr_t base __asm__("a7");
    /* This port is valid only at PC=0x12BD2: base becomes 0x2000C038.
     * The nominal linker and checker must prove placement, not assume it. */
    __asm__ volatile("auipc a7, 0x1fff9\naddi a7, a7, 1126\n"
                     : "=r"(base) : "r"(index) : "memory");
    register uint32_t stride __asm__("t3") = 12;
    __asm__ volatile("" : "+r"(stride) : : "memory");
    register uint32_t count __asm__("t1") = 32;
    __asm__ volatile("" : "+r"(count) : "r"(stride), "r"(base), "r"(index) : "memory");
    __builtin_unreachable();
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_ring_scan_12be0(void)
{
    register uint32_t result __asm__("a0");
    register uintptr_t payload __asm__("a1");
    register uint32_t length __asm__("a2");
    register uint32_t channel __asm__("a3");
    register uint32_t index __asm__("a5");
    register uintptr_t base __asm__("a7");
    register uint32_t stride __asm__("t3");
    register uint32_t count __asm__("t1");
    __asm__ volatile("" : "=r"(result), "=r"(payload), "=r"(length), "=r"(channel),
                         "=r"(index), "=r"(base), "=r"(stride), "=r"(count) : : "memory");
    register uint32_t offset __asm__("a4") = index * stride;
    __asm__ volatile("" : "+r"(offset), "+r"(base) : : "memory");
    register uintptr_t slot __asm__("s0") = base + offset;
    __asm__ volatile("" : "+r"(slot) : : "memory");
    register uint32_t occupied __asm__("a6") = *(volatile uint16_t *)slot;
    __asm__ volatile("" : "+r"(occupied) : : "memory");
    occupied <<= 16;
    __asm__ volatile("" : "+r"(occupied) : : "memory");
    occupied >>= 16;
    __asm__ volatile(".Lring_occupied:\nbne a6, zero, .Lring_occupied\n"
                     ".reloc .Lring_occupied, R_RISCV_BRANCH, tsl9_ring_advance_12c1c\n"
                     : : "r"(occupied), "r"(result), "r"(payload), "r"(length),
                         "r"(channel), "r"(index), "r"(base), "r"(stride), "r"(count) : "memory");

    *(volatile uint16_t *)slot = (uint16_t)result;
    *(volatile uint8_t *)(slot + 2u) = (uint8_t)length;
    register uintptr_t provider __asm__("a5") = *(volatile uint32_t *)UINT32_C(0x0004004c);
    __asm__ volatile("" : "+r"(provider), "+r"(offset) : : "memory");
    offset += 3;
    __asm__ volatile("mv s1, a3\n" : "+r"(offset), "+r"(base) : "r"(channel) : "memory");
    result = base + offset;
    __asm__ volatile("jalr a5\n"
                     : "+r"(result), "+r"(payload), "+r"(length)
                     : "r"(provider) : "a3", "a4", "a6", "a7", "t1", "t3", "memory");

    /* Read physical S0/S1 after the opaque resident call; do not substitute
     * the earlier C slot/channel values or assume callee-save behavior. */
    register uintptr_t live_slot __asm__("s0");
    register uint32_t live_tag __asm__("s1");
    __asm__ volatile("" : "=r"(live_slot), "=r"(live_tag) : : "memory");
    *(volatile uint8_t *)(live_slot + 11u) = (uint8_t)live_tag;
    __asm__ volatile("" : : "r"(result) : "memory");
    __builtin_unreachable();
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_ring_finish_12c12(void)
{
    __asm__ volatile("lw ra, 12(sp)\nlw s0, 8(sp)\nlw s1, 4(sp)\naddi sp, sp, 16\nret\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_ring_advance_12c1c(void)
{
    register uint32_t index __asm__("a5");
    register uint32_t count __asm__("t1");
    __asm__ volatile("" : "=r"(index), "=r"(count) : : "memory");
    index += 1;
    __asm__ volatile(".Lring_continue:\nbne a5, t1, .Lring_continue\n"
                     ".reloc .Lring_continue, R_RISCV_BRANCH, tsl9_ring_scan_12be0\n"
                     : : "r"(index), "r"(count) : "memory");
    __asm__ volatile(".Lring_full:\nc.j .Lring_full\n"
                     ".reloc .Lring_full, R_RISCV_RVC_JUMP, tsl9_ring_finish_12c12\n" : : : "memory");
    __builtin_unreachable();
}
