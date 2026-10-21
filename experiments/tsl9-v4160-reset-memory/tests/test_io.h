#ifndef TSL9_RESET_MEMORY_TEST_IO_H
#define TSL9_RESET_MEMORY_TEST_IO_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
uint32_t tsl9_rm_test_gp(void);
uint32_t tsl9_rm_test_read32(uint32_t address);
void tsl9_rm_test_write32(uint32_t address,uint32_t value);
void tsl9_rm_test_outputs(uint32_t a0,uint32_t a1,uint32_t a2);
#ifdef __cplusplus
}
#endif
#endif
