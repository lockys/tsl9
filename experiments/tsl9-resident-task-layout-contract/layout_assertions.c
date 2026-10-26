#include <stddef.h>
#include <stdint.h>
#include "../../analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h"
#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only original RV32 layout assertions.
#endif
#ifdef __cplusplus
#define ASSERT static_assert
#define ALIGNOF alignof
#else
#define ASSERT _Static_assert
#define ALIGNOF _Alignof
#endif
ASSERT(sizeof(void *) == 4, "RV32 pointer width");
ASSERT(sizeof(bleConfig_t) == 64, "candidate configuration size");
ASSERT(ALIGNOF(bleConfig_t) == 4, "candidate configuration alignment");
ASSERT(offsetof(bleConfig_t, MEMAddr) == 0, "MEMAddr offset");
ASSERT(offsetof(bleConfig_t, MEMLen) == 4, "MEMLen offset");
ASSERT(offsetof(bleConfig_t, staCB) == 52, "status callback offset");
ASSERT(sizeof(((bleConfig_t *)0)->staCB) == 4, "status callback pointer width");
ASSERT(offsetof(bleConfig_t, SNVAddr) == 8, "SNVAddr offset");
ASSERT(offsetof(bleConfig_t, SNVBlock) == 12, "SNVBlock offset");
ASSERT(offsetof(bleConfig_t, SNVNum) == 14, "SNVNum offset");
ASSERT(offsetof(bleConfig_t, readFlashCB) == 56, "readFlashCB offset");
ASSERT(offsetof(bleConfig_t, writeFlashCB) == 60, "writeFlashCB offset");
ASSERT(offsetof(bleConfig_t, TxPower) == 20, "TxPower offset");
ASSERT(offsetof(bleConfig_t, ConnectNumber) == 21, "ConnectNumber offset");
ASSERT(sizeof(((bleConfig_t *)0)->ConnectNumber) == 1, "connection-count byte");
typedef struct candidate_record_words {
    uint32_t callback_VA;
    uint32_t argument_word;
    uint32_t word8;
} candidate_record_words;
ASSERT(sizeof(candidate_record_words) == 12, "observed record stride");
ASSERT(ALIGNOF(candidate_record_words) == 4, "observed word alignment");
ASSERT(offsetof(candidate_record_words, callback_VA) == 0, "callback word offset");
ASSERT(offsetof(candidate_record_words, argument_word) == 4, "argument word offset");
ASSERT(offsetof(candidate_record_words, word8) == 8, "uninterpreted third word offset");
/* Types/assertions only. No runtime object,function,entry or provider is defined. */
