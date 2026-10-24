/* Saved SDK candidate layout only. Readonly constants; never linked into firmware. */
#include <stdint.h>
#include <stddef.h>
#if !defined(__riscv) || __riscv_xlen != 32
#error This provenance check requires the measured RV32 target.
#endif
#ifdef __cplusplus
#define DATA extern "C"
#define ASSERT static_assert
#define ALIGNOF(T) alignof(T)
#else
#define DATA
#define ASSERT _Static_assert
#define ALIGNOF(T) _Alignof(T)
#endif

typedef struct
{
    uint16_t handle;  //!< Handle of the attribute to be written (must be first field)
    uint16_t len;     //!< Length of value
    uint8_t *pValue;  //!< Value of the attribute to be written (0 to ATT_MTU_SIZE-3)
    uint8_t sig;      //!< Authentication Signature status (not included (0), valid (1), invalid (2))
    uint8_t cmd;      //!< Command Flag
} attWriteReq_t;

ASSERT(sizeof(void *) == 4, "Measured ILP32 pointer width");
ASSERT(sizeof(attWriteReq_t) == 12, "Saved candidate descriptor extent");
ASSERT(ALIGNOF(attWriteReq_t) == 4, "Saved candidate descriptor alignment");
ASSERT(offsetof(attWriteReq_t, handle) == 0, "Observed SP+4");
ASSERT(offsetof(attWriteReq_t, len) == 2, "Observed SP+6");
ASSERT(offsetof(attWriteReq_t, pValue) == 4, "Observed SP+8");
ASSERT(offsetof(attWriteReq_t, sig) == 8, "Observed zero halfword at SP+12");
ASSERT(offsetof(attWriteReq_t, cmd) == 9, "Observed zero halfword at SP+12");

DATA __attribute__((used,aligned(4),section(".rodata.tsl9_sdk_att_write_layout")))
const uint32_t tsl9_sdk_att_write_layout[12] = {
    sizeof(attWriteReq_t), ALIGNOF(attWriteReq_t),
    offsetof(attWriteReq_t, handle), offsetof(attWriteReq_t, len),
    offsetof(attWriteReq_t, pValue), offsetof(attWriteReq_t, sig),
    offsetof(attWriteReq_t, cmd),
    sizeof(((attWriteReq_t *)0)->handle),
    sizeof(((attWriteReq_t *)0)->len),
    sizeof(((attWriteReq_t *)0)->pValue),
    sizeof(((attWriteReq_t *)0)->sig),
    sizeof(((attWriteReq_t *)0)->cmd)
};
