/* Continuation inside the dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch50")))
void tsl9_ota_dispatch_149d4(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch50:\n"
        "lbu a5, 0(s0)\n"
        ".option rvc\n"
        "c.beqz a5, .Ldispatch50_zero\n"
        ".option norvc\n"
        "jal ra, .Ldispatch50-0xa370\n"
        "jal zero, .Ldispatch50-0x93c\n"
        ".Ldispatch50_zero:\n"
        "jal ra, .Ldispatch50-0xa32a\n"
        "jal zero, .Ldispatch50-0x93c\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
