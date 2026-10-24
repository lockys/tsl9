#include "main_ports.h"

#ifdef __cplusplus
extern "C"
#endif
__attribute__((used, noinline)) int tsl9_runtime_main(void)
{
    tsl9_main_first_call();
    tsl9_main_second_call();
    /* This return is reached only if both original providers return. */
    return 0;
}
