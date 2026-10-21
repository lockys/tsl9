#ifndef TSL9_OTA_TX_NATIVE_H
#define TSL9_OTA_TX_NATIVE_H
#include <stdint.h>
#if defined(TX_HOST_TEST)
#include "../../tsl9-v4160-ota-tx/src/host_io.h"
#define TX_CONTEXT tx_host *h,
typedef tx_result tx_return;
#else
#define TX_CONTEXT
typedef uint32_t tx_return;
#endif
#ifdef __cplusplus
extern "C" {
#endif
tx_return tsl9_ota_tx_8a56(TX_CONTEXT uint32_t context,uint32_t command,uint32_t source,uint32_t length);
#ifdef __cplusplus
}
#endif
#endif
