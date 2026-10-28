/* Two conditional16-byte read windows,not a full provider extent.
 * Original lookupCF5A:1A078+16*effective_mode+((fresh_record4+1)&15).
 * Mode1/3 writers and column bound are source-proven;global mode-at-read,
 * physical RAM mapping and hardware behavior remain unproved.
 */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#define TSL9_DATA_LINKAGE extern
#else
#define TSL9_DATA_LINKAGE
#endif
TSL9_DATA_LINKAGE const uint8_t tsl9_record_mode_read_window_1a088[16]
    __attribute__((used, aligned(4), section(".rodata.tsl9_record_mode_read_window_1a088"))) = {
    0xa6, 0xa4, 0xb2, 0x8d, 0xa3, 0xa1, 0x3d, 0x19,
    0xac, 0x45, 0x16, 0x6c, 0xa9, 0xcf, 0xd1, 0xdb,
};
TSL9_DATA_LINKAGE const uint8_t tsl9_record_mode_read_window_1a0a8[16]
    __attribute__((used, aligned(4), section(".rodata.tsl9_record_mode_read_window_1a0a8"))) = {
    0x49, 0x4b, 0x5d, 0x62, 0x4c, 0x4e, 0xd2, 0xf6,
    0x43, 0xaa, 0xf9, 0x83, 0x46, 0x20, 0x3e, 0x34,
};
#undef TSL9_DATA_LINKAGE
#ifdef __cplusplus
}
#endif
