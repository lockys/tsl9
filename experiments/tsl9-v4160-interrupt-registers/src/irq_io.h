#ifndef TSL9_INTERRUPT_REGISTER_IO_H
#define TSL9_INTERRUPT_REGISTER_IO_H
#include <stdint.h>
#if defined(TSL9_IRQ_REGISTERS_HOST_TEST)
#include "test_io.h"
#define IR_INLINE static inline
#define IR_READ32(a) tsl9_ir_test_read32(a)
#define IR_WRITE32(a,v) tsl9_ir_test_write32(a,v)
#define IR_WRITE8(a,v) tsl9_ir_test_write8(a,v)
#define IR_CSR_CLEAR(v) tsl9_ir_test_csr_clear(v)
#define IR_CSR_SET(v) tsl9_ir_test_csr_set(v)
#define IR_RCC_OUTPUTS(a0,a1,a4,a5) tsl9_ir_test_rcc_outputs(a0,a1,a4,a5)
#define IR_INIT_OUTPUTS(a0,a1,a4,a5) tsl9_ir_test_init_outputs(a0,a1,a4,a5)
#else
#if !defined(__riscv) || __riscv_xlen != 32
#error RV32 is required unless the explicit host-test adapter is selected.
#endif
#define IR_INLINE static inline __attribute__((always_inline))
#define IR_READ32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define IR_WRITE32(a,v) (*(volatile uint32_t *)(uintptr_t)(a)=(v))
#define IR_WRITE8(a,v) (*(volatile uint8_t *)(uintptr_t)(a)=(v))
#define IR_CSR_CLEAR(v) __asm__ volatile("csrc 0x800, %0" : : "r"((uint32_t)(v)) : "memory")
#define IR_CSR_SET(v) __asm__ volatile("csrs 0x800, %0" : : "r"((uint32_t)(v)) : "memory")
/* A1 is reserved from general allocation. Helper arguments retain their exact
 * incoming A1 bits; only explicit initializer commitments may assign it. */
#define IR_COMMIT(v0,v1,v4,v5) do { \
    register uint32_t ir_a0 __asm__("a0")=(v0); \
    register uint32_t ir_a1 __asm__("a1")=(v1); \
    register uint32_t ir_a4 __asm__("a4")=(v4); \
    register uint32_t ir_a5 __asm__("a5")=(v5); \
    __asm__ volatile("" : : "r"(ir_a0),"r"(ir_a1),"r"(ir_a4),"r"(ir_a5) : "memory"); \
} while(0)
#define IR_RCC_OUTPUTS(a0,a1,a4,a5) IR_COMMIT(a0,a1,a4,a5)
#define IR_INIT_OUTPUTS(a0,a1,a4,a5) IR_COMMIT(a0,a1,a4,a5)
#endif
#endif
