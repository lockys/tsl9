#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private packet receive candidate only; never execute on the host.
#endif

/* Diagnostic first candidate, not a C ABI replacement or flash-ready image.
 * C owns GPIO widths, selector, bytes, masks and packet validation. Explicit
 * architecture ports own the reserved frame and physical S0/S1/S2 state.
 * The loop tests then-live S0/S2 after each opaque SPI call, without silently
 * assuming ordinary C callee preservation. The full resident ABI stays open.
 */
static __attribute__((always_inline)) inline uint32_t transfer(uint32_t input)
{
    register uint32_t a0 __asm__("a0") = input;
    __asm__ volatile("jal ra, tsl9_spi_transfer_entry_16896\n"
                     : "+r"(a0) : : "a1", "a2", "a3", "a4", "a5", "memory");
    return a0;
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_receive_buffer_entry_16a7c(void)
{
    /* Original interleaving belongs to the private frame/alias contract. */
    __asm__ volatile("addi sp, sp, -48\nsw s1, 36(sp)\n"
                     "lui a5, 0x40011\nsw ra, 44(sp)\n"
                     "sw s0, 40(sp)\nsw s2, 32(sp)\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_packet_receive_body(void)
{
    register uint32_t channel __asm__("a0");
    register uintptr_t gpio __asm__("a5");
    __asm__ volatile("" : "=r"(channel), "=r"(gpio) : : "memory");
    register uint32_t selected __asm__("a4") = 1;
    __asm__ volatile("" : "+r"(selected), "+r"(channel), "+r"(gpio) : : "memory");
    __asm__ volatile("mv s1, a0\n" : : "r"(channel) : "memory");
    gpio -= UINT32_C(2048);
    __asm__ volatile("" : "+r"(gpio), "+r"(selected), "+r"(channel) : : "memory");
    if (channel == 1u)
        selected = 16;
    *(volatile uint32_t *)(gpio + 20u) = selected;

    register uint32_t command __asm__("a0") = 3;
    __asm__ volatile("" : "+r"(command) : : "memory");
    __asm__ volatile("sw a1, 12(sp)\n" : : : "memory");
    transfer(command);

    register uint32_t address __asm__("a1");
    __asm__ volatile("lw a1, 12(sp)\n" : "=r"(address) : : "memory");
    __asm__ volatile("li s0, 0\nli s2, 13\n" : : : "memory");
    transfer(address);

receive_next:
    {
        register uint32_t byte __asm__("a0") = transfer(0);
        register uintptr_t destination __asm__("a5");
        __asm__ volatile("addi %0, sp, 16\nadd %0, %0, s0\n"
                         : "=r"(destination) : : "memory");
        *(volatile uint8_t *)destination = (uint8_t)byte;
    }
    /* Physical branch preserves then-live S0/S2, including callee effects.
     * Thirteen actual iterations require the SPI provider's preserved state;
     * this open-call candidate does not manufacture that downstream fact. */
    __asm__ goto volatile("addi s0, s0, 1\nbne s0, s2, %l[receive_next]\n"
                          : : : "memory" : receive_next);

    gpio = UINT32_C(0x40011000);
    __asm__ volatile("" : "+r"(gpio) : : "memory");
    selected = 17;
    __asm__ volatile("" : "+r"(gpio), "+r"(selected) : : "memory");
    *(volatile uint32_t *)(gpio - UINT32_C(2032)) = selected;

    register uint32_t header __asm__("a5");
    __asm__ volatile("lbu %0, 17(sp)\n" : "=r"(header) : : "memory");
    register uint32_t unsupported __asm__("a4") = header & 24u;
    __asm__ volatile("" : "+r"(unsupported), "+r"(header) : : "memory");
    if (unsupported != 0u)
        goto finish;

    {
        register uint32_t length __asm__("a2");
        __asm__ volatile("lbu %0, 20(sp)\n" : "=r"(length) : : "memory");
        register uint32_t maximum __asm__("a3") = 7;
        __asm__ volatile("" : "+r"(maximum), "+r"(length), "+r"(header) : : "memory");
        length &= 15u;
        register uint32_t adjusted __asm__("a4") = (length - 1u) & 255u;
        __asm__ volatile("" : "+r"(adjusted), "+r"(length), "+r"(maximum), "+r"(header) : : "memory");
        if (adjusted > maximum)
            goto finish;

        register uint32_t identifier __asm__("a0");
        __asm__ volatile("lbu %0, 16(sp)\n" : "=r"(identifier) : : "memory");
        header >>= 5;
        __asm__ volatile("" : "+r"(header), "+r"(identifier) : : "memory");
        register uint32_t live_channel __asm__("a3");
        __asm__ volatile("mv %0, s1\n" : "=r"(live_channel) : : "memory");
        identifier <<= 3;
        __asm__ volatile("" : "+r"(identifier), "+r"(header) : : "memory");
        register uintptr_t payload __asm__("a1");
        __asm__ volatile("addi %0, sp, 21\n" : "=r"(payload) : : "memory");
        identifier |= header;
        __asm__ volatile("jal ra, tsl9_ring_insert_entry_12bc8\n"
                         : "+r"(identifier), "+r"(payload), "+r"(length), "+r"(live_channel)
                         : : "a4", "a5", "memory");
    }

finish:
    __asm__ volatile("lw ra, 44(sp)\nlw s0, 40(sp)\nlw s1, 36(sp)\n"
                     "lw s2, 32(sp)\naddi sp, sp, 48\nret\n" : : : "memory");
    __builtin_unreachable();
}
