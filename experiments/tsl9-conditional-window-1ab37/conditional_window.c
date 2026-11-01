/* Conditional read-window backing at nominal [0x1ab37,0x1ab44).
 * No claim of an original object, global index bound, or hardware compatibility.
 */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
extern
#endif
const uint8_t tsl9_conditional_window_1ab37[13]
    __attribute__((used, aligned(1), section(".rodata.tsl9_conditional_window_1ab37"))) = {
    0x00, 0x02, 0x00, 0x00, 0x00, 0x40, 0xab,
    0x01, 0x00, 0xf0, 0xff, 0x1c, 0x00
};
#ifdef __cplusplus
}
#endif
