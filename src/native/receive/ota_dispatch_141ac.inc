/* Original-PC continuation; 0x141ae is also a cross-fragment entry. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch80")))
void tsl9_ota_dispatch_141ac(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ld80:\n"
        "li a5, 0\n"
        "slli a5, a5, 2\n"
        "add a5, a5, a4\n"
        "lbu a5, 4(a5)\n"
        "andi a5, a5, 255\n"
        "c.bnez a5, .Ld80+0x2a\n"
        "li a2, 300\n"
        "li a3, 0\n"
        "li a1, 0\n"
        "auipc a0, 0\n"
        "addi a0, a0, -0x3f0\n"
        "jal ra, tsl9_dispatch80_scheduler_9124\n"
        "li a2, 255\n"
        "c.j .Ld80-0x4e\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
