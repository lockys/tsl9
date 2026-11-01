/* Offline adapter candidate; not a firmware entry or device integration. */
#include <stdint.h>

/* Candidate argument order observed at the original 0x8A56 TX entry.
 * The caller supplies the transport, connection and command; none are guessed.
 * The transport must consume/copy the stack payload before it returns.
 */
typedef void (*tsl9_probe_tx)(uint32_t connection, uint32_t command,
                              const uint8_t *payload, uint32_t length);

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline))
void tsl9_probe_send(tsl9_probe_tx tx, uint32_t connection, uint32_t command)
{
    if (!tx || connection > 0xffffu || connection == 0xfffeu || command > 0xffu) return;
    uint32_t architecture, implementation;
    __asm__ volatile ("csrr %0, 0xf12" : "=r" (architecture));
    __asm__ volatile ("csrr %0, 0xf13" : "=r" (implementation));
    uint8_t frame[12] = {'T', '9', 'D', 1};
    for (unsigned i = 0; i < 4; ++i) {
        frame[4 + i] = (uint8_t)(architecture >> (8u * i));
        frame[8 + i] = (uint8_t)(implementation >> (8u * i));
    }
    tx(connection, command, frame, sizeof frame);
}
