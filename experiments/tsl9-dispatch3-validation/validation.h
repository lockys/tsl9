#ifndef TSL9_DISPATCH3_VALIDATION_H
#define TSL9_DISPATCH3_VALIDATION_H
#include <stdint.h>
typedef struct {
    uint8_t bytes_checked;
    uint8_t release_requested;
    uint8_t continue_success;
} d3_validation_result;
/* Synthetic inputs: does not perform validation, allocation or release. */
int tsl9_dispatch3_validation(uint32_t validator_return,const uint8_t field[4],d3_validation_result *out);
#endif
