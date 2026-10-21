#include "reset_memory.h"
#include <stdint.h>

#if defined(TSL9_RESET_MEMORY_HOST_TEST)
#include "test_io.h"
#define RM_GP() tsl9_rm_test_gp()
#define RM_READ32(a) tsl9_rm_test_read32(a)
#define RM_WRITE32(a,v) tsl9_rm_test_write32(a,v)
#define RM_OUTPUTS(a0,a1,a2) tsl9_rm_test_outputs(a0,a1,a2)
#else
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 is required unless the explicit host-test adapter is selected.
#endif
static inline uint32_t rm_live_gp(void)
{
    register uint32_t value __asm__("gp");
    __asm__ volatile("" : "=r"(value) : : "memory");
    return value;
}
#define RM_GP() rm_live_gp()
#define RM_READ32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RM_WRITE32(a,v) (*(volatile uint32_t *)(uintptr_t)(a)=(v))
#define RM_OUTPUTS(v0,v1,v2) do { \
    register uint32_t rm_a0 __asm__("a0")=(v0); \
    register uint32_t rm_a1 __asm__("a1")=(v1); \
    register uint32_t rm_a2 __asm__("a2")=(v2); \
    __asm__ volatile("" : : "r"(rm_a0),"r"(rm_a1),"r"(rm_a2) : "memory"); \
} while (0)
#endif

/* Source ID2966 [0x186BA,0x186F8): separate GP observations, forward
 * interleaved word accesses and unsigned loop bounds. Do not force 32 copies
 * or add a timeout: under altered GP some original domains do not terminate.
 * Normal fixed-GP execution copies32 words and clears8758 words. */
void tsl9_rebuild_reset_memory_186ba(void)
{
    uint32_t source=UINT32_C(0x1ab60);
    uint32_t destination=RM_GP();
    const uint32_t copy_end=RM_GP()+128u;
    uint32_t clear;
    const uint32_t zero_end=UINT32_C(0x2000c958);
    while(destination<copy_end) {
        const uint32_t word=RM_READ32(source);
        RM_WRITE32(destination,word);
        source+=4u;destination+=4u;
    }
    clear=RM_GP()+128u;
    while(clear<zero_end) {
        RM_WRITE32(clear,0u);
        clear+=4u;
    }
    RM_OUTPUTS(clear,zero_end,copy_end);
#if defined(TSL9_RESET_MEMORY_FRAGMENT) && !defined(TSL9_RESET_MEMORY_HOST_TEST)
    /* Optional fragment interface: a real control transfer, not a reachable
     * bare __builtin_unreachable(). The continuation remains an obligation. */
    __asm__ volatile("c.j __tsl9_reset_resume_186f8" : : : "memory");
    __builtin_unreachable();
#endif
}
