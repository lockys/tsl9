/* Three conditional 16-byte lookup read windows, not a complete table declaration.
 * Original APP read: CF5A, base1A078 +16*mode+nibble; known setter: D0C8.
 * Only modes2/4/5 are added here. Mode0 already has a real DATA owner.
 * No provider alias, original-address layout, target startup or flash image.
 */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#define TSL9_ROW_LINKAGE extern
#else
#define TSL9_ROW_LINKAGE
#endif

TSL9_ROW_LINKAGE const uint8_t tsl9_lookup_mode_row_2_1a098[16]
    __attribute__((used, aligned(4), section(".rodata.tsl9_lookup_mode_row_2_1a098"))) = {
    0xa9, 0xab, 0xbd, 0x82, 0xac, 0xae, 0x32, 0x16,
    0xa3, 0x4a, 0x19, 0x63, 0xa6, 0xc0, 0xde, 0xd4
};

TSL9_ROW_LINKAGE const uint8_t tsl9_lookup_mode_row_4_1a0b8[16]
    __attribute__((used, aligned(4), section(".rodata.tsl9_lookup_mode_row_4_1a0b8"))) = {
    0xb7, 0xb5, 0xa3, 0x9c, 0xb2, 0xb0, 0x2c, 0x08,
    0xbd, 0x54, 0x07, 0x7d, 0xb8, 0xde, 0xc0, 0xca
};

TSL9_ROW_LINKAGE const uint8_t tsl9_lookup_mode_row_5_1a0c8[16]
    __attribute__((used, aligned(4), section(".rodata.tsl9_lookup_mode_row_5_1a0c8"))) = {
    0xaf, 0xad, 0xbb, 0x84, 0xaa, 0xa8, 0x34, 0x10,
    0xa5, 0x4c, 0x1f, 0x65, 0xa0, 0xc6, 0xd8, 0xd2
};

#undef TSL9_ROW_LINKAGE
#ifdef __cplusplus
}
#endif
