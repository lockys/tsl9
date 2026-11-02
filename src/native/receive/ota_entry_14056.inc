/* Original-PC entry fragment; requires placement and continuation by enclosing code. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_entry")))
void tsl9_ota_entry_14056(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Lentry:\n"
        "addi sp, sp, -192\n"
        "sw s0, 184(sp)\n"
        "sw s1, 180(sp)\n"
        "sw s2, 176(sp)\n"
        "sw ra, 188(sp)\n"
        "sw s3, 172(sp)\n"
        "li a5, 0x55\n"
        "mv s1, a0\n"
        "mv s0, a2\n"
        "mv s2, a3\n"
        "beq a1, a5, .Lentry+0x38\n"
        "bltu a5, a1, .Lentry+0x50\n"
        "li a5, 0x45\n"
        "beq a1, a5, .Lentry+0x38\n"
        "bltu a1, a5, .Lentry+0x64\n"
        "addi a5, a1, -0x52\n"
        "andi a5, a5, 0xff\n"
        "li a4, 1\n"
        "bltu a4, a5, .Lentry+0x64\n"
        "mv a3, s2\n"
        "mv a2, s0\n"
        "mv a0, s1\n"
        ".option norvc\n"
        "jal ra, tsl9_ota_entry_9c4a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
