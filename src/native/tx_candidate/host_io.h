#ifndef TSL9_OTA_TX_HOST_IO_H
#define TSL9_OTA_TX_HOST_IO_H
#include <stdint.h>
#include <stddef.h>

/* Named TX algorithm model, not a CPU/ISA interpreter. All addresses are u32
 * numbers. No numeric device address is dereferenced by the HOST build.
 * A returned READ/WRITE callback may change synthetic memory/frame contents,
 * but must preserve regs/known. Only named GATE/TAIL callbacks may change them.
 * GATE return is opaque except where the algorithm explicitly needs A0/S/GP.
 * TAIL never returns locally: TX_CONTINUE means the delegate returned through
 * the already-restored raw caller link; no normalized success value is added.
 */
typedef enum tx_flow { TX_CONTINUE=0, TX_RETURNED=1, TX_UNKNOWN=2,
                       TX_HALT=3, TX_TRANSFER=4 } tx_flow;
typedef enum tx_kind { TX_READ=1, TX_WRITE=2, TX_GATE_CALL=3,
                       TX_TAIL_CALL=4 } tx_kind;
typedef struct tx_event {
    tx_kind kind;
    uint32_t site,address,width,value;
    int value_known;
    uint32_t raw_target,target,args[4],args_known;
} tx_event;
struct tx_host;
typedef tx_flow (*tx_provider)(struct tx_host *,tx_event *,void *);
typedef struct tx_result {
    tx_flow flow;
    uint32_t value,raw_target,target,raw_link,link;
    int value_known,link_known,tail_delegated,budget_exhausted;
    int unsupported_memory_register_mutation;
} tx_result;
typedef struct tx_host {
    uint32_t regs[32],known;
    tx_provider provider;
    void *user;
    tx_flow flow;
    uint32_t loop_budget,loop_steps,event_count;
    int tail_delegated,budget_exhausted;
    int unsupported_memory_register_mutation;
    uint32_t delegated_raw_target,delegated_raw_link;
    int delegated_link_known;
} tx_host;

#ifdef __cplusplus
extern "C" {
#endif
void tx_host_init(tx_host *,tx_provider,void *);
uint32_t tx_set(tx_host *,unsigned,uint32_t);
uint32_t tx_get(tx_host *,unsigned);
uint32_t tx_read(tx_host *,uint32_t,uint32_t,unsigned,unsigned);
void tx_write(tx_host *,uint32_t,uint32_t,unsigned,uint32_t,int);
void tx_frame(tx_host *);
void tx_restore_failure(tx_host *);
void tx_restore_head(tx_host *);
void tx_restore_s0(tx_host *);
void tx_pop_frame(tx_host *);
void tx_gate(tx_host *,uint32_t,uint32_t,uint32_t,uint32_t);
void tx_tail(tx_host *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
void tx_budget(tx_host *);
tx_result tx_finish(tx_host *,int);
#ifdef __cplusplus
}
#endif

#define TX_STOP() do {if(h->flow!=TX_CONTINUE)return tx_finish(h,0);}while(0)
#define TX_ENTRY(ctx,cmd,src,len) do {tx_set(h,10,(ctx));tx_set(h,11,(cmd));tx_set(h,12,(src));tx_set(h,13,(len));}while(0)
#define TX_FRAME() do {tx_frame(h);TX_STOP();}while(0)
#define TX_RESTORE_FAILURE() do {tx_restore_failure(h);TX_STOP();}while(0)
#define TX_RESTORE_HEAD() do {tx_restore_head(h);TX_STOP();}while(0)
#define TX_RESTORE_S0() do {tx_restore_s0(h);TX_STOP();}while(0)
#define TX_POP_FRAME() do {tx_pop_frame(h);TX_STOP();}while(0)
#define TX_BUDGET() do {tx_budget(h);TX_STOP();}while(0)
#define TX_GP(v) do {(v)=tx_get(h,3);TX_STOP();}while(0)
#define TX_SET_S0(v) ((void)tx_set(h,8,(v)))
#define TX_SET_S1(v) ((void)tx_set(h,9,(v)))
#define TX_SET_S2(v) ((void)tx_set(h,18,(v)))
#define TX_SET_S3(v) ((void)tx_set(h,19,(v)))
#define TX_LIVE_S0(v) do {(v)=tx_get(h,8);TX_STOP();}while(0)
#define TX_LIVE_S1(v) do {(v)=tx_get(h,9);TX_STOP();}while(0)
#define TX_LIVE_S2(v) do {(v)=tx_get(h,18);TX_STOP();}while(0)
#define TX_LIVE_S3(v) do {(v)=tx_get(h,19);TX_STOP();}while(0)
#define TX_ARG0(v) tx_set(h,10,(v))
#define TX_ARG1(v) tx_set(h,11,(v))
#define TX_LANE2(v) tx_set(h,12,(v))
#define TX_ARG4(v) tx_set(h,14,(v))
#define TX_ARG5(v) tx_set(h,15,(v))
#define TX_ARG6(v) tx_set(h,16,(v))
#define TX_LIMIT5() TX_ARG5(1039u)
#define TX_INVALID5() TX_ARG5(0xfffeu)
#define TX_ACCEPT5() TX_ARG5(1u)
#define TX_INDEX0(v) TX_ARG0((v)&65535u)
#define TX_RECORD5(v) TX_ARG5((v)*TX_ARG5(1062u))
#define TX_PACKET5(v,b) TX_ARG5(TX_ARG5((v)+6u)+(b))
#define TX_HIGH4(v) TX_ARG4(tx_set(h,8,(v))>>8)
#define TX_SUM4(a,b) TX_ARG4(TX_ARG4(a)+(b))
#define TX_MASK4(v) TX_ARG4(TX_ARG4(v)&255u)
#define TX_LENGTH_S0(v) tx_set(h,8,tx_set(h,8,(v))+6u)
#define TX_MAGIC4() TX_ARG4(0x7f55u)
#define TX_STORAGE3() tx_set(h,13,0x2000b18cu)
#define TX_REG_NUMBER(reg) ((reg)[1]=='0'?10u:(reg)[1]=='4'?14u:15u)
#define TX_READ16(site,addr,v,reg) do {(v)=tx_read(h,(site),(addr),2,TX_REG_NUMBER(reg));TX_STOP();}while(0)
#define TX_READ8(site,addr,v,reg) do {(v)=tx_read(h,(site),(addr),1,TX_REG_NUMBER(reg));TX_STOP();}while(0)
#define TX_WRITE16(site,addr,v) do {tx_write(h,(site),(addr),2,(v),1);TX_STOP();}while(0)
#define TX_WRITE8(site,addr,v) do {tx_write(h,(site),(addr),1,(v),1);TX_STOP();}while(0)
#define TX_GATE_SLOT(site,target) do {TX_ARG5(0x40000u);(target)=tx_read(h,(site),0x4013cu,4,15);TX_STOP();}while(0)
#define TX_TAIL_SLOT(site,target) do {TX_ARG5(0x40000u);(target)=tx_read(h,(site),0x40050u,4,6);TX_STOP();}while(0)
#define TX_GATE(site,target,x0,x1,raw2,raw3,result) do {(void)(raw2);(void)(raw3);tx_gate(h,(site),(target),(x0),(x1));TX_STOP();(result)=h->regs[10];(raw2)=h->regs[12];(raw3)=h->regs[13];}while(0)
#define TX_RETURN_LARGE(v) do {(void)(v);return tx_finish(h,1);}while(0)
#define TX_RETURN_FAILURE(v) do {(void)(v);return tx_finish(h,1);}while(0)
#define TX_TAIL(target,x0,x1,x2,x3) do {tx_tail(h,(target),(x0),(x1),(x2),(x3));return tx_finish(h,0);}while(0)
#endif
