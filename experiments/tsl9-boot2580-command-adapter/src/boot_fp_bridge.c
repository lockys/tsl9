#include "boot_fp_bridge.h"
#include <string.h>
bc_flow bc_fp_program(const bc_request *q,fp_model *engine) {
    fp_source source;fp_flow flow;
    if(!q||!engine||engine->image!=FP_BOOT||q->kind!=BC_PROGRAM256||q->argc!=2||
       q->target.known!=UINT32_MAX||q->target.value!=0x20e6||
       q->args[0].known!=UINT32_MAX||q->args[1].known!=UINT32_MAX)return BC_HALT;
    memset(&source,0,sizeof source);source.kind=FP_ADDRESS;source.address=q->args[1].value;
    flow=fp_program_page(engine,q->args[0].value,&source);
    if(flow==FP_RETURNED)return BC_RETURNED;
    return flow==FP_TRANSFER?BC_TRANSFER:BC_HALT;
}
