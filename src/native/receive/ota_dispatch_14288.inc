/* Dispatcher continuation; requires original frame and resident slot contracts. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch3")))
void tsl9_ota_dispatch_14288(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch3:\n"
        "li a5, 162\n"
        "beq a1, a5, .Ldispatch3+0x774\n"
        "li a5, 163\n"
        "bne a1, a5, .Ldispatch3-0x1f0\n"
        "li a5, 76\n"
        "bne s2, a5, .Ldispatch3+0x79c\n"
        "lui a5, 0x40\n"
        "lw a5, 112(a5)\n"
        "li a0, 76\n"
        "jalr a5\n"
        "mv s2, a0\n"
        "beq a0, zero, .Ldispatch3+0x79c\n"
        "lui a5, 0x40\n"
        "lw a5, 76(a5)\n"
        "li a2, 76\n"
        "mv a1, s0\n"
        "jalr a5\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
