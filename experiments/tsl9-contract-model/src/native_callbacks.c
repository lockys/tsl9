#include "native_callbacks.h"
#include <string.h>
#define A(x) (TF_RAM_BASE+UINT32_C(x))
static int stop(nc_model *m,uint32_t va,uint32_t address){m->flow=NC_HALT;m->unknown_va=va;m->unknown_address=address;return 0;}
static int ram(nc_model *m,uint32_t address,unsigned n,uint32_t va,uint32_t *out){
    unsigned i;uint32_t v=0;if(address<TF_RAM_BASE||n>TF_RAM_SIZE||address-TF_RAM_BASE>TF_RAM_SIZE-n)return stop(m,va,address);
    for(i=0;i<n;i++){if(m->memory->known[address-TF_RAM_BASE+i]!=255)return stop(m,va,address+i);v|=(uint32_t)m->memory->ram[address-TF_RAM_BASE+i]<<(8*i);}*out=v;return 1;
}
static void request(nc_request *r,nc_kind kind,uint32_t va,uint32_t target,unsigned width){memset(r,0,sizeof(*r));r->kind=kind;r->va=va;r->target=target;r->width=width;}
static int invoke(nc_model *m,const nc_request *r,nc_result *out){
    nc_result result;nc_flow flow;if(m->flow!=NC_RETURNED)return 0;
    m->last_request=*r;++m->operations;memset(&result,0,sizeof(result));
    if(!m->backend.invoke)return stop(m,r->va,r->target);
    flow=m->backend.invoke(m->backend.context,m,r,&result);
    if(r->kind==NC_RESET_WAIT){if(flow==NC_TRANSFER){m->flow=NC_TRANSFER;return 0;}return stop(m,r->va,r->target);}
    if(flow!=NC_RETURNED){if(flow==NC_TRANSFER)m->flow=NC_TRANSFER;else stop(m,r->va,r->target);return 0;}
    if(out)*out=result;return 1;
}
static int scalar(nc_model *m,nc_kind kind,uint32_t va,uint32_t target,unsigned width,uint32_t *out){
    nc_request q;nc_result r;uint32_t mask=width==32?UINT32_MAX:((1u<<width)-1u);
    request(&q,kind,va,target,width);if(kind==NC_ROM_SCALAR)q.slot=target-0x40000u;
    if(!invoke(m,&q,&r))return 0;if((r.known&mask)!=mask)return stop(m,va,target);*out=r.value&mask;return 1;
}
static int effect(nc_model *m,nc_kind kind,uint32_t va,uint32_t target,unsigned width,uint32_t value){
    nc_request q;request(&q,kind,va,target,width);q.count=1;q.arguments[0]=width==16?value&65535u:value;return invoke(m,&q,NULL);
}
static int disconnect(nc_model *m,uint32_t va,uint32_t handle){
    nc_request q;request(&q,NC_ROM_DISCONNECT,va,0x4017c,0);q.slot=380;q.count=1;q.arguments[0]=handle;return invoke(m,&q,NULL);
}
static int system_ms(nc_model *m,uint32_t *out){uint32_t raw;if(!scalar(m,NC_ROM_SCALAR,0x81ba,0x4007c,32,&raw))return 0;*out=(raw*UINT32_C(10))>>4;return 1;}
static int spi(nc_model *m,uint32_t data,uint32_t *out){
    uint32_t status;unsigned n;
    for(n=255;n;n--){if(!scalar(m,NC_MMIO_READ,0x16612,0x40013008,16,&status))return 0;if(status&2u)break;}
    if(!n){*out=0;return 1;}
    if(!effect(m,NC_MMIO_WRITE,0x1661e,0x4001300c,16,data))return 0;
    for(n=255;n;n--){if(!scalar(m,NC_MMIO_READ,0x1662a,0x40013008,16,&status))return 0;if(status&1u)break;}
    if(!n){*out=0;return 1;}
    if(!scalar(m,NC_MMIO_READ,0x16632,0x4001300c,16,&status))return 0;
    *out=status&255u;return 1;
}
static int select_channel(nc_model *m,uint32_t channel,uint32_t va1,uint32_t va2){
    if((channel&1u)&&!effect(m,NC_MMIO_WRITE,va1,0x40010814,32,16))return 0;
    if((channel&2u)&&!effect(m,NC_MMIO_WRITE,va2,0x40010814,32,1))return 0;
    return 1;
}
static int radio_read(nc_model *m,uint32_t channel,uint32_t address,uint32_t *out){
    uint32_t ignored;if(!select_channel(m,channel,0x16718,0x16726)||!spi(m,3,&ignored)||!spi(m,address,&ignored)||!spi(m,0,out)||!effect(m,NC_MMIO_WRITE,0x16748,0x40010810,32,17))return 0;return 1;
}
static int reset_channel(nc_model *m,uint32_t channel,uint32_t *out){
    uint32_t ignored,start,now,value;uint32_t hops=0;
    if(!select_channel(m,channel,0x16b92,0x16ba2)||!spi(m,192,&ignored)||!effect(m,NC_MMIO_WRITE,0x16bb4,0x40010810,32,17)||!system_ms(m,&start))return 0;
    for(;;){
        if(hops++>=m->spin_budget)return stop(m,0x16bc4,0x81b0);
        if(!system_ms(m,&now))return 0;
        if((uint32_t)(now-start)>2u){*out=1;return 1;}
        if(!radio_read(m,channel,14,&value))return 0;
        if((value&224u)==128u){*out=0;return 1;}
    }
}
static int reset_gpio(nc_model *m){
    uint32_t value;
    if(!scalar(m,NC_MMIO_READ,0x18ed8,0x40021010,32,&value)||!effect(m,NC_MMIO_WRITE,0x18edc,0x40021010,32,value|UINT32_C(0x02000000)))return 0;
    if(!scalar(m,NC_MMIO_READ,0x18ee4,0x40021010,32,&value)||!effect(m,NC_MMIO_WRITE,0x18eec,0x40021010,32,value&~UINT32_C(0x02000000)))return 0;
    return 1;
}
static int reset_tail(nc_model *m,int boot){
    nc_request q;if(!effect(m,NC_CSR_CLEAR,boot?0x1ffau:0x99eeu,0x800,32,136)||!effect(m,NC_MMIO_WRITE,boot?0x200au:0x99feu,0xe000e048,32,0xbeef0080))return 0;
    request(&q,NC_RESET_WAIT,boot?0x200cu:0x9a00u,boot?0x200cu:0x9a00u,0);return invoke(m,&q,NULL);
}
static int runtime_reset(nc_model *m){
    uint32_t ignored;if(!reset_gpio(m)||!reset_channel(m,1,&ignored)||!reset_channel(m,2,&ignored))return 0;return reset_tail(m,0);
}
static int copy(nc_model *m,nc_buffer_kind source,const uint8_t *data,const uint8_t *known,uint8_t *out,uint8_t *out_known,uint32_t va){
    unsigned i;nc_request q;nc_result result;request(&q,NC_ROM_COPY,va,0x4004c,0);q.slot=76;q.source=source;q.destination=NC_VALUE_VIEW;q.length=8;
    if(source==NC_ADDRESS)q.source_address=0x08077b00;
    else{for(i=0;i<8;i++){q.data[i]=data[i];q.known[i]=known[i];}}
    if(!invoke(m,&q,&result))return 0;if(result.length<8)return stop(m,va,0x4004c);
    memcpy(out,result.data,8);memcpy(out_known,result.bytes_known,8);return 1;
}
static int flash_call(nc_model *m,uint32_t va,uint32_t target,uint32_t argument,int has_argument,const uint8_t *data,const uint8_t *known){
    nc_request q;request(&q,NC_FLASH_CALL,va,target,0);if(has_argument){q.count=1;q.arguments[0]=argument;}
    if(data){q.source=NC_VALUE_VIEW;q.length=256;memcpy(q.data,data,256);memcpy(q.known,known,256);}return invoke(m,&q,NULL);
}
static int write_metadata(nc_model *m,const uint8_t *record,const uint8_t *known){
    uint8_t page[256],page_known[256];memset(page,0,sizeof(page));memset(page_known,0,sizeof(page_known));
    if(!copy(m,NC_VALUE_VIEW,record,known,page,page_known,0x9d88)||!effect(m,NC_CSR_CLEAR,0x9b7c,0x800,32,136)||
       !flash_call(m,0x9b80,0x18bec,0,0,NULL,NULL)||!flash_call(m,0x9b88,0x18be4,49,1,NULL,NULL)||
       !flash_call(m,0x9b8e,0x18c18,0x08077b00,1,NULL,NULL)||
       !flash_call(m,0x9b96,0x18c46,0x08077b00,1,page,page_known)||
       !flash_call(m,0x9b9a,0x18c0a,0,0,NULL,NULL)||!effect(m,NC_CSR_SET,0x9b9e,0x800,32,136))return 0;
    return 1;
}
static int boot_mode(nc_model *m){
    uint8_t record[8],known[8];unsigned attempt;
    m->metadata_status_known=0;
    for(attempt=0;attempt<5;attempt++){
        if(!copy(m,NC_ADDRESS,NULL,NULL,record,known,0x9db4))return 0;
        if(((record[4]^1u)&known[4])==0){
            if(known[4]!=255)return stop(m,0x9dd6,0x08077b04);
            m->metadata_status=0;m->metadata_status_known=1;return 1;
        }
        record[4]=1;known[4]=255;if(!write_metadata(m,record,known))return 0;
    }
    m->metadata_status=1;m->metadata_status_known=1;return 1;
}
void nc_init(nc_model *m,tf_model *p,const nc_backend *b){memset(m,0,sizeof(*m));m->memory=p;if(b)m->backend=*b;m->spin_budget=65536;}
void nc_resume(nc_model *m){m->flow=NC_RETURNED;m->unknown_va=m->unknown_address=0;}
nc_flow nc_run(nc_model *m,nc_callback entry,uint32_t argument){
    uint32_t handle;int first_called;nc_request q;if(m->flow!=NC_RETURNED)return m->flow;if(!m->memory){stop(m,0,0);return m->flow;}
    switch(entry){
    case NC_RUNTIME_DISCONNECT:
        if(!ram(m,A(0x409e),2,0x8e14,&handle))return m->flow;
        first_called=handle!=65534u;
        if(first_called&&!disconnect(m,0x8e2a,handle))return m->flow;
        if(!ram(m,A(0x40a2),2,first_called?0x8e2eu:0x8e4eu,&handle))return m->flow;
        if(handle!=65534u)disconnect(m,0x8e44,handle);
        break;
    case NC_BOOT_DISCONNECT:
        if(!ram(m,A(0x407e),2,0x192e,&handle))return m->flow;
        if(handle!=65534u)disconnect(m,0x1940,handle);
        break;
    case NC_BOOT_JUMP:
        request(&q,NC_JUMP,0x20e4,0x8000,0);q.count=1;q.arguments[0]=argument;invoke(m,&q,NULL);break;
    case NC_BOOT_RESET:reset_tail(m,1);break;
    case NC_RUNTIME_RESET:runtime_reset(m);break;
    case NC_RUNTIME_BOOT_REQUEST:if(boot_mode(m))runtime_reset(m);break;
    default:stop(m,0,0);break;
    }
    return m->flow;
}
