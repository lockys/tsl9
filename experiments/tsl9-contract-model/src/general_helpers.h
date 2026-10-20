#ifndef TSL9_GENERAL_HELPERS_H
#define TSL9_GENERAL_HELPERS_H
#include "general_ble.h"
#include "dnd_actions.h"
#define GH_DND_ACTIONS_API_VERSION 1
#define GH_DND_CORE_API_VERSION 1
#define GH_DND_EFFECTS_API_VERSION 2
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { GH_NATIVE, GH_ROM, GH_MMIO_READ, GH_MMIO_WRITE } gh_kind;
typedef struct {
    gh_kind kind;
    uint32_t callsite,target; /* ROM target is table byte offset; MMIO target is address. */
    uint32_t arguments[4],known[4];unsigned argument_count;
    unsigned width; /* MMIO width in bytes; no actual device IO. */
} gh_request;
struct gh_model;
typedef struct {
    void *context;
    /* Provider must explicitly establish call return. Missing/GB_HALT stops at
       this native instruction, preserving preceding authoritative SRAM writes. */
    gb_flow (*invoke)(void *,struct gh_model *,const gh_request *,gb_scalar *);
    gb_flow (*reply)(void *,struct gh_model *,const gb_reply_request *);
    gb_flow (*schedule)(void *,struct gh_model *,uint32_t,uint32_t,uint32_t,uint32_t,gb_scalar *);
} gh_backend;
typedef struct gh_model {
    tf_model *memory;gh_backend backend;
    gb_flow flow;uint32_t entry,argument,boundary_va,boundary_address;
    gh_request last_request;
    uint32_t calls,replies,schedules;
    uint8_t recognized;
} gh_model;
void gh_init(gh_model *,tf_model *,const gh_backend *);
/* Recognizes Runtime908E/13BE8/13D9C/95EC/13A62 plus transparent dependencies
   13B5C/133FA/13156/81AA/81B0/9432/93EE/93CC/9388/94E6. a0-only public entries
   use argument;94CC also needs a1/a2, so its internal typed route is separate.
   No second native RAM, host clock field, original target execution, or IO. */
gb_flow gh_dispatch(gh_model *,uint32_t,uint32_t,gb_scalar *);
/* Fixed-BIN DND entries16F4A/17024/17048/170E2/17176. a0/a1 are complete
   synthetic words;17048 preserves fullword tests and only truncates its store.
   Only170E2 defines a task-mask result. Missing primitive contracts halt; core and actions both use freestanding
   dnd_actions with the same backend. Feedback and mode0 now run there too;
   ROM/MMIO arguments and schedule returns preserve value/known metadata.
   No duplicate host core algorithms; no physical backend binding is implied. */
gb_flow gh_dispatch_pair(gh_model *,uint32_t,uint32_t,uint32_t,gb_scalar *);
/* Runtime94CC registration: callback plus original native a1/a2 values;
   their hardware-level meanings are not established by this slice. */
gb_flow gh_pattern_register(gh_model *,uint32_t,uint32_t,uint16_t,gb_scalar *);
#ifdef __cplusplus
}
#endif
#endif
