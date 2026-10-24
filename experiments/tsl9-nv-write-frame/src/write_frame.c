#include "../../tsl9-nv-write-callback/src/nv_write_callback.h"

/* Conditional normal call/effect surface, not a recovered original C ABI.
 * Providers remain the genuine separately compiled repaired-overlay helpers.
 * Volatile requests a fresh source-slot load after erase; placement is measured. */
#ifdef __cplusplus
extern "C"
#endif
uint32_t tsl9_nv_write_frame_197be(uint32_t destination,
                                 uint32_t unused_a1,
                                 uint32_t source)
{
    volatile uint32_t source_slot = source;
    uint32_t saved_destination = destination;
    uint32_t program_a0;
    (void)unused_a1;
    (void)tsl9_flash_unlock_18e98(saved_destination);
    (void)tsl9_flash_erase_18ec4(saved_destination);
    program_a0 = tsl9_flash_program_18ef2(saved_destination, source_slot);
    (void)tsl9_flash_lock_18eb6(program_a0);
    (void)tsl9_delay_19764(1u);
    return 0;
}
