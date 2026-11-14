#ifndef TSL9_DISPATCH_148B4_MODEL_H
#define TSL9_DISPATCH_148B4_MODEL_H
#include <stdint.h>
/* Projections assume all indicated loads/stores succeed; no traps or memory effects.
 * A write is an event, not confirmation of a physical write. Event addresses and
 * values are meaningful only when wrote != 0. Bridge pointers must be non-null
 * and point to correctly sized, ABI-compatible objects. */
typedef struct { uint32_t a0, a1, a2, a3, s0, sp, t1, t3; } regs148b4;
typedef struct { regs148b4 r; uint32_t pc, read_addr, write_addr; uint16_t write_value; int wrote; } result148b4;
result148b4 step_148b4(regs148b4 r, uint16_t loaded);
uint32_t gate_1488e(uint32_t a2, uint32_t s2);
typedef struct { uint32_t a1, a2, a4, a5, a6, a7, sp, t1, t3; } regs148de;
typedef struct { regs148de r; uint32_t pc, write_addr; uint16_t write_value; int wrote; } result148de;
result148de step_148de(regs148de r);
#endif
