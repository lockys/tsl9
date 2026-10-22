#ifndef TSL9_NV_READ_CALLBACK_H
#define TSL9_NV_READ_CALLBACK_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Conditional physical-register projection, not a recovered C prototype:
 * valid only when the freshly loaded slot implements the reviewed normal
 * copy projection (A0 destination, A1 source, A2 byte count, normal A0 result).
 * This callback ignores that result. Callee full ABI remains unproved. */
typedef uint32_t (*tsl9_nv_copy_normal_projection_fn)(uint32_t,uint32_t,uint32_t);
uint32_t tsl9_nv_read_callback_1979a(uint32_t source,uint32_t words,uint32_t destination);
#ifdef __cplusplus
}
#endif
#endif
