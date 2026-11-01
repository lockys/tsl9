#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
__attribute__((noinline,section(".text.tsl9_tx_oversized_return")))
uint32_t tsl9_tx_oversized_return(uint32_t context,uint32_t command,uint32_t source,uint32_t length)
{
    (void)command;(void)source;(void)length;
    return context;
}
