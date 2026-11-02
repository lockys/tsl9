#ifndef TSL9_DISPATCH3_MODEL_H
#define TSL9_DISPATCH3_MODEL_H
#include <stdint.h>
typedef enum { D3_TO_149FC, D3_TO_14098, D3_TO_14A24, D3_TO_142C0 } d3_target;
typedef struct {
    d3_target target;
    uint8_t allocate_requested;
    uint8_t copy_requested;
    uint32_t allocate_length;
    uint32_t copy_source;
    uint32_t copy_destination;
    uint32_t copy_length;
} d3_result;
/* Pure local branch model; addresses are values only and are never accessed. */
int tsl9_dispatch3_model(uint32_t command,uint32_t length,uint32_t source,
                         uint32_t allocation_result,d3_result *out);
#endif
