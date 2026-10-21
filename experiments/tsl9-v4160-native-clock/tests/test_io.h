#ifndef TSL9_NATIVE_CLOCK_TEST_IO_H
#define TSL9_NATIVE_CLOCK_TEST_IO_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
uint32_t tsl9_nc_test_gp(void);
uint32_t tsl9_nc_test_read32(uint32_t address);
uint8_t tsl9_nc_test_read8(uint32_t address);
void tsl9_nc_test_write32(uint32_t address,uint32_t value);
void tsl9_nc_test_write8(uint32_t address,uint8_t value);
void tsl9_nc_test_write16(uint32_t address,uint16_t value);
#ifdef __cplusplus
}
#endif
#endif
