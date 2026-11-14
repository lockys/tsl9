/* Host projection only: no actual callback or physical device access.
 * Assumes stable table and successful calls preserving callee-saved registers.
 * A matched nonzero payload projects a provider call before the two stores;
 * any provider side effects and the tail target's behavior are excluded. */
#include <stdint.h>

#ifdef __cplusplus
#define LINKAGE extern "C"
#else
#define LINKAGE
#endif
#ifdef _WIN32
#define EXPORT LINKAGE __declspec(dllexport)
#else
#define EXPORT LINKAGE
#endif

/* result: [matched, selected-index, provider-called, provider-argument,
 *          tail-a0, tail-a1, miss-return]. keys and values contain 15 words. */
EXPORT void callback_table_model(uint32_t key, uint32_t keys[15],
                                 uint32_t values[15], uint32_t gp_byte,
                                 uint32_t result[7])
{
    uint32_t i;
    for (i = 0; i < 7; ++i) result[i] = 0;
    for (i = 0; i < 15; ++i) {
        if (keys[i] == key) {
            uint32_t payload = values[i];
            result[0] = 1;
            result[1] = i;
            result[2] = payload != 0;
            result[3] = payload;
            keys[i] = 0;
            values[i] = 0;
            result[4] = gp_byte & UINT32_C(255);
            result[5] = UINT32_C(1) << i;
            return;
        }
    }
    result[6] = 1;
}
