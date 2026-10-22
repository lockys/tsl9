#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 is required; this source is not a host hardware driver.
#endif

#define NR_FIXED(reg, value) __extension__ ({ \
    register uint32_t nr_value __asm__(reg) = (uint32_t)(value); \
    __asm__ volatile("" : "+r"(nr_value) : : "memory"); nr_value; \
})

/* Preserve the original unshifted count in physical A1 at the A2 result
 * boundary. The arithmetic is still a genuine C uint32_t shift. */
static __attribute__((always_inline)) inline uint32_t count_port(uint32_t words, uint32_t saved_destination)
{
    register uint32_t original_count __asm__("a1") = words;
    register uint32_t destination __asm__("a4") = saved_destination;
    __asm__ volatile("" : "+r"(original_count) : "r"(destination) : "memory");
    register uint32_t byte_count __asm__("a2") = (uint32_t)(original_count << 2);
    __asm__ volatile("" : "+r"(byte_count) : "r"(original_count) : "memory");
    return byte_count;
}

static __attribute__((always_inline)) inline uint32_t destination_port(uint32_t value)
{
    register uint32_t destination __asm__("a4");
    __asm__ volatile("mv %0, %1" : "=r"(destination) : "r"(value) : "memory");
    return destination;
}

/* This describes only the reviewed normal three-register projection. The
 * freshly selected installed provider and its full ABI are still unknown. */
typedef uint32_t (*nr_copy_projection)(uint32_t, uint32_t, uint32_t);

static __attribute__((always_inline)) inline void copy_call_port(
    uint32_t target, uint32_t destination, uint32_t source, uint32_t bytes)
{
    register uint32_t a0 __asm__("a0") = source;
    register uint32_t a1 __asm__("a1");
    register uint32_t a2 __asm__("a2") = bytes;
    register uint32_t a4 __asm__("a4") = destination;
    register uint32_t a5 __asm__("a5") = target;
    /* The fresh provider is opaque. This is only its register-call boundary;
     * the slot read and 32-bit byte-count calculation remain C above it. */
    __asm__ volatile("mv %1, %0\n\tmv %0, %3\n\tjalr ra, 0(%4)"
                     : "+r"(a0), "=&r"(a1), "+r"(a2), "+r"(a4), "+r"(a5)
                     : : "ra", "t0", "t1", "t2", "a3", "a6", "a7",
                         "t3", "t4", "t5", "t6", "memory");
}

#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_nv_read_live_count_1979a(uint32_t source, uint32_t words, uint32_t destination)
{
    const uint32_t slot_base = NR_FIXED("a5", UINT32_C(0x40000));
    const uint32_t target = NR_FIXED("a5", *(volatile uint32_t *)(uintptr_t)(slot_base + 76u));
    const uint32_t saved_destination = destination_port(destination);
    const uint32_t bytes = count_port(words, saved_destination);
    copy_call_port(target, saved_destination, source, bytes);
    return 0;
}
