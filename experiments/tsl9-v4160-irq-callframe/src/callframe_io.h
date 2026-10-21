#ifndef TSL9_IRQ_CALLFRAME_IO_H
#define TSL9_IRQ_CALLFRAME_IO_H
#include "../../tsl9-v4160-irq-native/src/native_io.h"

#if defined(TSL9_IRQ_REGISTERS_HOST_TEST)
#define CF_CSR_DECLARE uint32_t cf_csr=0x88u
#define CF_CSR_CLEAR() IR_CSR_CLEAR(cf_csr)
#define CF_CSR_SET() IR_CSR_SET(cf_csr)
#define CF_FAST_DECLARE uint32_t cf_fast=0x02020000u
#define CF_SLOW_DECLARE uint32_t cf_slow=0x1000u
#define CF_FAST_MASK() (cf_fast+6u)
#define CF_SLOW_MASK() (cf_slow+29u)
#define CF_CALL(name,mask,enabled) name((mask),(enabled))
#define CF_FINAL_CLEAR(name,mask) name((mask),0u)
#define CF_RETURN(value) ir_init_return((value),0u,0x80u,UINT32_C(0xe000e000))
#define CF_NVIC_DECLARE uint32_t cf_nvic=UINT32_C(0xe000e000)
#define CF_ZERO8(offset) IR_WRITE8(cf_nvic+(offset),0u)
#define CF_WRITE8(offset,value) IR_WRITE8(cf_nvic+(offset),(value))
#define CF_WRITE32(offset,value) IR_WRITE32(cf_nvic+(offset),(value))
#else
/* Only narrow ABI/ISA boundary primitives are assembly. The sequencing,
 * masks, peripheral stores and exported functions remain readable C/C++. */
#define CF_CSR_DECLARE \
    register uint32_t cf_csr __asm__("s2"); \
    __asm__ volatile("li %0, 0x88" : "=r"(cf_csr) : : "memory")
#define CF_CSR_CLEAR() __asm__ volatile("csrc 0x800, %0" : : "r"(cf_csr) : "memory")
#define CF_CSR_SET() __asm__ volatile("csrs 0x800, %0" : : "r"(cf_csr) : "memory")
#define CF_FAST_DECLARE \
    register uint32_t cf_fast __asm__("s1"); \
    __asm__ volatile("lui %0, 0x2020" : "=r"(cf_fast) : : "memory")
#define CF_SLOW_DECLARE \
    register uint32_t cf_slow __asm__("s0"); \
    __asm__ volatile("lui %0, 0x1" : "=r"(cf_slow) : : "memory")
#define CF_LIVE_ADD(reg,addend) __extension__ ({ \
    __asm__ volatile("" : "+r"(reg) : : "memory"); (reg)+(addend); \
})
#define CF_FAST_MASK() CF_LIVE_ADD(cf_fast,6u)
#define CF_SLOW_MASK() CF_LIVE_ADD(cf_slow,29u)
/* An explicit four-byte JAL is needed under --no-relax. The known leaf
 * helpers preserve A1 and every register except A0/A4/A5. RA is declared
 * clobbered so the compiler must preserve its incoming return address. */
#define CF_CALL(name,mask,enabled) __extension__ ({ \
    register uint32_t cf_a0 __asm__("a0")=(mask); \
    register uint32_t cf_a1 __asm__("a1")=(enabled); \
    __asm__ volatile("jal ra, " #name : "+r"(cf_a0) : "r"(cf_a1) \
                     : "ra","a4","a5","memory"); \
    cf_a0; \
})
/* The original last call establishes A1=0 before the final mask add. A
 * volatile output-only assignment pins that instruction ordering. */
#define CF_FINAL_CLEAR(name,mask) __extension__ ({ \
    register uint32_t cf_a1 __asm__("a1"); \
    __asm__ volatile("li %0, 0" : "=r"(cf_a1) : : "memory"); \
    register uint32_t cf_a0 __asm__("a0")=(mask); \
    __asm__ volatile("jal ra, " #name : "+r"(cf_a0) : "r"(cf_a1) \
                     : "ra","a4","a5","memory"); \
    cf_a0; \
})
/* A1/A4/A5 already hold their required normal outputs after the last clear
 * and pinned PFIC stores. Re-loading constants here adds ten bytes. Their
 * actual final definitions must be checked in the linked machine code. */
#define CF_RETURN(value) __extension__ ({ \
    register uint32_t cf_a0 __asm__("a0")=(value); \
    __asm__ volatile("" : "+r"(cf_a0) : : "memory"); cf_a0; \
})
#define CF_NVIC_DECLARE \
    register uint32_t cf_nvic __asm__("a5"); \
    __asm__ volatile("lui %0, 0xe000e" : "=r"(cf_nvic) : : "memory")
#define CF_ZERO8(offset) do { \
    __asm__ volatile("" : "+r"(cf_nvic) : : "memory"); \
    IR_WRITE8(cf_nvic+(offset),0u); \
} while(0)
#define CF_STORE(width,offset,value) do { \
    register uint32_t cf_word __asm__("a4")=(value); \
    __asm__ volatile("" : "+r"(cf_nvic),"+r"(cf_word) : : "memory"); \
    IR_WRITE##width(cf_nvic+(offset),cf_word); \
} while(0)
#define CF_WRITE8(offset,value) CF_STORE(8,offset,value)
#define CF_WRITE32(offset,value) CF_STORE(32,offset,value)
#endif
#endif
