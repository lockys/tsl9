/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch39")))
void tsl9_ota_dispatch_14928(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        "c.li a1, 2\n"
        "c.mv a0, s1\n"
        ".4byte 0x000000ef\n"
        ".reloc .-4, R_RISCV_JAL, tsl9_dispatch39_call_13ba6\n"
        ".4byte 0x000000ef\n"
        ".reloc .-4, R_RISCV_JAL, tsl9_dispatch39_call_1070a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
