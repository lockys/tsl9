/* Mid-function machine-frame epilogue; not callable as an independent ABI. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_epilogue")))
void tsl9_ota_epilogue_14098(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        "lw ra, 188(sp)\n"
        "lw s0, 184(sp)\n"
        "lw s1, 180(sp)\n"
        "lw s2, 176(sp)\n"
        "lw s3, 172(sp)\n"
        "addi sp, sp, 192\n"
        "ret\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
