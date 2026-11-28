/* Continuation within the original dispatcher frame; not independently callable. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch47")))
void tsl9_ota_dispatch_1499a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option rvc\n"
        ".Ldispatch47:\n"
        "c.jal .Ldispatch47+0x32e\n"
        "c.swsp a0, 48(sp)\n"
        "c.li a3, 4\n"
        "c.addi4spn a2, sp, 48\n"
        ".option norvc\n"
        "addi a1, zero, 193\n"
        ".option rvc\n"
        "c.mv a0, s1\n"
        ".option norvc\n"
        "jal ra, .Ldispatch47-0xe4e\n"
        "jal zero, .Ldispatch47-0x902\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
