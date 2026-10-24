#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 private main entry only; never execute on the host.
#endif

/* Private architectural ports, not ordinary callable C ABI helpers.
 * No provider is defined for either external call. */
static __attribute__((always_inline)) inline void frame_enter(void)
{
    __asm__ volatile("addi sp, sp, -16\nsw ra, 12(sp)\n" : : : "memory");
}

static __attribute__((always_inline)) inline void first_call(void)
{
    register unsigned int call_ra __asm__("ra");
    /* A local mnemonic fixes the original compressed width; the explicit
     * relocation binds its real external provider role without an ABS alias.
     * An unresolved external c.jal mnemonic is widened by this assembler. */
    __asm__ volatile(
        "1: c.jal 1b\n"
        ".reloc 1b, R_RISCV_RVC_JUMP, tsl9_runtime_entry_9250\n"
        : "=r"(call_ra) : : "memory");
}

static __attribute__((always_inline)) inline void second_call(void)
{
    register unsigned int call_ra __asm__("ra");
    __asm__ volatile("jal ra, tsl9_runtime_entry_8180\n" : "=r"(call_ra) : : "memory");
}

static __attribute__((always_inline, noreturn)) inline void frame_return(void)
{
    __asm__ volatile("lw ra, 12(sp)\nli a0, 0\naddi sp, sp, 16\nret\n" : : : "memory");
    __builtin_unreachable();
}

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline, noreturn)) void tsl9_runtime_main_private(void)
{
    frame_enter();
    first_call();
    second_call();
    frame_return();
}
