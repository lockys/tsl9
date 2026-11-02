#ifndef TSL9_DISPATCH2_MODEL_H
#define TSL9_DISPATCH2_MODEL_H
#include <stdint.h>
typedef enum { TSL9_AT_141FA, TSL9_AT_141F6, TSL9_AT_14098 } tsl9_dispatch2_destination;
typedef struct {
    tsl9_dispatch2_destination destination;
    uint8_t queue_requested;
    uint8_t scheduler_requested;
    uint32_t scheduler_callback;
    uint32_t scheduler_delay;
} tsl9_dispatch2_result;
/* Local transfer model; queue_result is meaningful only when requested. */
int tsl9_dispatch2_model(uint32_t entry, uint32_t command, uint32_t queue_result,
                         tsl9_dispatch2_result *out);
#endif
