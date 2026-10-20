#ifndef TSL9_FEATURE_H
#define TSL9_FEATURE_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define TF_RAM_BASE UINT32_C(0x20000000)
#define TF_GP UINT32_C(0x20004000)
#define TF_REGISTRY UINT32_C(0x2000be08)
#define TF_RAM_SIZE 65536u
#define TF_UNKNOWN (-1)
typedef struct { uint8_t value[258], known[258]; size_t available; } tf_frame;
struct tf_model;
typedef struct {
    void *context;
    /* Return the declared ROM scalar, or -1 for an unknown external result. */
    int (*rom_status)(void *, unsigned, uint8_t, uint16_t, uint32_t);
    /* An acceptance is local adapter acceptance, never a vehicle ACK. */
    int (*tx)(void *, const tf_frame *);
    /* Synthetic observer/adapter only; unsupported callback effects stay unknown. */
    void (*delivery)(void *, struct tf_model *, uint32_t, uint32_t);
    /* Explicit host assumption for declared ROM memset byte effects, not physical proof. */
    int memory_contracts;
    /* Optional native JT+104 call adapter: 1 establishes call return, -1 is an
       unclosed call. The native scalar status is unchecked. Absent hook keeps
       the older free_requests diagnostic-only abstraction. */
    int (*free_argument)(void *,uint32_t);
} tf_backend;
typedef struct tf_model {
    uint8_t ram[TF_RAM_SIZE], known[TF_RAM_SIZE];
    const uint8_t *runtime; size_t runtime_length;
    tf_backend backend;
    uint32_t tx_requests, tx_gate_refused, tx_accepted, unknown_effects;
    uint32_t schedule_requests, free_requests, callback_calls;
    uint32_t last_callback, last_argument, last_ticks, last_rom_offset;
    uint32_t last_unknown_va, last_unknown_address;
    tf_frame last_tx;
} tf_model;
/* Native .data/BSS slice only, not the complete startup or feature initializer. */
void tf_init(tf_model *,const uint8_t *,size_t,const tf_backend *);
int tf_schedule(tf_model *,uint32_t,uint32_t,uint32_t,uint32_t);
int tf_cancel(tf_model *,uint32_t);
uint16_t tf_dispatch(tf_model *,uint16_t);
/* int64 distinguishes unknown=-1 from every uint32 original return bit pattern. */
int64_t tf_hold(tf_model *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
int tf_admit(tf_model *,uint8_t,uint16_t,uint8_t);
void tf_bridge(tf_model *);
void tf_delay_bridge(tf_model *,uint32_t);
void tf_door_consume(tf_model *,tf_frame *,uint8_t);
/* Confirmed/raw/aggregate slice; per-ID holds and event actions remain separate. */
void tf_observe_pair(tf_model *,unsigned,uint8_t,uint8_t);
void tf_body273(tf_model *,tf_frame *,uint32_t);
void tf_fog_set(tf_model *,uint32_t,uint32_t);
void tf_ceba(tf_model *,uint32_t,uint32_t,uint32_t);
void tf_ceda(tf_model *,uint32_t,uint16_t);
void tf_229(tf_model *,tf_frame *);
void tf_fed4(tf_model *,uint32_t,uint32_t);
void tf_678_observe(tf_model *,const tf_frame *);
void tf_678_consume(tf_model *,tf_frame *);
int tf_checksum(const tf_frame *,uint8_t *);
void tf_threshold118(tf_model *,uint8_t);
/* Listed local clearing slices only, not the entire mode-reset sequence. */
void tf_reset_scope(tf_model *,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
