/* Read the actual vendor header under RV32 ILP32; never execute target code. */
#include <stdint.h>
#include TSL9_CONFIG_HEADER

__attribute__((used,section(".rodata.tsl9_config_layout")))
const uint32_t tsl9_config_layout[] = {
    __builtin_offsetof(bleConfig_t, MEMAddr),
    __builtin_offsetof(bleConfig_t, MEMLen),
    __builtin_offsetof(bleConfig_t, SNVAddr),
    __builtin_offsetof(bleConfig_t, SNVBlock),
    __builtin_offsetof(bleConfig_t, SNVNum),
    __builtin_offsetof(bleConfig_t, staCB),
    __builtin_offsetof(bleConfig_t, readFlashCB),
    __builtin_offsetof(bleConfig_t, writeFlashCB),
    sizeof(bleConfig_t),
    sizeof(pfnLibStatusErrorCB)
};
