#ifndef TSL9_NATIVE_CALLBACKS_H
#define TSL9_NATIVE_CALLBACKS_H
#include "feature.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { NC_RETURNED,NC_HALT,NC_TRANSFER } nc_flow;
typedef enum { NC_RUNTIME_DISCONNECT,NC_RUNTIME_RESET,NC_RUNTIME_BOOT_REQUEST,
               NC_BOOT_DISCONNECT,NC_BOOT_JUMP,NC_BOOT_RESET } nc_callback;
typedef enum { NC_MMIO_READ,NC_MMIO_WRITE,NC_ROM_SCALAR,NC_ROM_DISCONNECT,
               NC_ROM_COPY,NC_FLASH_CALL,NC_CSR_CLEAR,NC_CSR_SET,
               NC_JUMP,NC_RESET_WAIT } nc_kind;
typedef enum { NC_NO_BUFFER,NC_ADDRESS,NC_VALUE_VIEW } nc_buffer_kind;
typedef struct {
    nc_kind kind;uint32_t va,target,arguments[3];unsigned count,width,slot;
    nc_buffer_kind source,destination;
    /* count includes scalar arguments only; a VALUE_VIEW separately binds
       the corresponding source/destination ABI pointer without a fake address. */
    uint32_t source_address,destination_address;
    unsigned length;
    uint8_t data[256],known[256];
} nc_request;
typedef struct {uint32_t value,known;unsigned length;uint8_t data[256],bytes_known[256];} nc_result;
struct nc_model;
typedef struct {
    void *context;
    /* Typed synthetic provider only. ROM target is its JT slot address, slot
       identifies the ABI, not an identified physical function pointer.
       VALUE_VIEW is an ephemeral byte value, never an invented stack address.
       CALL return scalars may be ignored; flow must still be established.
       RESET_WAIT accepts only TRANSFER; JUMP accepts explicit return/transfer. */
    nc_flow (*invoke)(void *,struct nc_model *,const nc_request *,nc_result *);
} nc_backend;
typedef struct nc_model {
    tf_model *memory;nc_backend backend;nc_flow flow;nc_request last_request;
    uint32_t unknown_va,unknown_address,operations,spin_budget;
    uint32_t metadata_status,metadata_status_known; /* Host diagnostic of9DC0 scalar. */
} nc_model;
void nc_init(nc_model *,tf_model *,const nc_backend *);
void nc_resume(nc_model *);
/* Exact six native entry bodies plus selected source callees. argument is
   inherited raw a0 for BOOT20E2; other bodies overwrite/ignore it as native.
   No target execution, hardware success, stack address or global setup. */
nc_flow nc_run(nc_model *,nc_callback,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
