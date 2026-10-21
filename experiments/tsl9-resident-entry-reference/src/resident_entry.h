#ifndef TSL9_RESIDENT_ENTRY_REFERENCE_H
#define TSL9_RESIDENT_ENTRY_REFERENCE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Fixed source-specific entry/initializer data effects, not an ISA interpreter.
 * Reference selection never identifies the physical resident. Numeric addresses
 * remain numeric. Memory callbacks preserve modeled registers; their shared
 * memory may change, including saved frame words. No original code is run.
 * bind is a separate HOST precondition: attest the then-installed RAM helper
 * matches this exact source body. It is not an extra original memory read. */
typedef enum { RI_UNKNOWN_PROFILE=0,RI_DEC2023_133D3705=1 } ri_profile;
typedef enum { RI_RETURNED=0,RI_HALT,RI_TRANSFER,RI_LIMIT } ri_flow;
typedef enum { RI_READ32,RI_WRITE32,RI_RETURN,RI_MRET,RI_BIND_COPY,RI_BIND_ZERO } ri_kind;
typedef enum { RI_NONE,RI_PROFILE,RI_MISSING_PROVIDER,RI_PROVIDER_STOP,
               RI_PROVIDER_TRANSFER,RI_BUDGET,RI_UNKNOWN_CONTROL,
               RI_OTHER_RETURN,RI_MRET_BOUNDARY } ri_boundary;
typedef enum { RI_SEED,RI_GLOBALS,RI_COPY1,RI_COPY2,RI_EPILOGUE,RI_ZERO,RI_FINAL } ri_stage;
typedef struct {uint32_t value,known;} ri_value;
typedef struct {
    ri_kind kind;ri_stage stage;uint32_t pc,argc;
    ri_value address,data,raw_target,target,args[3];
} ri_request;
typedef struct {
    void *context;
    ri_flow (*effect)(void *,const ri_request *,ri_value *);
    ri_flow (*bind)(void *,const ri_request *);
} ri_backend;
typedef struct {
    ri_profile profile;ri_backend backend;
    ri_value gp,sp,ra,a0,a1,a2,a4,a5,t0,return_target;
    ri_flow flow;ri_boundary boundary;ri_stage stage;
    uint32_t operations,budget,boundary_pc,seed_words,first_words,second_words,zero_words,bindings;
    ri_request last_request;
} ri_model;
void ri_init(ri_model *,ri_profile,const ri_backend *);
/* Distinct host activation, never native instruction resumption or cleanup. */
void ri_new_activation(ri_model *);
/* Starts the selected40000 jump/6DE7E entry, not arbitrary guest instructions.
 * Ordinary completion reaches MRET and terminates as RI_TRANSFER. For RI_MRET,
 * the effect result describes the provider's fresh synthetic transfer target
 * (e.g. shared MEPC bank); it is not an invented CSR_READ instruction. Unknown
 * target remains unknown. No MRET acknowledgement makes a physical run true. */
ri_flow ri_enter(ri_model *);
#ifdef __cplusplus
}
#endif
#endif
