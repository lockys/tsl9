#ifndef TSL9_RESIDENT_MEMORY_NATIVE_H
#define TSL9_RESIDENT_MEMORY_NATIVE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Three numeric arguments and one u32 result; fixed-placement/original
 * physical register preservation still requires actual artifact review. */
uint32_t tsl9_native_compare_200004bc(uint32_t,uint32_t,uint32_t);
uint32_t tsl9_native_fill_2000039c(uint32_t,uint32_t,uint32_t);
uint32_t tsl9_native_copy_20000332(uint32_t,uint32_t,uint32_t);
#ifdef __cplusplus
}
#endif
#endif
