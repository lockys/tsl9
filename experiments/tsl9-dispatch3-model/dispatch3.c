#include "dispatch3.h"
int tsl9_dispatch3_model(uint32_t command,uint32_t length,uint32_t source,
                         uint32_t allocation_result,d3_result *out)
{
    if (out==0) return 0;
    out->target=D3_TO_14098;
    out->allocate_requested=0;out->copy_requested=0;
    out->allocate_length=0;out->copy_source=0;out->copy_destination=0;out->copy_length=0;
    if (command==162u) {out->target=D3_TO_149FC;return 1;}
    if (command!=163u) return 1;
    out->target=D3_TO_14A24;
    if (length!=76u) return 1;
    out->allocate_requested=1;out->allocate_length=76u;
    if (allocation_result==0u) return 1;
    out->copy_requested=1;out->copy_source=source;out->copy_destination=allocation_result;
    out->copy_length=76u;out->target=D3_TO_142C0;
    return 1;
}
