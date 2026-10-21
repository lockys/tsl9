#ifndef TSL9_RESET_ENTRY_BRIDGE_H
#define TSL9_RESET_ENTRY_BRIDGE_H
#include "resident_entry.h"
#include "reset_contract.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Exact existing Runtime reset handoff only. Caller owns one shared synthetic
 * memory/CSR bank; RI's MRET callback observes its then-current MEPC. Does not
 * turn reset initial_gp/sp diagnostics into live register snapshots. The
 * resident entry itself establishes its GP/SP. No native symbol is defined.
 * This bridge maps RI_LIMIT to RC_OBSERVATION_LIMIT; the existing frozen reset
 * caller folds that nonreturn into outer RC_HALT/RC_PROVIDER_UNKNOWN. Inspect
 * both models: inner RI_LIMIT and its exact prefix are still preserved. */
rc_flow ri_reset_handoff(ri_model *,const rc_request *,rc_scalar *);
#ifdef __cplusplus
}
#endif
#endif
