#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error This component requires RV32; no host hardware driver is provided.
#endif

/* These are register/call-boundary ports, not copied function instructions.
 * Each JAL remains relocatable and must bind to a genuine C definition. */
#define WF_CALL_ONE(name, value, ...) __extension__ ({ \
    register uint32_t wf_a0 __asm__("a0") = (value); \
    __asm__ volatile("jal ra, " #name : "+r"(wf_a0) : : "ra", __VA_ARGS__, "memory"); \
    wf_a0; \
})

static __attribute__((always_inline)) inline uint32_t save_destination(uint32_t incoming)
{
    register uint32_t saved __asm__("s0");
    __asm__ volatile("mv %0, %1" : "=r"(saved) : "r"(incoming) : "memory");
    return saved;
}

static __attribute__((always_inline)) inline uint32_t reload_source(volatile uint32_t *slot)
{
    register uint32_t source __asm__("a2") = *slot;
    __asm__ volatile("" : "+r"(source) : : "memory");
    return source;
}

static __attribute__((always_inline)) inline uint32_t program(uint32_t destination, uint32_t source)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a2 __asm__("a2") = source;
    /* Keep fresh A2 available while setting A0, before the A1 argument move. */
    __asm__ volatile("mv %0, %2" : "=r"(a0), "+r"(a2) : "r"(destination) : "memory");
    register uint32_t a1 __asm__("a1") = a2;
    __asm__ volatile("jal ra, tsl9_flash_program_18ef2" : "+r"(a0) : "r"(a1)
                     : "ra", "a2", "a3", "a4", "a5", "a6", "memory");
    return a0;
}

struct source_frame {
    uint32_t reserved_before[3];
    uint32_t source_slot;
    uint32_t reserved_after[2];
};
typedef char source_frame_extent_is_24[(sizeof(struct source_frame) == 24) ? 1 : -1];

#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_nv_write_frame_contract_197be(uint32_t destination,
                                          uint32_t unused_a1,
                                          uint32_t source)
{
    volatile struct source_frame frame;
    uint32_t saved_destination, fresh_source, program_result;
    (void)unused_a1;
    /* Reserve the whole C stack object without touching reserved bytes. */
    __asm__ volatile("" : "=m"(frame) : : "memory");
    frame.source_slot = source;
    saved_destination = save_destination(destination);
    (void)WF_CALL_ONE(tsl9_flash_unlock_18e98, destination, "a1", "a3", "a4", "a5");
    (void)WF_CALL_ONE(tsl9_flash_erase_18ec4, saved_destination, "a1", "a3", "a4", "a5");
    fresh_source = reload_source(&frame.source_slot);
    program_result = program(saved_destination, fresh_source);
    (void)WF_CALL_ONE(tsl9_flash_lock_18eb6, program_result, "a3", "a4", "a5");
    (void)WF_CALL_ONE(tsl9_delay_registers_19764, 1u, "a2", "a3", "a4", "a5");
    return 0;
}
