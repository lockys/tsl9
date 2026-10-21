#ifndef TSL9_V4160_FLASH_HOST_IO_H
#define TSL9_V4160_FLASH_HOST_IO_H
#include <stdint.h>
typedef struct { uint32_t value,known; } fn_word;
typedef enum { FN_RETURNED=0,FN_HALTED=1,FN_TRANSFERRED=2 } fn_flow;
typedef enum { FN_READ32_REQUEST,FN_WRITE32_REQUEST,FN_CSR_CLEAR_REQUEST,FN_CSR_SET_REQUEST } fn_kind;
typedef enum { FN_NO_BOUNDARY,FN_PROVIDER_BOUNDARY,FN_UNKNOWN_ADDRESS,FN_UNKNOWN_CONDITION,FN_HOST_POLL_BUDGET,FN_UNKNOWN_RETURN_TARGET,FN_RETURN_TARGET_TRANSFER } fn_boundary;
typedef struct { fn_kind kind;uint32_t site,address,value,known,width; } fn_request;
struct fn_host;
/* Providers may apply an effect then halt/transfer: the model never rolls it back.
 * They may mutate memory/peripherals, not silently clobber architectural GPRs. */
typedef fn_flow (*fn_provider)(void *,struct fn_host *,const fn_request *,fn_word *);
typedef struct fn_host {
    fn_word regs[32];
    fn_provider invoke;void *context;
    fn_flow flow;fn_boundary boundary;
    uint32_t boundary_site,boundary_address,needed_mask;
    uint32_t poll_budget,operations,words_written;
    fn_request last_request;
    fn_word incoming_return_target;
    /* Register results are normal-return contracts. HALT prefix claims cover
     * ordered provider effects, not every intermediate original GPR residue. */
    uint32_t normal_register_outputs_valid;
} fn_host;
#ifdef __cplusplus
extern "C" {
#endif
fn_word fn_constant(uint32_t);
fn_word fn_failed(void);
fn_word fn_and(fn_word,fn_word);
fn_word fn_or(fn_word,fn_word);
fn_word fn_add(fn_word,fn_word);
void fn_host_init(fn_host *,fn_provider,void *);
fn_flow fn_run(fn_host *,uint32_t,fn_word,fn_word);
int fn_read(fn_host *,uint32_t,fn_word,fn_word *);
int fn_write(fn_host *,uint32_t,fn_word,fn_word);
int fn_poll_step(fn_host *,uint32_t,uint32_t,unsigned *);
int fn_poll_true(fn_host *,uint32_t,fn_word,uint32_t);
fn_word fn_commit(fn_host *,fn_word,const fn_word *,const fn_word *,const fn_word *,const fn_word *,fn_word,const fn_word *,uint32_t);
int fn_frame_begin(fn_host *,fn_word,fn_word);
int fn_frame_end(fn_host *);
int fn_csr(fn_host *,fn_kind,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
