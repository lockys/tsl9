#ifndef TSL9_APK_OTA_H
#define TSL9_APK_OTA_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

/* Host-only reconstruction of the APK 1.2.7 receive/acceptance semantics.
 * No transport, firmware interpreter, target address dereference or sender. */
typedef enum { AK_NO=0, AK_YES=1, AK_UNKNOWN=2 } ak_truth;
typedef enum { AK_RETURNED=0, AK_THROWN=1, AK_EFFECT_UNKNOWN=2 } ak_effect;
typedef ak_effect (*ak_callback)(void *, uint8_t, uint8_t *, size_t);
typedef struct {
    uint8_t state, type, sum;
    uint16_t declared, index;
    uint8_t retained[4096];
    size_t retained_length;
    int64_t notification_time;
} ak_rx;
typedef struct {
    size_t consumed, callbacks;
    ak_effect effect;
} ak_feed_result;

void ak_rx_init(ak_rx *);
/* Explicit monotonic-or-backwards JS Date values, restricted to exact int64
 * differences. Callback must not reenter or mutate the parser fields. It may
 * modify its borrowed buffer during the call, but must not keep/use that
 * pointer after returning. JS array identity/lifetime is not represented.
 * Input notification bytes must not alias parser storage. All original
 * TypedArray allocations are assumed to succeed. A thrown/unknown callback halts this notification before
 * the APK's subsequent reset; its outside exception handling is unmodelled. */
ak_feed_result ak_rx_feed(ak_rx *, const uint8_t *, size_t, int64_t,
                          ak_callback, void *);
/* A missing expected page is UNKNOWN (the original can throw). Empty input
 * returns NO without accessing the expected page. JS out-of-range expected
 * elements compare unequal to U8 inputs. This is NOT full page verification. */
ak_truth ak_verify(const uint8_t *, size_t, const uint8_t *, size_t);
/* APK W acceptance expression only; caller updataIng/index/retry/Write gates
 * are outside this function. PageSize is supplied metadata, not a constant. */
ak_truth ak_w_accepts(const uint8_t *, size_t, const uint8_t *, size_t, size_t);
#ifdef __cplusplus
}
#endif
#endif
