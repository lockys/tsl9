#ifndef TSL9_IRQ_NATIVE_IO_H
#define TSL9_IRQ_NATIVE_IO_H
#include <stdint.h>
#if defined(TSL9_IRQ_REGISTERS_HOST_TEST)
#include "test_io.h"
#define IR_INLINE static inline
#define IR_BASE_ON() UINT32_C(0x40021000)
#define IR_BASE_OFF() UINT32_C(0x40021000)
#define IR_MASK_VALUE(v) (v)
#define IR_MASK_LITERAL(v) (v)
#define IR_READ32(a) tsl9_ir_test_read32(a)
#define IR_WRITE32(a,v) tsl9_ir_test_write32(a,v)
#define IR_WRITE8(a,v) tsl9_ir_test_write8(a,v)
#define IR_CSR_CLEAR(v) tsl9_ir_test_csr_clear(v)
#define IR_CSR_SET(v) tsl9_ir_test_csr_set(v)
IR_INLINE uint32_t ir_rcc_return(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5)
{
    tsl9_ir_test_rcc_outputs(a0,a1,a4,a5);return a0;
}
IR_INLINE uint32_t ir_init_return(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5)
{
    tsl9_ir_test_init_outputs(a0,a1,a4,a5);return a0;
}
#else
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 is required unless the explicit host-test adapter is selected.
#endif
#define IR_INLINE static inline __attribute__((always_inline))
/* Per-branch output-only LUI avoids a shared constant/input SSA value and
 * keeps the base in the register actually required at the helper boundary. */
IR_INLINE uint32_t ir_base_on(void)
{
    register uint32_t base __asm__("a4");
    __asm__ volatile("lui %0, 0x40021" : "=r"(base) : : "memory");return base;
}
IR_INLINE uint32_t ir_base_off(void)
{
    register uint32_t base __asm__("a5");
    __asm__ volatile("lui %0, 0x40021" : "=r"(base) : : "memory");return base;
}
IR_INLINE uint32_t ir_mask_value(uint32_t value)
{
    register uint32_t mask __asm__("a0")=value;
    __asm__ volatile("" : "+r"(mask) : : "memory");return mask;
}
#define IR_BASE_ON() ir_base_on()
#define IR_BASE_OFF() ir_base_off()
#define IR_MASK_VALUE(v) ir_mask_value(v)
/* The initializer's masks are immediate operands, rather than C values kept
 * live across other RMWs. Standalone helpers keep their dynamic mask input. */
#define IR_MASK_LITERAL(v) __extension__ ({ \
    register uint32_t ir_literal __asm__("a0"); \
    __asm__ volatile("li %0, %1" : "=r"(ir_literal) : "i"(v) : "memory"); \
    ir_literal; \
})
#define IR_READ32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define IR_WRITE32(a,v) (*(volatile uint32_t *)(uintptr_t)(a)=(v))
#define IR_WRITE8(a,v) (*(volatile uint8_t *)(uintptr_t)(a)=(v))
/* CSR masks are also emitted per use; no cross-function constant cache. */
#define IR_CSR_CLEAR(v) do { \
    register uint32_t ir_csr __asm__("a4"); \
    __asm__ volatile("li %0, %1\n\tcsrc 0x800, %0" : "=r"(ir_csr) : "i"(v) : "memory"); \
} while(0)
#define IR_CSR_SET(v) do { \
    register uint32_t ir_csr __asm__("a4"); \
    __asm__ volatile("li %0, %1\n\tcsrs 0x800, %0" : "=r"(ir_csr) : "i"(v) : "memory"); \
} while(0)
IR_INLINE uint32_t ir_commit(uint32_t v0,uint32_t v1,uint32_t v4,uint32_t v5)
{
    register uint32_t a0 __asm__("a0")=v0;
    register uint32_t a1 __asm__("a1")=v1;
    register uint32_t a4 __asm__("a4")=v4;
    register uint32_t a5 __asm__("a5")=v5;
    __asm__ volatile("" : "+r"(a0) : "r"(a1),"r"(a4),"r"(a5) : "memory");
    return a0;
}
#define ir_rcc_return(a0,a1,a4,a5) ir_commit(a0,a1,a4,a5)
#define ir_init_return(a0,a1,a4,a5) ir_commit(a0,a1,a4,a5)
#endif
#endif
