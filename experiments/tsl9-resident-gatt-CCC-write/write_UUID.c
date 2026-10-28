#include <stdint.h>
/* Original two-byte GATT attribute type UUID,read by APP88D0 via GP+36.
 * Conditional on original reset/GP pointer provenance;not a full table/provider.
 * Reference-coordinate DATA only;no physical placement or BLE success claim. */
#ifdef __cplusplus
extern "C" {
#define DATA_CONST extern const
#else
#define DATA_CONST const
#endif
__attribute__((used,section(".rodata.tsl9_gatt_write_UUID_1ab44"),aligned(2)))
DATA_CONST uint16_t tsl9_gatt_write_UUID_1ab44 = UINT16_C(0xfff1);
#ifdef __cplusplus
}
#endif
