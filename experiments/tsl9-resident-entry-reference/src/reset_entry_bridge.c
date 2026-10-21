#include "reset_entry_bridge.h"
rc_flow ri_reset_handoff(ri_model *m,const rc_request *q,rc_scalar *out){
    ri_flow flow;
    if(!m||!q||!out||q->kind!=RC_HANDOFF||q->pc!=0x18730||q->target!=0x40000)return RC_HALT;
    flow=ri_enter(m);
    if(flow==RI_TRANSFER){out->value=m->return_target.value;out->known=m->return_target.known;return RC_TRANSFER;}
    if(flow==RI_LIMIT)return RC_OBSERVATION_LIMIT;
    return RC_HALT;
}
