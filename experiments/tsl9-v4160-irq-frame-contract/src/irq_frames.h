#ifndef TSL9_V4160_IRQ_FRAMES_H
#define TSL9_V4160_IRQ_FRAMES_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Own finite frame-data model, not a CPU stepper or hardware ISR. Target
 * addresses remain integers and are never cast to host pointers. */
typedef enum {IQ_RETURNED,IQ_HALT,IQ_TRANSFER,IQ_OBSERVATION_LIMIT} iq_flow;
typedef enum {IQ_READ32,IQ_WRITE32,IQ_CSR_SET,IQ_CSR_WRITE,IQ_CALLBACK,IQ_MRET} iq_kind;
typedef enum {IQ_NONE,IQ_UNKNOWN_ADDRESS,IQ_UNKNOWN_TARGET,IQ_PROVIDER_UNKNOWN,
    IQ_PROVIDER_TRANSFER,IQ_CALLBACK_BOUNDARY,IQ_MRET_BOUNDARY,IQ_BUDGET} iq_boundary;
typedef struct {uint32_t value,known;} iq_scalar;
typedef struct {
    iq_kind kind;uint32_t pc,address,csr; iq_scalar value,target;
} iq_request;
struct iq_model;
typedef struct {
    void *context;
    /* READ/WRITE/CSR/MRET observations. Returned means the explicitly supplied
     * synthetic effect completed. No implicit device access is implemented. */
    iq_flow (*effect)(void *,const iq_request *,iq_scalar *);
    /* Explicit callee contract; may mutate frame memory and the live register
     * data below, including sp/gp. Return never establishes a physical ABI. */
    iq_flow (*callback)(void *,struct iq_model *,const iq_request *);
} iq_backend;
typedef struct iq_model {
    iq_backend backend;iq_scalar gpr[32],mepc,csr804;
    iq_flow flow;iq_boundary boundary;uint32_t boundary_pc;
    uint32_t operations,max_operations,saved_words,restored_words;
    iq_request last_request;
} iq_model;
void iq_init(iq_model *,const iq_backend *);
/* 8448 uses an inherited frame; 8498 creates128B and uses a live callback.
 * Ending at MRET records only the original control boundary, not execution. */
iq_flow iq_restore_8448(iq_model *);
iq_flow iq_irq_8498(iq_model *);
#ifdef __cplusplus
}
#endif
#endif
