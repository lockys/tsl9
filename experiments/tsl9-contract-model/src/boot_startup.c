#include "boot_startup.h"
#include <string.h>
#define S(x) (TF_RAM_BASE+UINT32_C(x))
static int stop(bs_model *m,uint32_t va,uint32_t address){m->flow=BS_HALT;m->boundary_va=va;m->boundary_address=address;m->boundary_is_abstract=0;m->boundary_offset=0;return 0;}
static int span(uint32_t a,unsigned n){return a>=TF_RAM_BASE&&a-TF_RAM_BASE<=TF_RAM_SIZE&&n<=TF_RAM_SIZE-(a-TF_RAM_BASE);}
static int put(bs_model *m,uint32_t a,uint32_t v,unsigned n,uint32_t va){unsigned i;if(!span(a,n))return stop(m,va,a);for(i=0;i<n;i++){m->memory->ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));m->memory->known[a-TF_RAM_BASE+i]=255;}return 1;}
static uint32_t mask(unsigned width){return width==32?UINT32_MAX:((UINT32_C(1)<<width)-1);}
static int call(bs_model *m,bs_operation op,uint32_t va,uint32_t address,unsigned width,uint32_t value,uint32_t argument,bs_result *out){
    bs_request q;bs_result r;bs_flow flow;if(m->flow!=BS_RETURNED)return 0;
    q.operation=op;q.va=va;q.address=address;q.width=width;q.value=value;q.argument=argument;r.value=r.known=0;++m->requests;
    if(!m->backend.hal)return stop(m,va,address);
    flow=m->backend.hal(m->backend.context,m,&q,&r);
    if(op==BS_JUMP&&flow==BS_TRANSFER){m->flow=BS_TRANSFER;return 0;}
    if(op==BS_RESET_WAIT){if(flow==BS_TRANSFER){m->flow=BS_TRANSFER;return 0;}return stop(m,va,address);}
    if(flow!=BS_RETURNED)return stop(m,va,address);
    if((op==BS_MMIO_READ||op==BS_CLOCK||op==BS_MEMORY_READ)&&(r.known&mask(width))!=mask(width))return stop(m,va,address);
    if(out)*out=r;
    return 1;
}
static int get(bs_model *m,uint32_t a,unsigned n,uint32_t va,uint32_t *v){
    unsigned i;bs_result r;*v=0;
    if(!span(a,n)){if(!call(m,BS_MEMORY_READ,va,a,n*8,0,0,&r))return 0;*v=r.value&mask(n*8);return 1;}
    for(i=0;i<n;i++){if(m->memory->known[a-TF_RAM_BASE+i]!=255)return stop(m,va,a+i);*v|=(uint32_t)m->memory->ram[a-TF_RAM_BASE+i]<<(i*8);}return 1;
}
static int read_mmio(bs_model *m,uint32_t va,uint32_t a,unsigned width,uint32_t *v){bs_result r;if(!call(m,BS_MMIO_READ,va,a,width,0,0,&r))return 0;*v=r.value&mask(width);return 1;}
static int write_mmio(bs_model *m,uint32_t va,uint32_t a,unsigned width,uint32_t v){return call(m,BS_MMIO_WRITE,va,a,width,v&mask(width),0,NULL);}
static int clock_value(bs_model *m,uint32_t va,uint32_t *v){bs_result r;if(!call(m,BS_CLOCK,va,0x11a2,32,0,0,&r))return 0;*v=r.value;return 1;}
static int release(bs_model *m,uint32_t p,uint32_t va){uint32_t scalar;int known;++m->requests;if(m->candidate)known=rc_msg_deallocate(m->candidate,p,&scalar);else known=m->backend.msg_deallocate?m->backend.msg_deallocate(m->backend.context,p):0;return known?1:stop(m,va,p);}
static int allocate(bs_model *m,uint32_t n,uint32_t *p){int known;++m->requests;if(m->candidate)known=rc_msg_allocate_register(m->candidate,n,p);else known=m->backend.msg_allocate?m->backend.msg_allocate(m->backend.context,n,p):0;return known?1:stop(m,0x1d52,0x40070);}
static int disable(bs_model *m){uint32_t v;return write_mmio(m,0x1cf4,0x4000042c,16,65535)&&write_mmio(m,0x1cf8,0x4000043c,16,0)&&read_mmio(m,0x1cfc,0x40000400,16,&v)&&write_mmio(m,0x1d0a,0x40000400,16,v&~1u);}
static int enable(bs_model *m){uint32_t v;return put(m,S(0x9580),0,4,0x1ccc)&&put(m,S(0x9586),0,1,0x1cd0)&&put(m,S(0x9585),0,1,0x1cd4)&&write_mmio(m,0x1cdc,0x40000424,16,0)&&read_mmio(m,0x1ce0,0x40000400,16,&v)&&write_mmio(m,0x1ce8,0x40000400,16,v|1u);}
static int rom(bs_model *m,unsigned offset,uint16_t event,uint32_t ticks,uint32_t va){uint32_t task;int result;if(!get(m,S(0x408d),1,va,&task))return 0;++m->requests;result=m->candidate?rc_rom_status(m->candidate,offset,(uint8_t)task,event,ticks):(m->backend.rom_status?m->backend.rom_status(m->backend.context,offset,(uint8_t)task,event,ticks):TF_UNKNOWN);return result!=TF_UNKNOWN?1:stop(m,va,0x40000u+offset);}
void bs_init(bs_model *m,tf_model *memory,const bs_backend *b){memset(m,0,sizeof(*m));m->memory=memory;if(b)m->backend=*b;m->poll_budget=4096;m->byte_budget=65536;}
void bs_resume(bs_model *m){m->flow=BS_RETURNED;m->boundary_va=m->boundary_address=0;m->boundary_is_abstract=0;m->boundary_offset=0;}
int bs_attach_candidate(bs_model *m,rc_adapter *a){if(!a||a->memory!=m->memory||a->profile!=RC_WCH_64BE955_V130)return 0;m->candidate=a;return 1;}
bs_flow bs_configure(bs_model *m,uint32_t n,uint32_t *out){
    uint32_t old,p;if(m->flow!=BS_RETURNED)return m->flow;
    if(!get(m,S(0x9590),4,0x1d1e,&old))return m->flow;
    if(old){if(!release(m,old,0x1d2a)||!put(m,S(0x9590),0,4,0x1d30)||!put(m,S(0x958c),0,4,0x1d38)||!disable(m))return m->flow;}
    if(allocate(m,n*UINT32_C(6),&p))*out=p;
    return m->flow;
}
bs_flow bs_pattern(bs_model *m,uint32_t n){
    uint32_t p,i,entries;if(m->flow!=BS_RETURNED)return m->flow;entries=n<=19?(uint32_t)(uint8_t)(n+1u):2u;
    if(bs_configure(m,entries,&p)!=BS_RETURNED)return m->flow;
    if(!put(m,S(0x9590),p,4,n<=19?0x1d76:0x1dc6)||p==0)return m->flow;
    if(n<=19){
        for(i=0;i<n;i++)if(!put(m,p+6u*i,3000,2,0x1daa)||!put(m,p+6u*i+2,40,2,0x1dae)||!put(m,p+6u*i+4,80,2,0x1db2))return m->flow;
        if(!put(m,p+6u*n,0,2,0x1d9a))return m->flow;
    }else if(!put(m,p,3000,2,0x1dd2)||!put(m,p+2,n,2,0x1dd6)||!put(m,p+4,0,2,0x1dda)||!put(m,p+6,0,2,0x1dde))return m->flow;
    enable(m);return m->flow;
}
static int next_deadline(bs_model *m,uint32_t now,unsigned field,uint32_t va){
    uint32_t index,p,v,phase,pointer_va=field==2?0x1e98u:0x1ed0u,value_va=field==2?0x1e9cu:0x1ed4u;
    if(!get(m,S(0x9586),1,va,&index)||!get(m,S(0x9590),4,pointer_va,&p)||!get(m,p+6u*index+field,2,value_va,&v)||!put(m,S(0x9580),now+v,4,0x1ea6)||!get(m,S(0x9585),1,0x1eaa,&phase)||!put(m,S(0x9585),phase+1u,1,0x1eb4))return 0;return 1;
}
bs_flow bs_pattern_irq(bs_model *m){
    uint32_t status,now,deadline,phase,index,p,frequency,hold,callback,reload;if(m->flow!=BS_RETURNED)return m->flow;
    if(!read_mmio(m,0x1dfa,0x40000410,16,&status)||!(status&1u))return m->flow;
    if(!read_mmio(m,0x1e06,0x40000410,16,&status)||!write_mmio(m,0x1e1e,0x40000410,16,status&~1u)||!clock_value(m,0x1e22,&now)||!get(m,S(0x9580),4,0x1e26,&deadline)||now<deadline)return m->flow;
    if(!get(m,S(0x9585),1,0x1e30,&phase))return m->flow;
    if(phase==0){
        if(!get(m,S(0x9586),1,0x1e58,&index)||!get(m,S(0x9590),4,0x1e62,&p)||!get(m,p+6u*index,2,0x1e6e,&frequency))return m->flow;
        /* Native signed DIV by zero returns -1; low16(-1-1) is FFFE. */
        reload=(frequency?UINT32_C(1000000)/frequency:UINT32_MAX)-1u;
        if(!write_mmio(m,0x1e7c,0x4000042c,16,reload)||!write_mmio(m,0x1e84,0x4000043c,16,200)||!clock_value(m,0x1e88,&now))return m->flow;
        next_deadline(m,now,2,0x1e90);
    }else if(phase==1){
        if(!write_mmio(m,0x1eba,0x4000043c,16,0)||!clock_value(m,0x1ebe,&now))return m->flow;
        next_deadline(m,now,4,0x1ec6);
    }else if(phase==2){
        if(!get(m,S(0x9586),1,0x1eda,&index)||!get(m,S(0x9590),4,0x1ede,&p)||!put(m,S(0x9586),(uint8_t)(index+1u),1,0x1eea))return m->flow;
        if(!get(m,p+6u*(uint8_t)(index+1u),2,0x1ef6,&frequency))return m->flow;
        if(frequency){put(m,S(0x9585),0,1,0x1f44);return m->flow;}
        if(p&&(!release(m,p,0x1f04)||!put(m,S(0x9590),0,4,0x1f0a)))return m->flow;
        if(!get(m,S(0x9588),2,0x1f12,&hold))return m->flow;
        if(hold){
            if(!clock_value(m,0x1f18,&now)||!get(m,S(0x9588),2,0x1f20,&hold)||!put(m,S(0x9580),now+hold,4,0x1f2a)||!put(m,S(0x9588),0,2,0x1f32)||!get(m,S(0x9585),1,0x1f36,&phase)||!put(m,S(0x9585),phase+1u,1,0x1eb4))return m->flow;
        }else disable(m);
    }else if(phase==3){
        if(!disable(m)||!get(m,S(0x958c),4,0x1f4c,&callback))return m->flow;
        if(callback&&(!put(m,S(0x958c),0,4,0x1f54)||!call(m,BS_CALLBACK,0x1f5a,callback,32,0,0,NULL)))return m->flow;
        put(m,S(0x9585),0,1,0x1f60);
    }
    return m->flow;
}
static int poll_uart(bs_model *m,uint32_t va){uint32_t i,value;for(i=0;i<m->poll_budget;i++){if(!read_mmio(m,va,0x40004400,16,&value))return 0;if(value&64u)return 1;}return stop(m,va,0x40004400);}
static int uart_byte(bs_model *m,uint32_t value){return poll_uart(m,0x23c6)&&write_mmio(m,0x23d4,0x40004404,16,value)&&poll_uart(m,0x23dc);}
static int uart_payload(bs_model *m,const bs_uart_view *view,uint32_t p,uint32_t i,uint32_t va,uint32_t *out){
    if(!view)return get(m,p+i,1,va,out);
    if(!view->data||!view->known||i>=view->available||view->known[i]!=255){stop(m,va,0);m->boundary_is_abstract=1;m->boundary_offset=i;return 0;}
    *out=view->data[i];return 1;
}
static bs_flow uart_reply_body(bs_model *m,uint32_t command,uint32_t p,const bs_uart_view *view,uint32_t n){
    uint32_t sum,byte,i;if(m->flow!=BS_RETURNED)return m->flow;
    if(!put(m,S(0x999b),0,1,0x2400)||!uart_byte(m,85)||!uart_byte(m,127)||!uart_byte(m,command)||!get(m,S(0x999b),1,0x241a,&sum)||!put(m,S(0x999b),command+sum,1,0x2426)||!uart_byte(m,0)||!uart_byte(m,(uint8_t)n)||!get(m,S(0x999b),1,0x2434,&sum)||!put(m,S(0x999b),(uint8_t)n+sum,1,0x2440))return m->flow;
    for(i=0;i<n;i++){
        if(i>=m->byte_budget){stop(m,0x2444,p+i);return m->flow;}
        if(!uart_payload(m,view,p,i,0x245e,&byte)||!uart_byte(m,byte)||!uart_payload(m,view,p,i,0x2466,&byte)||!get(m,S(0x999b),1,0x246a,&sum)||!put(m,S(0x999b),sum+byte,1,0x2474))return m->flow;
    }
    if(get(m,S(0x999b),1,0x2456,&sum))uart_byte(m,sum);
    return m->flow;
}
bs_flow bs_uart_reply(bs_model *m,uint32_t command,uint32_t p,uint32_t n){return uart_reply_body(m,command,p,NULL,n);}
bs_flow bs_uart_reply_view(bs_model *m,uint32_t command,const bs_uart_view *view,uint32_t n){
    bs_uart_view missing={NULL,NULL,0};
    return uart_reply_body(m,command,0,view?view:&missing,n);
}
bs_flow bs_startup_dispatch(bs_model *m,uint16_t e,uint16_t *out){
    uint32_t value;unsigned bit=0;*out=e;if(m->flow!=BS_RETURNED)return m->flow;
    if(e&1u){bit=1;if(!read_mmio(m,0x20b2,0x4001080c,32,&value)||!write_mmio(m,0x20ba,0x4001080c,32,value^2u)||!rom(m,88,1,160,0x24ca))return m->flow;}
    else if(e&8u){bit=8;if(bs_uart_reply(m,65,0,0)!=BS_RETURNED)return m->flow;}
    else if(e&2u){bit=2;if(!call(m,BS_JUMP,0x20e4,0x8000,32,0,0,NULL))return m->flow;}
    else if(e&4u){
        if(!call(m,BS_CSR_CLEAR,0x1ffa,0x800,32,136,0,NULL)||!write_mmio(m,0x200a,0xe000e048,32,0xbeef0080))return m->flow;
        call(m,BS_RESET_WAIT,0x200c,0x200c,32,0,0,NULL);return m->flow;
    }
    *out=bit?(uint16_t)(e^bit):0;return m->flow;
}
bs_flow bs_stay(bs_model *m){
    if(m->flow!=BS_RETURNED)return m->flow;
    if(!put(m,S(0x408c),1,1,0x2524)||!rom(m,92,2,0,0x251c)||!rom(m,80,1,0,0x2536))return m->flow;
    return bs_pattern(m,3);
}
bs_flow bs_startup_policy_tail(bs_model *m,uint32_t status){
    uint32_t byte,stay;if(m->flow!=BS_RETURNED)return m->flow;
    if(status!=2u){
        if(!get(m,0x8000,1,0x25f4,&byte))return m->flow;
        if(byte==111u){rom(m,88,2,320,0x2616);return m->flow;}
    }
    if(!get(m,S(0x408c),1,0x2600,&stay)||stay)return m->flow;
    return bs_stay(m);
}
