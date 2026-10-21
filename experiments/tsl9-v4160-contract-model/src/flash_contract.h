#ifndef TSL9_V4160_FLASH_CONTRACT_H
#define TSL9_V4160_FLASH_CONTRACT_H
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Host semantic model of original instructions, not an original ROM/C ABI or
 * physical driver. Backend operations are explicit synthetic evidence. */
typedef enum {FC_RETURNED,FC_HALT,FC_TRANSFER} fc_flow;
typedef enum {FC_MMIO_READ,FC_MMIO_WRITE,FC_SOURCE_WORD_READ,FC_DEST_WORD_STORE,FC_RAM_BYTE_READ} fc_kind;
typedef enum {FC_NO_BOUNDARY,FC_PROVIDER_UNKNOWN,FC_CONDITION_UNKNOWN,FC_OPERAND_UNKNOWN,FC_SPIN_BUDGET} fc_boundary;
typedef struct {fc_kind kind;uint32_t pc,address,value,known;unsigned width;} fc_request;
typedef struct {uint32_t value,known;} fc_scalar;
typedef struct {void *context;fc_flow (*invoke)(void *,const fc_request *,fc_scalar *);} fc_backend;
typedef struct {
    fc_backend backend;fc_flow flow;fc_boundary boundary;
    fc_request last_request;uint32_t boundary_pc,needed_mask;
    uint32_t gp,gp_known,poll_budget,destination,source,words_written,operations,result,result_known;
} fc_model;
void fc_init(fc_model *,const fc_backend *);
/* Original197BE entry-register relations: a0 destination, a1 ignored by this
 * captured body, a2 source address. No original callback signature is claimed.
 * Returned zero means ordinary native return; it is not controller success. */
fc_flow fc_write_registers(fc_model *,uint32_t,uint32_t,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
