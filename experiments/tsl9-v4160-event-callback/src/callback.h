#ifndef TSL9_EVENT_CALLBACK_H
#define TSL9_EVENT_CALLBACK_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Named source-carried values, not a CPU/ISA interpreter. Parentheses in the
 * field descriptions name original registers only as evidence coordinates. */
typedef struct cb_values {
    uint32_t events;       /* S0: complete event word, never truncated */
    uint32_t record;       /* S1 */
    uint32_t lane;         /* S2: may subsequently carry a ROM base */
    uint32_t span;         /* S3: path-dependent length/offset/ROM base */
    uint32_t task;         /* S4 */
    uint32_t connection;   /* S5 */
    uint32_t cursor;       /* S6 */
    uint32_t rom_base;     /* S7 */
    uint32_t base_copy;    /* S8 */
    uint32_t shared_base;  /* S9 */
    uint32_t gp,sp,return_address;
} cb_values;
typedef enum cb_flow { CB_CONTINUE=0, CB_HALT=1, CB_TRANSFER=2, CB_UNKNOWN=3 } cb_flow;
typedef enum cb_effect_kind { CB_READ=0, CB_WRITE=1, CB_OPAQUE_CALL=2 } cb_effect_kind;
typedef struct cb_effect {
    cb_effect_kind kind;
    uint32_t source_site,address,width,value;
    uint32_t target,target_register;
    uint32_t args[8];
    uint32_t defined_argument_mask; /* Explicit algorithm-call argument
     * projection, not proof of every intermediate physical GPR residue. */
} cb_effect;
/* Memory callbacks may supply values or edit synthetic memory, but must not
 * mutate carried values/argument residues. Only named opaque-call callbacks
 * may mutate those values. The dispatcher enforces this distinction. An odd
 * raw target is retained as identity; the architectural target is raw&~1. */
struct cb_host;
typedef cb_flow (*cb_provider)(void *user,struct cb_host *host,cb_effect *effect);
typedef struct cb_host {
    cb_values values;
    uint32_t args[8];
    cb_provider provider;
    void *user;
    cb_flow flow;
    uint32_t result;
    uint32_t effects;
    uint32_t diagnostic_budget; /* HOST stop only; never a native timeout */
} cb_host;
/* The HOST contract models named algorithm effects and fresh saved-frame
 * values. It makes no physical GPR-prefix or native callee-preservation claim. */
void tsl9_callback_host_8614(cb_host *host,uint32_t context,uint32_t event_word);
/* Conditional conventional-C-ABI native probe only. Ambient A2..A7 are raw
 * register inputs, not inferred SDK parameter types. Not a drop-in provider. */
uint32_t tsl9_callback_native_8614(uint32_t context,uint32_t event_word,
    uint32_t ambient2,uint32_t ambient3,uint32_t ambient4,uint32_t ambient5,
    uint32_t ambient6,uint32_t ambient7);
#ifdef __cplusplus
}
#endif
#endif
