#ifndef TSL9_APK_TX_H
#define TSL9_APK_TX_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

/* Readable host contract for original APK tx/txData/txCallback.
 * This interface never writes BLE. A WRITE is an observation at the SDK call,
 * not a success, completion, firmware acknowledgement or Flash result. */
typedef enum { AT_OK=0, AT_CAPACITY, AT_DOMAIN, AT_NO_PROGRESS } at_status;
typedef enum { AT_IDLE=0, AT_WRITE, AT_DISCONNECTED, AT_BOUNDARY } at_kind;
typedef struct {
    int32_t mtu; /* usable bytes, initially20; original MTU event stores ATT-3 */
    const char *device_id, *service_id, *characteristic_id;
    unsigned notify, write_no_response;
} at_transport;
typedef struct {
    at_transport transport;
    uint8_t *wire;
    size_t capacity, wire_length, stride, chunks;
    uint64_t index, retry_count;
    unsigned initialized, stalled;
} at_sender;
typedef struct {
    at_kind kind;
    at_status status;
    uint64_t index, retry_count;
    unsigned value_defined, write_no_response;
    const uint8_t *value;
    size_t length;
    const char *device_id, *service_id, *characteristic_id;
} at_observation;

/* Valid U8 command/payload; length<=UINT32_MAX. Pure framing, including the
 * original low16 length wrap. Capacity/domain failures write no output bytes.
 * Output/input must not overlap; all allocations and JS coercions outside the
 * byte-array/integer-MTU domain are outside this contract. */
at_status at_encode(uint8_t, const uint8_t *, size_t, uint8_t *, size_t, size_t *);
/* init/transport_init require a nonNULL state object. */
void at_init(at_sender *, uint8_t *, size_t);
/* Original txvarinit resets only transport fields, not shared queue state. */
void at_transport_init(at_sender *, const char *);
/* Replaces ONE shared queue, even with older writes still in flight. Returned
 * byte/string views are borrowed until the next mutation: the host observer
 * must copy them immediately, like retaining the original ArrayBuffer value.
 * No generation filter, serialization, auto resume or automatic callback.
 * Callbacks below mean explicit delivery of a previously submitted SDK callback
 * (one success OR fail per call is the provider assumption, not a source proof).
 * They act on current state regardless of which request produced the callback.
 * NULL sender/storage, insufficient capacity, uninitialized callbacks or JS
 * integer-exactness exhaustion are own interface boundaries, not APK guards.
 * A nonprogressing source loop ends the admitted trace: later calls remain
 * stopped until at_init starts an independent scenario. stalled is host-only. */
at_observation at_begin(at_sender *, uint8_t, const uint8_t *, size_t);
at_observation at_success(at_sender *);
at_observation at_failure(at_sender *);
/* Typed-byte-array helper only. has_object=0 denotes absent/unknown object and
 * returns DOMAIN rather than inventing 14zero bytes for a JS property error. */
at_status at_uid14(unsigned has_object, const uint8_t *, size_t, uint8_t[14]);
#ifdef __cplusplus
}
#endif
#endif
