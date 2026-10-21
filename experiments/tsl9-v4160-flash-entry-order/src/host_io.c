#include "flash_native.h"
#include <string.h>
fn_word fn_constant(uint32_t v) { fn_word r={v,UINT32_MAX};return r; }
fn_word fn_failed(void) { fn_word r={0u,0u};return r; }
fn_word fn_and(fn_word a,fn_word b) {
    fn_word r;r.value=a.value&b.value;r.known=(a.known&b.known)|(a.known&~a.value)|(b.known&~b.value);return r;
}
fn_word fn_or(fn_word a,fn_word b) {
    fn_word r;r.value=a.value|b.value;r.known=(a.known&b.known)|(a.known&a.value)|(b.known&b.value);return r;
}
fn_word fn_add(fn_word a,fn_word b) {
    fn_word r;r.value=a.value+b.value;r.known=(a.known==UINT32_MAX&&b.known==UINT32_MAX)?UINT32_MAX:0u;return r;
}
void fn_host_init(fn_host *h,fn_provider provider,void *context) {
    memset(h,0,sizeof(*h));h->invoke=provider;h->context=context;
    /* Synthetic diagnostic limit only; native loops have no limit. */
    h->poll_budget=65536u;
}
static int boundary(fn_host *h,fn_boundary b,uint32_t site,uint32_t address,uint32_t needed) {
    h->flow=FN_HALTED;h->boundary=b;h->boundary_site=site;h->boundary_address=address;h->needed_mask=needed;return 0;
}
static int invoke(fn_host *h,fn_kind kind,uint32_t site,fn_word address,fn_word value,fn_word *out) {
    fn_request r;fn_word result=fn_failed();fn_flow flow;
    if(address.known!=UINT32_MAX)return boundary(h,FN_UNKNOWN_ADDRESS,site,address.value,~address.known);
    r.kind=kind;r.site=site;r.address=address.value;r.value=value.value;r.known=value.known;r.width=32u;
    h->last_request=r;h->operations++;
    if(!h->invoke)return boundary(h,FN_PROVIDER_BOUNDARY,site,address.value,0u);
    flow=h->invoke(h->context,h,&r,&result);
    if(flow!=FN_RETURNED) {
        h->flow=flow==FN_TRANSFERRED?FN_TRANSFERRED:FN_HALTED;h->boundary=FN_PROVIDER_BOUNDARY;h->boundary_site=site;h->boundary_address=address.value;return 0;
    }
    if(out)*out=result;
    return 1;
}
int fn_read(fn_host *h,uint32_t site,fn_word address,fn_word *out) { return invoke(h,FN_READ32_REQUEST,site,address,fn_failed(),out); }
int fn_write(fn_host *h,uint32_t site,fn_word address,fn_word value) { return invoke(h,FN_WRITE32_REQUEST,site,address,value,0); }
int fn_poll_step(fn_host *h,uint32_t site,uint32_t mask,unsigned *count) {
    if(*count>=h->poll_budget)return boundary(h,FN_HOST_POLL_BUDGET,site,0x4002200cu,mask);
    ++*count;return 1;
}
int fn_poll_true(fn_host *h,uint32_t site,fn_word value,uint32_t mask) {
    if((value.known&mask)!=mask)return boundary(h,FN_UNKNOWN_CONDITION,site,0x4002200cu,mask&~value.known);
    return (value.value&mask)!=0u;
}
fn_word fn_commit(fn_host *h,fn_word a0,const fn_word *a1,const fn_word *a2,const fn_word *a3,const fn_word *a4,fn_word a5,const fn_word *a6,uint32_t mask) {
    h->regs[10]=a0;
    if(mask&2u)h->regs[11]=*a1;
    if(mask&4u)h->regs[12]=*a2;
    if(mask&8u)h->regs[13]=*a3;
    if(mask&16u)h->regs[14]=*a4;
    if(mask&32u)h->regs[15]=a5;
    if(mask&64u)h->regs[16]=*a6;
    return a0;
}
int fn_frame_begin(fn_host *h,fn_word destination,fn_word source) {
    h->incoming_return_target=h->regs[1];
    h->regs[2]=fn_add(h->regs[2],fn_constant(0xffffffe0u));
    if(!fn_write(h,0x9c0cu,fn_add(h->regs[2],fn_constant(24u)),h->regs[8]))return 0;
    if(!fn_write(h,0x9c0eu,fn_add(h->regs[2],fn_constant(20u)),h->regs[9]))return 0;
    if(!fn_write(h,0x9c10u,fn_add(h->regs[2],fn_constant(28u)),h->regs[1]))return 0;
    h->regs[9]=destination;h->regs[10]=destination;h->regs[11]=source;
    if(!fn_write(h,0x9c14u,fn_add(h->regs[2],fn_constant(12u)),source))return 0;
    h->regs[8]=fn_constant(136u);return 1;
}
int fn_frame_end(fn_host *h) {
    if(!fn_read(h,0x9c40u,fn_add(h->regs[2],fn_constant(28u)),&h->regs[1]))return 0;
    if(!fn_read(h,0x9c42u,fn_add(h->regs[2],fn_constant(24u)),&h->regs[8]))return 0;
    if(!fn_read(h,0x9c44u,fn_add(h->regs[2],fn_constant(20u)),&h->regs[9]))return 0;
    h->regs[2]=fn_add(h->regs[2],fn_constant(32u));
    if(h->regs[1].known!=UINT32_MAX||h->incoming_return_target.known!=UINT32_MAX)
        return boundary(h,FN_UNKNOWN_RETURN_TARGET,0x9c48u,h->regs[1].value,~h->regs[1].known);
    if(h->regs[1].value!=h->incoming_return_target.value) {
        h->flow=FN_TRANSFERRED;h->boundary=FN_RETURN_TARGET_TRANSFER;h->boundary_site=0x9c48u;h->boundary_address=h->regs[1].value;return 0;
    }
    return 1;
}
int fn_csr(fn_host *h,fn_kind kind,uint32_t site) { return invoke(h,kind,site,fn_constant(0x800u),h->regs[8],0); }
fn_flow fn_run(fn_host *h,uint32_t entry,fn_word a0,fn_word a1) {
    fn_word result=fn_failed();
    h->flow=FN_RETURNED;h->boundary=FN_NO_BOUNDARY;h->boundary_site=h->boundary_address=h->needed_mask=0u;h->operations=h->words_written=0u;h->normal_register_outputs_valid=0u;
    h->regs[10]=a0;h->regs[11]=a1;
    switch(entry) {
    case 0x9c0au:result=tsl9_flash_quarter_9c0a(h,a0,a1);break;
    case 0x18e90u:result=tsl9_flash_status_18e90(h,a0);break;
    case 0x18e98u:result=tsl9_flash_unlock_18e98(h,a0);break;
    case 0x18eb6u:result=tsl9_flash_lock_18eb6(h,a0);break;
    case 0x18ec4u:result=tsl9_flash_erase_18ec4(h,a0);break;
    case 0x18ef2u:result=tsl9_flash_program_18ef2(h,a0,a1);break;
    default:(void)boundary(h,FN_PROVIDER_BOUNDARY,entry,entry,0u);break;
    }
    if(h->flow==FN_RETURNED) { h->regs[10]=result;h->normal_register_outputs_valid=1u; }
    return h->flow;
}
