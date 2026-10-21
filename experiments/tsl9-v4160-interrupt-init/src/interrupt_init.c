#include "interrupt_init.h"

/* The same calculation is built for hosted tests and a freestanding RV32
 * component. Only the access primitives differ; neither build selects a board
 * or establishes the original entry/interrupt ABI. */
#if defined(TSL9_IRQ_HOST_TEST)
#include "test_io.h"
static uint32_t read32(uint32_t address) { return tsl9_test_read32(address); }
static void write32(uint32_t address,uint32_t value) { tsl9_test_write32(address,value); }
static void write8(uint32_t address,uint8_t value) { tsl9_test_write8(address,value); }
static void clear_csr800(uint32_t mask) { tsl9_test_csr_clear(mask); }
static void set_csr800(uint32_t mask) { tsl9_test_csr_set(mask); }
#else
#if !defined(__riscv) || __riscv_xlen != 32
#error "Native access requires RV32; host verification requires TSL9_IRQ_HOST_TEST"
#endif
static uint32_t read32(uint32_t address) {
    return *(volatile uint32_t *)(uintptr_t)address;
}
static void write32(uint32_t address,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)address=value;
}
static void write8(uint32_t address,uint8_t value) {
    *(volatile uint8_t *)(uintptr_t)address=value;
}
static void clear_csr800(uint32_t mask) {
    __asm__ volatile("csrc 0x800, %0" : : "r"(mask) : "memory");
}
static void set_csr800(uint32_t mask) {
    __asm__ volatile("csrs 0x800, %0" : : "r"(mask) : "memory");
}
#endif

static uint32_t update32(uint32_t address,uint32_t mask,uint32_t enabled) {
    const uint32_t before=read32(address);
    const uint32_t after=enabled?(before|mask):(before&~mask);
    write32(address,after);
    return after;
}
uint32_t tsl9_rebuild_rcc_19124(uint32_t mask,uint32_t enabled) {
    return update32(UINT32_C(0x40021018),mask,enabled);
}
uint32_t tsl9_rebuild_rcc_19142(uint32_t mask,uint32_t enabled) {
    return update32(UINT32_C(0x4002101c),mask,enabled);
}
uint32_t tsl9_rebuild_rcc_19160(uint32_t mask,uint32_t enabled) {
    return update32(UINT32_C(0x4002100c),mask,enabled);
}
uint32_t tsl9_rebuild_rcc_1917e(uint32_t mask,uint32_t enabled) {
    return update32(UINT32_C(0x40021010),mask,enabled);
}
uint32_t tsl9_rebuild_interrupt_init_9a42(void) {
    uint32_t result;
    clear_csr800(UINT32_C(0x88));
    (void)tsl9_rebuild_rcc_19142(UINT32_C(0x02020006),1);
    (void)tsl9_rebuild_rcc_19124(UINT32_C(0x101d),1);
    (void)tsl9_rebuild_rcc_1917e(UINT32_C(0x02020006),1);
    (void)tsl9_rebuild_rcc_1917e(UINT32_C(0x02020006),0);
    (void)tsl9_rebuild_rcc_19160(UINT32_C(0x101d),1);
    result=tsl9_rebuild_rcc_19160(UINT32_C(0x101d),0);
    write8(UINT32_C(0xe000e42d),0);
    write32(UINT32_C(0xe000e104),UINT32_C(0x2000));
    write8(UINT32_C(0xe000e424),UINT8_C(0x20));
    write32(UINT32_C(0xe000e104),UINT32_C(0x10));
    write8(UINT32_C(0xe000e427),UINT8_C(0x30));
    write32(UINT32_C(0xe000e104),UINT32_C(0x80));
    set_csr800(UINT32_C(0x88));
    return result;
}
