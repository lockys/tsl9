#include <stdint.h>

#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private receive wrapper only; never execute on the host.
#endif

/* Every opaque call may change the working bank. The architectural frame
 * ports own reserved RA/SP/S0/S1. Import S0/S1 again at their actual
 * observation points instead of assuming an ordinary C callee ABI.
 * Clobber lists constrain only the C allocator bank A0..A5. Other registers
 * stay reserved; the downstream resident provider's full effects are unknown. */
static __attribute__((always_inline)) inline uint32_t live_s1(void)
{
    register uint32_t value __asm__("a0");
    __asm__ volatile("mv %0, s1\n" : "=r"(value) : : "memory");
    return value;
}

static __attribute__((always_inline)) inline uint32_t read_status(void)
{
    register uint32_t a0 __asm__("a0");
    register uint32_t a1 __asm__("a1");
    __asm__ volatile("" : "=r"(a0), "=r"(a1) : : "memory");
    __asm__ volatile("jal ra, tsl9_register_read_entry_16994\n"
                     : "+r"(a0), "+r"(a1)
                     : : "a2", "a3", "a4", "a5", "memory");
    return a0;
}

static __attribute__((always_inline)) inline void receive_buffer(uint32_t address)
{
    register uint32_t a1 __asm__("a1") = address;
    __asm__ volatile("" : "+r"(a1) : : "memory");
    register uint32_t a0 __asm__("a0") = live_s1();
    __asm__ volatile("" : "+r"(a0), "+r"(a1) : : "memory");
    __asm__ volatile("jal ra, tsl9_receive_buffer_entry_16a7c\n"
                     : "+r"(a0), "+r"(a1)
                     : : "a2", "a3", "a4", "a5", "memory");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((naked, used, aligned(2))) void tsl9_receive_entry_16b0a(void)
{
    /* Original order includes A1 setup before frame-slot writes. */
    __asm__ volatile("addi sp, sp, -16\nli a1, 44\nsw s0, 8(sp)\n"
                     "sw s1, 4(sp)\nsw ra, 12(sp)\nmv s1, a0\n");
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn, aligned(2))) void tsl9_receive_body(void)
{
    register uint32_t status __asm__("a0") = read_status();
    register uint32_t first_bit __asm__("a5") = status & UINT32_C(1);
    __asm__ volatile("" : "+r"(first_bit), "+r"(status) : : "memory");
    __asm__ volatile("mv s0, a0\n" : : "r"(status), "r"(first_bit) : "memory");
    if (first_bit != 0u)
        receive_buffer(UINT32_C(0x61));

    /* This architecture port consumes then-live S0, including any effects
     * of the opaque first callee. Binding a C output to S0 causes LLVM18
     * to insert another frame. The explicit port preserves the original
     * physical S0 update and branch without assuming callee preservation. */
    __asm__ goto volatile("andi s0, s0, 2\nbeqz s0, %l[finish]\n"
                          : : : "memory" : finish);
    receive_buffer(UINT32_C(0x71));

finish:

    /* Fresh stack-slot reads after the last possible callee, in original order. */
    __asm__ volatile("lw s0, 8(sp)\nlw ra, 12(sp)\n" : : : "memory");
    register uint32_t a0 __asm__("a0") = live_s1();
    __asm__ volatile("" : "+r"(a0) : : "memory");
    __asm__ volatile("lw s1, 4(sp)\n" : : : "memory");
    register uint32_t a2 __asm__("a2") = 0;
    __asm__ volatile("" : "+r"(a2) : : "memory");
    register uint32_t a1 __asm__("a1") = UINT32_C(0x2c);
    __asm__ volatile("addi sp, sp, 16\nj tsl9_register_write_entry_16a30\n"
                     : : "r"(a0), "r"(a1), "r"(a2) : "memory");
    __builtin_unreachable();
}
