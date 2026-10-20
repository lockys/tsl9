#ifndef TSL9_FLASH_PAGE_H
#define TSL9_FLASH_PAGE_H
#include "feature.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {FP_RETURNED,FP_HALT,FP_TRANSFER} fp_flow;
typedef enum {FP_BOOT,FP_RUNTIME} fp_image;
typedef enum {FP_READ_REGISTER,FP_WRITE_REGISTER,FP_SOURCE_READ,FP_WORD_STORE,FP_CSR_CLEAR,FP_CSR_SET} fp_kind;
typedef enum {FP_ADDRESS,FP_VALUE_VIEW} fp_source_kind;
typedef enum {FP_NO_BOUNDARY,FP_PRIMITIVE_UNRESOLVED,FP_SOURCE_UNBACKED,FP_CONDITION_UNKNOWN,FP_SPIN_BUDGET} fp_boundary_kind;
typedef struct {
 fp_source_kind kind;uint32_t address;
 const uint8_t *data,*known;size_t available;
} fp_source;
typedef struct {fp_kind kind;uint32_t va,address,value,known,offset;unsigned width;} fp_request;
typedef struct {uint32_t value,known;} fp_scalar;
struct fp_model;
typedef struct {void *context;fp_flow (*invoke)(void *,struct fp_model *,const fp_request *,fp_scalar *);} fp_backend;
typedef struct fp_model {
 tf_model *memory;fp_backend backend;fp_image image;fp_flow flow;
 fp_request last_request;fp_boundary_kind boundary_kind;uint32_t boundary_va,boundary_address,needed_mask;
 uint32_t raw_destination,destination,source_offset,words_written,operations,spin_budget;
} fp_model;
/* Aligned SRAM words use this memory; unaligned native loads require a source
   primitive (alignment/trap outcome is not inferred from a byte view).
   Reconstructs original page body only. MMIO and CSR providers are explicit
   synthetic primitive contracts, never physical persistence or write success. */
void fp_init(fp_model *,tf_model *,fp_image,const fp_backend *);
fp_flow fp_program_page(fp_model *,uint32_t,const fp_source *);
/* Full helpers: BOOT2FE2/2FEA/3008/3016/3044, Runtime18BE4/18BEC/
   18C0A/18C18/18C46. Does not add the enclosing caller's CSR operations. */
fp_flow fp_dispatch_helper(fp_model *,uint32_t,uint32_t,const fp_source *);
#ifdef __cplusplus
}
#endif
#endif
