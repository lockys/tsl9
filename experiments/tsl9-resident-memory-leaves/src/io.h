#ifndef TSL9_RESIDENT_MEMORY_IO_H
#define TSL9_RESIDENT_MEMORY_IO_H
#include "memory_leaves.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Native compilation deliberately leaves these five real I/O ports UND.
 * host_io.c implements them using synthetic callbacks; it is not linked into
 * the native object or offered as a resident/physical memory provider. */
int ml_port_read8(ml_io *,uint32_t,uint32_t *);
int ml_port_read32(ml_io *,uint32_t,uint32_t *);
int ml_port_write8(ml_io *,uint32_t,uint32_t);
int ml_port_write32(ml_io *,uint32_t,uint32_t);
int ml_port_fence_i(ml_io *);
#ifdef __cplusplus
}
#endif
#endif
