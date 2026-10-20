/* R80: only the 52-byte difference of a conditional 1572-byte source view.
 * The declaration spans other real inputs only after exact RO coalescing.
 * No physical ROM identity, original object extent or target execution claim.
 */
#include "target_ble_compare_view_r80.h"
__asm__(
".section .rodata.tsl9_r80_fragment_1a2d0,\"a\",@progbits\n"
".p2align 0\n"
".local tsl9_r80_fragment_1a2d0\n"
".type tsl9_r80_fragment_1a2d0,@object\n"
"tsl9_r80_fragment_1a2d0:\n"
".byte 0x02,0x00,0xee,0x02,0x5e,0x01,0x03,0x00,0xee,0x02,0x5e,0x01,0x02,0x00,0xfa,0x00\n"
".byte 0x5e,0x01,0x03,0x00,0xfa,0x00,0x5e,0x01,0x02,0x00,0xf4,0x01,0xee,0x02,0x03,0x00\n"
".byte 0xf4,0x01,0xee,0x02,0x02,0x00,0xf4,0x01,0xfa,0x00,0x03,0x00,0xf4,0x01,0xfa,0x00\n"
".size tsl9_r80_fragment_1a2d0,48\n"
".global __tsl9_ble_event_ro_1a2d0\n"
".type __tsl9_ble_event_ro_1a2d0,@object\n"
".set __tsl9_ble_event_ro_1a2d0,tsl9_r80_fragment_1a2d0\n"
".size __tsl9_ble_event_ro_1a2d0,1572\n"
".section .rodata.tsl9_r80_fragment_1a338,\"a\",@progbits\n"
".p2align 0\n"
".local tsl9_r80_fragment_1a338\n"
".type tsl9_r80_fragment_1a338,@object\n"
"tsl9_r80_fragment_1a338:\n"
".byte 0x00,0x00,0x00,0x00\n"
".size tsl9_r80_fragment_1a338,4\n"
);
