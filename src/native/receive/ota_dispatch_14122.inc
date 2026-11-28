/* Original-PC fragment; requires the enclosing dispatcher frame and registers. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch79")))
void tsl9_ota_dispatch_14122(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ld79:\n"
        "li a5, 4\n"
        "bne a3, a5, .Ld79-0x8a\n"
        "lui a5, 0x62426\n"
        "addi a5, a5, 321\n"
        "sw a5, 48(sp)\n"
        "addi a5, gp, 84\n"
        "lw a2, 0(a5)\n"
        "li a3, 4\n"
        "li a5, 0\n"
        ".Lloop79:\n"
        "add a4, s0, a5\n"
        "add a1, a2, a5\n"
        "lbu a4, 0(a4)\n"
        "lbu a1, 12(a1)\n"
        "beq a1, a4, .Lnext79\n"
        "addi a1, sp, 48\n"
        "add a1, a1, a5\n"
        "lbu a1, 0(a1)\n"
        "beq a1, a4, .Lnext79\n"
        "li a2, 0\n"
        "li a1, 168\n"
        "c.j .Ld79-8\n"
        ".Lnext79:\n"
        "addi a5, a5, 1\n"
        "bne a5, a3, .Lloop79\n"
        "li a1, 1\n"
        "mv a0, s1\n"
        "jal ra, tsl9_ota_code_13e0e\n"
        "li a0, 0\n"
        "jal ra, tsl9_ota_code_13dd4\n"
        "c.j .Ld79-0x8a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
