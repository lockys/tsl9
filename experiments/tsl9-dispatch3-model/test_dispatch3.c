#include "dispatch3.h"
#include <stdio.h>
int main(void)
{
    const uint32_t lengths[]={0u,76u,77u};
    unsigned c,l,a,n=0;
    d3_result r;
    for(c=0;c<256;c++) for(l=0;l<3;l++) for(a=0;a<2;a++) {
        uint32_t ptr=a ? 0x1000u : 0u;
        int alloc=(c==163u && lengths[l]==76u);
        int copy=(alloc && ptr!=0u);
        d3_target dest=c==162u ? D3_TO_149FC : c!=163u ? D3_TO_14098 : copy ? D3_TO_142C0 : D3_TO_14A24;
        if (!tsl9_dispatch3_model(c,lengths[l],0x2000u,ptr,&r)) return 1;
        if(r.target!=dest || r.allocate_requested!=alloc || r.copy_requested!=copy) return 2;
        if(r.allocate_length!=(alloc?76u:0u)) return 3;
        if(r.copy_source!=(copy?0x2000u:0u) || r.copy_destination!=(copy?ptr:0u) || r.copy_length!=(copy?76u:0u)) return 4;
        n++;
    }
    if(!tsl9_dispatch3_model(0x1a3u,76u,1u,2u,&r) || r.target!=D3_TO_14098 || r.allocate_requested) return 5;
    if(!tsl9_dispatch3_model(163u,0x1004cu,1u,2u,&r) || r.target!=D3_TO_14A24 || r.allocate_requested) return 6;
    if(tsl9_dispatch3_model(163u,76u,1u,2u,0)) return 7;
    printf("DISPATCH3_CASES=%u\n",n+2);
    return 0;
}
