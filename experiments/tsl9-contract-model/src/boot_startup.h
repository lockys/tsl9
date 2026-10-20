#ifndef TSL9_BOOT_STARTUP_H
#define TSL9_BOOT_STARTUP_H
#include "rom_candidate.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { BS_RETURNED=0, BS_HALT=1, BS_TRANSFER=2 } bs_flow;
typedef enum { BS_MMIO_READ, BS_MMIO_WRITE, BS_CLOCK, BS_CALLBACK,
               BS_CSR_CLEAR, BS_JUMP, BS_RESET_WAIT, BS_MEMORY_READ } bs_operation;
typedef struct {
    bs_operation operation;
    uint32_t va,address,value,argument;
    unsigned width;
} bs_request;
typedef struct { uint32_t value,known; } bs_result;
/* Caller-produced abstract payload. It has no invented native stack address.
   The two live reads around each UART write use these same buffers. */
typedef struct { const uint8_t *data,*known;uint32_t available; } bs_uart_view;
struct bs_model;
typedef struct {
    void *context;
    /* Raw entry-register argument, not an implicit uint16 host narrowing.
       Return1 establishes return and known pointer, including known NULL. */
    int (*msg_allocate)(void *,uint32_t,uint32_t *);
    /* Scalar status is ignored by native callers; 1 establishes call return. */
    int (*msg_deallocate)(void *,uint32_t);
    int (*rom_status)(void *,unsigned,uint8_t,uint16_t,uint32_t);
    /* Explicit synthetic HAL only. READ/CLOCK require known width bits.
       JUMP can return or transfer; RESET_WAIT must transfer to close its
       nonreturning native loop. Missing or unknown effects preserve prefix. */
    bs_flow (*hal)(void *,struct bs_model *,const bs_request *,bs_result *);
} bs_backend;
typedef struct bs_model {
    tf_model *memory; /* Sole authoritative SRAM/known bytes. */
    rc_adapter *candidate; /* Optional explicit fixed public candidate. */
    bs_backend backend;
    bs_flow flow;
    uint32_t boundary_va,boundary_address,requests;
    uint32_t boundary_offset;int boundary_is_abstract;
    uint32_t poll_budget,byte_budget; /* Host evidence bounds, not native checks. */
} bs_model;
void bs_init(bs_model *,tf_model *,const bs_backend *);
void bs_resume(bs_model *);
int bs_attach_candidate(bs_model *,rc_adapter *);
bs_flow bs_configure(bs_model *,uint32_t,uint32_t *);
bs_flow bs_pattern(bs_model *,uint32_t);
bs_flow bs_pattern_irq(bs_model *);
bs_flow bs_uart_reply(bs_model *,uint32_t,uint32_t,uint32_t);
bs_flow bs_uart_reply_view(bs_model *,uint32_t,const bs_uart_view *,uint32_t);
bs_flow bs_startup_dispatch(bs_model *,uint16_t,uint16_t *);
bs_flow bs_stay(bs_model *);
/* Exact25EC..2618 tail with raw s2 check result. Caller must already have
   supplied the peripheral initialization prefix; this is not2542 startup. */
bs_flow bs_startup_policy_tail(bs_model *,uint32_t);
/* This scope excludes startup2542 peripheral/config/image-check initialization,
   actual MMIO, native execution, TMOS dispatch scheduling and system equivalence. */
#ifdef __cplusplus
}
#endif
#endif
