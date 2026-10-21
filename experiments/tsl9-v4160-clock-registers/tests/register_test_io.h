#ifndef TSL9_CLOCK_REGISTER_TEST_IO_H
#define TSL9_CLOCK_REGISTER_TEST_IO_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
uint32_t tsl9_ca_test_gp(void);
uint32_t tsl9_ca_test_read32(uint32_t address);
uint8_t tsl9_ca_test_read8(uint32_t address);
void tsl9_ca_test_write32(uint32_t address,uint32_t value);
void tsl9_ca_test_write8(uint32_t address,uint8_t value);
void tsl9_ca_test_write16(uint32_t address,uint16_t value);
void tsl9_ca_test_set_a2(uint32_t value);
void tsl9_ca_test_query_outputs(uint32_t a3,uint32_t a4,uint32_t a5);
void tsl9_ca_test_field_outputs(uint32_t a4,uint32_t a5);
#ifdef __cplusplus
}
#endif
#endif
