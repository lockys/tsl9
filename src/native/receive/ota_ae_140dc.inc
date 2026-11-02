/* Original-PC command path; dependent on the enclosing dispatcher frame. */
#ifdef __cplusplus
extern "C" {
#endif
__attribute__((naked, used, section(".tsl9_ota_ae")))
void tsl9_ota_ae_140dc(void)
{
    __asm__ volatile(
        ".option push\n"
        ".option rvc\n"
        ".Lae:\n"
        "li a5, 0xad\n"
        "beq a1, a5, .Lae+0x9e\n"
        "li a5, 0xae\n"
        "bne a1, a5, .Lae-0x22\n"
        "andi a1, a3, 0xff\n"
        "mv a0, a2\n"
        "jal ra, tsl9_ota_entry_92f2\n"
        "c.bnez a0, .Lae-0x44\n"
        "auipc a0, 0\n"
        "addi a0, a0, -0x170\n"
        "jal ra, tsl9_callback_table_entry_90b0\n"
        "jal ra, tsl9_queue_status_81aa\n"
        "c.beqz a0, .Lae+0x38\n"
        "li a0, 0\n"
        "jal ra, tsl9_selector_notifications_provider_9ef0\n"
        "jal ra, tsl9_settings_state_inputs_provider_e20c\n"
        "li a2, 1\n"
        "li a1, 0xae\n"
        "mv a0, s1\n"
        "jal ra, tsl9_ota_external_13f66\n"
        "c.j .Lae-0x44\n"
        ".option pop\n");
}
#ifdef __cplusplus
}
#endif
