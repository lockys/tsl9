#ifndef TSL9_OTA_PAGE_REPLY_H
#define TSL9_OTA_PAGE_REPLY_H
#include <stdint.h>
#if defined(OP_HOST_TEST)
#include "host_io.h"
#define OP_CONTEXT op_host *h,
typedef op_result op_return;
#else
#define OP_CONTEXT
typedef uint32_t op_return;
#endif
#ifdef __cplusplus
extern "C" {
#endif
op_return tsl9_ota_page_reply_9b8e(OP_CONTEXT uint32_t connection,uint32_t command,uint32_t index);
#ifdef __cplusplus
}
#endif
#endif
