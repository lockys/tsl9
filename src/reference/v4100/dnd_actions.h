#ifndef TSL9_DND_ACTIONS_H
#define TSL9_DND_ACTIONS_H
#include <stdint.h>
#define DA_CORE_API_VERSION 1
#define DA_EFFECTS_API_VERSION 2
#ifdef __cplusplus
extern "C" {
#endif
/* Freestanding fixed-input logic. No target RAM object, heap, MMIO, clock,
   startup, ROM implementation or transport. The backend owns those contracts. */
typedef enum { DA_RETURNED,DA_HALT,DA_TRANSFER } da_flow;
typedef enum { DA_ROM,DA_NATIVE,DA_MMIO_READ,DA_MMIO_WRITE } da_kind;
typedef struct {uint32_t value,known;} da_scalar;
typedef struct {
 void *context;
 da_flow (*read)(void *,uint32_t,unsigned,uint32_t,uint32_t,da_scalar *);
 da_flow (*write)(void *,uint32_t,uint32_t,unsigned,uint32_t,uint32_t);
 da_flow (*call)(void *,da_kind,uint32_t,uint32_t,const da_scalar *,unsigned,da_scalar *);
 da_flow (*schedule)(void *,uint32_t,uint32_t,uint32_t,da_scalar *);
} da_backend;
/* Memory widths are bytes; write receives value, width, known mask, site.
   read need=0 returns raw value/known for branch-specific consumption.
   MMIO_READ args=[width_bits]; MMIO_WRITE args=[value,width_bits].
   ROM/native args and scheduling results retain their value/known metadata. */
typedef struct {
 da_backend io;da_flow flow;uint32_t boundary_va,boundary_address;
} da_machine;
void da_init(da_machine *,const da_backend *);
int da_recognizes(uint32_t);
/* Queries/task/cancel define scalar results where supported; other entries
   retain unknown return data. Providers preserve prefix on failure; TRANSFER
   is sticky. da_run keeps the legacy single-register API with a1=0. */
da_flow da_run(da_machine *,uint32_t,uint32_t,da_scalar *);
da_flow da_run_pair(da_machine *,uint32_t,uint32_t,uint32_t,da_scalar *);
#ifdef __cplusplus
}
#endif
#endif
