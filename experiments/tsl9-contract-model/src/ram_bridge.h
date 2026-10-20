#ifndef TSL9_RAM_BRIDGE_H
#define TSL9_RAM_BRIDGE_H
#include "feature.h"
#include "tsl9_contract.h"
#include "boot_ram.h"
#include "general_ble.h"
#include "rom_candidate.h"
#include "general_helpers.h"
#include "boot_startup.h"
#include "rom_kernel.h"
#include "native_callbacks.h"
#include "general_deep.h"
#include "general_reports.h"
#include "flash_page.h"
#include "spi_can.h"
#include "can_receive.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
    void *context;
    /* Declared ROM+316 query: 1 accepts, 0 refuses, -1 is unknown. */
    int (*connection_status)(void *,uint16_t,uint32_t);
} ta_link_backend;
typedef struct {
    /* The sole authoritative native SRAM. ota below is command-call staging. */
    tf_model memory;
    tc_model ota;
    tc_backend external;
    tf_backend external_features;
    gb_backend external_general;
    gb_model general;
    br_model boot;
    gh_model helpers;
    bs_model startup;
    rk_model kernel;
    nc_model native_callbacks;
    gd_model deep;
    gr_model reports;
    fp_model flash;
    sc_model spi;
    cr_model receive;
    gh_backend external_helpers;
    bs_backend external_startup;
    rk_backend external_kernel;
    nc_backend external_native;
    gd_backend external_deep;
    gr_backend external_reports;
    fp_backend external_flash;
    sc_backend external_spi;
    cr_backend external_receive;
    int flash_enabled;
    int startup_enabled;
    rc_adapter *candidate;
    ta_link_backend link;
    tc_transport transport;
    uint16_t handle;
    uint32_t unresolved, last_unknown_address, replies_committed;
    uint32_t reply_source_address; /* 0: declared abstract stack/core staging. */
    const uint8_t *reply_source_data,*reply_source_known;
    size_t reply_source_available;
    uint32_t reply_wrapper_va; /* 8CFA direct builder; other existing requests include copy wrapper. */
    uint32_t callback_return_boundary; /* Native callback stopped at an evidence boundary. */
    int halted,transferred,last_schedule_result;
} ta_model;
/* Runtime initializes the previously verified .data/BSS slice. BOOT RAM remains
   unknown until the caller supplies an explicit startup/synthetic fixture. */
void ta_init(ta_model *,tc_image,const uint8_t *,size_t,const tc_backend *,const tf_backend *,const ta_link_backend *);
/* Explicit host choice of a new activation after TRANSFER. No native suffix,
   parser/RAM reset, hardware reset or future-device execution is inferred. */
int ta_resume_activation(ta_model *);
/* Explicit native clock result and incoming chunk handle; n<=65535 and a readable
   input span are API preconditions. Keep the initialized model at a stable address.
   Returns bytes interpreted;
   halted stops interpretation; transferred distinguishes a declared nonreturn
   from an evidence boundary. Neither is a claimed native early return. */
size_t ta_receive(ta_model *,uint16_t,const uint8_t *,size_t,uint32_t);
/* Invoke OTA callback effects through the same SRAM staging. No timer is run here. */
void ta_deliver_ota(ta_model *,uint32_t,uint32_t);
/* Runtime task event bits are explicit synthetic input, not a wall-clock timer. */
uint16_t ta_dispatch_runtime(ta_model *,uint16_t);
void ta_set_general_backend(ta_model *,const gb_backend *);
void ta_set_helper_backend(ta_model *,const gh_backend *);
/* Explicit host invocation of the reconstructed DND core. This is not a
   hardware timer, BLE transport, or a native firmware entrypoint. */
gb_flow ta_dispatch_dnd(ta_model *,uint32_t,uint32_t,uint32_t,gb_scalar *);
/* Explicit HAL opts into the complete new BOOT stay/pattern route; absent
   providers remain unknown. Earlier explicit GB1D54 provider can still supply
   its own declared call contract when this opt-in has not been selected. */
void ta_set_startup_backend(ta_model *,const bs_backend *);
void ta_set_kernel_backend(ta_model *,const rk_backend *);
void ta_set_native_backend(ta_model *,const nc_backend *);
nc_flow ta_dispatch_native(ta_model *,uint32_t,uint32_t);
/* Supplied invoke/reply callbacks override the corresponding primitive only.
   A supplied HALT is preserved; an absent callback uses the default adapter. */
void ta_set_deep_backend(ta_model *,const gd_backend *);
gb_flow ta_dispatch_deep(ta_model *,uint32_t,uint32_t);
void ta_set_reports_backend(ta_model *,const gr_backend *);
gb_flow ta_dispatch_report_d1(ta_model *,uint32_t);
gb_flow ta_dispatch_report_d1_view(ta_model *,const gr_view *);
/* Selecting even a NULL flash backend enables full native page/helper bodies;
   missing primitives then stop. Legacy TC helper provider remains explicit
   when no full Flash HAL has been selected. */
void ta_set_flash_backend(ta_model *,const fp_backend *);
fp_flow ta_program_page(ta_model *,uint32_t,const fp_source *);
void ta_set_spi_backend(ta_model *,const sc_backend *);
sc_flow ta_dispatch_spi(ta_model *,uint32_t,const sc_arguments *);
void ta_set_receive_backend(ta_model *,const cr_backend *);
cr_flow ta_dispatch_receive(ta_model *,uint32_t,const cr_arguments *);
/* Explicit delegation for a custom receive primitive provider; no fallback is
   performed after its HALT. Default CSR/MMIO remain unimplemented primitives. */
cr_flow ta_receive_primitive(ta_model *,const cr_request *,cr_result *);
/* Candidate opt-in is validated against this exact shared memory/profile. */
int ta_attach_candidate(ta_model *,rc_adapter *);
br_flow ta_boot_cold_start(ta_model *,const uint8_t *,size_t);
size_t ta_receive_uart(ta_model *,const uint8_t *,size_t,uint32_t);
uint16_t ta_dispatch_boot(ta_model *,uint16_t);
bs_flow ta_dispatch_startup(ta_model *,uint16_t,uint16_t *);
bs_flow ta_pattern_irq(ta_model *);
rk_flow ta_system_process(ta_model *);
rk_flow ta_msg_receive(ta_model *,uint8_t,uint32_t *);
#ifdef __cplusplus
}
#endif
#endif
