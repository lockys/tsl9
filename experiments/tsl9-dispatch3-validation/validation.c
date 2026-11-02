#include "validation.h"
int tsl9_dispatch3_validation(uint32_t validator_return,const uint8_t field[4],d3_validation_result *out)
{
    unsigned i;uint8_t ok;
    if(field==0 || out==0) return 0;
    out->bytes_checked=0;out->release_requested=0;out->continue_success=0;
    ok=(uint8_t)(validator_return==0u);
    for(i=0;i<4;i++) {
        out->bytes_checked++;
        if(field[i]<32u || field[i]>126u) {ok=0;break;}
    }
    out->release_requested=1;
    out->continue_success=ok;
    return 1;
}
