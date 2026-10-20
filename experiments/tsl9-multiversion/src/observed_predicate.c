#include "observed_predicate.h"
uint32_t tsl9_observed_predicate(uint8_t cfg_byte4, uint32_t index,
                                 const uint8_t *state3) {
    if ((cfg_byte4 & UINT8_C(0x08)) != 0 || index > UINT32_C(2)) {
        return UINT32_C(0);
    }
    return state3[index] < UINT8_C(3) ? UINT32_C(1) : UINT32_C(0);
}
