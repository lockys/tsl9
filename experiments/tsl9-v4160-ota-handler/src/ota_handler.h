#ifndef TSL9_V4160_OTA_HANDLER_H
#define TSL9_V4160_OTA_HANDLER_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Source-carried algorithm values, not a CPU/register interpreter. Values may
 * change at named callee boundaries. Frame links are saved-data bookkeeping;
 * this HOST contract does not execute a restored target. */
typedef struct oh_values {
    uint32_t buffer;       /* original S0: payload, then W quarter offset */
    uint32_t flash;        /* S1: W destination, or S status byte */
    uint32_t context;      /* S2 */
    uint32_t source;       /* S3: W aligned source */
    uint32_t page;         /* S4: complete BE16 page */
    uint32_t limit;        /* S5: W loop limit */
    uint32_t gp,sp,return_address;
} oh_values;
typedef enum oh_flow { OH_CONTINUE=0,OH_HALT=1,OH_TRANSFER=2,OH_UNKNOWN=3 } oh_flow;
typedef enum oh_effect_kind { OH_READ=0,OH_WRITE=1,OH_CALL=2 } oh_effect_kind;
typedef enum oh_callee {
    OH_UID_92F2=0,OH_QUARTER_9C0A=1,OH_SCHEDULE_9124=2,
    OH_SMALL_REPLY_13F66=3,OH_PACKET_REPLY_13E98=4,
    OH_PAGE_REPLY_9B8E=5,OH_COPY_SLOT_4C=6
} oh_callee;
typedef struct oh_effect {
    oh_effect_kind kind;
    uint32_t source_site,address,width,value,value_known;
    oh_callee callee;
    uint32_t target; /* raw target identity; architectural JALR clears bit0 */
    uint32_t args[8];
    uint32_t defined_argument_mask; /* explicit algorithm projection ONLY;
     * ambient/intermediate physical scratch residues are not all modelled */
} oh_effect;
struct oh_host;
typedef oh_flow (*oh_provider)(void *user,struct oh_host *host,oh_effect *effect);
typedef struct oh_host {
    oh_values values;
    uint32_t args[8];
    oh_provider provider;
    void *user;
    oh_flow flow;
    uint32_t result,result_known; /* last algorithm A0, never common status */
    uint32_t return_value_known;
    uint32_t effects,diagnostic_budget;
} oh_host;
/* Memory effects: READ8/READ32 and WRITE8; synthetic frame saves also WRITE32.
 * Memory providers may alter synthetic memory, but cannot mutate values/args.
 * A READ provider must set value_known=1. OH_CALL returns A0 through the same
 * value/value_known pair; unknown UID results stop before a branch. Other raw
 * output argument residues may be placed in host->args explicitly.
 * Named OH_CALL providers may mutate values, ambient args and memory, and must
 * explicitly select RETURN/CONTINUE, HALT, TRANSFER or UNKNOWN. Diagnostic
 * budget is a HOST stop only; it never becomes a native timeout/guard. */
void tsl9_ota_handler_host_9c4a(oh_host *,uint32_t context,uint32_t command,
                             uint32_t payload,uint32_t length);
/* Four full-width semantic inputs plus explicit ambient A4..A7. Conventional
 * native callee preservation is conditional; not full original raw8 ABI. */
uint32_t tsl9_ota_handler_native_9c4a(uint32_t context,uint32_t command,
    uint32_t payload,uint32_t length,uint32_t ambient4,uint32_t ambient5,
    uint32_t ambient6,uint32_t ambient7);
#ifdef __cplusplus
}
#endif
#endif
