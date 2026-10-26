#include <stdint.h>
#ifdef __cplusplus
#define ASSERT static_assert
#else
#define ASSERT _Static_assert
#endif
ASSERT(sizeof(void *) == 4, "RV32 pointer width");
ASSERT(sizeof(uint32_t) == 4, "32-bit unsigned word");
ASSERT(sizeof(uint64_t) == 8, "64-bit unsigned integer");
ASSERT(UINT32_MAX == 0xffffffffu, "unsigned word maximum");
ASSERT(UINT64_MAX == 0xffffffffffffffffull, "unsigned pair maximum");
/* Compile-only sizes, not a proof of the helper's register calling convention. */
