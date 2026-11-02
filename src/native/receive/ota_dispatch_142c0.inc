/* Dispatcher continuation; depends on its original frame and resident slots. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch4")))
void tsl9_ota_dispatch_142c0(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch4:\n"
        "li a1, 14\n"
        "addi a0, s2, 4\n"
        "jal ra, tsl9_dispatch4_checker_92f2\n"
        "seqz s3, a0\n"
        "addi a4, s2, 36\n"
        "addi a3, s2, 40\n"
        "li a2, 94\n"
        "lbu a5, 0(a4)\n"
        "addi a5, a5, -32\n"
        "andi a5, a5, 255\n"
        "bltu a2, a5, .Ldispatch4+0x75e\n"
        "addi a4, a4, 1\n"
        "bne a3, a4, .Ldispatch4+0x1a\n"
        "lui a5, 0x40\n"
        "lw a5, 104(a5)\n"
        "mv a0, s2\n"
        "jalr a5\n"
        "beq s3, zero, .Ldispatch4+0x764\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
