/* Offline diagnostic component only: NOT a bootable firmware image.
 * The caller must supply valid machine-mode context, stack and emit callback.
 * It deliberately reads no device UID, VIN, BLE address or memory-mapped I/O.
 */
#include <stdint.h>
typedef void (*tsl9_probe_emit)(const uint8_t *bytes, uint32_t length);
#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline))
void tsl9_probe_capture(tsl9_probe_emit emit)
{
    if (!emit) return;
    uint32_t architecture, implementation;
    __asm__ volatile ("csrr %0, 0xf12" : "=r" (architecture));
    __asm__ volatile ("csrr %0, 0xf13" : "=r" (implementation));
    uint8_t frame[12] = {'T', '9', 'D', 1};
    for (unsigned i = 0; i < 4; ++i) {
        frame[4 + i] = (uint8_t)(architecture >> (8u * i));
        frame[8 + i] = (uint8_t)(implementation >> (8u * i));
    }
    emit(frame, sizeof frame);
}
