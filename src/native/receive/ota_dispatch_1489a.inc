/* Continuation in the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch34")))
void tsl9_ota_dispatch_1489a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".option norelax\n"
        ".Ldispatch34:\n"
        "jal ra, .Ldispatch34-0x1ddc\n"
        "c.addi4spn a1, sp, 24\n"
        "c.li a2, 12\n"
        "c.li a0, 1\n"
        "jal ra, .Ldispatch34-0x1ddc\n"
        "c.li a2, 12\n"
        "c.addi4spn a1, sp, 36\n"
        "c.li a0, 2\n"
        "jal ra, .Ldispatch34-0x1ddc\n"
        "c.j .Ldispatch34-0x76\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
