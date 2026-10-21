#include "flash_contract.h"
#include <string.h>
void fc_init(fc_model *m,const fc_backend *b) {memset(m,0,sizeof(*m));if(b)m->backend=*b;m->poll_budget=1024;}
static int stop(fc_model *m,fc_boundary why,uint32_t pc,uint32_t needed) {
    m->flow=FC_HALT;m->boundary=why;m->boundary_pc=pc;m->needed_mask=needed;return 0;
}
static int operation(fc_model *m,fc_kind kind,uint32_t pc,uint32_t address,uint32_t value,uint32_t known,unsigned width,fc_scalar *out) {
    fc_request q;fc_scalar result;fc_flow flow;
    memset(&q,0,sizeof(q));memset(&result,0,sizeof(result));
    q.kind=kind;q.pc=pc;q.address=address;q.value=value;q.known=known;q.width=width;
    m->last_request=q;m->operations++;
    if(!m->backend.invoke)return stop(m,FC_PROVIDER_UNKNOWN,pc,0);
    flow=m->backend.invoke(m->backend.context,&q,&result);
    if(flow==FC_TRANSFER){m->flow=FC_TRANSFER;return 0;}
    if(flow!=FC_RETURNED)return stop(m,FC_PROVIDER_UNKNOWN,pc,0);
    if(out)*out=result;
    return 1;
}
static int read_reg(fc_model *m,uint32_t pc,uint32_t address,fc_scalar *out) {return operation(m,FC_MMIO_READ,pc,address,0,0,32,out);}
static int write_reg(fc_model *m,uint32_t pc,uint32_t address,uint32_t value,uint32_t known) {return operation(m,FC_MMIO_WRITE,pc,address,value,known,32,NULL);}
static int change(fc_model *m,uint32_t read_pc,uint32_t write_pc,uint32_t address,uint32_t set,uint32_t clear) {
    fc_scalar v;if(!read_reg(m,read_pc,address,&v))return 0;
    return write_reg(m,write_pc,address,(v.value|set)&~clear,v.known|set|clear);
}
static int poll(fc_model *m,uint32_t pc,uint32_t address,uint32_t mask,int want_set) {
    uint32_t i;fc_scalar v;
    /* Host evidence budget: the original loops have no finite software limit. */
    for(i=0;i<m->poll_budget;i++) {
        if(!read_reg(m,pc,address,&v))return 0;
        if((v.known&mask)!=mask)return stop(m,FC_CONDITION_UNKNOWN,pc,mask);
        if(((v.value&mask)!=0)==want_set)return 1;
    }
    return stop(m,FC_SPIN_BUDGET,pc,mask);
}
static int unlock(fc_model *m) {
    return write_reg(m,0x18ea8,0x40022004,0x45670123,UINT32_MAX)
        && write_reg(m,0x18eae,0x40022004,0xcdef89ab,UINT32_MAX)
        && write_reg(m,0x18eb0,0x40022024,0x45670123,UINT32_MAX)
        && write_reg(m,0x18eb2,0x40022024,0xcdef89ab,UINT32_MAX);
}
static int erase(fc_model *m) {
    return change(m,0x18ec8,0x18ed4,0x40022010,0x20000,0)
        && write_reg(m,0x18ed6,0x40022014,m->destination,UINT32_MAX)
        && change(m,0x18ed8,0x18ede,0x40022010,0x40,0)
        && poll(m,0x18ee0,0x4002200c,1,0)
        && change(m,0x18ee6,0x18eee,0x40022010,0,0x20000);
}
static int program(fc_model *m) {
    uint32_t offset;fc_scalar word;
    if(!change(m,0x18ef6,0x18f00,0x40022010,0x10000,0)
       || !poll(m,0x18f02,0x4002200c,1,0)
       || !poll(m,0x18f0c,0x4002200c,2,0))return 0;
    for(offset=0;offset<256;offset+=4) {
        /* Original per-word source load, not a pre-copied buffer: aliases,
         * unaligned loads and physical persistence belong to the provider. */
        if(!operation(m,FC_SOURCE_WORD_READ,0x18f1e,m->source+offset,0,0,32,&word)
           || !operation(m,FC_DEST_WORD_STORE,0x18f26,m->destination+offset,word.value,word.known,32,NULL))return 0;
        m->words_written++;
        if(!poll(m,0x18f2a,0x4002200c,2,0))return 0;
    }
    return change(m,0x18f36,0x18f3e,0x40022010,0x200000,0)
        && poll(m,0x18f44,0x4002200c,1,0)
        && change(m,0x18f4a,0x18f52,0x40022010,0,0x10000);
}
static int timer_wait(fc_model *m,uint32_t argument) {
    fc_scalar scale;uint32_t compare;
    if(!change(m,0x19768,0x1976e,0xe000f004,0,1))return 0;
    if(m->gp_known!=UINT32_MAX)return stop(m,FC_OPERAND_UNKNOWN,0x19770,UINT32_MAX);
    if(!operation(m,FC_RAM_BYTE_READ,0x19770,m->gp+382u,0,0,8,&scale))return 0;
    if((scale.known&255u)!=255u)return stop(m,FC_OPERAND_UNKNOWN,0x19770,255);
    compare=(scale.value&255u)*argument;
    return write_reg(m,0x19778,0xe000f010,compare,UINT32_MAX)
        && write_reg(m,0x1977a,0xe000f014,0,UINT32_MAX)
        && change(m,0x1977c,0x19782,0xe000f000,16,0)
        && change(m,0x19784,0x1978a,0xe000f000,33,0)
        && poll(m,0x1978c,0xe000f004,1,1)
        && change(m,0x19792,0x19796,0xe000f000,0,1);
}
fc_flow fc_write_registers(fc_model *m,uint32_t a0,uint32_t a1,uint32_t a2) {
    (void)a1;
    m->flow=FC_RETURNED;m->boundary=FC_NO_BOUNDARY;m->boundary_pc=m->needed_mask=0;
    m->result=m->result_known=m->words_written=m->operations=0;
    memset(&m->last_request,0,sizeof(m->last_request));
    m->destination=a0&UINT32_C(0xffffff00);m->source=a2;
    /* 197C8/CE/D8/DC/E2. No CSR save/restore and no returned-status check is
     * added. Provider HALT/TRANSFER stops with partial effects retained. */
    if(!unlock(m)||!erase(m)||!program(m)
       || !change(m,0x18eba,0x18ec0,0x40022010,0x8000,0)
       || !timer_wait(m,1))return m->flow;
    m->result=0;m->result_known=UINT32_MAX;return m->flow;
}
