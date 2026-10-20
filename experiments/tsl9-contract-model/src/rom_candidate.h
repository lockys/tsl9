#ifndef TSL9_ROM_CANDIDATE_H
#define TSL9_ROM_CANDIDATE_H
#include "feature.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { RC_PHYSICAL_UNKNOWN=0, RC_WCH_64BE955_V130=1 } rc_profile;
struct rc_adapter;
typedef struct {
    void *context;
    /* Explicit synthetic raw-clock callback result; token is the SRAM provider.
       Return1 only when the result is known; callback may mutate shared RAM. */
    int (*clock)(void *,uint32_t,uint32_t *);
    int (*status)(void *,struct rc_adapter *,unsigned,uint32_t);
    int (*calibration)(void *,struct rc_adapter *,uint32_t);
} rc_hooks;
typedef struct rc_adapter {
    /* No second SRAM: every native state byte and known mask lives here. */
    tf_model *memory;
    rc_hooks hooks;
    rc_profile profile;
    uint32_t operations, clock_calls, status_calls, unknowns;
    uint32_t last_unknown_va, last_unknown_address;
    unsigned boundary_flags;
    int fault;
} rc_adapter;
enum { RC_BOUND_MMIO=1u, RC_BOUND_MEMORY=2u, RC_BOUND_OPERAND=4u,
       RC_BOUND_CALLBACK=8u, RC_BOUND_CORRUPT_LIST=16u, RC_BOUND_PROFILE=32u };
/* Profile selection is an explicit caller opt-in, not hardware identification. */
int rc_attach(rc_adapter *,tf_model *,rc_profile,const rc_hooks *);
void rc_resume(rc_adapter *);
/* Selected task/heap-init slice, not BLE_LibInit. Other cfg fields remain caller
   supplied RAM/known bytes. Clears the recorded TMOS task globals before heap
   initialization, allocates48 callback records and task metadata, registers3
   internal handlers. Known result1 means selected slice completed. */
int rc_prepare(rc_adapter *,uint32_t,uint16_t,uint8_t);
int rc_heap_alloc(rc_adapter *,uint32_t,uint32_t,uint32_t *);
int rc_heap_free(rc_adapter *,uint32_t);
int rc_heap_free_sum(rc_adapter *,uint32_t *);
/* JT+112 declared ABI takes uint16 length. _register exposes the exact raw32
   entry-register body before its internal u16(len+8) narrowing. */
int rc_msg_allocate(rc_adapter *,uint16_t,uint32_t *);
int rc_msg_allocate_register(rc_adapter *,uint32_t,uint32_t *);
int rc_msg_deallocate(rc_adapter *,uint32_t,uint32_t *);
int rc_task_register(rc_adapter *,uint32_t,uint8_t *);
int rc_timer_find(rc_adapter *,uint32_t,uint16_t,uint32_t *);
/* Return1 means scalar output/effects known. Output includes native rejection
   values; return0 is an evidence boundary, not a fabricated native rejection. */
int rc_timer_start(rc_adapter *,uint32_t,uint16_t,uint32_t,uint32_t *);
int rc_timer_reload(rc_adapter *,uint32_t,uint16_t,uint32_t,uint32_t *);
int rc_timer_stop(rc_adapter *,uint32_t,uint16_t,uint32_t *);
int rc_timer_remaining(rc_adapter *,uint32_t,uint16_t,uint32_t *);
int rc_timer_pump(rc_adapter *);
int rc_set_event(rc_adapter *,uint32_t,uint16_t,uint32_t *);
int rc_clear_event(rc_adapter *,uint32_t,uint16_t,uint32_t *);
int rc_take_event(rc_adapter *,uint8_t,uint16_t *);
/* Return slice re-reads the SRAM cursor; task is the original dispatched ID.
   It does not execute handlers, task-priority scan, idle/radio or one-shot cb. */
int rc_return_event(rc_adapter *,uint8_t,uint16_t);
/* token0 requests recorded null-config defaults. Calibration hook occurs first.
   Reserved input byte is forcibly zeroed, as in this candidate. */
int rc_clock_init(rc_adapter *,uint32_t,uint32_t,uint16_t,uint16_t,uint8_t,uint32_t *);
/* supplied distinguishes a null config from nonnull config with token0.
   Scalar inputs construct a known16-byte staging config with zero padding. */
int rc_clock_configure(rc_adapter *,int,uint32_t,uint32_t,uint16_t,uint16_t,uint8_t,uint32_t *);
int rc_clock_get(rc_adapter *,uint32_t *);
/* Matches tf_backend.rom_status for offsets80/84/88/92/556 only. For full32
   values use typed APIs rather than int return values. */
int rc_rom_status(void *,unsigned,uint8_t,uint16_t,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
