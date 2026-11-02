/* Original-PC command path; dependent on the enclosing dispatcher frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_ad")))
void tsl9_ota_ad_1417a(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Lad:\n"
        "andi a1, a3, 0xff\n"
        "mv a0, a2\n"
        "jal ra, tsl9_ota_entry_92f2\n"
        ".option norvc\n"
        "bne a0, zero, .Lad-0xe2\n"
        ".option rvc\n"
        "auipc a0, 0\n"
        "addi a0, a0, -0x200\n"
        "jal ra, tsl9_callback_table_entry_90b0\n"
        "jal ra, tsl9_queue_status_81aa\n"
        "c.beqz a0, .Lad+0x26\n"
        "li a0, 0\n"
        "jal ra, tsl9_selector_notifications_provider_9ef0\n"
        "li a1, 0xad\n"
        "mv a0, s1\n"
        "jal ra, tsl9_secondary_message_dispatch_entry_1400c\n"
        "c.j .Lad-0xe2\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
