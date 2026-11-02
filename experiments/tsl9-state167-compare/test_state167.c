#include "state167.h"
#include <stdint.h>
#include <stdio.h>
int main(void)
{
    uint32_t hi, n=0;
    for (hi=0;hi<65536u;++hi) {
        uint32_t source=(hi<<16)|0xa55au;
        if (tsl9_state167_compare(source,hi)!=1u) return 1;
        if (tsl9_state167_compare(source,hi^1u)!=0u) return 2;
        if (tsl9_state167_compare(source,hi|0x10000u)!=0u) return 3;
        n+=3;
    }
    if (tsl9_state167_compare(0xffffffffu,0xffffu)!=1u) return 4;
    if (tsl9_state167_compare(0xffffffffu,0xffffffffu)!=0u) return 5;
    printf("STATE167_CASES=%u\n",n+2);
    return 0;
}
