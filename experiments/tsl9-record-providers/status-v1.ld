/* Real six-byte81AA status function only. */
SECTIONS { .provider_status_code 0 : SUBALIGN(1) { *(.text.tsl9_queue_status_81aa) } }
