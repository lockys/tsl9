#ifndef TSL9_OTA_PAGE_REPLY_HOST_IO_H
#define TSL9_OTA_PAGE_REPLY_HOST_IO_H
#include <stdint.h>
typedef enum op_flow {OP_RETURNED,OP_UNKNOWN,OP_HALT,OP_TRANSFER} op_flow;
typedef enum op_kind {OP_READ,OP_WRITE,OP_ALLOCATE,OP_COPY_BYTES,OP_TRANSMIT,OP_RELEASE_TAIL} op_kind;
typedef struct op_event {
    op_kind kind;uint32_t site,address,width,value,value_known;
    uint32_t target,raw_target,args[4],args_known;
    op_flow flow;
} op_event;
typedef struct op_result {
    op_flow flow;uint32_t value,value_known,caller_link_raw,caller_link_target,caller_link_known,tail_delegated;
} op_result;
struct op_host;
typedef int (*op_provider)(struct op_host *,op_event *);
typedef struct op_host {
    uint32_t regs[32],known;op_flow flow;op_provider provider;void *user;
    uint32_t delegated,unsupported_memory_register_mutation;
} op_host;
/* READ/WRITE callbacks may edit synthetic memory, not registers on return.
 * Named opaque calls may edit all exposed registers/known bits and frame memory.
 * target is raw_target & ~1; links likewise retain raw and masked identities.
 * HOST mutation scenarios do not prove native callee-save/SP preservation. */
int op_live(op_host *,unsigned,uint32_t *);
int op_slot(op_host *,uint32_t,uint32_t,unsigned,uint32_t *);
int op_write(op_host *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
int op_frame_head(op_host *);
int op_frame_rest(op_host *);
int op_restore_null(op_host *);
int op_restore_s0(op_host *);
int op_restore_tail(op_host *);
int op_call(op_host *,op_kind,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
op_result op_finish(op_host *,uint32_t,uint32_t);
op_result op_tail(op_host *,uint32_t,uint32_t);
void op_set(op_host *,unsigned,uint32_t);
uint32_t op_bind(op_host *,unsigned,uint32_t);
#define OP_NEED(condition) do {if(!(condition)) return op_finish(h,0u,0u);}while(0)
#define OP_ENTRY(connection,command,index) do {op_set(h,10u,(connection));op_set(h,11u,(command));op_set(h,12u,(index));}while(0)
#define OP_FRAME_HEAD() OP_NEED(op_frame_head(h))
#define OP_FRAME_REST() OP_NEED(op_frame_rest(h))
#define OP_RESTORE_NULL() OP_NEED(op_restore_null(h))
#define OP_RESTORE_S0() OP_NEED(op_restore_s0(h))
#define OP_RESTORE_TAIL() OP_NEED(op_restore_tail(h))
#define OP_SET_S0(v) op_set(h,8u,(v))
#define OP_SET_S1(v) op_set(h,9u,(v))
#define OP_SET_S2(v) op_set(h,18u,(v))
#define OP_SET_S3(v) op_set(h,19u,(v))
#define OP_SET_S4(v) op_set(h,20u,(v))
#define OP_LIVE_S0(v) OP_NEED(op_live(h,8u,&(v)))
#define OP_LIVE_S1(v) OP_NEED(op_live(h,9u,&(v)))
#define OP_LIVE_S2(v) OP_NEED(op_live(h,18u,&(v)))
#define OP_LIVE_S3(v) OP_NEED(op_live(h,19u,&(v)))
#define OP_LIVE_S4(v) OP_NEED(op_live(h,20u,&(v)))
#define OP_SLOT(site,address,out) OP_NEED(op_slot(h,(site),(address),15u,&(out)))
#define OP_FREE_SLOT(site,address,out) OP_NEED(op_slot(h,(site),(address),6u,&(out)))
#define OP_WRITE8(site,address,value) OP_NEED(op_write(h,(site),(address),1u,(value)&255u,1u))
#define OP_ALLOC_SIZE0() op_bind(h,10u,1026u)
#define OP_HEADER_HIGH5(value) op_bind(h,15u,(value)>>8)
#define OP_SOURCE_HIGH1() op_bind(h,11u,0x20000u)
#define OP_SOURCE_LOW1(value) op_bind(h,11u,(uint32_t)((value)+4u))
#define OP_SOURCE_ADD1(value,index) op_bind(h,11u,(uint32_t)((value)+(index)))
#define OP_COPY_SIZE2() op_bind(h,12u,1024u)
#define OP_SOURCE_SHIFT1(value) op_bind(h,11u,(value)<<10)
#define OP_BUFFER_ADVANCE0(value) op_bind(h,10u,(uint32_t)((value)+2u))
#define OP_ARG0(value) op_bind(h,10u,(value))
#define OP_ARG1(value) op_bind(h,11u,(value))
#define OP_ARG2(value) op_bind(h,12u,(value))
#define OP_TX_SIZE3() op_bind(h,13u,1026u)
#define OP_ALLOC(target,n,cmd,index,out) do {OP_NEED(op_call(h,OP_ALLOCATE,0x9baeu,(target),(n),(cmd),(index),0u));OP_NEED(op_live(h,10u,&(out)));}while(0)
#define OP_COPY(target,dst,src,n) OP_NEED(op_call(h,OP_COPY_BYTES,0x9bd4u,(target),(dst),(src),(n),0u))
#define OP_TX(ctx,cmd,buf,n,r1,r2) do {OP_NEED(op_call(h,OP_TRANSMIT,0x9be0u,0x8a56u,(ctx),(cmd),(buf),(n)));(r1)=h->regs[11];(r2)=h->regs[12];}while(0)
#define OP_RETURN_NULL(value) return op_finish(h,(value),1u)
#define OP_TAIL_RELEASE(target,buf,r1,r2) do {(void)(r1);(void)(r2);return op_tail(h,(target),(buf));}while(0)
#endif
