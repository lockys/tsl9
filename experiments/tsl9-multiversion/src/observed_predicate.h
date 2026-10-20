#ifndef TSL9_OBSERVED_PREDICATE_H
#define TSL9_OBSERVED_PREDICATE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Value-level reconstruction of one complete 42-byte read-only routine.
 * cfg_byte4 is the captured value at (*(GP+84))+4.
 * state3 represents bytes GP+193..195. It must be readable when
 * cfg bit3 is clear and index<=2. No hardware addresses are dereferenced here.
 * This routine does not establish caller behavior or the meaning of these states. */
uint32_t tsl9_observed_predicate(uint8_t cfg_byte4, uint32_t index,
                                 const uint8_t *state3);
/* Evidence metadata only: lookup is not an image verifier or firmware selector. */
typedef struct tsl9_observed_profile {
    uint32_t firmware_id;
    uint32_t file_offset;
    uint32_t image_bytes;
    char source_sha256[65];
} tsl9_observed_profile;
/* Only the 15 exact-match images are listed. Unknown IDs return null. */
const tsl9_observed_profile *tsl9_find_observed_profile(uint32_t firmware_id);
#ifdef __cplusplus
}
#endif
#endif
