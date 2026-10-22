#include "nv_write_callback.h"

/* Preserve genuine C call boundaries without editing the sealed bodies.
 * The two unused status/quarter definitions remain genuine emitted code. */
__attribute__((noinline)) fn_word tsl9_flash_status_18e90(fn_word);
__attribute__((noinline)) fn_word tsl9_flash_unlock_18e98(fn_word);
__attribute__((noinline)) fn_word tsl9_flash_lock_18eb6(fn_word);
__attribute__((noinline)) fn_word tsl9_flash_erase_18ec4(fn_word);
__attribute__((noinline)) fn_word tsl9_flash_program_18ef2(fn_word,fn_word);
__attribute__((noinline)) fn_word tsl9_flash_quarter_9c0a(fn_word,fn_word);
__attribute__((noinline)) uint32_t tsl9_delay_19764(uint32_t);
#include "../../tsl9-v4160-flash-entry-order/src/flash_native.c"

/* Same legitimate live-GP port pattern as the retained native-clock model.
 * This is a physical GP read, not a constant provider or original-code ASM. */
static __attribute__((always_inline)) inline uint32_t current_gp(void)
{
    uint32_t value;__asm__ volatile("mv %0, gp" : "=r"(value) : : "memory");return value;
}

uint32_t tsl9_delay_19764(uint32_t incoming_a0)
{
    uint32_t value,scale,product;
    value=*(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004)=value&UINT32_C(0xfffffffe);
    scale=*(volatile uint8_t *)(uintptr_t)(uint32_t)(current_gp()+382u);
    product=scale*incoming_a0;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f010)=product;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f014)=0;
    value=*(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000)=value|16u;
    value=*(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000)=value|33u;
    do {
        value=*(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004);
    } while((value&1u)==0u);
    value=*(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000)=value&UINT32_C(0xfffffffe);
    return incoming_a0;
}

uint32_t tsl9_nv_write_callback_197be(uint32_t destination,uint32_t unused_a1,uint32_t source)
{
    uint32_t program_a0;
    (void)unused_a1;
    (void)tsl9_flash_unlock_18e98(destination);
    (void)tsl9_flash_erase_18ec4(destination);
    program_a0=tsl9_flash_program_18ef2(destination,source);
    (void)tsl9_flash_lock_18eb6(program_a0);
    (void)tsl9_delay_19764(1u);
    return 0;
}
