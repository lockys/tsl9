/* Dispatcher-frame continuation [0x14a6c, 0x14a96); not callable alone. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch57")))
void tsl9_ota_dispatch_14a6c(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norelax\n"
        ".option norvc\n"
        ".Ldispatch57:\n"
        "auipc a0, 0xffff4\n"
        "addi a0, a0, 940\n" /* 0x8e18 */
        "jal ra, .Ldispatch57-0xb948\n" /* 0x9124 */
        "addi a2, zero, 200\n"
        ".option rvc\n"
        "c.li a1, 0\n"
        "c.li a3, 0\n"
        ".option norvc\n"
        "auipc a0, 0xffff5\n"
        "addi a0, a0, -152\n" /* 0x99e8 */
        "jal ra, .Ldispatch57-0xb948\n" /* 0x9124 */
        ".option rvc\n"
        "c.li a2, 1\n"
        ".option norvc\n"
        "addi a1, zero, 165\n"
        "jal zero, .Ldispatch57-0x952\n" /* 0x1411a */
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
