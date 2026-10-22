#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 startup ports only; never execute on the host.
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* GP/SP must be established before any C prologue. This private entry's
 * first16B use real owned RAM/stack section endpoints; the extra JAL x0
 * reaches the readable C memory core without changing incoming RA. */
__attribute__((naked,used)) void tsl9_runtime_reset_entry(void)
{
    __asm__ volatile(
        ".option push\n.option norelax\n.option norvc\n"
        ".Lreset_gp:\n"
        "auipc gp, %pcrel_hi(tsl9_runtime_reset_ram)\n"
        "addi gp, gp, %pcrel_lo(.Lreset_gp)\n"
        ".Lreset_sp:\n"
        "auipc sp, %pcrel_hi(tsl9_runtime_reset_stack_top)\n"
        "addi sp, sp, %pcrel_lo(.Lreset_sp)\n"
        "j tsl9_runtime_reset_memory\n.option pop\n");
}

#ifdef __cplusplus
}
#endif
