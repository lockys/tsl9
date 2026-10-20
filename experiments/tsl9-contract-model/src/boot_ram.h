#ifndef TSL9_BOOT_RAM_H
#define TSL9_BOOT_RAM_H
#include "feature.h"
#ifdef __cplusplus
extern "C" {
#endif
#define BR_REGISTRY UINT32_C(0x200094cc)
#define BR_UART UINT32_C(0x20009594)
typedef enum { BR_RETURNED,BR_HALT,BR_TRANSFER } br_flow;
struct br_model;
typedef struct {
    void *context;
    int (*rom_status)(void *,unsigned,uint8_t,uint16_t,uint32_t);
    br_flow (*free_argument)(void *,uint32_t);
    br_flow (*callback)(void *,struct br_model *,uint32_t,uint32_t);
    br_flow (*uart_command)(void *,struct br_model *,uint8_t,uint32_t,uint16_t);
} br_backend;
typedef struct br_model {
    tf_model *memory;br_backend backend;br_flow flow;
    uint32_t boundary_address,boundary_va,last_ticks,last_rom_offset;
    uint32_t requests,callback_calls,free_calls,uart_commands;
} br_model;
void br_init(br_model *,tf_model *,const br_backend *);
/* Only original target .data/BSS stores; leave ROM/external SRAM unaffected. */
br_flow br_cold_start(br_model *,const uint8_t *,size_t);
int br_schedule(br_model *,uint32_t,uint32_t,uint32_t,uint32_t);
/* Original250E stops startup task event2, not a94CC registry cancellation. */
int br_stop_startup(br_model *);
uint16_t br_dispatch(br_model *,uint16_t);
/* Explicit UART IRQ byte and native clock result; empty batch invokes no IRQ.
   UART command body must be supplied through a declared adapter, not a noop. */
size_t br_uart_receive(br_model *,const uint8_t *,size_t,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
