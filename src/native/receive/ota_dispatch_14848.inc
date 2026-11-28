/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch31")))
void tsl9_ota_dispatch_14848(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        "lui s3, 0x40\n"
        "lw a5, 72(s3)\n"
        "li a2, 112\n"
        "c.li a1, 0\n"
        "c.addi4spn a0, sp, 48\n"
        "c.jalr a5\n"
        "lw a5, 72(s3)\n"
        "c.li a2, 12\n"
        "c.li a1, 0\n"
        "c.addi4spn a0, sp, 24\n"
        "c.jalr a5\n"
        "lw a5, 72(s3)\n"
        "c.addi s2, -2\n"
        "c.li a2, 12\n"
        "c.addi4spn a0, sp, 36\n"
        "c.li a1, 0\n"
        "c.slli s2, 16\n"
        "c.jalr a5\n"
        "srli s2, s2, 16\n"
        "srli s2, s2, 1\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
