#ifndef TSL9_BOOT2580_COMMAND_H
#define TSL9_BOOT2580_COMMAND_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { BC_RETURNED=0, BC_HALT, BC_TRANSFER } bc_flow;
typedef enum { BC_NONE=0, BC_MISSING_PROVIDER, BC_PROVIDER_STOP,
               BC_CONDITION_UNKNOWN, BC_OBSERVATION_BUDGET } bc_boundary;
typedef enum { BC_READ8, BC_READ32, BC_WRITE8, BC_WRITE32, BC_IDENTITY,
               BC_INDIRECT_COPY, BC_PROGRAM256, BC_CANCEL_STARTUP,
               BC_METADATA, BC_REPLY, BC_SCHEDULE } bc_kind;
typedef struct { uint32_t value, known; } bc_value;
typedef struct {
    bc_kind kind; uint32_t pc, nominal_slot, argc;
    bc_value target, raw_target, args[4];
} bc_request;
struct bc_model;
typedef struct {
    void *context;
    bc_flow (*invoke)(void *,struct bc_model *,const bc_request *,bc_value *);
} bc_backend;
typedef struct bc_model {
    bc_backend backend;
    bc_value gp, body_sp, page, destination;
    bc_flow flow; bc_boundary boundary;
    uint32_t boundary_pc, operations, observation_budget;
    uint32_t program_attempts, reply_attempts;
    bc_request last_request;
} bc_model;

/* Host data/command contract, not an ISA interpreter or original C ABI.
 * body_sp denotes original SP AFTER the48-byte prologue. Caller supplies that
 * memory snapshot: prologue/epilogue register saves, RET and stack validity are
 * outside this adapter. No numeric target address is dereferenced on the host.
 * Providers may change synthetic memory and live gp/body_sp; they preserve
 * local callee-saved values and engine control on RETURNED (host interface
 * assumption, not a proof of original helper ABI). HALT/TRANSFER retain prefix.
 * READ/WRITE args: address, [value]. Named call args preserve a0..argc-1.
 * Every argument and result has a bit-known mask. Partial addresses/indirect
 * targets require an explicit provider that can justify its returned effects.
 * COPY is only a nominal role for the loaded4004C slot, not proved memcpy ABI.
 * REPLY is a whole wrapper call request, not observed BLE delivery. */
void bc_init(bc_model *,const bc_backend *);
/* Select a distinct host activation after nonreturn; does not resume an original
 * caller or reset provider memory, GP or SP. Dispatch also selects a fresh
 * activation after a normal return; never silently resumes HALT/TRANSFER. */
void bc_new_activation(bc_model *);
bc_flow bc_dispatch(bc_model *,uint32_t connection,uint32_t command,
                    uint32_t payload,uint32_t length);
#ifdef __cplusplus
}
#endif
#endif
