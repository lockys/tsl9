/* Command dispatcher continuation; requires the enclosing original frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch2")))
void tsl9_ota_dispatch_14230(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch2:\n"
        "addi a5, a1, 86\n"
        "andi a5, a5, 255\n"
        "li a4, 1\n"
        "bltu a4, a5, .Ldispatch2-0x36\n"
        "sw a1, 12(sp)\n"
        "jal ra, tsl9_dispatch2_queue_81aa\n"
        "lw a1, 12(sp)\n"
        "c.bnez a0, .Ldispatch2-0x36\n"
        "li a3, 0\n"
        "li a2, 300\n"
        "li a1, 0\n"
        "auipc a0, 0\n"
        "addi a0, a0, -712\n"
        "jal ra, tsl9_dispatch2_scheduler_9124\n"
        "c.j .Ldispatch2-0x198\n"
        "li a5, 193\n"
        "bltu a5, a1, .Ldispatch2+0x4a\n"
        "li a5, 192\n"
        "bgeu a1, a5, .Ldispatch2+0xe\n"
        "addi a5, a1, 71\n"
        "andi a5, a5, 255\n"
        "li a4, 2\n"
        "c.j .Ldispatch2+0xa\n"
        "li a5, 208\n"
        "beq a1, a5, .Ldispatch2+0xe\n"
        "li a5, 240\n"
        "c.j .Ldispatch2-0x3a\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
