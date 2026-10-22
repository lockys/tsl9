#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error This source requires RV32; it is not a host hardware driver.
#endif

struct clock_frame {
    uint32_t reserved[2];
    uint32_t count;
    uint32_t ready;
};
typedef char clock_frame_is_16[(sizeof(struct clock_frame) == 16) ? 1 : -1];

/* BOOT ID2580 [2C78,2D62) and Runtime ID2966 [1874A,18834) are
 * byte-identical234B. This C body preserves ordinary volatile accesses,
 * including live stack fields. It does not prove the original register,
 * fault/IRQ prefix, physical memory map or clock configuration. */
#ifdef __cplusplus
extern "C"
#endif
void tsl9_boot_clock_registers_2c78(void)
{
    volatile uint32_t *const reg =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40021000);
    volatile struct clock_frame frame;
    /* Reserve storage without adding writes to the original reserved words. */
    __asm__ volatile("" : "=m"(frame) : : "memory");

    reg[0] = reg[0] | UINT32_C(1);
    reg[1] = reg[1] & UINT32_C(0xf8ff0000);
    reg[0] = reg[0] & UINT32_C(0xfef6ffff);
    reg[0] = reg[0] & UINT32_C(0xfffbffff);
    reg[1] = reg[1] & UINT32_C(0xff80ffff);
    reg[2] = UINT32_C(0x009f0000);
    frame.count = 0;
    frame.ready = 0;
    reg[0] = reg[0] | UINT32_C(0x10000);
    for (;;) {
        frame.ready = reg[0] & UINT32_C(0x20000);
        frame.count = (uint32_t)(frame.count + 1u);
        if (frame.ready != 0u)
            break;
        if (frame.count == UINT32_C(0x1000))
            break;
    }
    /* Fresh status read after the loop; the last sample is not reused. */
    if ((reg[0] & UINT32_C(0x20000)) != 0u)
        frame.ready = 1;
    else
        frame.ready = 0;
    const uint32_t selected_ready = frame.ready;
    uint32_t final_a4 = selected_ready;
    uint32_t final_a5 = 1u;
    if (selected_ready == 1u) {
        reg[1] = reg[1];
        reg[1] = reg[1];
        reg[1] = reg[1] | UINT32_C(0x400);
        reg[1] = reg[1] & UINT32_C(0xffc0ffff);
        reg[1] = reg[1] | UINT32_C(0x00290000);
        reg[0] = reg[0] | UINT32_C(0x01000000);
        while ((reg[0] & UINT32_C(0x02000000)) == 0u) {
            /* Original has no software timeout on this loop. */
        }
        reg[1] = reg[1] & UINT32_C(0xfffffffc);
        reg[1] = reg[1] | UINT32_C(2);
        while ((reg[1] & UINT32_C(12)) != UINT32_C(8)) {
            /* Observation budgets must not become firmware timeouts. */
        }
        final_a4 = 8u;
        final_a5 = 8u;
    }
    /* Normal exit register projection only; no extra MMIO/stack sample. */
    register uint32_t a2 __asm__("a2") = UINT32_C(0x20000);
    register uint32_t a3 __asm__("a3") = UINT32_C(0x40021000);
    register uint32_t a4 __asm__("a4") = final_a4;
    register uint32_t a5 __asm__("a5") = final_a5;
    __asm__ volatile("" : : "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
}
