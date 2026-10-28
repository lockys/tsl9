/* Observed8-byte conditional halfword lookup window,not a full table declaration.
 * Original read A158:1AB48+2*counter;known masked writes A0FA/A344.
 * No provider alias,frame writer,startup,hardware command or firmware image.
 */
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#define TSL9_DATA_LINKAGE extern
#else
#define TSL9_DATA_LINKAGE
#endif
TSL9_DATA_LINKAGE const uint16_t tsl9_input_counter_read_window_1ab48[4]
    __attribute__((used, aligned(4), section(".rodata.tsl9_input_counter_read_window_1ab48"))) = {
    UINT16_C(0x0096), UINT16_C(0x00b4), UINT16_C(0xff6a), UINT16_C(0xff4c)
};
#undef TSL9_DATA_LINKAGE
#ifdef __cplusplus
}
#endif
