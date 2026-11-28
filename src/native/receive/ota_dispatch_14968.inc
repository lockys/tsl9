/* Fall-through continuation in the original dispatcher frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_dispatch43")))
void tsl9_ota_dispatch_14968(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option norvc\n"
        ".option norelax\n"
        "sb zero, 59(sp)\n"
        "lbu a0, 59(sp)\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
