#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private startup ABI only; never execute on the host.
#endif

static __attribute__((always_inline)) inline uint32_t live_gp(void)
{
    register uint32_t value __asm__("gp");
    __asm__ volatile("" : "=r"(value) : : "memory");
    return value;
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn)) void tsl9_runtime_reset_memory(void)
{
    register uint32_t last_word __asm__("t0");
    __asm__ volatile("" : "=r"(last_word) : : "memory");
    register uint32_t source __asm__("a0") = UINT32_C(0x1ab60);
    register uint32_t destination __asm__("a1") = live_gp();
    register uint32_t copy_end __asm__("a2") = (uint32_t)(live_gp() + UINT32_C(128));
    __asm__ volatile("" : "+r"(source), "+r"(destination), "+r"(copy_end), "+r"(last_word) : : "memory");
    if (destination < copy_end) {
        do {
            last_word = *(volatile uint32_t *)(uintptr_t)source;
            __asm__ volatile("" : "+r"(last_word) : : "memory");
            *(volatile uint32_t *)(uintptr_t)destination = last_word;
            __asm__ volatile("" : : "r"(source), "r"(destination), "r"(copy_end), "r"(last_word) : "memory");
            source = (uint32_t)(source + 4u);
            __asm__ volatile("" : "+r"(source) : : "memory");
            destination = (uint32_t)(destination + 4u);
            __asm__ volatile("" : "+r"(destination) : : "memory");
        } while (destination < copy_end);
    }
    source = (uint32_t)(live_gp() + UINT32_C(128));
    destination = UINT32_C(0x2000c958);
    __asm__ volatile("" : "+r"(source), "+r"(destination), "+r"(copy_end), "+r"(last_word) : : "memory");
    if (source < destination) {
        do {
            *(volatile uint32_t *)(uintptr_t)source = 0;
            __asm__ volatile("" : : "r"(source), "r"(destination), "r"(copy_end), "r"(last_word) : "memory");
            source = (uint32_t)(source + 4u);
            __asm__ volatile("" : "+r"(source) : : "memory");
        } while (source < destination);
    }
    /* Normal memory-slice output. No extra memory read, stack frame or call. */
    register uint32_t t0 __asm__("t0") = last_word;
    register uint32_t a0 __asm__("a0") = source;
    register uint32_t a1 __asm__("a1") = destination;
    register uint32_t a2 __asm__("a2") = copy_end;
    __asm__ volatile("" : : "r"(t0), "r"(a0), "r"(a1), "r"(a2) : "memory");
    /* Architectural CSR/transfer port follows the readable C loops.
     * Fixed nominal placement is checked after the actual link. LUI-based
     * address formation differs from original AUIPC intermediates.
     * The last JAL targets an external, UNIMPLEMENTED resident at0x40000. */
    __asm__ volatile(
        ".option push\n.option norelax\n.option rvc\n"
        "li t0, 31\ncsrw 0xbc0, t0\n"
        "li t0, 3\ncsrw 0x804, t0\n"
        ".option norvc\n"
        "lui t0, 2\naddi t0, t0, -1912\ncsrs mstatus, t0\n"
        "lui t0, 8\naddi t0, t0, 56\nori t0, t0, 3\ncsrw mtvec, t0\n"
        "jal ra, tsl9_clock_prefix_entry\n"
        "lui t0, 9\naddi t0, t0, 8\ncsrw mepc, t0\n"
        /* At checked PC18730, this displacement reaches40000; no provider
         * or ELF symbol is created at the destination. */
        "jal zero, . + 0x278d0\n.option pop\n" : : : "memory");
    __builtin_unreachable();
}
