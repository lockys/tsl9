/* Conditional seven-word read window at original1AAE8..1AB04.
 * Consumer17844 reads1AAE8+4*uint8(GP+370) BEFORE the modulo7 update.
 * Requires index0..6 at its read;global index/ROM/RAM/IRQ contracts unproved.
 * Low24-bit values resemble a palette;physical channel meanings unconfirmed.
 */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#define TSL9_DATA_LINKAGE extern
#else
#define TSL9_DATA_LINKAGE
#endif
TSL9_DATA_LINKAGE const uint32_t tsl9_event_word_read_window_1aae8[7]
    __attribute__((used, aligned(4), section(".rodata.tsl9_event_word_read_window_1aae8"))) = {
    UINT32_C(0x000000ff),
    UINT32_C(0x00007dff),
    UINT32_C(0x0000ffff),
    UINT32_C(0x0000ff00),
    UINT32_C(0x00ffff00),
    UINT32_C(0x00ff0000),
    UINT32_C(0x00ff00ff),
};
#undef TSL9_DATA_LINKAGE
#ifdef __cplusplus
}
#endif
