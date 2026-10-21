#ifndef TSL9_INTERRUPT_INIT_TEST_IO_H
#define TSL9_INTERRUPT_INIT_TEST_IO_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
uint32_t tsl9_test_read32(uint32_t address);
void tsl9_test_write32(uint32_t address, uint32_t value);
void tsl9_test_write8(uint32_t address, uint8_t value);
void tsl9_test_csr_clear(uint32_t mask);
void tsl9_test_csr_set(uint32_t mask);
#ifdef __cplusplus
}
#endif
#endif
