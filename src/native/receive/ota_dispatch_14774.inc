/* Dispatcher continuation; pack three halfwords then rejoin filter call. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch25")))
void tsl9_ota_dispatch_14774(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch25:\n"
        "lbu a5, 52(sp)\n"
        "lbu a4, 51(sp)\n"
        "c.li a3, 8\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "sh a5, 36(sp)\n"
        "lbu a5, 54(sp)\n"
        "lbu a4, 53(sp)\n"
        ".2byte 0x1050\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "sh a5, 38(sp)\n"
        "lbu a5, 56(sp)\n"
        "lbu a4, 55(sp)\n"
        "li a1, 210\n"
        "c.slli a5, 8\n"
        "c.or a5, a4\n"
        "sh a5, 40(sp)\n"
        "c.j .Ldispatch25-0x3e\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
