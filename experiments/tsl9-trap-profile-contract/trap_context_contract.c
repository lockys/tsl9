#include <stdint.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error Offline RV32 compile-only evidence; never execute on host or hardware.
#endif
#ifdef __cplusplus
#define CHECK static_assert
#else
#define CHECK _Static_assert
#endif
/* Numeric constraints only: no functions, DATA, firmware provider or startup policy. */
#define TSL9_INITIAL_GP UINT32_C(0x20004000)
#define TSL9_INITIAL_SP UINT32_C(0x20010000)
#define TSL9_ZERO_START UINT32_C(0x20004080)
#define TSL9_ZERO_END UINT32_C(0x2000c958)
#define TSL9_LLE_POINTER UINT32_C(0x20004180)
#define TSL9_VECTOR_BASE UINT32_C(0x8038)
#define TSL9_MTVEC_WRITE UINT32_C(0x803b)
#define TSL9_RESET_CSR804 UINT32_C(0x3)
#define TSL9_RESTORE_CSR804_SET UINT32_C(0x20)
#define TSL9_ECALL_M_MODE_IRQN 5u
CHECK(TSL9_VECTOR_BASE + TSL9_ECALL_M_MODE_IRQN * 4u == UINT32_C(0x804c), "pinned enum vector word location");
#define TSL9_ECALL_U_MODE_IRQN 8u
CHECK(TSL9_VECTOR_BASE + TSL9_ECALL_U_MODE_IRQN * 4u == UINT32_C(0x8058), "pinned enum vector word location");
#define TSL9_BB_IRQN 63u
CHECK(TSL9_VECTOR_BASE + TSL9_BB_IRQN * 4u == UINT32_C(0x8134), "pinned enum vector word location");
#define TSL9_LLE_IRQN 64u
CHECK(TSL9_VECTOR_BASE + TSL9_LLE_IRQN * 4u == UINT32_C(0x8138), "pinned enum vector word location");
CHECK(TSL9_LLE_POINTER == TSL9_INITIAL_GP + 384u, "initial live GP-relative callback word");
CHECK(TSL9_LLE_POINTER >= TSL9_ZERO_START && TSL9_LLE_POINTER + 4u <= TSL9_ZERO_END, "callback word initially falls in zero interval");
CHECK((TSL9_MTVEC_WRITE & ~UINT32_C(3)) == TSL9_VECTOR_BASE && (TSL9_MTVEC_WRITE & 3u) == 3u, "original encoded vector operands only; mode semantics unproved");
CHECK((TSL9_RESET_CSR804 & 2u) == 2u, "primary candidate nesting bit initially set");
CHECK((TSL9_RESTORE_CSR804_SET & 2u) == 0u, "restore CSRRS mask does not clear or set nesting bit");
CHECK(120u + 4u <= 128u && 29u * 4u == 116u, "prior inherited frame arithmetic only");
