#include <stdint.h>

/* Original Runtime ID2966 initializer data, not recovered symbols/providers.
 * RAM and one clock frame are nominal ELF allocations, not hardware proof. */
#ifdef __cplusplus
extern "C" {
#define DATA_CONST extern const
#else
#define DATA_CONST const
#endif
__attribute__((used,section(".rodata.tsl9_reset_initializer"),aligned(4)))
DATA_CONST uint32_t tsl9_runtime_reset_initializer[32] = {
    UINT32_C(0x00000002), UINT32_C(0x0004000c), UINT32_C(0x00000001), UINT32_C(0x0001ab38),
    UINT32_C(0x00000002), UINT32_C(0x00040012), UINT32_C(0x00000001), UINT32_C(0x0001ab42),
    UINT32_C(0x00000002), UINT32_C(0x0001ab44), UINT32_C(0x00000002), UINT32_C(0x20004088),
    UINT32_C(0x00000002), UINT32_C(0x00040018), UINT32_C(0x00000003), UINT32_C(0x20004080),
    UINT32_C(0x00000000), UINT32_C(0x00000000), UINT32_C(0x04030201), UINT32_C(0x09080706),
    UINT32_C(0x00010000), UINT32_C(0x2000c29c), UINT32_C(0x2000c30c), UINT32_C(0x2000c40c),
    UINT32_C(0x2000c494), UINT32_C(0x2000c594), UINT32_C(0x2000c694), UINT32_C(0x05b8d800),
    UINT32_C(0x018900a9), UINT32_C(0x0000068c), UINT32_C(0x037a03ea), UINT32_C(0x000003a1),
};
__attribute__((used,section(".bss.tsl9_reset_ram"),aligned(4)))
uint32_t tsl9_runtime_reset_ram[8790];
__attribute__((used,section(".bss.tsl9_reset_stack"),aligned(16)))
uint32_t tsl9_runtime_reset_stack[4];
#ifdef __cplusplus
}
#endif
