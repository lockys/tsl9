#include "requirements-v1.h"

#if !defined(__riscv) || __riscv_xlen != 32
#error Compile-only RV32 requirement checks; no host or target execution.
#endif

#ifdef __cplusplus
#define REQUIREMENT(condition, message) static_assert(condition, message)
#else
#define REQUIREMENT(condition, message) _Static_assert(condition, message)
#endif

/* No functions, objects, runtime accesses, linking, or firmware generation. */
REQUIREMENT(sizeof(uint32_t) == 4, "32-bit word required");
REQUIREMENT(sizeof(uintptr_t) == 4, "32-bit address required");
REQUIREMENT(sizeof(void (*)(void)) == 4, "32-bit function pointer required");
REQUIREMENT(TSL9_FW_END - TSL9_FW_BASE == 76800, "exact image extent");
REQUIREMENT(TSL9_RESET_PC >= TSL9_FW_BASE && TSL9_RESET_PC < TSL9_FW_END,
            "reset entry belongs to this image");
REQUIREMENT((TSL9_INITIAL_GP & 3) == 0, "word-aligned initialization");
REQUIREMENT((TSL9_INITIAL_SP & 15) == 0, "numeric initial SP alignment");
REQUIREMENT((TSL9_ZERO_END & 3) == 0, "word-aligned zero endpoint");
REQUIREMENT(TSL9_COPY_END == UINT32_C(0x20004080), "initialized data endpoint");
REQUIREMENT(TSL9_INITIALIZATION_SPAN == 35160, "ID2966 initialization span");
REQUIREMENT(TSL9_ZERO_BYTES == 35032, "ID2966 zero span");
REQUIREMENT(TSL9_NUMERIC_GAP_TO_SP == 13992, "numeric gap only, not stack budget");
REQUIREMENT(TSL9_INITIALIZER_SOURCE >= TSL9_FW_BASE &&
            TSL9_INITIALIZER_SOURCE + TSL9_INITIALIZED_BYTES <= TSL9_FW_END,
            "initializer source must fit in the supplied image");
REQUIREMENT(TSL9_CANDIDATE_RAM_END - TSL9_CANDIDATE_RAM_BASE == 65536,
            "explicit conditional candidate capacity");
REQUIREMENT(TSL9_CANDIDATE_RAM_BASE <= TSL9_INITIAL_GP &&
            TSL9_INITIAL_GP <= TSL9_COPY_END && TSL9_COPY_END <= TSL9_ZERO_END &&
            TSL9_ZERO_END <= TSL9_INITIAL_SP &&
            TSL9_INITIAL_SP <= TSL9_CANDIDATE_RAM_END,
            "numeric containment only, not physical memory validation");
REQUIREMENT((TSL9_VECTOR_BASE & 3) == 0 &&
            TSL9_VECTOR_BASE >= TSL9_FW_BASE && TSL9_VECTOR_BASE < TSL9_FW_END,
            "vector address fit only; interrupt behavior remains unproved");
REQUIREMENT(TSL9_INITIAL_MEPC >= TSL9_FW_BASE && TSL9_INITIAL_MEPC < TSL9_FW_END,
            "initial MEPC address fit only");
REQUIREMENT(TSL9_RESIDENT_ENTRY >= TSL9_FW_END,
            "resident executable body is outside this image");
REQUIREMENT(TSL9_SDK_TABLE_BASE == TSL9_RESIDENT_ENTRY + 0x34,
            "saved SDK default table offset");
REQUIREMENT(TSL9_SDK_MEMSET_SLOT == TSL9_SDK_TABLE_BASE + 5 * TSL9_SDK_SLOT_STRIDE,
            "saved SDK index 5 pointer slot, not a function entry");
REQUIREMENT(TSL9_SDK_MEMCPY_SLOT == TSL9_SDK_TABLE_BASE + 6 * TSL9_SDK_SLOT_STRIDE,
            "saved SDK index 6 pointer slot, not a function entry");
