#include "native.h"
/* Force source computation into each public wrapper to remove its local
 * context/sret. The immutable algorithm bodies below remain included text.
 * Real exported algorithm/I/O functions are retained and reported. */
#include "../../tsl9-resident-memory-leaves/src/io.h"
__attribute__((always_inline)) ml_result tsl9_candidate_compare_200004bc(ml_io *,uint32_t,uint32_t,uint32_t);
__attribute__((always_inline)) ml_result tsl9_candidate_fill_2000039c(ml_io *,uint32_t,uint32_t,uint32_t);
__attribute__((always_inline)) ml_result tsl9_candidate_copy_20000332(ml_io *,uint32_t,uint32_t,uint32_t);
static __attribute__((always_inline)) inline int begin(ml_io *,uint32_t *);
__attribute__((always_inline)) int ml_port_read8(ml_io *,uint32_t,uint32_t *);
__attribute__((always_inline)) int ml_port_read32(ml_io *,uint32_t,uint32_t *);
__attribute__((always_inline)) int ml_port_write8(ml_io *,uint32_t,uint32_t);
__attribute__((always_inline)) int ml_port_write32(ml_io *,uint32_t,uint32_t);
__attribute__((always_inline)) int ml_port_fence_i(ml_io *);
#include "../../tsl9-resident-memory-leaves/src/memory_leaves.c"

int ml_port_read8(ml_io *io,uint32_t address,uint32_t *out)
{
    (void)io;*out=*(volatile uint8_t *)(uintptr_t)address;return 1;
}
int ml_port_read32(ml_io *io,uint32_t address,uint32_t *out)
{
    (void)io;*out=*(volatile uint32_t *)(uintptr_t)address;return 1;
}
int ml_port_write8(ml_io *io,uint32_t address,uint32_t value)
{
    (void)io;*(volatile uint8_t *)(uintptr_t)address=(uint8_t)value;return 1;
}
int ml_port_write32(ml_io *io,uint32_t address,uint32_t value)
{
    (void)io;*(volatile uint32_t *)(uintptr_t)address=value;return 1;
}
int ml_port_fence_i(ml_io *io)
{
    (void)io;__asm__ volatile("fence.i":::"memory");return 1;
}

static __attribute__((always_inline)) inline uint32_t return_arguments(uint32_t value,uint32_t input1,uint32_t input2)
{
    register uint32_t a0 __asm__("a0")=value,a1 __asm__("a1")=input1,a2 __asm__("a2")=input2;
    __asm__ volatile("":"+r"(a0),"+r"(a1),"+r"(a2)::"memory");return a0;
}

uint32_t tsl9_native_compare_200004bc(uint32_t address,uint32_t expected,uint32_t count)
{
    ml_io io;ml_result result=tsl9_candidate_compare_200004bc(&io,address,expected,count);return return_arguments(result.value,expected,count);
}
uint32_t tsl9_native_fill_2000039c(uint32_t destination,uint32_t value,uint32_t count)
{
    ml_io io;ml_result result=tsl9_candidate_fill_2000039c(&io,destination,value,count);return return_arguments(result.value,value,count);
}
uint32_t tsl9_native_copy_20000332(uint32_t destination,uint32_t source,uint32_t count)
{
    ml_io io;ml_result result=tsl9_candidate_copy_20000332(&io,destination,source,count);return return_arguments(result.value,source,count);
}
