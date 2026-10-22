#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error This component requires RV32 and must not run on the host.
#endif

#ifdef __cplusplus
#define LINKAGE extern "C"
#else
#define LINKAGE
#endif

struct clock_frame {
    uint32_t reserved[2];
    uint32_t count;
    uint32_t ready;
};
typedef char frame_size_is_16[(sizeof(struct clock_frame) == 16) ? 1 : -1];

/* Private architectural entry: the first MMIO read precedes the frame.
 * There is no branch to the C body. The linker MUST prove exact adjacency;
 * never call the C body using a normal C ABI or place these functions alone. */
LINKAGE __attribute__((naked, used, aligned(2))) void tsl9_clock_prefix_entry(void)
{
    __asm__ volatile(
        "lui a5, 0x40021\n"
        "lw a4, 0(a5)\n"
        "lui a3, 0xf8ff0\n"
        "addi sp, sp, -16\n");
}

LINKAGE __attribute__((used, noinline, aligned(2))) void tsl9_clock_prefix_body(void)
{
    register uint32_t first_sample __asm__("a4");
    register volatile struct clock_frame *frame __asm__("sp");
    /* Import the entry's actual register sample and already allocated frame.
     * Empty port, no resampling, stack allocation, initialization or call. */
    __asm__ volatile("" : "=r"(first_sample), "=r"(frame) : : "memory");
    volatile uint32_t *const reg =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40021000);

    reg[0] = first_sample | UINT32_C(1);
    reg[1] = reg[1] & UINT32_C(0xf8ff0000);
    reg[0] = reg[0] & UINT32_C(0xfef6ffff);
    reg[0] = reg[0] & UINT32_C(0xfffbffff);
    reg[1] = reg[1] & UINT32_C(0xff80ffff);
    reg[2] = UINT32_C(0x009f0000);
    frame->count = 0;
    frame->ready = 0;
    reg[0] = reg[0] | UINT32_C(0x10000);
    for (;;) {
        frame->ready = reg[0] & UINT32_C(0x20000);
        frame->count = (uint32_t)(frame->count + 1u);
        if (frame->ready != 0u)
            break;
        if (frame->count == UINT32_C(0x1000))
            break;
    }
    if ((reg[0] & UINT32_C(0x20000)) != 0u)
        frame->ready = 1;
    else
        frame->ready = 0;
    const uint32_t selected_ready = frame->ready;
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
            /* Original unbounded poll. */
        }
        reg[1] = reg[1] & UINT32_C(0xfffffffc);
        reg[1] = reg[1] | UINT32_C(2);
        while ((reg[1] & UINT32_C(12)) != UINT32_C(8)) {
            /* Original unbounded poll. */
        }
        final_a4 = 8u;
        final_a5 = 8u;
    }
    register uint32_t a2 __asm__("a2") = UINT32_C(0x20000);
    register uint32_t a3 __asm__("a3") = UINT32_C(0x40021000);
    register uint32_t a4 __asm__("a4") = final_a4;
    register uint32_t a5 __asm__("a5") = final_a5;
    __asm__ volatile("" : : "r"(a2), "r"(a3), "r"(a4), "r"(a5) : "memory");
    __asm__ volatile("addi sp, sp, 16\nret\n" : : : "memory");
    __builtin_unreachable();
}
