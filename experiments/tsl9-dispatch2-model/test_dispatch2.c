#include "dispatch2.h"
#include <stdio.h>
static int test_case(uint32_t entry, uint32_t command, uint32_t status, int queue, int dest)
{
    tsl9_dispatch2_result got;
    if (!tsl9_dispatch2_model(entry,command,status,&got)) return 0;
    if (got.queue_requested != queue || got.destination != dest) return 0;
    if (got.scheduler_requested != (queue && status == 0u)) return 0;
    if (got.scheduler_requested && (got.scheduler_callback != 0x13f88u || got.scheduler_delay != 300u)) return 0;
    if (!got.scheduler_requested && (got.scheduler_callback != 0u || got.scheduler_delay != 0u)) return 0;
    return 1;
}
int main(void)
{
    unsigned cmd, status, cases=0;
    tsl9_dispatch2_result ignored;
    const uint32_t wide[]={0x100u,0x1aau,0x1abu,0x80000000u,0xffffffffu};
    for (cmd=0;cmd<256;cmd++) for (status=0;status<2;status++) {
        int q1=(cmd==170u || cmd==171u);
        int q2=(cmd==185u || cmd==186u || cmd==187u || cmd==192u || cmd==193u || cmd==208u);
        int d1=q1 && status==0u ? TSL9_AT_14098 : TSL9_AT_141FA;
        int d2=q2 && status==0u ? TSL9_AT_14098 : (cmd>193u && cmd!=208u ? TSL9_AT_141F6 : TSL9_AT_141FA);
        if (!test_case(0x14230u,cmd,status,q1,d1) || !test_case(0x1425eu,cmd,status,q2,d2)) return 1;
        cases+=2;
    }
    for (cmd=0;cmd<sizeof(wide)/sizeof(wide[0]);cmd++) {
        int q=(wide[cmd]==0x1aau || wide[cmd]==0x1abu);
        if (!test_case(0x14230u,wide[cmd],0,q,q ? TSL9_AT_14098 : TSL9_AT_141FA)) return 2;
        if (!test_case(0x1425eu,wide[cmd],0,0,TSL9_AT_141F6)) return 3;
        cases+=2;
    }
    if (tsl9_dispatch2_model(0,0,0,&ignored) || tsl9_dispatch2_model(0x14230u,0,0,0)) return 4;
    printf("DISPATCH2_CASES=%u\n",cases);
    return 0;
}
