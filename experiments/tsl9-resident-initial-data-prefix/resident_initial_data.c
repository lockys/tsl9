#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Candidate RV32 initialized data only.
#endif
#ifdef __cplusplus
static_assert(sizeof(uint32_t) == 4, "original word width");
extern "C" {
#else
_Static_assert(sizeof(uint32_t) == 4, "original word width");
#endif
/* Exact public SDK prefix; not installed-ROM identity or a Flash image.
 * Source [0x6EAA4,0x6EB2C), conditional destination [0x20002E70,0x20002EF8).
 * The next requested source word is absent. Do not append zero or FF filler.
 * Encoded pointer-looking words are data, not native function providers. */
extern const uint32_t tsl9_candidate_initial_state_6eaa4[34];
__attribute__((used, aligned(4), section(".rodata.tsl9_candidate_initial_state_6eaa4")))
const uint32_t tsl9_candidate_initial_state_6eaa4[34] = {
    UINT32_C(0x00049156), /* source 0x6EAA4 -> conditional RAM 0x20002E70 */
    UINT32_C(0x00049270), /* source 0x6EAA8 -> conditional RAM 0x20002E74 */
    UINT32_C(0x00000000), /* source 0x6EAAC -> conditional RAM 0x20002E78 */
    UINT32_C(0x00000002), /* source 0x6EAB0 -> conditional RAM 0x20002E7C */
    UINT32_C(0x0006ea90), /* source 0x6EAB4 -> conditional RAM 0x20002E80 */
    UINT32_C(0x00000001), /* source 0x6EAB8 -> conditional RAM 0x20002E84 */
    UINT32_C(0x20002ee4), /* source 0x6EABC -> conditional RAM 0x20002E88 */
    UINT32_C(0x00000002), /* source 0x6EAC0 -> conditional RAM 0x20002E8C */
    UINT32_C(0x0006ea6c), /* source 0x6EAC4 -> conditional RAM 0x20002E90 */
    UINT32_C(0x00000001), /* source 0x6EAC8 -> conditional RAM 0x20002E94 */
    UINT32_C(0x20002eef), /* source 0x6EACC -> conditional RAM 0x20002E98 */
    UINT32_C(0x00000002), /* source 0x6EAD0 -> conditional RAM 0x20002E9C */
    UINT32_C(0x0006eaa0), /* source 0x6EAD4 -> conditional RAM 0x20002EA0 */
    UINT32_C(0x00000000), /* source 0x6EAD8 -> conditional RAM 0x20002EA4 */
    UINT32_C(0x00000000), /* source 0x6EADC -> conditional RAM 0x20002EA8 */
    UINT32_C(0x00000002), /* source 0x6EAE0 -> conditional RAM 0x20002EAC */
    UINT32_C(0x0006ea70), /* source 0x6EAE4 -> conditional RAM 0x20002EB0 */
    UINT32_C(0x00000003), /* source 0x6EAE8 -> conditional RAM 0x20002EB4 */
    UINT32_C(0x00000000), /* source 0x6EAEC -> conditional RAM 0x20002EB8 */
    UINT32_C(0x00000000), /* source 0x6EAF0 -> conditional RAM 0x20002EBC */
    UINT32_C(0x0004b500), /* source 0x6EAF4 -> conditional RAM 0x20002EC0 */
    UINT32_C(0x00000000), /* source 0x6EAF8 -> conditional RAM 0x20002EC4 */
    UINT32_C(0x012f81c3), /* source 0x6EAFC -> conditional RAM 0x20002EC8 */
    UINT32_C(0x02020102), /* source 0x6EB00 -> conditional RAM 0x20002ECC */
    UINT32_C(0x00020202), /* source 0x6EB04 -> conditional RAM 0x20002ED0 */
    UINT32_C(0x00a00050), /* source 0x6EB08 -> conditional RAM 0x20002ED4 */
    UINT32_C(0x03e80000), /* source 0x6EB0C -> conditional RAM 0x20002ED8 */
    UINT32_C(0xff020802), /* source 0x6EB10 -> conditional RAM 0x20002EDC */
    UINT32_C(0x000000ff), /* source 0x6EB14 -> conditional RAM 0x20002EE0 */
    UINT32_C(0x00000002), /* source 0x6EB18 -> conditional RAM 0x20002EE4 */
    UINT32_C(0x0006ea80), /* source 0x6EB1C -> conditional RAM 0x20002EE8 */
    UINT32_C(0x20ff0001), /* source 0x6EB20 -> conditional RAM 0x20002EEC */
    UINT32_C(0x01020501), /* source 0x6EB24 -> conditional RAM 0x20002EF0 */
    UINT32_C(0x01011001), /* source 0x6EB28 -> conditional RAM 0x20002EF4 */
};
#ifdef __cplusplus
}
#endif
