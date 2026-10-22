/* The algorithm and eight-register bridges remain in the sealed compact TU.
 * This same-TU strong alias is a real compiler definition, not an address map. */
#include "../../tsl9-v4160-ota-handler-compact/src/ota_handler.c"

#ifdef __cplusplus
extern "C" {
#endif
uint32_t __tsl9v4160_ota_code_9c4a(uint32_t context,uint32_t command,
    uint32_t payload,uint32_t length,uint32_t ambient4,uint32_t ambient5,
    uint32_t ambient6,uint32_t ambient7)
    __attribute__((alias("tsl9_ota_handler_native_9c4a")));
#ifdef __cplusplus
}
#endif
