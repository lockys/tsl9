#include "validation.h"
#include <stdio.h>
int main(void)
{
    unsigned pos,val,ret,n=0;
    d3_validation_result r;
    for(pos=0;pos<4;pos++) for(val=0;val<256;val++) for(ret=0;ret<2;ret++) {
        uint8_t field[4]={65,65,65,65};
        int printable=val>=32 && val<=126;
        field[pos]=(uint8_t)val;
        if(!tsl9_dispatch3_validation(ret,field,&r))return 1;
        if(r.bytes_checked!=(printable?4u:pos+1u) || r.release_requested!=1u || r.continue_success!=(ret==0 && printable))return 2;
        n++;
    }
    if(tsl9_dispatch3_validation(0,0,&r))return 3;
    printf("VALIDATION_CASES=%u\n",n);
    return 0;
}
