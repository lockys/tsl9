#include <stdint.h>
#include <stddef.h>

/* Provider is opaque: it may mutate queue and returns normally. */
typedef void (*provider_fn)(uint8_t *, const uint8_t *, uint32_t, uint32_t);
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif
#ifdef __cplusplus
extern "C" {
#endif
EXPORT void producer(uint8_t *queue, uint32_t id, const uint8_t *source,
                     uint32_t length, uint32_t tag, provider_fn provider)
{
    size_t i;
    for (i = 0; i < 32; ++i) {
        uint8_t *slot = queue + i * 12;
        if (slot[0] == 0 && slot[1] == 0) {
            slot[0] = (uint8_t)id;
            slot[1] = (uint8_t)(id >> 8);
            slot[2] = (uint8_t)length;
            provider(slot + 3, source, length, tag);
            slot[11] = (uint8_t)tag;
            return;
        }
    }
}
#ifdef __cplusplus
}
#endif
