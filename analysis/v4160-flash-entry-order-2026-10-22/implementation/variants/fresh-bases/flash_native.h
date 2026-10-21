#ifndef TSL9_V4160_FLASH_NATIVE_H
#define TSL9_V4160_FLASH_NATIVE_H
#include <stdint.h>
#if defined(TSL9_FLASH_HOST_TEST)
#include "host_io.h"
#define FN_CONTEXT fn_host *h,
#else
typedef uint32_t fn_word;
#define FN_CONTEXT
#endif
#ifdef __cplusplus
extern "C" {
#endif
/* A0 is the architectural input/result, not a Boolean success indicator. */
fn_word tsl9_flash_status_18e90(FN_CONTEXT fn_word status);
fn_word tsl9_flash_unlock_18e98(FN_CONTEXT fn_word incoming_a0);
fn_word tsl9_flash_lock_18eb6(FN_CONTEXT fn_word incoming_a0);
fn_word tsl9_flash_erase_18ec4(FN_CONTEXT fn_word destination);
fn_word tsl9_flash_program_18ef2(FN_CONTEXT fn_word destination,fn_word source);
fn_word tsl9_flash_quarter_9c0a(FN_CONTEXT fn_word destination,fn_word source);
#ifdef __cplusplus
}
#endif
#endif
