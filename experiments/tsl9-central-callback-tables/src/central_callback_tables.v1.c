#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Original RV32 pointer representation required.
#endif
typedef void (*tsl9_original_callback_t)(void);
#ifdef __cplusplus
static_assert(sizeof(tsl9_original_callback_t) == 4, "RV32 callback address width");
extern "C" {
#else
_Static_assert(sizeof(tsl9_original_callback_t) == 4, "RV32 callback address width");
#endif

/* Original table cells only. Callback addresses are genuine function
 * relocations, never ABS substitutes or replacement stubs. Declarations
 * specify address identity; installed callback calling conventions remain
 * unproved. Signed event offsets require the measured original layout.
 * No neighboring loop/default bytes, inferred padding or terminators. */

extern void tsl9_central_callback_leaves_10c36(void);
extern void tsl9_central_callback_leaves_10d2e(void);
extern void tsl9_central_callback_leaves_10d30(void);
extern void tsl9_central_event_callbacks_entry_11544(void);
extern void tsl9_feature_state_records_block_10c34(void);

extern const int32_t tsl9_central_event_callbacks_static_data_1a548[17];
const int32_t __attribute__((used,aligned(4),section(".rodata.tsl9_central_event_callbacks_static_data_1a548"))) tsl9_central_event_callbacks_static_data_1a548[17] = {
    -36026, /* cell 0: original target 0x1188E */
    -36142, /* cell 1: original target 0x1181A */
    -36178, /* cell 2: original target 0x117F6 */
    -36178, /* cell 3: original target 0x117F6 */
    -36178, /* cell 4: original target 0x117F6 */
    -36092, /* cell 5: original target 0x1184C */
    -35840, /* cell 6: original target 0x11948 */
    -36178, /* cell 7: original target 0x117F6 */
    -36178, /* cell 8: original target 0x117F6 */
    -36178, /* cell 9: original target 0x117F6 */
    -36178, /* cell 10: original target 0x117F6 */
    -36178, /* cell 11: original target 0x117F6 */
    -36178, /* cell 12: original target 0x117F6 */
    -36824, /* cell 13: original target 0x11570 */
    -36178, /* cell 14: original target 0x117F6 */
    -36178, /* cell 15: original target 0x117F6 */
    -36156, /* cell 16: original target 0x1180C */
};

extern const tsl9_original_callback_t tsl9_registered_callbacks_static_data_1a668[3];
const tsl9_original_callback_t __attribute__((used,aligned(4),section(".rodata.tsl9_registered_callbacks_static_data_1a668"))) tsl9_registered_callbacks_static_data_1a668[3] = {
    tsl9_central_callback_leaves_10d30, /* cell 0: original target 0x10D30 */
    tsl9_central_callback_leaves_10d2e, /* cell 1: original target 0x10D2E */
    0, /* cell 2: original target 0x0 */
};

extern const tsl9_original_callback_t tsl9_registered_callbacks_static_data_1a674[3];
const tsl9_original_callback_t __attribute__((used,aligned(4),section(".rodata.tsl9_registered_callbacks_static_data_1a674"))) tsl9_registered_callbacks_static_data_1a674[3] = {
    tsl9_central_callback_leaves_10c36, /* cell 0: original target 0x10C36 */
    tsl9_central_event_callbacks_entry_11544, /* cell 1: original target 0x11544 */
    tsl9_feature_state_records_block_10c34, /* cell 2: original target 0x10C34 */
};

#ifdef __cplusplus
}
#endif
