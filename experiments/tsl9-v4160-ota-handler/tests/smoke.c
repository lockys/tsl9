#include "ota_handler.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define RAM UINT32_C(0x20000000)
#define FLASH UINT32_C(0x08001000)
typedef struct fixture {oh_host host;uint8_t ram[16384],flash[4096];uint32_t payload,uid,uid_length,calls,quarters,schedules,replies,page,command,mask,copy,checks,readpairs,read_pending;int change_mode,change_s1,mismatch,halt_schedule;} fixture;
static unsigned checks,cases;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"check failed line %d\n",__LINE__);exit(1);}}while(0)
static uint8_t *byte(fixture *f,uint32_t address){if(address>=RAM && address-RAM<sizeof(f->ram))return &f->ram[address-RAM];if(address>=FLASH && address-FLASH<sizeof(f->flash))return &f->flash[address-FLASH];return NULL;}
static uint32_t load(fixture *f,uint32_t address,unsigned width){uint32_t value=0;unsigned i;for(i=0;i<width/8u;i++){uint8_t *b=byte(f,address+i);CHECK(b!=NULL);value|=(uint32_t)*b<<(8u*i);}return value;}
static void store(fixture *f,uint32_t address,unsigned width,uint32_t value){unsigned i;for(i=0;i<width/8u;i++){uint8_t *b=byte(f,address+i);CHECK(b!=NULL);*b=(uint8_t)(value>>(8u*i));}}
static oh_flow provide(void *user,oh_host *host,oh_effect *e)
{
    fixture *f=(fixture *)user;unsigned i;
    if(e->kind==OH_READ){
        if(!byte(f,e->address))return OH_UNKNOWN;
        e->value=load(f,e->address,e->width);e->value_known=1;
        if(e->source_site==0x9d10u){CHECK(!f->read_pending);f->read_pending=1;if(f->mismatch)e->value^=1u;}
        if(e->source_site==0x9d16u){CHECK(f->read_pending);f->read_pending=0;f->readpairs++;}
        return OH_CONTINUE;
    }
    if(e->kind==OH_WRITE){if(!byte(f,e->address))return OH_UNKNOWN;store(f,e->address,e->width,e->value);return OH_CONTINUE;}
    f->calls++;e->value_known=1;e->value=77u;
    if(e->callee==OH_UID_92F2){f->uid_length=e->args[1];e->value=f->uid;if(f->change_mode)store(f,f->payload,8,0);if(f->change_s1)host->values.flash=7u;}
    else if(e->callee==OH_QUARTER_9C0A){CHECK(e->args[0]==FLASH+256u*f->quarters);CHECK(host->values.buffer==256u*(f->quarters+1u));for(i=0;i<256u;i++)store(f,e->args[0]+i,8,load(f,e->args[1]+i,8));f->quarters++;}
    else if(e->callee==OH_COPY_SLOT_4C){for(i=0;i<1024u;i++)store(f,e->args[0]+i,8,load(f,e->args[1]+i,8));f->copy++;}
    else if(e->callee==OH_SCHEDULE_9124){CHECK(load(f,host->values.gp+0xa9u,8)==0);CHECK(e->args[1]==0 && e->args[3]==0);CHECK(e->args[2]==(f->schedules?400u:200u));f->schedules++;if(f->halt_schedule)return OH_HALT;}
    else{f->replies++;f->command=e->args[1];f->mask=e->defined_argument_mask;
        if(e->callee==OH_PAGE_REPLY_9B8E)f->page=e->args[2];
        if(e->args[1]==0x57u){CHECK(e->args[4]==1024u);CHECK(e->args[5]==(f->mismatch?0u:1024u));CHECK(e->defined_argument_mask==63u);}
        if(e->args[1]==0x53u){CHECK(e->args[3]==2u);CHECK(load(f,e->args[2],8)==2u);CHECK(load(f,e->args[2]+1u,8)==1u);}
        if(e->args[1]==0x45u)CHECK(e->args[2]==0 && e->args[3]==0);
    }
    return OH_CONTINUE;
}
static void init(fixture *f){memset(f,0,sizeof(*f));f->payload=RAM+0x1002u;f->host.values.gp=RAM+0x100u;f->host.values.sp=RAM+0x3000u;f->host.values.return_address=0x12345679u;f->host.provider=provide;f->host.user=f;f->host.diagnostic_budget=4000u;store(f,f->host.values.gp+0xa9u,8,1u);cases++;}
static void run(fixture *f,uint32_t command,uint32_t length){tsl9_ota_handler_host_9c4a(&f->host,0x1234u,command,f->payload,length);}
int main(void)
{
    fixture f;unsigned i;
    init(&f);run(&f,0x155u,0);CHECK(f.calls==0 && f.host.result==0x1234u && f.host.result_known);
    init(&f);f.uid=1;run(&f,'U',0);CHECK(f.uid_length==255u && f.replies==0 && load(&f,f.host.values.gp+0xa9u,8)==0);
    init(&f);store(&f,f.payload,8,1);run(&f,'U',0);CHECK(f.uid_length==255u && f.schedules==2 && f.replies==1 && f.command=='U');
    init(&f);store(&f,f.payload,8,2);f.change_mode=1;f.change_s1=1;run(&f,'S',1);CHECK(f.replies==1 && load(&f,f.host.values.gp+0xa9u,8)==7u);
    init(&f);store(&f,f.payload,8,255);store(&f,f.payload+1u,8,255);run(&f,'R',16);CHECK(f.replies==1 && f.page==65535u);
    init(&f);run(&f,'E',15);CHECK(f.schedules==2 && f.replies==1 && f.command=='E');
    init(&f);for(i=0;i<1024u;i++)store(&f,f.payload+2u+i,8,i);run(&f,'W',1026);CHECK(f.quarters==4 && f.readpairs==256 && f.replies==1 && f.page==0);
    init(&f);f.mismatch=1;run(&f,'W',1026);CHECK(f.quarters==4 && f.readpairs==1 && f.replies==1 && f.command=='W');
    init(&f);f.payload=0x30000000u;run(&f,'S',15);CHECK(f.host.flow==OH_UNKNOWN && f.calls==0);
    init(&f);store(&f,f.payload,8,1);f.halt_schedule=1;run(&f,'U',15);CHECK(f.host.flow==OH_HALT && f.schedules==1 && f.replies==0);
    printf("{\"groups\":1,\"cases\":%u,\"checks\":%u}\n",cases,checks);return 0;
}
