#include "tsl9_contract.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Literal expectations cite immutable VA/raw-range fixtures in evidence.json.
   Fake backend represents explicit RAM assumptions, never a hardware outcome. */
typedef struct {
    uint8_t ram[98304], ram_mask[98304], meta[256], meta_mask[256];
    uint8_t last_program[256], last_mask[256];
    tc_event events[4096]; size_t event_count;
    unsigned writes, reads, meta_reads, meta_writes;
    unsigned mismatch_read, unknown_read, busy_write, stale_meta_reads;
    unsigned dropped_write;
    uint32_t base;
    tc_truth schedule_result;
} fake_flash;
static fake_flash f;
static tc_model m;
static uint8_t p[1040], k[1040];
static unsigned assertions, failures, cases;
static const uint8_t synthetic_id[14]={0,1,2,3,4,5,6,7,8,9,10,11,12,13};
#define CHECK(x) do { ++assertions; if(!(x)) { ++failures; printf("FAIL %s:%d: %s\n",__func__,__LINE__,#x); } } while(0)

static void note(void *v,const tc_event *e) {
    fake_flash *b=(fake_flash *)v;
    if(b->event_count<4096) b->events[b->event_count++]=*e;
}
static void read_ram(void *v,uint32_t addr,uint8_t *d,uint8_t *mask,size_t n) {
    fake_flash *b=(fake_flash *)v;
    if(addr==0x08077B00u) {
        ++b->meta_reads; memcpy(d,b->meta,n); memcpy(mask,b->meta_mask,n);
        if(b->stale_meta_reads) d[4]=0;
    } else {
        size_t off=addr-b->base; ++b->reads;
        if(off+n<=sizeof(b->ram)) { memcpy(d,b->ram+off,n); memcpy(mask,b->ram_mask+off,n); }
        else { memset(d,0,n); memset(mask,0,n); }
        if(b->reads==b->mismatch_read) d[0]^=1;
        if(b->reads==b->unknown_read) memset(mask,0,n);
    }
}
static tc_flow write_ram(void *v,uint32_t addr,const uint8_t *d,const uint8_t *mask) {
    fake_flash *b=(fake_flash *)v;
    if(addr==0x08077B00u) {
        ++b->meta_writes; memcpy(b->meta,d,256); memcpy(b->meta_mask,mask,256);
    } else {
        size_t off=addr-b->base; ++b->writes;
        if(b->writes==b->busy_write) return TC_BUSY;
        if(b->writes==b->dropped_write) return TC_RETURNED;
        if(off+256<=sizeof(b->ram)) { memcpy(b->ram+off,d,256); memcpy(b->ram_mask+off,mask,256); }
    }
    memcpy(b->last_program,d,256); memcpy(b->last_mask,mask,256);
    return TC_RETURNED;
}
static tc_truth request_schedule(void *v,uint32_t va,uint32_t arg,uint32_t delay) {
    fake_flash *b=(fake_flash *)v; (void)va;(void)arg;(void)delay;return b->schedule_result;
}
static void copy_assumption(void *v,uint8_t *d,uint8_t *mask,const uint8_t *s,const uint8_t *sk,size_t n) {
    (void)v;memmove(d,s,n);memmove(mask,sk,n);
}
static void setup(tc_image image) {
    tc_backend b; uint8_t idmask[14];
    memset(&f,0,sizeof(f)); memset(&b,0,sizeof(b)); memset(idmask,255,sizeof(idmask));
    memset(f.meta_mask,255,8); f.meta[0]=16; f.meta[1]=16;
    f.base=image==TC_BOOT?0x08008000u:0x08001000u; f.schedule_result=TC_UNKNOWN;
    b.context=&f;b.read=read_ram;b.program256=write_ram;b.schedule=request_schedule;b.event=note;
    tc_init(&m,image,&b);tc_identity(&m,synthetic_id,idmask);
    m.alloc_ok=TC_YES;m.link_ok=TC_YES;m.uart_ready=TC_YES;m.general_auth=TC_YES;
    memset(p,0,sizeof(p));memset(k,255,sizeof(k));
}
static void control(uint8_t target) { memset(p,0,sizeof(p));p[0]=target;memcpy(p+1,synthetic_id,14); }
static void call(uint8_t command,uint16_t n) { tc_gatt_command(&m,command,p,k,n,2); }
static size_t count(tc_event_kind kind) {
    size_t n=0,i;for(i=0;i<f.event_count;++i) if(f.events[i].kind==kind) ++n;return n;
}
static const tc_event *nth(tc_event_kind kind,size_t index) {
    size_t i;for(i=0;i<f.event_count;++i) if(f.events[i].kind==kind) { if(index==0)return &f.events[i];--index; }return NULL;
}
static void page(unsigned n,uint8_t value) { p[0]=(uint8_t)(n>>8);p[1]=(uint8_t)n;memset(p+2,value,1024); }
static size_t frame(uint8_t command,const uint8_t *data,uint16_t n,uint8_t *out) {
    size_t i;unsigned sum=command+(n>>8)+(n&255u);
    out[0]=0x55;out[1]=0x7F;out[2]=command;out[3]=(uint8_t)(n>>8);out[4]=(uint8_t)n;
    for(i=0;i<n;++i) { out[i+5]=data[i];sum+=data[i]; }
    out[n+5]=(uint8_t)sum;return (size_t)n+6;
}
static void uart(uint8_t command,const uint8_t *data,uint16_t n,uint32_t clock) {
    uint8_t wire[1046];size_t size=frame(command,data,n,wire);tc_receive(&m,TC_UART,wire,size,clock);
}

/* Catches a stricter length==15 gate, wrong truncation, or U failing to clear active. */
static void token_aliases(void) {
    static const uint16_t lengths[]={15,271,527,783,1039};size_t i;unsigned image;
    for(image=0;image<2;++image) for(i=0;i<5;++i) {
        setup((tc_image)image);m.active=1;control(7);call('U',lengths[i]);
        CHECK(m.active==0);CHECK(m.reply_command=='U');CHECK(m.reply_length==1);
        CHECK(m.reply_data[0]==(uint8_t)image);CHECK(m.reply_queued==TC_YES);CHECK(count(TC_EV_SCHEDULE)==0);
    }
    setup(TC_BOOT);m.active=1;control(1);p[3]^=1;call('U',15);
    CHECK(m.active==0);CHECK(m.outcome==TC_SILENT);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_BOOT);m.active=1;control(1);call('U',1040);CHECK(m.active==0);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_BOOT);m.active=1;control(1);k[3]=0;call('U',15);CHECK(m.active==0);CHECK(m.outcome==TC_INDETERMINATE);
}
/* Catches success-only S ACK, loss of original echo length, wrong image target. */
static void start_echo_and_drop(void) {
    setup(TC_BOOT);control(1);call('S',271);
    CHECK(m.active==1);CHECK(m.reply_length==271);CHECK(m.reply_data[0]==1);CHECK(m.reply_data[1]==0);
    CHECK(count(TC_EV_CANCEL_STARTUP)==1);CHECK(f.meta[4]==2);CHECK(f.meta_writes==1);
    setup(TC_RUNTIME);control(0);call('S',15);CHECK(m.active==1);CHECK(m.reply_length==15);CHECK(f.meta_writes==0);
    control(1);call('S',15);CHECK(m.active==0);CHECK(p[0]==255);CHECK(m.reply_data[0]==255);
    setup(TC_BOOT);control(1);call('S',1040);CHECK(m.active==0);CHECK(p[0]==255);
    CHECK(m.reply_length==1040);CHECK(m.reply_queued==TC_NO);
    setup(TC_RUNTIME);control(0);m.alloc_ok=TC_NO;call('S',15);CHECK(m.active==1);CHECK(m.reply_queued==TC_NO);
    setup(TC_RUNTIME);control(0);m.link_ok=TC_UNKNOWN;call('S',15);CHECK(m.active==1);CHECK(m.reply_queued==TC_UNKNOWN);
    setup(TC_BOOT);p[0]=9;call('S',0);CHECK(p[0]==255);CHECK(m.reply_length==0);CHECK(m.reply_queued==TC_YES);
}
/* Catches page order/dedup logic or replacing silent failure with abort/NACK. */
static void write_boundaries_and_failure(void) {
    setup(TC_BOOT);page(95,0xA7);call('W',1026);CHECK(f.writes==0);CHECK(m.outcome==TC_SILENT);
    m.active=1;call('W',1025);CHECK(f.writes==0);CHECK(m.active==1);
    page(96,0xA7);call('W',1026);CHECK(f.writes==0);CHECK(m.active==1);
    page(95,0xA7);call('W',1026);CHECK(f.writes==4);CHECK(f.reads==256);CHECK(m.reply_command=='W');CHECK(m.reply_length==0);
    CHECK(nth(TC_EV_PROGRAM,0)!=NULL && nth(TC_EV_PROGRAM,0)->address==0x0801FC00u);
    page(2,0x19);call('W',1026);call('W',1026);CHECK(f.writes==12);CHECK(f.ram[2048]==0x19);
    setup(TC_RUNTIME);m.active=1;page(27,0x44);call('W',1026);
    CHECK(f.writes==4);CHECK(nth(TC_EV_PROGRAM,0)!=NULL && nth(TC_EV_PROGRAM,0)->address==0x08007C00u);
    page(28,0x44);call('W',1026);CHECK(f.writes==4);CHECK(m.active==1);CHECK(m.outcome==TC_SILENT);
    setup(TC_BOOT);m.active=1;page(0,0x42);f.mismatch_read=17;call('W',1026);
    CHECK(f.writes==4);CHECK(f.reads==17);CHECK(m.active==1);CHECK(count(TC_EV_REPLY)==0);CHECK(m.outcome==TC_SILENT);
    call('E',0);CHECK(m.reply_command=='E');CHECK(m.active==0);
    setup(TC_BOOT);m.active=1;page(0,0x42);call('W',1026);CHECK(m.reply_queued==TC_YES);
    setup(TC_BOOT);m.active=1;page(0,0x42);f.unknown_read=1;call('W',1026);
    CHECK(m.outcome==TC_INDETERMINATE);CHECK(m.active==1);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_BOOT);m.active=1;page(0,0x42);f.busy_write=2;call('W',1026);
    CHECK(m.outcome==TC_STALLED);CHECK(f.writes==2);CHECK(f.reads==0);CHECK(m.active==1);
}
/* Catches treating unknown ROM overlap copy as ordinary host memcpy/success. */
static void overlap_boundary(void) {
    setup(TC_BOOT);m.active=1;page(0,0x66);tc_gatt_command(&m,'W',p,k,1026,0);
    CHECK(count(TC_EV_ROM_COPY)==1);CHECK(f.writes==4);CHECK(f.last_mask[0]==0);CHECK(m.outcome==TC_INDETERMINATE);
    CHECK(k[0]==0);CHECK(k[1023]==0);
    setup(TC_BOOT);m.backend.rom_copy=copy_assumption;m.active=1;page(0,0x66);
    tc_gatt_command(&m,'W',p,k,1026,0);CHECK(m.reply_queued==TC_YES);CHECK(f.ram[0]==0x66);
    CHECK(p[0]==0x66);CHECK(p[1]==0x66);CHECK(p[1023]==0x66);
}
/* Catches End completeness checks, rollback on timer errors, wrong handoff kind. */
static void end_and_prepare_callbacks(void) {
    const tc_event *e;
    setup(TC_BOOT);call('E',0);CHECK(count(TC_EV_SCHEDULE)==0);CHECK(count(TC_EV_REPLY)==0);
    m.active=1;f.schedule_result=TC_NO;call('E',1040);
    CHECK(m.active==0);CHECK(m.reply_queued==TC_YES);CHECK(count(TC_EV_SCHEDULE)==2);
    e=nth(TC_EV_SCHEDULE,0);CHECK(e!=NULL && e->va==0x192Cu && e->argument==200);
    e=nth(TC_EV_SCHEDULE,1);CHECK(e!=NULL && e->va==0x20E2u && e->argument==400);
    CHECK(count(TC_EV_JUMP_REQUEST)==0);tc_deliver_callback(&m,0x20E2,0);
    CHECK(count(TC_EV_JUMP_REQUEST)==1);CHECK(count(TC_EV_RESET_REQUEST)==0);
    setup(TC_RUNTIME);m.active=1;call('E',0);e=nth(TC_EV_SCHEDULE,1);
    CHECK(e!=NULL && e->va==0x99C6u && e->argument==400);tc_deliver_callback(&m,0x99C6,0);
    CHECK(count(TC_EV_RESET_REQUEST)==1);CHECK(count(TC_EV_JUMP_REQUEST)==0);
    setup(TC_RUNTIME);control(1);call('U',15);CHECK(count(TC_EV_SCHEDULE)==2);CHECK(f.meta_writes==0);
    e=nth(TC_EV_SCHEDULE,1);CHECK(e!=NULL && e->va==0x9DFAu);
    f.stale_meta_reads=1;tc_deliver_callback(&m,0x9DFA,0);CHECK(f.meta_writes==5);CHECK(count(TC_EV_RESET_REQUEST)==1);
    setup(TC_BOOT);call('R',0);CHECK(f.reads==0);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_RUNTIME);call('R',0);CHECK(f.reads==0);CHECK(count(TC_EV_REPLY)==0);
}
/* Catches a sixth metadata read, initialized tail, result equated to final write failure. */
static void metadata_budget_and_unknown_tail(void) {
    unsigned i;
    setup(TC_BOOT);f.meta[4]=2;CHECK(tc_metadata_select(&m,2)==0);CHECK(f.meta_reads==1);CHECK(f.meta_writes==0);
    setup(TC_BOOT);f.stale_meta_reads=1;CHECK(tc_metadata_select(&m,2)==1);
    CHECK(f.meta_reads==5);CHECK(f.meta_writes==5);CHECK(f.meta[4]==2);
    for(i=0;i<8;++i) CHECK(f.last_mask[i]==255);
    for(i=8;i<256;++i) CHECK(f.last_mask[i]==0);
    setup(TC_RUNTIME);f.meta_mask[4]=0;CHECK(tc_metadata_select(&m,1)==-1);CHECK(f.meta_writes==0);
    setup(TC_BOOT);f.meta[0]=0;tc_metadata_initialize(&m);CHECK(f.meta[0]==16);CHECK(f.meta_reads==1);CHECK(f.meta_writes==1);
    setup(TC_RUNTIME);f.meta[1]=0;f.meta[4]=2;tc_metadata_initialize(&m);
    CHECK(f.meta[1]==16);CHECK(f.meta[4]==0);CHECK(f.meta_writes==1);CHECK(count(TC_EV_ELIGIBILITY_REFRESH)==1);
}
/* Catches gap threshold500, resetting OTA state, bad-frame invocation or buffer erasure. */
static void gatt_parser_branches(void) {
    uint8_t wire[1046];size_t n;
    setup(TC_BOOT);control(1);n=frame('S',p,15,wire);tc_receive(&m,TC_GATT,wire,4,100);
    tc_receive(&m,TC_GATT,wire+4,n-4,399);CHECK(m.active==1);CHECK(m.command_count==1);
    setup(TC_BOOT);m.active=1;tc_receive(&m,TC_GATT,wire,4,100);tc_receive(&m,TC_GATT,wire+4,n-4,400);
    CHECK(m.active==1);CHECK(m.command_count==0);
    setup(TC_BOOT);m.active=1;wire[n-1]^=1;tc_receive(&m,TC_GATT,wire,n,1);
    CHECK(m.active==1);CHECK(m.command_count==0);CHECK(m.gatt.state==0);
    setup(TC_BOOT);control(1);n=frame('S',p,15,wire);tc_receive(&m,TC_GATT,wire,n,1);
    n=frame('S',p,0,wire);tc_receive(&m,TC_GATT,wire,n,2);
    CHECK(m.active==0);CHECK(m.gatt.data[0]==255);CHECK(m.reply_length==0);
    setup(TC_BOOT);{const uint8_t too_large[]={0x55,0x7F,'S',4,17};tc_receive(&m,TC_GATT,too_large,5,1);}
    CHECK(m.gatt.state==0);CHECK(m.command_count==0);
}
/* Catches parsing W from the wrong native address alignment and fabricated TX checksums. */
static void wire_and_stall_boundaries(void) {
    uint8_t wire[1046];size_t n;const uint8_t eframe[]={0x55,0x7F,0x45,0,0,0x45};
    const uint8_t kframe[]={0x55,0x7F,0x4B,0,1,0x41,0x8D};
    setup(TC_BOOT);m.active=1;call('E',0);CHECK(m.reply_frame_length==6);CHECK(memcmp(m.reply_frame,eframe,6)==0);
    setup(TC_BOOT);uart('R',NULL,0,1);CHECK(m.reply_frame_length==7);CHECK(memcmp(m.reply_frame,kframe,7)==0);
    setup(TC_BOOT);m.active=1;page(0,0x51);n=frame('W',p,1026,wire);tc_receive(&m,TC_GATT,wire,n,1);
    CHECK(count(TC_EV_ROM_COPY)==0);CHECK(m.reply_command=='W');CHECK(m.reply_queued==TC_YES);
    setup(TC_BOOT);m.active=1;page(0,0x42);f.busy_write=1;call('W',1026);call('E',0);
    CHECK(m.outcome==TC_STALLED);CHECK(m.active==1);CHECK(count(TC_EV_REPLY)==0);CHECK(count(TC_EV_SCHEDULE)==0);
    setup(TC_BOOT);m.active=1;page(0,0x42);f.dropped_write=2;memset(f.ram_mask,255,sizeof(f.ram_mask));call('W',1026);
    CHECK(f.writes==4);CHECK(f.reads==65);CHECK(m.outcome==TC_SILENT);CHECK(m.active==1);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_BOOT);m.identity_mask[1]=0;uart('I',NULL,0,1);
    CHECK(m.uart_key_mask==0);CHECK(m.reply_mask[1]==0);CHECK(m.reply_frame_mask[20]==0);
    setup(TC_RUNTIME);uart('R',NULL,0,1);CHECK(m.outcome==TC_INDETERMINATE);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_BOOT);call(0xA0,0);CHECK(m.outcome==TC_INDETERMINATE);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_RUNTIME);call(0xA0,0);CHECK(m.outcome==TC_INDETERMINATE);CHECK(count(TC_EV_REPLY)==0);
    setup(TC_RUNTIME);m.general_auth=TC_YES;call('R',0);CHECK(m.outcome==TC_SILENT);CHECK(f.reads==0);
    setup(TC_RUNTIME);m.general_auth=TC_NO;call('R',0);CHECK(m.outcome==TC_INDETERMINATE);CHECK(f.reads==0);
    setup(TC_BOOT);m.uart_ready=TC_NO;uart('R',NULL,0,1);
    CHECK(m.outcome==TC_STALLED);CHECK(count(TC_EV_SCHEDULE)==0);CHECK(count(TC_EV_RESET_REQUEST)==0);
    setup(TC_BOOT);uart('G',NULL,0,1);CHECK(m.reply_command=='K');
    CHECK(nth(TC_EV_SCHEDULE,0)!=NULL && nth(TC_EV_SCHEDULE,0)->address==2);
    tc_deliver_callback(&m,0x24A8,2);CHECK(count(TC_EV_JUMP_REQUEST)==1);CHECK(count(TC_EV_RESET_REQUEST)==0);
}
/* I uses synthetic 0..11; sum=66+16+4=86, key=(86 XOR1)+2=89; S key=(89 XOR2)+3=94. */
static void uart_challenge_and_independence(void) {
    uint8_t challenge=89;
    setup(TC_BOOT);m.active=1;uart('I',NULL,0,1);
    CHECK(m.active==1);CHECK(m.uart_session==1);CHECK(m.uart_key==89);CHECK(m.reply_command=='I');CHECK(m.reply_length==15);
    CHECK(m.reply_data[12]==16);CHECK(m.reply_data[13]==4);CHECK(m.reply_data[14]==0);CHECK(count(TC_EV_STAY)==1);
    challenge=88;uart('S',&challenge,1,2);CHECK(m.uart_session==1);CHECK(m.uart_key==89);CHECK(m.outcome==TC_SILENT);
    challenge=89;uart('S',&challenge,1,3);CHECK(m.uart_session==2);CHECK(m.uart_key==94);CHECK(m.uart_sum==0);
    CHECK(m.reply_command=='K');CHECK(m.reply_data[0]==0x41);CHECK(f.meta[4]==2);CHECK(m.active==1);
    uart('U',NULL,0,4);CHECK(m.uart_session==2);CHECK(count(TC_EV_SCHEDULE)==0);CHECK(m.outcome==TC_SILENT);
}
/* Catches short-length rejection, sum rollback, dedup, R mislabeled flash read. */
static void uart_write_retry_short_and_reset(void) {
    unsigned i;uint8_t challenge=89,end=88;uint8_t badwire[]={0x55,0x7F,'S',0,1,0,0};
    setup(TC_BOOT);uart('I',NULL,0,1);uart('S',&challenge,1,2);
    page(0,0);for(i=0;i<1024;++i)p[i+2]=(uint8_t)(94+i);p[2]^=3;
    f.mismatch_read=1;uart('W',p,1026,3);CHECK(m.uart_sum==3);CHECK(m.uart_session==2);CHECK(m.outcome==TC_SILENT);
    f.mismatch_read=0;uart('W',p,1026,4);CHECK(m.uart_sum==6);CHECK(f.writes==8);CHECK(f.ram[0]==3);CHECK(m.reply_command=='K');
    uart('E',&end,1,5);CHECK(m.uart_session==3);CHECK(count(TC_EV_SCHEDULE)==1);
    setup(TC_BOOT);uart('I',NULL,0,1);uart('S',&challenge,1,2);
    page(0,0);for(i=0;i<1024;++i)p[i+2]=(uint8_t)(94+i);
    uart('Z',p,1026,3);uart('W',NULL,0,4);CHECK(f.writes==4);CHECK(m.reply_command=='K');CHECK(m.uart_sum==0);
    setup(TC_BOOT);uart('R',NULL,0,1);CHECK(m.reply_command=='K');CHECK(f.reads==0);CHECK(f.meta_reads==0);
    CHECK(nth(TC_EV_SCHEDULE,0)!=NULL && nth(TC_EV_SCHEDULE,0)->va==0x24A8u);
    CHECK(nth(TC_EV_SCHEDULE,0)!=NULL && nth(TC_EV_SCHEDULE,0)->address==4);
    tc_deliver_callback(&m,0x24A8,4);CHECK(count(TC_EV_RESET_REQUEST)==1);CHECK(count(TC_EV_JUMP_REQUEST)==0);
    setup(TC_BOOT);uart('I',NULL,0,1);uart('S',&challenge,1,2);
    tc_receive(&m,TC_UART,badwire,sizeof(badwire),3);CHECK(m.uart_session==2);CHECK(m.uart_key==94);
    uart('Z',NULL,0,3002);CHECK(m.uart_session==2);uart('Z',NULL,0,6002);
    CHECK(m.uart_session==0);CHECK(m.uart_key==0);CHECK(m.uart_sum==0);CHECK(m.uart.data[100]==0);
    setup(TC_BOOT);m.uart_session=2;m.uart_key=94;page(96,0);uart('W',p,1026,1);
    CHECK(f.writes==0);CHECK(m.uart_sum==0);CHECK(m.uart_session==2);CHECK(m.outcome==TC_SILENT);
    challenge=0;uart('E',&challenge,1,2);CHECK(m.uart_session==2);CHECK(m.outcome==TC_SILENT);CHECK(count(TC_EV_SCHEDULE)==0);
    setup(TC_BOOT);uart('I',NULL,0,1);challenge=89;uart('Z',&challenge,1,2);uart('S',NULL,0,3);
    CHECK(m.uart_session==2);CHECK(m.uart_key==94);CHECK(m.reply_command=='K');
}
static int read_payload(const char *root,const char *name,uint8_t *out,size_t n) {
    char path[1024];FILE *fp;size_t got;int tail;
    if(snprintf(path,sizeof(path),"%s/apk-analysis/tsl9-server-current/%s",root,name)<0)return 0;
    fp=fopen(path,"rb");if(!fp)return 0;got=fread(out,1,n,fp);tail=fgetc(fp);fclose(fp);return got==n && tail==EOF;
}
/* Captured bytes are inert data. Reverse order plus all 87 pages exercises native geometry. */
static void replay_87_pages(const char *root) {
    static uint8_t payload[76800];uint8_t wire[1046];unsigned image;
    for(image=0;image<2;++image) {
        size_t bytes=image==0?76800:12288;unsigned pages=image==0?75:12,j;
        const char *file=image==0?"TSL9-runtime-api-payload.bin":"TSL9-boot-api-payload.bin";
        CHECK(read_payload(root,file,payload,bytes));setup(image==0?TC_BOOT:TC_RUNTIME);
        if(image==1)m.backend.rom_copy=copy_assumption; /* Explicit forward-copy RAM assumption for Runtime ROM. */
        control(image==0?1:0);call('S',15);
        for(j=pages;j>0;--j) {
            size_t total,off;page(j-1,0);memcpy(p+2,payload+(j-1)*1024,1024);total=frame('W',p,1026,wire);
            for(off=0;off<total;off+=244)tc_receive(&m,TC_GATT,wire+off,total-off<244?total-off:244,pages-j+1);
            CHECK(m.reply_command=='W');CHECK(m.reply_queued==TC_YES);
        }
        CHECK(f.writes==pages*4);CHECK(f.reads==pages*256);CHECK(memcmp(f.ram,payload,bytes)==0);
        CHECK(m.active==1);call('E',0);CHECK(m.active==0);CHECK(m.reply_command=='E');
        printf("REPLAY %s pages=%u bytes=%zu writes256=%u read_words=%u exact_ram=%s\n",image==0?"runtime":"boot",pages,bytes,f.writes,f.reads,memcmp(f.ram,payload,bytes)==0?"yes":"no");
    }
}
static void run(const char *name,void (*test)(void)) {
    unsigned before=failures;++cases;test();printf("CASE %s %s\n",name,failures==before?"PASS":"FAIL");
}
int main(int argc,char **argv) {
    run("token_low8_aliases",token_aliases);run("S_original_echo_and_send_drop",start_echo_and_drop);
    run("W_bounds_sequence_failure",write_boundaries_and_failure);run("ROM_overlap_unknown",overlap_boundary);
    run("E_U_callback_contract",end_and_prepare_callbacks);run("metadata_5_writes_unknown_tail",metadata_budget_and_unknown_tail);
    run("GATT_parser_gap_checksum_stale",gatt_parser_branches);run("UART_challenge_independent",uart_challenge_and_independence);
    run("wire_native_alignment_stall_unknown",wire_and_stall_boundaries);
    run("UART_retry_short_R_reset_gap",uart_write_retry_short_and_reset);
    if(argc>1) { ++cases;replay_87_pages(argv[1]); }
    printf("RESULT cases=%u assertions=%u failures=%u execution=new-host-model-only\n",cases,assertions,failures);
    return failures?1:0;
}
