#include "spi_can.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static tf_model ram_state;static sc_model model;static uint8_t runtime[76800];
static unsigned groups,checks,failures;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%u %s\n",(unsigned)__LINE__,#x);}}while(0)
static void group(const char *s){++groups;printf("GROUP %s\n",s);}
static sc_request trace[32768];static unsigned traces,tx_count;static uint8_t tx[8192],regs[3][256],reg_known[3][256];
static uint32_t addresses[128],values[128],masks[128];static unsigned mmio_count;
static unsigned selected,command,position,address;static uint32_t response,response_known;
static uint32_t clock_raw,clock_step,clock_values[32];static unsigned clock_count,clock_length;
static int auto_mode,force_status,partial_status,halt_copy,mutate_frame_copy,mutate_dlc_read,queue_add_flag,irq_returned,arr_live,rx_live_regs,mutate_ram;
static sc_buffer live_frame;static uint32_t halt_va;
static uint32_t transfer_va;static int free_allowed,free_mutation,source_snapshot_mutation,cleanup_live_config;
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram_state.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(i*8));ram_state.known[a-TF_RAM_BASE+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)ram_state.ram[a-TF_RAM_BASE+i]<<(i*8);return v;}
static unsigned mmio_index(uint32_t a){unsigned i;for(i=0;i<mmio_count;i++)if(addresses[i]==a)return i;CHECK(mmio_count<128);addresses[mmio_count]=a;values[mmio_count]=0;masks[mmio_count]=UINT32_MAX;return mmio_count++;}
static void mmio_set(uint32_t a,uint32_t v){values[mmio_index(a)]=v;}
static uint32_t mmio_get(uint32_t a){return values[mmio_index(a)];}
static int buffer_byte(const sc_buffer *b,uint32_t i,uint8_t *v,uint8_t *k){if(b->kind==SC_RAM){uint32_t a=b->address+i;if(a<TF_RAM_BASE||a-TF_RAM_BASE>=TF_RAM_SIZE)return 0;*v=ram_state.ram[a-TF_RAM_BASE];*k=ram_state.known[a-TF_RAM_BASE];return 1;}if(b->kind!=SC_VIEW||i>=b->available||!b->data||!b->known)return 0;*v=b->data[i];*k=b->known[i];return 1;}
static int buffer_write(const sc_buffer *b,uint32_t i,uint8_t v,uint8_t k){if(b->kind==SC_RAM){uint32_t a=b->address+i;if(a<TF_RAM_BASE||a-TF_RAM_BASE>=TF_RAM_SIZE)return 0;ram_state.ram[a-TF_RAM_BASE]=v;ram_state.known[a-TF_RAM_BASE]=k;return 1;}if(b->kind!=SC_VIEW||i>=b->available||!b->data||!b->known)return 0;b->data[i]=v;b->known[i]=k;return 1;}
static sc_flow provider(void *ctx,sc_model *m,const sc_request *q,sc_result *out){
    unsigned ch=selected==2?2:1,i;uint8_t v,k;(void)ctx;CHECK(m==&model);CHECK(traces<32768);if(traces<32768)trace[traces++]=*q;if(q->va==halt_va)return SC_HALT;if(q->va==transfer_va)return SC_TRANSFER;
    if(q->operation==SC_INTERRUPT_RETURN)return irq_returned?SC_RETURNED:SC_TRANSFER;
    if(q->operation==SC_CSR_CLEAR||q->operation==SC_CSR_SET)return SC_RETURNED;
    if(q->operation==SC_ROM_COPY||q->operation==SC_ROM_MEMSET){if(halt_copy&&q->operation==SC_ROM_COPY)return SC_HALT;for(i=0;i<q->length;i++){if(q->operation==SC_ROM_MEMSET){v=(uint8_t)q->arguments[0];k=255;}else if(!buffer_byte(&q->source,i,&v,&k))return SC_HALT;if(!buffer_write(&q->destination,i,v,k))return SC_HALT;}out->memory_effects=1;if(mutate_frame_copy&&q->operation==SC_ROM_COPY&&live_frame.kind!=SC_NONE){buffer_write(&live_frame,11,2,255);mutate_frame_copy=0;}if(queue_add_flag&&q->destination.kind==SC_RAM&&q->destination.address>=SC_QUEUE_ADDRESS&&q->destination.address<SC_QUEUE_ADDRESS+384){put(SC_FLAGS_ADDRESS,get(SC_FLAGS_ADDRESS,1)|2,1);queue_add_flag=0;}return SC_RETURNED;}
    if(q->operation==SC_ROM_CALL){if(q->slot==104){if(!free_allowed)return SC_HALT;if(free_mutation){put(TF_GP+174,9,1);put(TF_RAM_BASE+0xbe08+12*3+4,0x1049a,4);free_mutation=0;}out->value=0xabcdef00;out->known=0;return SC_RETURNED;}if(q->slot==124){out->value=clock_count<clock_length?clock_values[clock_count]:clock_raw;out->known=UINT32_MAX;++clock_count;clock_raw+=clock_step;return SC_RETURNED;}if(q->slot==128){out->value=7;out->known=UINT32_MAX;return SC_RETURNED;}if(q->slot==80||q->slot==88||q->slot==92||q->slot==556){if(cleanup_live_config&&q->slot==92&&q->arguments[1]==4){put(TF_GP+120,0x3ab,2);put(TF_GP+122,0x123,2);put(TF_GP+124,0x7ff,2);cleanup_live_config=0;}out->known=0;out->value=0xdeafbeef;return SC_RETURNED;}return SC_HALT;}
    if(q->operation==SC_MMIO_READ){CHECK(q->width==16||q->width==32);out->known=UINT32_MAX;if(q->target==0x40013008){out->value=force_status<0?3u:(uint32_t)force_status;if(partial_status)out->known&=~2u;}else if(q->target==0x4001300c){out->value=response;out->known=UINT32_C(0xffffff00)|response_known;if(mutate_dlc_read&&command==3&&address==0x31){buffer_write(&live_frame,2,2,255);mutate_dlc_read=0;}}else{unsigned at=mmio_index(q->target);out->value=values[at];out->known=masks[at];if(rx_live_regs){switch(q->va){case 0x18b04:out->value=0x11;break;case 0x18b0c:out->value=0x2200;break;case 0x18b16:out->value=0x330000;break;case 0x18b20:out->value=0x44000000;break;case 0x18b2a:out->value=0x55;break;case 0x18b32:out->value=0x6600;break;case 0x18b3c:out->value=0x770000;break;case 0x18b46:out->value=0x88000000;break;default:break;}}}return SC_RETURNED;}
    if(q->operation!=SC_MMIO_WRITE)return SC_HALT;
    CHECK(q->width==16||q->width==32);
    if(source_snapshot_mutation&&q->va==0x1890c){put(TF_RAM_BASE+0x6000,0xffff,2);source_snapshot_mutation=0;}
    if(q->target==0x40010814){if(q->value==16){selected|=1;position=0;}if(q->value==1){selected|=2;position=0;}return SC_RETURNED;}
    if(q->target==0x40010810&&q->value==17){selected=0;position=0;return SC_RETURNED;}
    if(q->target==0x4001300c){CHECK(tx_count<sizeof(tx));if(tx_count<sizeof(tx))tx[tx_count++]=(uint8_t)q->value;v=(uint8_t)q->value;k=(uint8_t)q->known;response=0;response_known=255;
        if(position==0){if(k!=255)return SC_HALT;command=v;if(v==192){regs[ch][0x0e]=0x80;reg_known[ch][0x0e]=255;}}
        else if(position==1){if(k!=255)return SC_HALT;address=v;}
        else if(command==3){response=regs[ch][address&255];response_known=reg_known[ch][address&255];++address;}
        else if(command==2){regs[ch][address&255]=v;reg_known[ch][address&255]=k;++address;}
        else if(command==5){if(position==2){response=v;response_known=k;}else if(position==3){uint8_t bits=tx[tx_count-2];regs[ch][address]=(uint8_t)((regs[ch][address]&~bits)|(v&bits));reg_known[ch][address]=(uint8_t)((reg_known[ch][address]&~bits)|(k&bits));if(auto_mode&&address==15){regs[ch][14]=(uint8_t)(regs[ch][15]&224);reg_known[ch][14]=255;}}}
        if(mutate_ram&&command==2&&position==2){put(TF_RAM_BASE+0x6001,0xcc,1);mutate_ram=0;}++position;return SC_RETURNED;}
    if(q->target==0x40010414){values[mmio_index(q->target)]&=~q->value;return SC_RETURNED;}
    i=mmio_index(q->target);values[i]=q->value;masks[i]=q->known;if(arr_live&&q->target==0x4000082c)values[i]=6;return SC_RETURNED;
}
static void fresh(void){sc_backend b;memset(&ram_state,0,sizeof(ram_state));memset(ram_state.known,255,sizeof(ram_state.known));ram_state.runtime=runtime;ram_state.runtime_length=sizeof(runtime);memset(trace,0,sizeof(trace));traces=tx_count=mmio_count=0;memset(regs,0,sizeof(regs));memset(reg_known,255,sizeof(reg_known));selected=command=position=address=0;response=0;response_known=255;clock_raw=clock_step=clock_count=clock_length=0;auto_mode=1;force_status=-1;partial_status=halt_copy=mutate_frame_copy=mutate_dlc_read=queue_add_flag=irq_returned=arr_live=rx_live_regs=mutate_ram=0;free_allowed=free_mutation=source_snapshot_mutation=cleanup_live_config=0;halt_va=transfer_va=UINT32_MAX;memset(&live_frame,0,sizeof(live_frame));put(TF_GP+84,TF_RAM_BASE+0x5000,4);put(SC_TASK_ADDRESS,5,1);put(TF_GP+112,96000000,4);memset(&b,0,sizeof(b));b.invoke=provider;sc_init(&model,&ram_state,&b);}
static sc_flow run(uint32_t entry,uint32_t a0,uint32_t a1,uint32_t a2,uint32_t a3,sc_buffer b){sc_arguments a;a.registers[0]=a0;a.registers[1]=a1;a.registers[2]=a2;a.registers[3]=a3;a.buffer=b;return sc_run(&model,entry,&a);}
static sc_buffer none(void){sc_buffer b;memset(&b,0,sizeof(b));return b;}
static sc_buffer view(uint8_t *v,uint8_t *k,uint32_t n){sc_buffer b=none();b.kind=SC_VIEW;b.data=v;b.known=k;b.available=n;return b;}
static sc_buffer ramb(uint32_t a){sc_buffer b=none();b.kind=SC_RAM;b.address=a;return b;}
static const sc_request *find(sc_operation kind,unsigned slot){unsigned i;for(i=0;i<traces;i++)if(trace[i].operation==kind&&(kind!=SC_ROM_CALL||trace[i].slot==slot))return &trace[i];return NULL;}
static unsigned count_target(uint32_t target){unsigned i,n=0;for(i=0;i<traces;i++)if(trace[i].target==target)++n;return n;}
static unsigned count_write(uint32_t target){unsigned i,n=0;for(i=0;i<traces;i++)if(trace[i].operation==SC_MMIO_WRITE&&trace[i].target==target)++n;return n;}
static unsigned count_slot(unsigned slot){unsigned i,n=0;for(i=0;i<traces;i++)if(trace[i].operation==SC_ROM_CALL&&trace[i].slot==slot)++n;return n;}
static void frame_bytes(uint8_t *v,uint8_t *k,uint16_t id,uint8_t len,uint8_t channel){unsigned i;memset(v,0,12);memset(k,255,12);v[0]=(uint8_t)id;v[1]=(uint8_t)(id>>8);v[2]=len;v[11]=channel;for(i=0;i<8;i++)v[3+i]=(uint8_t)(0xa0+i);}
static void byte_cases(void){group("native SPI255 retries, partial operand boundary and no fake release");fresh();CHECK(run(SC_SPI_BYTE,0x1234,0,0,0,none())==SC_RETURNED);CHECK(tx_count==1&&tx[0]==0x34);CHECK(model.result_defined&&model.result==0&&model.result_known==UINT32_MAX);fresh();force_status=0;CHECK(run(SC_SPI_BYTE,1,0,0,0,none())==SC_RETURNED);CHECK(count_target(0x40013008)==255&&tx_count==0&&model.result==0);fresh();partial_status=1;CHECK(run(SC_SPI_BYTE,1,0,0,0,none())==SC_HALT);CHECK(tx_count==0&&model.unknown_va==0x16616);fresh();halt_va=0x1661e;CHECK(run(SC_READ_REGISTER,1,44,0,0,none())==SC_HALT);CHECK(count_target(0x40010814)==1&&count_target(0x40010810)==0);}
static void primitive_cases(void){uint8_t v[3]={0xaa,0xbb,0xcc},k[3]={255,255,255};group("WRITE READ BITMODIFY block order and channel bits");fresh();CHECK(run(SC_WRITE_BYTES,3,0x20,0,3,view(v,k,3))==SC_RETURNED);CHECK(count_target(0x40010814)==2&&tx_count==5&&tx[0]==2&&tx[1]==0x20);CHECK(regs[1][0x20]==0xaa&&regs[1][0x22]==0xcc);fresh();regs[2][44]=0x81;CHECK(run(SC_READ_REGISTER,2,44,0,0,none())==SC_RETURNED);CHECK(model.result==0x81&&model.result_known==UINT32_MAX);CHECK(tx_count==3&&tx[0]==3&&tx[1]==44&&tx[2]==0);CHECK(run(SC_MODIFY,2,44,0x80,0,none())==SC_RETURNED);CHECK(regs[2][44]==1);fresh();regs[2][44]=2;reg_known[2][44]=254;CHECK(run(SC_READ_REGISTER,2,44,0,0,none())==SC_RETURNED);CHECK(model.result==2&&model.result_known==UINT32_C(0xfffffffe));}
static void modes(void){group("mode/reset native elapsed tests and low32 clock transform");fresh();CHECK(run(SC_SET_MODE,1,128,0,0,none())==SC_RETURNED);CHECK(model.result_defined&&model.result==0);fresh();clock_step=16;CHECK(run(SC_SET_MODE,1,128,0,0,none())==SC_RETURNED);CHECK(model.result==1&&clock_count==2);fresh();model.spin_budget=2;auto_mode=0;regs[1][14]=0;CHECK(run(SC_SET_MODE,1,128,0,0,none())==SC_HALT);CHECK(model.unknown_va==0x16774);fresh();CHECK(run(SC_RESET,2,0,0,0,none())==SC_RETURNED);CHECK(model.result==0&&tx[0]==192&&tx_count==4);}
static void rx_packet(unsigned ch,unsigned start,uint8_t sidl,uint8_t dlc){unsigned i;regs[ch][start]=0x12;regs[ch][start+1]=sidl;regs[ch][start+2]=0xaa;regs[ch][start+3]=0xbb;regs[ch][start+4]=dlc;for(i=0;i<8;i++)regs[ch][start+5+i]=(uint8_t)(0x30+i);}
static void receive_cases(void){group("RX13 standard gates, DLC nibble and queue literal layout");fresh();rx_packet(1,0x61,0xe0,0xf2);CHECK(run(SC_RECEIVE_BUFFER,1,0x61,0,0,none())==SC_RETURNED);CHECK(model.queued==1&&get(SC_QUEUE_ADDRESS,2)==0x97&&get(SC_QUEUE_ADDRESS+2,1)==2);CHECK(get(SC_QUEUE_ADDRESS+3,1)==0x30&&get(SC_QUEUE_ADDRESS+11,1)==1);CHECK(tx_count==15&&tx[0]==3&&tx[1]==0x61);fresh();rx_packet(1,0x61,0x18,2);CHECK(run(SC_RECEIVE_BUFFER,1,0x61,0,0,none())==SC_RETURNED);CHECK(model.rx_rejected==1&&model.queued==0);fresh();rx_packet(2,0x71,0,0);CHECK(run(SC_RECEIVE_BUFFER,2,0x71,0,0,none())==SC_RETURNED);CHECK(model.rx_rejected==1);fresh();rx_packet(2,0x71,0,9);CHECK(run(SC_RECEIVE_BUFFER,2,0x71,0,0,none())==SC_RETURNED);CHECK(model.rx_rejected==1);}
static void pending_cases(void){group("pending snapshot drains both buffers before CANINTF write0");fresh();regs[1][44]=3;rx_packet(1,0x61,0,1);rx_packet(1,0x71,0x20,2);CHECK(run(SC_RECEIVE_PENDING,1,0,0,0,none())==SC_RETURNED);CHECK(model.queued==2&&regs[1][44]==0);CHECK(get(SC_QUEUE_ADDRESS,2)==0x90&&get(SC_QUEUE_ADDRESS+12,2)==0x91);CHECK(tx_count==36&&tx[tx_count-3]==2&&tx[tx_count-2]==44&&tx[tx_count-1]==0);}
static void send_cases(void){uint8_t v[12],k[12];unsigned i;group("TX3 buffers, unsafe live DLC/channel rereads and packet encoding");fresh();frame_bytes(v,k,0x1abc,1,1);regs[1][0x30]=8;regs[1][0x40]=0;CHECK(run(SC_SEND,0,0,0,0,view(v,k,12))==SC_RETURNED);CHECK(model.result_defined&&model.result==0);CHECK(regs[1][0x41]==0x57&&regs[1][0x42]==0x80&&regs[1][0x45]==1&&regs[1][0x46]==0xa0);CHECK((regs[1][0x40]&8)==8);fresh();frame_bytes(v,k,1,1,1);for(i=0;i<3;i++)regs[1][0x30+i*16]=8;CHECK(run(SC_SEND,0,0,0,0,view(v,k,12))==SC_RETURNED);CHECK(model.result==4&&tx_count==9);fresh();frame_bytes(v,k,1,9,1);CHECK(run(SC_SEND,0,0,0,0,view(v,k,12))==SC_RETURNED);CHECK(model.result==4&&traces==0);fresh();frame_bytes(v,k,1,1,1);live_frame=view(v,k,12);mutate_frame_copy=1;CHECK(run(SC_SEND,0,0,0,0,live_frame)==SC_RETURNED);CHECK(v[11]==2&&regs[2][0x36]==0xa0&&regs[1][0x36]==0);fresh();frame_bytes(v,k,1,1,1);live_frame=view(v,k,12);mutate_dlc_read=1;CHECK(run(SC_SEND,0,0,0,0,live_frame)==SC_RETURNED);CHECK(v[2]==2&&regs[1][0x35]==1&&regs[1][0x36]==0xa0&&regs[1][0x37]==0);}
static void queue_cases(void){uint8_t v[10],k[10];unsigned i;group("queue32 first-free, zero-ID sentinel, unchecked count overflow and copy prefix");for(i=0;i<10;i++){v[i]=(uint8_t)(0x20+i);k[i]=255;}fresh();CHECK(run(SC_QUEUE,0x1234,0,10,2,view(v,k,10))==SC_RETURNED);CHECK(get(SC_QUEUE_ADDRESS,2)==0x1234&&get(SC_QUEUE_ADDRESS+2,1)==10&&get(SC_QUEUE_ADDRESS+11,1)==2);CHECK(get(SC_QUEUE_ADDRESS+12,1)==0x29);fresh();CHECK(run(SC_QUEUE,0,0,1,1,view(v,k,10))==SC_RETURNED);CHECK(get(SC_QUEUE_ADDRESS,2)==0&&model.queued==1);fresh();for(i=0;i<32;i++)put(SC_QUEUE_ADDRESS+12*i,1,2);CHECK(run(SC_QUEUE,2,0,1,1,view(v,k,10))==SC_RETURNED);CHECK(model.queue_full==1&&!find(SC_ROM_COPY,0));fresh();halt_copy=1;CHECK(run(SC_QUEUE,0x1234,0,2,2,view(v,k,10))==SC_HALT);CHECK(get(SC_QUEUE_ADDRESS,2)==0x1234&&get(SC_QUEUE_ADDRESS+2,1)==2&&get(SC_QUEUE_ADDRESS+11,1)==0);}
static void filter_cases(void){uint8_t v[13]={0xff,0xff,0x99,3},k[13];const sc_request *r;unsigned i;group("six encoded filters, two masks, reserved raw RXM and reload ROM556");memset(k,255,sizeof(k));fresh();CHECK(run(SC_FILTERS,1,0,13,1,view(v,k,13))==SC_RETURNED);CHECK(regs[1][0]==255&&regs[1][1]==224&&regs[1][4]==0x73&&regs[1][5]==0x20);CHECK(regs[1][0x60]==32&&regs[1][0x70]==32);r=find(SC_ROM_COPY,0);CHECK(r&&r->length==12);r=find(SC_ROM_CALL,556);CHECK(r&&r->arguments[0]==5&&r->arguments[1]==2&&r->arguments[2]==1600);fresh();CHECK(run(SC_SET_MASK,2,1,0,0,none())==SC_RETURNED);CHECK(regs[2][0x24]==255&&regs[2][0x25]==224);fresh();CHECK(run(SC_SPECIAL_FILTERS,2,0,0,0,none())==SC_RETURNED);CHECK(regs[2][0]==0x6e&&regs[2][1]==0&&regs[2][4]==0);for(i=1;i<6;i++){static const unsigned offsets[6]={0,4,8,16,20,24};CHECK(regs[2][offsets[i]]==0);}fresh();CHECK(run(SC_ACCEPT_ALL,1,0,0,0,none())==SC_RETURNED);CHECK(regs[1][0x60]==96&&regs[1][0x70]==96&&find(SC_ROM_CALL,92));fresh();CHECK(run(SC_CLEAR_FILTERS,0,0,0,0,none())==SC_RETURNED&&traces==0);}
static void init_cases(void){group("full controller init returns cached reset status, ignores mode scalar");fresh();CHECK(run(SC_CONTROLLER_INIT,1,0,0,0,none())==SC_RETURNED);CHECK(model.result_defined&&model.result==0&&regs[1][42]==0&&regs[1][41]==144&&regs[1][40]==130);CHECK(regs[1][32]==255&&regs[1][33]==224&&regs[1][36]==255&&regs[1][37]==224&&regs[1][43]==3&&regs[1][44]==0);fresh();clock_length=4;clock_values[0]=clock_values[1]=clock_values[2]=0;clock_values[3]=16;CHECK(run(SC_CONTROLLER_INIT,2,0,0,0,none())==SC_RETURNED);CHECK(model.result==0&&regs[2][43]==3);fresh();clock_step=16;CHECK(run(SC_CONTROLLER_INIT,1,0,0,0,none())==SC_RETURNED);CHECK(model.result==1&&regs[1][43]==0);}
static void irq_cases(void){group("EXTI double live MMIO reads/mret and main drain rereads shared flags");fresh();mmio_set(0x40010414,192);ram_state.known[0x4168]=254;CHECK(run(SC_EXTI_IRQ,0,0,0,0,none())==SC_TRANSFER);CHECK(get(SC_FLAGS_ADDRESS,1)==3&&ram_state.known[0x4168]==255);CHECK(count_target(0x40010414)==4);fresh();irq_returned=1;CHECK(run(SC_EXTI_IRQ,0,0,0,0,none())==SC_HALT&&model.unknown_va==0x16d6a);fresh();put(SC_FLAGS_ADDRESS,1,1);put(SC_FLAGS_ADDRESS+1,2,1);put(SC_FLAGS_ADDRESS+2,2,1);regs[1][44]=1;regs[2][44]=2;rx_packet(1,0x61,0,1);rx_packet(2,0x71,0,1);queue_add_flag=1;CHECK(run(SC_DRAIN,0,0,0,0,none())==SC_RETURNED);CHECK(model.queued==2&&get(SC_FLAGS_ADDRESS,1)==0&&get(SC_FLAGS_ADDRESS+1,1)==0&&get(SC_FLAGS_ADDRESS+2,1)==0);fresh();put(SC_FLAGS_ADDRESS,1,1);put(SC_FLAGS_ADDRESS+1,2,1);regs[1][44]=1;rx_packet(1,0x61,0,1);halt_copy=1;CHECK(run(SC_DRAIN,0,0,0,0,none())==SC_HALT);CHECK(get(SC_FLAGS_ADDRESS,1)==0&&get(SC_FLAGS_ADDRESS+1,1)==2);}
static void task_cases(void){const sc_request *r;group("task priority2/4/1, u8 counter wrap, retry48 and successful outer cleanup");fresh();put(SC_FLAGS_ADDRESS+1,1,1);CHECK(run(SC_TASK,7,7,0,0,none())==SC_RETURNED);CHECK(model.result_defined&&model.result==5&&get(SC_FLAGS_ADDRESS+1,1)==2&&traces==0);fresh();put(SC_FLAGS_ADDRESS+2,255,1);CHECK(run(SC_TASK,7,4,0,0,none())==SC_RETURNED);CHECK(model.result==0&&get(SC_FLAGS_ADDRESS+2,1)==0&&traces==0);fresh();clock_step=16;CHECK(run(SC_TASK,7,1,0,0,none())==SC_RETURNED);CHECK(model.result==0);r=find(SC_ROM_CALL,88);CHECK(r&&r->arguments[0]==7&&r->arguments[1]==1&&r->arguments[2]==48);fresh();CHECK(run(SC_TASK,7,1,0,0,none())==SC_RETURNED);CHECK(model.result_defined&&model.result==0&&model.unknown_va==0);CHECK(count_target(0x40010810)>0&&count_write(0x40006600)==56);}
static void peripheral_cases(void){const sc_request *r;group("GPIO/EXTI/SPI/TIM setup bodies, live ARR and task registration/post");fresh();arr_live=1;CHECK(run(SC_PERIPHERAL_INIT,0,0,0,0,none())==SC_RETURNED);CHECK(get(SC_TASK_ADDRESS,1)==7&&get(SC_FLAGS_ADDRESS,3)==0);CHECK(mmio_get(0x4000082c)==6&&mmio_get(0x4000083c)==3);CHECK(mmio_get(0x40013000)==0x354&&mmio_get(0x40013010)==7);CHECK((mmio_get(0x40010400)&192)==192&&(mmio_get(0x4001040c)&192)==192);r=find(SC_ROM_CALL,128);CHECK(r&&r->arguments[0]==0x16c6c);r=find(SC_ROM_CALL,80);CHECK(r&&r->arguments[0]==7&&r->arguments[1]==1);}
static void route_cases(void){uint8_t v[12],k[12];unsigned i;group("source gate and onchip mailbox writes retain unknown wrapper tail");fresh();frame_bytes(v,k,0x123,1,0);mmio_set(0x40006408,UINT32_C(1)<<26);CHECK(run(SC_ROUTE_SEND,0,0,0,0,view(v,k,12))==SC_RETURNED);CHECK(mmio_get(0x40006580)==((uint32_t)0x123<<21|1));CHECK((mmio_get(0x40006588)&255)==0xa0);i=mmio_index(0x40006588);CHECK(masks[i]==255);i=mmio_index(0x4000658c);CHECK(masks[i]==0);fresh();frame_bytes(v,k,1,1,1);put(TF_RAM_BASE+0x5004,8,1);CHECK(run(SC_ROUTE_SEND,0,0,0,0,view(v,k,12))==SC_RETURNED&&traces==0);fresh();put(TF_GP+193,3,1);CHECK(run(SC_GATE,0,0,0,0,none())==SC_RETURNED&&model.result==0);fresh();CHECK(run(SC_ROUTE_FILTERS,0,0,0,0,none())==SC_RETURNED&&count_write(0x40006600)==28);}
static void can_irq_cases(void){group("onchip FIFO0 body keeps live register reads and unknown extended standard-ID");fresh();mmio_set(0x4000640c,1);mmio_set(0x400065b0,(uint32_t)0x123<<21);mmio_set(0x400065b4,2);mmio_set(0x400065b8,0x44332211);mmio_set(0x400065bc,0x88776655);CHECK(run(SC_CAN_FIFO0_IRQ,0,0,0,0,none())==SC_TRANSFER);CHECK(model.queued==1&&get(SC_QUEUE_ADDRESS,2)==0x123&&get(SC_QUEUE_ADDRESS+3,2)==0x2211&&get(SC_QUEUE_ADDRESS+11,1)==0);CHECK(mmio_get(0x4000640c)==33);fresh();mmio_set(0x4000640c,0);CHECK(run(SC_CAN_FIFO0_IRQ,0,0,0,0,none())==SC_TRANSFER&&model.queued==0);}
static void can_source_prefix(void){uint8_t v[20]={0x23,1},k[20];sc_buffer b;group("onchip first source12 read VA, repeated live RX words and extended unknown STD field");memset(k,255,sizeof(k));v[10]=1;v[11]=0xab;fresh();mmio_set(0x40006408,UINT32_C(1)<<26);CHECK(run(SC_CAN_TRANSMIT,0x40006400,0,0,0,view(v,k,12))==SC_HALT);CHECK(model.unknown_va==0x18a62);fresh();rx_live_regs=1;mmio_set(0x400065b0,(uint32_t)0x123<<21);mmio_set(0x400065b4,8);memset(v,0,sizeof(v));memset(k,0,sizeof(k));b=view(v,k,20);CHECK(run(SC_CAN_RECEIVE,0x40006400,0,0,0,b)==SC_RETURNED);CHECK(v[11]==0x11&&v[12]==0x22&&v[13]==0x33&&v[14]==0x44&&v[15]==0x55&&v[16]==0x66&&v[17]==0x77&&v[18]==0x88);fresh();mmio_set(0x4000640c,1);mmio_set(0x400065b0,((uint32_t)0x123<<3)|4);mmio_set(0x400065b4,1);mmio_set(0x400065b8,0xaa);CHECK(run(SC_CAN_FIFO0_IRQ,0,0,0,0,none())==SC_TRANSFER);CHECK(model.queued==1&&ram_state.known[SC_QUEUE_ADDRESS-TF_RAM_BASE]==0&&ram_state.known[SC_QUEUE_ADDRESS-TF_RAM_BASE+1]==0);}
static void ram_alias_cases(void){uint8_t v[12],k[12];unsigned i;group("same authoritative RAM sources remain live through SPI and ROM-copy provider calls");fresh();put(TF_RAM_BASE+0x6000,0xbbaa,2);mutate_ram=1;CHECK(run(SC_WRITE_BYTES,1,0x20,0,2,ramb(TF_RAM_BASE+0x6000))==SC_RETURNED);CHECK(regs[1][0x20]==0xaa&&regs[1][0x21]==0xcc&&get(TF_RAM_BASE+0x6001,1)==0xcc);fresh();frame_bytes(v,k,1,1,1);for(i=0;i<12;i++)put(TF_RAM_BASE+0x6000+i,v[i],1);live_frame=ramb(TF_RAM_BASE+0x6000);mutate_frame_copy=1;CHECK(run(SC_SEND,0,0,0,0,live_frame)==SC_RETURNED);CHECK(get(TF_RAM_BASE+0x600b,1)==2&&regs[2][0x36]==0xa0);}
static void clock_cases(void){group("original clock helper low32 multiplication differs from widened arithmetic");fresh();clock_raw=0x40000000;CHECK(run(SC_TIME_MS,0,0,0,0,none())==SC_RETURNED&&model.result_defined&&model.result==0x08000000);fresh();clock_raw=0x1999999a;CHECK(run(SC_TIME_MS,0,0,0,0,none())==SC_RETURNED&&model.result==0);}
static uint16_t shifted_id(const uint8_t *p){return (uint16_t)(((uint32_t)p[0]|((uint32_t)p[1]<<8))<<5);}
static uint32_t fixture_word(uint32_t va){uint32_t v=0;unsigned i;for(i=0;i<4;i++)v|=(uint32_t)runtime[va-0x8000+i]<<(i*8);return v;}
static uint32_t fixture_immediate_pair(uint32_t pc,int relative){uint32_t hi=fixture_word(pc)&UINT32_C(0xfffff000);int32_t lo=(int32_t)(fixture_word(pc+4)>>20);if(lo&2048)lo-=4096;return hi+(uint32_t)lo+(relative?pc:0);}
static void expect_bank(unsigned bank,const uint8_t *v){uint32_t a=0x40006640u+bank*8;
    CHECK(mmio_get(a)==((uint32_t)shifted_id(v+2)|((uint32_t)shifted_id(v+6)<<16)));
    CHECK(mmio_get(a+4)==((uint32_t)shifted_id(v)|((uint32_t)shifted_id(v+4)<<16)));}
static void channel0_cases(void){uint8_t v[112],k[112],zeroes[112]={0};unsigned i;group("12780 fourteen filter banks, full112 snapshot, raw32 count clamp and zero padding");
    for(i=0;i<112;i++){v[i]=(uint8_t)(i*37+11);k[i]=255;}fresh();CHECK(run(0x12780,0,112,0,0,view(v,k,112))==SC_RETURNED);
    CHECK(!model.result_defined&&count_write(0x40006600)==28);for(i=0;i<14;i++)expect_bank(i,v+i*8);
    CHECK((mmio_get(0x4000661c)&0x3fff)==0x3fff&&(mmio_get(0x40006604)&0x3fff)==0x3fff);
    CHECK((mmio_get(0x4000660c)&0x3fff)==0&&(mmio_get(0x40006614)&0x3fff)==0&&(mmio_get(0x40006600)&1)==0);
    fresh();CHECK(run(0x12780,0,0x100,0,0,view(v,k,112))==SC_RETURNED);CHECK(find(SC_ROM_COPY,0)&&find(SC_ROM_COPY,0)->length==112);expect_bank(13,v+104);
    fresh();CHECK(run(0x12780,0,0,0,0,none())==SC_RETURNED);for(i=0;i<14;i++)expect_bank(i,zeroes+i*8);
    fresh();CHECK(run(0x12820,0,0,0,0,none())==SC_RETURNED);CHECK(!find(SC_ROM_COPY,0)&&!find(SC_ROM_MEMSET,0));for(i=0;i<14;i++)expect_bank(i,zeroes+i*8);
}
static void filter_snapshot_cases(void){uint8_t v[8]={0x23,1,0x56,4,0x89,7,0xbc,0x0a},k[8];unsigned i;group("12780 COPY snapshot, partial encoded masks and missing COPY exact prefix");
    memset(k,255,sizeof(k));k[0]=127;fresh();CHECK(run(0x12780,0,8,0,0,view(v,k,8))==SC_RETURNED);CHECK(masks[mmio_index(0x40006644)]==(UINT32_MAX^(UINT32_C(1)<<12)));
    fresh();for(i=0;i<8;i++)put(TF_RAM_BASE+0x6000+i,v[i],1);source_snapshot_mutation=1;
    CHECK(run(0x12780,0,8,0,0,ramb(TF_RAM_BASE+0x6000))==SC_RETURNED);CHECK(get(TF_RAM_BASE+0x6000,2)==65535);expect_bank(0,v);
    fresh();halt_va=0x127bc;CHECK(run(0x12780,0,8,0,0,view(v,k,8))==SC_HALT);CHECK(model.unknown_va==0x127bc&&count_write(0x40006600)==0&&traces==2);
    fresh();transfer_va=0x127bc;CHECK(run(0x12780,0,8,0,0,view(v,k,8))==SC_TRANSFER);CHECK(count_write(0x40006600)==0&&traces==2);
}
static void descriptor_put(uint8_t *v,unsigned off,uint32_t n,unsigned count){unsigned i;for(i=0;i<count;i++)v[off+i]=(uint8_t)(n>>(i*8));}
static void filter_descriptor_cases(void){uint8_t v[20]={0},k[20];unsigned i;group("188F6 full raw descriptor branches, RV shift masking and no invented bank bounds");
    memset(k,255,sizeof(k));for(i=0;i<4;i++)descriptor_put(v,i*2,0x1111*(i+1),2);v[10]=1;v[11]=1;descriptor_put(v,16,1,4);
    fresh();CHECK(run(0x188f6,0,0,0,0,view(v,k,20))==SC_RETURNED);CHECK(mmio_get(0x40006648)==0x44442222&&mmio_get(0x4000664c)==0x33331111);CHECK(!model.result_defined&&(mmio_get(0x40006604)&2)==2);
    fresh();v[12]=1;v[11]=0;descriptor_put(v,8,1,2);CHECK(run(0x188f6,0,0,0,0,view(v,k,20))==SC_RETURNED);CHECK(mmio_get(0x40006648)==0x11112222&&mmio_get(0x4000664c)==0x33334444);CHECK((mmio_get(0x4000660c)&2)==2&&(mmio_get(0x40006614)&2)==2);
    fresh();v[10]=33;v[12]=2;k[12]=254;descriptor_put(v,8,2,2);descriptor_put(v,16,2,4);k[16]=254;mmio_set(0x40006614,UINT32_MAX);mmio_set(0x4000661c,UINT32_MAX);
    CHECK(run(0x188f6,0,0,0,0,view(v,k,20))==SC_RETURNED);CHECK(count_target(0x4000660c)==0&&count_write(0x40006748)==0);CHECK(mmio_get(0x40006614)==UINT32_MAX&&mmio_get(0x4000661c)==(UINT32_MAX^2u));
    fresh();v[10]=1;CHECK(run(0x188f6,0,0,0,0,view(v,k,11))==SC_HALT);CHECK(model.unknown_va==0x18922&&(mmio_get(0x40006600)&1)==1);
    fresh();transfer_va=0x1890c;CHECK(run(0x188f6,0,0,0,0,view(v,k,20))==SC_TRANSFER);CHECK(traces==2);
}
static void cancel_cases(void){const sc_request *r;uint32_t slot=TF_RAM_BASE+0xbe08+24;group("908E first matching callback, free prefix, live task reread, low16 event and ignored scalar");
    fresh();CHECK(run(0x908e,0x1049a,0,0,0,none())==SC_RETURNED);CHECK(model.result_defined&&model.result==1&&model.result_known==UINT32_MAX&&traces==0);
    fresh();put(slot+4,0x1049a,4);put(slot+8,TF_RAM_BASE+0x6000,4);put(TF_GP+174,6,1);free_allowed=free_mutation=1;
    CHECK(run(0x908e,0x1049a,0,0,0,none())==SC_RETURNED);r=find(SC_ROM_CALL,104);CHECK(r&&r->count==1&&r->arguments[0]==TF_RAM_BASE+0x6000);r=find(SC_ROM_CALL,92);CHECK(r&&r->count==2&&r->arguments[0]==9&&r->arguments[1]==4);
    CHECK(get(slot+4,4)==0&&get(slot+8,4)==0&&get(TF_RAM_BASE+0xbe08+36+4,4)==0x1049a);CHECK(model.result_defined&&model.result_known==0&&model.result==0xdeafbeef);
    fresh();put(slot+4,0x1049a,4);put(slot+8,TF_RAM_BASE+0x6000,4);halt_va=0x90bc;CHECK(run(0x908e,0x1049a,0,0,0,none())==SC_HALT);CHECK(get(slot+4,4)==0x1049a&&get(slot+8,4)==TF_RAM_BASE+0x6000&&count_slot(92)==0);
    fresh();ram_state.known[0xbe0c]=254;put(TF_RAM_BASE+0xbe08+14*12+4,0x1063c,4);put(TF_GP+174,255,1);
    CHECK(run(0x908e,0x1063c,0,0,0,none())==SC_RETURNED);r=find(SC_ROM_CALL,92);CHECK(r&&r->arguments[0]==255&&r->arguments[1]==0x4000&&r->argument_known[0]==UINT32_MAX);
}
static void cleanup_mode_cases(void){unsigned mode,i;uint8_t want[112];uint32_t word;group("1291C full mode0..6 signed table, raw32 default, fixed110 ROM IDs and external filters");
    for(mode=0;mode<8;mode++){
        fresh();for(i=0;i<6;i++){put(TF_GP+120+i,0x40+i,1);put(TF_GP+128+i,0x70+i,1);}put(TF_RAM_BASE+0xbfb4,UINT32_MAX,4);put(TF_GP+300,0xffffff,3);
        CHECK(run(0x1291c,mode,0,0,0,none())==SC_RETURNED);CHECK(!model.result_defined&&get(TF_RAM_BASE+0xbfb4,4)==0&&get(TF_GP+300,3)==0);
        memset(want,0,112);word=mode==0?fixture_immediate_pair(0x12950,0):(mode==2||mode==3?0x021c00a9:fixture_immediate_pair(0x129a4,0));
        if(mode==1)memcpy(want,runtime+fixture_immediate_pair(0x1297e,1)-0x8000,110);else if(mode==4||mode==5)for(i=0;i<6;i++)want[i]=(uint8_t)((mode==4?0x40:0x70)+i);else if(mode<7)descriptor_put(want,0,word,4);
        for(i=0;i<14;i++)expect_bank(i,want+i*8);
        CHECK(count_write(0x40006600)==(mode<7?56u:28u));
        if(mode==0)CHECK(regs[1][0]==0&&regs[1][1]==32&&regs[2][0]==0&&count_slot(556)==0);
        else if(mode==1)CHECK(regs[1][0]==0x73&&regs[1][1]==0x20&&regs[2][0]==0x6e&&count_slot(556)==2);
        else CHECK(regs[1][0]==0&&regs[2][0]==0&&count_slot(556)==0);
    }
    fresh();CHECK(run(0x1291c,UINT32_MAX,0,0,0,none())==SC_RETURNED);CHECK(count_write(0x40006600)==28);
}
static void cleanup_prefix_cases(void){uint32_t slot=TF_RAM_BASE+0xbe08;group("10586 nested cleanup repeats, free HALT preserves byte prefix, provider transfer and ROM data boundary");
    fresh();put(slot+4,0x1049a,4);put(slot+8,TF_RAM_BASE+0x6000,4);put(TF_RAM_BASE+0xbfb4,0x44332211,4);put(TF_GP+300,0xaabbcc,3);halt_va=0x90bc;
    CHECK(run(0x1291c,0,0,0,0,none())==SC_HALT);CHECK(model.unknown_va==0x90bc&&get(TF_GP+300,3)==0&&get(TF_RAM_BASE+0xbfb4,4)==0x44332200);CHECK(count_write(0x40006600)==0&&get(slot+4,4)==0x1049a);
    fresh();transfer_va=0x105a6;put(TF_RAM_BASE+0xbfb4,0x44332211,4);CHECK(run(0x10586,0,0,0,0,none())==SC_TRANSFER);CHECK(get(TF_RAM_BASE+0xbfb4,4)==0x44332200&&count_write(0x40010810)==0);
    fresh();halt_va=0x127a0;CHECK(run(0x1291c,0,0,0,0,none())==SC_HALT);CHECK(model.unknown_va==0x127a0&&count_write(0x40006600)==28);
    fresh();ram_state.runtime_length=0x199fc-0x8000+32;CHECK(run(0x1291c,1,0,0,0,none())==SC_HALT);CHECK(model.unknown_va==0x1294a&&model.unknown_address==0x1a31c);CHECK(count_write(0x40006600)==28);
}
static void cleanup_live_cases(void){uint8_t v[112]={0};const sc_request *r;group("late shared mode4/5 sources, route-clear body and completed event1 success under exact primitive flow");
    fresh();cleanup_live_config=1;CHECK(run(0x1291c,4,0,0,0,none())==SC_RETURNED);descriptor_put(v,0,0x3ab,2);descriptor_put(v,2,0x123,2);descriptor_put(v,4,0x7ff,2);expect_bank(0,v);CHECK(get(TF_GP+120,2)==0x3ab&&cleanup_live_config==0);
    fresh();CHECK(run(0x128ec,0,0,0,0,none())==SC_RETURNED);CHECK(count_write(0x40006600)==28&&traces>0);
    fresh();CHECK(run(0x128ec,1,0,0,0,none())==SC_RETURNED);CHECK(count_write(0x40006600)==0&&regs[1][0x60]==32);r=find(SC_ROM_CALL,92);CHECK(r&&r->arguments[1]==2);
    fresh();halt_va=0x1890c;CHECK(run(SC_TASK,7,1,0,0,none())==SC_HALT);CHECK(model.unknown_va==0x1890c&&!model.result_defined&&count_slot(88)==0);
    fresh();transfer_va=0x1890c;CHECK(run(SC_TASK,7,1,0,0,none())==SC_TRANSFER);CHECK(!model.result_defined&&count_slot(88)==0);
}
static void literal_cases(void){static const struct{uint32_t a;const char *s;} items[]={
{0x165fa,"0283"},
{0x16612,"03d78600"},
{0x1661e,"2396a600"},
{0x1662a,"03d78600"},
{0x16632,"03d5c600"},
{0x1666a,"23aae780"},
{0x1669c,"23a8e780"},
{0x16832,"e31824ff"},
{0x16844,"13f78701"},
{0x16850,"3d8a"},
{0x1686e,"efc0af96"},
{0x1697a,"0345b400"},
{0x16988,"83462400"},
{0x16996,"93f6f60f"},
{0x16aca,"93f7f77f"},
{0x16c02,"aa84"},
{0x16c7c,"83c79116"},
{0x16c82,"93f7f70f"},
{0x16c90,"13452400"},
{0x16d06,"efb07fc1"},
{0x16d26,"03a74741"},
{0x16d4a,"03a74741"},
{0x16d70,"83c78116"},
{0x16d8c,"83c78116"},
{0x16ddc,"2300a900"},
{0x16e28,"3357c702"},
{0x16e3a,"03d7c682"},
{0x19454,"2310f500"},
{0x18a7e,"23a4e718"},
{0x129ea,"314e"},
{0x12a1c,"8297"}
};unsigned i,j;group("fresh whole native field literal bindings");for(i=0;i<sizeof(items)/sizeof(items[0]);i++)for(j=0;j<strlen(items[i].s)/2;j++){char c[3];c[0]=items[i].s[j*2];c[1]=items[i].s[j*2+1];c[2]=0;CHECK(runtime[items[i].a-0x8000+j]==(uint8_t)strtoul(c,NULL,16));}}
int main(int argc,char **argv){FILE *f;if(argc!=2)return 2;f=fopen(argv[1],"rb");if(!f||fread(runtime,1,sizeof(runtime),f)!=sizeof(runtime)){if(f)fclose(f);return 2;}fclose(f);byte_cases();primitive_cases();modes();receive_cases();pending_cases();send_cases();queue_cases();filter_cases();init_cases();irq_cases();task_cases();peripheral_cases();route_cases();can_irq_cases();can_source_prefix();clock_cases();ram_alias_cases();channel0_cases();filter_snapshot_cases();filter_descriptor_cases();cancel_cases();cleanup_mode_cases();cleanup_prefix_cases();cleanup_live_cases();literal_cases();printf("SPI_CAN_RESULT groups=%u checks=%u failures=%u original_executed=no hardware=no\n",groups,checks,failures);return failures?1:0;}

