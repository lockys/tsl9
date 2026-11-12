#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
extern volatile uint8_t destination;
uint32_t tsl9_record_dispatch_provider_b0b0(uint32_t value) { destination = (uint8_t)value; return value; }
#ifdef __cplusplus
}
#endif
