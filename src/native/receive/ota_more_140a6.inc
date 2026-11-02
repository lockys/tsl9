/* Original-PC dispatch continuation, dependent on enclosing frame and state. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_more")))
void tsl9_ota_more_140a6(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Lmore:\n"
        "li a5, 0xa8\n"
        "beq a1, a5, .Lmore+0x7c\n"
        "bltu a5, a1, .Lmore+0x36\n"
        "li a5, 0x57\n"
        "beq a1, a5, .Lmore-0x18\n"
        "auipc a5, 0x1fff8\n"
        "addi a5, a5, 0x6da\n"
        "auipc a3, 0x1fff8\n"
        "lhu a3, 0x6d4(a3)\n"
        "mv a4, a5\n"
        "beq s1, a3, .Lmore+0x106\n"
        "lhu a5, 6(a5)\n"
        "bne s1, a5, .Lmore+0xbd8\n"
        "li a5, 1\n"
        "c.j .Lmore+0x108\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
