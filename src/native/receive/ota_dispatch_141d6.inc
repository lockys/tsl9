/* Partial command dispatcher; requires the original enclosing stack/register frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch")))
void tsl9_ota_dispatch_141d6(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch:\n"
        "li a5, 176\n"
        "beq a1, a5, .Ldispatch+0x68\n"
        "bltu a5, a1, .Ldispatch+0x88\n"
        "li a5, 167\n"
        "bltu a5, a1, .Ldispatch+0x5a\n"
        "li a5, 163\n"
        "bgeu a1, a5, .Ldispatch+0x68\n"
        "li a5, 161\n"
        "beq a1, a5, .Ldispatch+0x68\n"
        "li a5, 171\n"
        "beq a1, a5, .Ldispatch+0x904\n"
        "bltu a5, a1, .Ldispatch+0x1f4\n"
        "li a5, 164\n"
        "beq a1, a5, .Ldispatch+0x86a\n"
        "bltu a5, a1, .Ldispatch+0x1ac\n"
        "li a5, 161\n"
        "beq a1, a5, .Ldispatch+0x7ec\n"
        "bltu a5, a1, .Ldispatch+0xb2\n"
        "li a5, 160\n"
        "bne a1, a5, .Ldispatch-0x13e\n"
        "li a1, 0\n"
        "mv a0, s1\n"
        "jal ra, tsl9_dispatch_provider_13ba6\n"
        "c.j .Ldispatch-0x64\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
