#include "ota_handler.h"
#include "io.h"

/* Shared readable source algorithm. Source sites annotate effects only; the
 * native ports discard them rather than retain trace metadata in firmware. */
static void handler(oh_port *h,uint32_t context,uint32_t command,uint32_t payload,uint32_t length)
{
    oh_values *s=&h->values;uint32_t *a=h->args;uint32_t first,second,mode,offset,flash_word,source_word,target;
    s->context=context;s->buffer=payload;
    if(command==0x57u){
        OH_READ(h,0x9c9c,OH_GP(h)+0xa9u,8,first);
        if(!first || length!=1026u)return;
        OH_READ(h,0x9caa,payload,8,first);OH_READ(h,0x9cae,payload+1u,8,second);
        s->page=(first<<8)|second;s->flash=(UINT32_C(0x20004)+s->page)<<10;
        if(s->flash+UINT32_C(0xf7fff000)>UINT32_C(0x6f00))return;
        s->flash=OH_FLASH_BASE(s->flash);
        first=payload+2u;second=first&3u;s->source=first-second;
        if(second){
            OH_READ(h,0x9ce4,UINT32_C(0x4004c),32,target);
            a[0]=s->source;a[1]=first;a[2]=1024u;
            OH_CALL(h,0x9cec,OH_COPY_SLOT_4C,target,7u);
        }
        s->buffer=0;s->limit=1024u;
        do{
            a[1]=s->source+s->buffer;a[0]=s->flash+s->buffer;s->buffer+=256u;
            OH_CALL(h,0x9d00,OH_QUARTER_9C0A,0x9c0au,3u);
            s->buffer=OH_QUARTER_OFFSET(s->buffer);
        }while(s->buffer!=s->limit);
        for(offset=0;offset!=1024u;offset+=4u){
            OH_READ(h,0x9d10,s->flash+offset,32,flash_word);
            OH_READ(h,0x9d16,s->source+offset,32,source_word);
            if(flash_word!=source_word){
                a[0]=s->context;a[1]=0x57u;a[2]=255u;a[3]=source_word;a[4]=1024u;a[5]=offset;
                goto small_reply;
            }
        }
        a[0]=s->context;a[1]=0x57u;a[2]=s->page;a[3]=source_word;a[4]=1024u;a[5]=offset;
        goto page_reply;
    }
    if(command==0x55u){
        a[1]=(length-1u)&255u;a[0]=payload+1u;
        OH_WRITE(h,0x9d36,OH_GP(h)+0xa9u,8,0);
        OH_CALL(h,0x9d3a,OH_UID_92F2,0x92f2u,3u);OH_REQUIRE_A0(h);
        if(a[0])return;
        OH_READ(h,0x9d40,s->buffer,8,mode);
        if(mode==1u){
            a[0]=OH_CB_8E18();a[1]=0;a[2]=200u;a[3]=0;
            OH_CALL(h,0x9d5a,OH_SCHEDULE_9124,0x9124u,15u);
            a[0]=OH_CB_9EE0();a[1]=0;a[2]=400u;a[3]=0;
            OH_CALL(h,0x9d6e,OH_SCHEDULE_9124,0x9124u,15u);
        }
        a[0]=s->context;a[1]=0x55u;a[2]=1u;
        goto small_reply;
    }
    if(command==0x53u){
        OH_READ(h,0x9d80,payload,8,mode);
        a[1]=(length-1u)&255u;s->flash=1u;a[0]=payload+1u;
        OH_WRITE(h,0x9d92,OH_STACK(h,12u),8,mode);
        OH_WRITE(h,0x9d96,OH_STACK(h,13u),8,s->flash);
        OH_CALL(h,0x9d9a,OH_UID_92F2,0x92f2u,3u);OH_REQUIRE_A0(h);
        first=a[0];
        if(!first){OH_READ(h,0x9da0,s->buffer,8,first);}
        if(!first){OH_WRITE(h,0x9da6,OH_GP(h)+0xa9u,8,s->flash);}
        else{
            OH_WRITE(h,0x9dba,OH_GP(h)+0xa9u,8,0);
            OH_WRITE(h,0x9dc0,OH_STACK(h,12u),8,255u);
        }
        a[0]=s->context;a[1]=0x53u;a[2]=OH_STACK(h,12u);a[3]=2u;
        goto packet_reply;
    }
    if(command==0x52u){
        OH_READ(h,0x9dc6,OH_GP(h)+0xa9u,8,first);
        if(!first || length!=16u)return;
        a[0]=payload+2u;a[1]=14u;
        OH_CALL(h,0x9dda,OH_UID_92F2,0x92f2u,3u);OH_REQUIRE_A0(h);
        if(a[0])return;
        OH_READ(h,0x9de2,s->buffer,8,first);OH_READ(h,0x9de6,s->buffer+1u,8,second);
        a[0]=s->context;a[1]=0x52u;a[2]=second|(first<<8);
        goto page_reply;
    }
    if(command==0x45u){
        OH_READ(h,0x9df8,OH_GP(h)+0xa9u,8,first);
        if(!first || length!=15u)return;
        OH_READ(h,0x9e06,payload,8,mode);if(mode)return;
        a[0]=payload+1u;a[1]=14u;
        OH_CALL(h,0x9e14,OH_UID_92F2,0x92f2u,3u);OH_REQUIRE_A0(h);
        if(a[0])return;
        a[0]=OH_CB_8E18();a[1]=0;a[2]=200u;a[3]=0;
        OH_WRITE(h,0x9e2c,OH_GP(h)+0xa9u,8,0);
        OH_CALL(h,0x9e30,OH_SCHEDULE_9124,0x9124u,15u);
        a[0]=OH_CB_99E8();a[1]=0;a[2]=400u;a[3]=0;
        OH_CALL(h,0x9e44,OH_SCHEDULE_9124,0x9124u,15u);
        a[0]=s->context;a[1]=0x45u;a[2]=0;a[3]=0;
        goto packet_reply;
    }
    return;
small_reply:
    OH_CALL(h,0x9d7a,OH_SMALL_REPLY_13F66,0x13f66u,command==0x57u?63u:7u);return;
packet_reply:
    OH_CALL(h,0x9db4,OH_PACKET_REPLY_13E98,0x13e98u,15u);return;
page_reply:
    OH_CALL(h,0x9df4,OH_PAGE_REPLY_9B8E,0x9b8eu,command==0x57u?63u:7u);
}

#ifdef OH_HOST
void tsl9_ota_handler_host_9c4a(oh_host *h,uint32_t context,uint32_t command,uint32_t payload,uint32_t length)
{
    h->flow=OH_CONTINUE;h->effects=0;h->result=context;h->result_known=1;h->return_value_known=1;
    h->args[0]=context;h->args[1]=command;h->args[2]=payload;h->args[3]=length;
    oh_host_enter(h);if(OH_STOP(h))return;
    handler(h,context,command,payload,length);if(OH_STOP(h))return;
    h->result=h->args[0];h->result_known=h->return_value_known;oh_host_leave(h);
}
#else
uint32_t tsl9_ota_handler_native_9c4a(uint32_t context,uint32_t command,uint32_t payload,uint32_t length,
    uint32_t ambient4,uint32_t ambient5,uint32_t ambient6,uint32_t ambient7)
{
#ifdef __cplusplus
    alignas(4) volatile uint8_t response[4];
#else
    _Alignas(4) volatile uint8_t response[4];
#endif
    oh_port h;h.response=response;
    h.args[0]=context;h.args[1]=command;h.args[2]=payload;h.args[3]=length;
    h.args[4]=ambient4;h.args[5]=ambient5;h.args[6]=ambient6;h.args[7]=ambient7;
    handler(&h,context,command,payload,length);return h.args[0];
}
#endif
