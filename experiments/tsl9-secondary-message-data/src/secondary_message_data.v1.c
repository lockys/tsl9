#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 data representation required.
#endif
#ifdef __cplusplus
extern "C" {
#endif

/* Only the guarded event cells and the observed constant-length copy source.
 * No adjacent padding, inferred terminators or private data is selected.
 * Signed event offsets require original-coordinate CODE/DATA placement.
 * Copy-source extent is the observed A2=12 call, not a recovered declaration.
 * Physical RAM, stack, installed ROM/IRQ and OTA remain unproved. */

extern const int32_t tsl9_secondary_message_dispatch_static_data_1a58c[7];
const int32_t __attribute__((used,aligned(4),section(".rodata.tsl9_secondary_message_dispatch_static_data_1a58c"))) tsl9_secondary_message_dispatch_static_data_1a58c[7] = {
    -32420, /* cell0: original CODE 0x126E8 */
    -32378, /* cell1: original CODE 0x12712 */
    -31938, /* cell2: original CODE 0x128CA */
    -32354, /* cell3: original CODE 0x1272A */
    -32334, /* cell4: original CODE 0x1273E */
    -31938, /* cell5: original CODE 0x128CA */
    -32158, /* cell6: original CODE 0x127EE */
};

extern const uint8_t tsl9_secondary_message_dispatch_static_data_19dd4[12];
const uint8_t __attribute__((used,aligned(4),section(".rodata.tsl9_secondary_message_dispatch_static_data_19dd4"))) tsl9_secondary_message_dispatch_static_data_19dd4[12] = {
    UINT8_C(0x39),
    UINT8_C(0x03),
    UINT8_C(0x08),
    UINT8_C(0x00),
    UINT8_C(0x00),
    UINT8_C(0x00),
    UINT8_C(0x00),
    UINT8_C(0x00),
    UINT8_C(0xf0),
    UINT8_C(0x00),
    UINT8_C(0x00),
    UINT8_C(0x00),
};

#ifdef __cplusplus
}
#endif
