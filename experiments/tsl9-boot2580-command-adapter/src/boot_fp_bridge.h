#ifndef TSL9_BOOT2580_FP_BRIDGE_H
#define TSL9_BOOT2580_FP_BRIDGE_H
#include "boot_command.h"
#include "flash_page.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Thin host composition seam, not an original ABI or a hardware backend.
 * Only handles a known selected-BOOT20E6 request. FP_ADDRESS retains live source
 * reads in the existing FP_BOOT engine; there is no256B input snapshot here.
 * Other command requests need their own explicit memory/callee providers.
 * The fp_model must share the command provider's synthetic memory. */
bc_flow bc_fp_program(const bc_request *,fp_model *);
#ifdef __cplusplus
}
#endif
#endif
