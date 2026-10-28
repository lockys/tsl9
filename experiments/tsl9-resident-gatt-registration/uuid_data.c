#include <stdint.h>
/* Exactly20 traced archived SDK UUID bytes;no device-specific identifiers.
 * Reference-coordinate DATA only;installed ROM and physical layout remain unproved. */
#ifdef __cplusplus
extern "C" {
#define DATA_CONST extern const
#else
#define DATA_CONST const
#endif
__attribute__((used,section(".rodata.tsl9_candidate_gatt_UUID_template_6e370"),aligned(2)))
DATA_CONST uint8_t tsl9_candidate_gatt_UUID_template_6e370[16] = {
    UINT8_C(0xfb), UINT8_C(0x34), UINT8_C(0x9b), UINT8_C(0x5f), UINT8_C(0x80), UINT8_C(0x00), UINT8_C(0x00), UINT8_C(0x80), UINT8_C(0x00), UINT8_C(0x10), UINT8_C(0x00), UINT8_C(0x00), UINT8_C(0x00), UINT8_C(0x00), UINT8_C(0x00), UINT8_C(0x00)
};
__attribute__((used,section(".rodata.tsl9_candidate_gatt_primary_UUID_6ea90"),aligned(2)))
DATA_CONST uint8_t tsl9_candidate_gatt_primary_UUID_6ea90[2] = {
    UINT8_C(0x00), UINT8_C(0x28)
};
__attribute__((used,section(".rodata.tsl9_candidate_gatt_secondary_UUID_6ea9c"),aligned(2)))
DATA_CONST uint8_t tsl9_candidate_gatt_secondary_UUID_6ea9c[2] = {
    UINT8_C(0x01), UINT8_C(0x28)
};
#ifdef __cplusplus
}
#endif
