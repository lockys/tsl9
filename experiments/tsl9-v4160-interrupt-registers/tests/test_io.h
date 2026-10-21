#ifndef TSL9_IRQ_REGISTER_TEST_IO_H
#define TSL9_IRQ_REGISTER_TEST_IO_H
#include <stdint.h>
uint32_t tsl9_ir_test_read32(uint32_t address);
void tsl9_ir_test_write32(uint32_t address,uint32_t value);
void tsl9_ir_test_write8(uint32_t address,uint8_t value);
void tsl9_ir_test_csr_clear(uint32_t mask);
void tsl9_ir_test_csr_set(uint32_t mask);
void tsl9_ir_test_rcc_outputs(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5);
void tsl9_ir_test_init_outputs(uint32_t a0,uint32_t a1,uint32_t a4,uint32_t a5);
#endif
