#ifndef TSL9_RESIDENT_MEMORY_LEAVES_H
#define TSL9_RESIDENT_MEMORY_LEAVES_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Numeric address effects only. This is not a CPU/register-state model.
 * CONTINUE from a read means that the complete requested value is known.
 * Callbacks may change synthetic memory; they must not modify ml_io itself.
 * HALT/TRANSFER/UNKNOWN stop the authored algorithm at that effect boundary. */
typedef enum ml_flow { ML_CONTINUE=0,ML_HALT=1,ML_TRANSFER=2,ML_UNKNOWN=3 } ml_flow;
typedef ml_flow (*ml_read_callback)(void *,uint32_t,uint32_t *);
typedef ml_flow (*ml_write_callback)(void *,uint32_t,uint32_t);
typedef ml_flow (*ml_fence_callback)(void *);
typedef struct ml_io {
    void *user;
    ml_read_callback read8,read32;
    ml_write_callback write8,write32;
    ml_fence_callback fence_i;
    uint32_t diagnostic_budget,effects; /* HOST only; no native loop timeout */
    ml_flow flow;
} ml_io;
typedef struct ml_result { ml_flow flow;uint32_t value,known; } ml_result;
/* Candidate-address names identify source evidence, not installed providers.
 * These typed C interfaces explicitly take an I/O context and return flow;
 * they do not claim the original physical register ABI or fixed placement. */
ml_result tsl9_candidate_compare_200004bc(ml_io *,uint32_t address,uint32_t expected,uint32_t count);
ml_result tsl9_candidate_fill_2000039c(ml_io *,uint32_t destination,uint32_t value,uint32_t count);
ml_result tsl9_candidate_copy_20000332(ml_io *,uint32_t destination,uint32_t source,uint32_t count);
#ifdef __cplusplus
}
#endif
#endif
