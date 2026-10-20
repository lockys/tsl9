#ifndef TSL9_V4160_VECTOR_NATIVE_H
#define TSL9_V4160_VECTOR_NATIVE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* 82 captured words; logical vector extent and IRQ ABI remain unknown. */
extern const uint32_t tsl9v4160_vector_captured_view[82];
/* __tsl9v4160_vector_base is a size0 NOTYPE linker address, not a second object.
 * FUNC symbols are assembly entry labels only. No C-callable ISR prototypes
 * are declared because their calling/interrupt ABI has not been proved. */
#ifdef __cplusplus
}
#endif
#endif
