/* Dispatcher continuation; final 208-path store then filter call. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch23")))
void tsl9_ota_dispatch_1471a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Ldispatch23:\n"
        "c.lwsp a5, 72(sp)\n"
        "slli a4, a0, 14\n"
        "c.srli a0, 18\n"
        "c.slli a5, 18\n"
        "c.srli a5, 18\n"
        "c.or a5, a4\n"
        "c.swsp a5, 72(sp)\n"
        "sb a0, 76(sp)\n"
        "c.li a3, 29\n"
        "addi a2, sp, 48\n"
        "li a1, 208\n"
        "c.mv a0, s1\n"
        "jal ra, tsl9_dispatch23_filter_8a56\n"
        "c.j .Ldispatch23-0x682\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
