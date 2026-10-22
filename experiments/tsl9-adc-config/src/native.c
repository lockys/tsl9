#include "adc_config.h"
#include "../../tsl9-resident-memory-leaves/src/io.h"
__attribute__((always_inline)) ml_result tsl9_adc_config_io(ml_io *,uint32_t,uint32_t);
__attribute__((always_inline)) int ml_port_read8(ml_io *,uint32_t,uint32_t *);
__attribute__((always_inline)) int ml_port_read32(ml_io *,uint32_t,uint32_t *);
__attribute__((always_inline)) int ml_port_write32(ml_io *,uint32_t,uint32_t);
#include "adc_config.c"

int ml_port_read8(ml_io *io,uint32_t address,uint32_t *out)
{
    (void)io;*out=*(volatile uint8_t *)(uintptr_t)address;return 1;
}
int ml_port_read32(ml_io *io,uint32_t address,uint32_t *out)
{
    (void)io;*out=*(volatile uint32_t *)(uintptr_t)address;return 1;
}
int ml_port_write32(ml_io *io,uint32_t address,uint32_t value)
{
    (void)io;*(volatile uint32_t *)(uintptr_t)address=value;return 1;
}
uint32_t tsl9_adc_config_1892e(uint32_t base,uint32_t config)
{
    ml_io io;ml_result result=tsl9_adc_config_io(&io,base,config);
    register uint32_t a0 __asm__("a0")=result.value;
    register uint32_t a1 __asm__("a1")=config;
    __asm__ volatile("":"+r"(a0),"+r"(a1)::"memory");return a0;
}
