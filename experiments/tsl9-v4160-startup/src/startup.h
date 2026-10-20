#ifndef TSL9_V4160_STARTUP_H
#define TSL9_V4160_STARTUP_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Native RV32 component, compile/static-link audit only. Never call on host. */
void tsl9v4160_reset(void);
extern const uint8_t __tsl9v4160_initializer[128];
extern uint8_t __tsl9v4160_ram[35160];
#ifdef __cplusplus
}
#endif
#endif
