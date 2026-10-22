#include "callback.h"
#include "io.h"

/* ID2966 8614..888C. Numeric resident slots remain opaque, not SDK types.
 * This shared algorithm is authoritative; physical native placement/register
 * prefix is an additional unproved layer, not supplied by HOST frame hooks. */
#ifdef CB_HOST
#define CB_CONTEXT cb_host
#else
#define CB_CONTEXT cb_native
#endif
static void callback_logic(CB_CONTEXT *h,uint32_t context,uint32_t event_word)
{
    uint32_t v,target,type,length,base,address,capacity,difference,descriptor;
    cb_values *s=&CB_STATE(h);uint32_t *a=CB_ARGS(h);
#ifdef CB_HOST
    cb_host_frame_enter(h);if(CB_STOP(h))return;
#endif
    s->events=event_word;
    /* The sign test is LOW16 bit15; preserve the full event word for XOR. */
    if(event_word&0x8000u){
        s->lane=0x40000u;CB_READ(h,0x863cu,s->lane+0x6cu,32,target);CB_CALL(h,0x8640u,target,5,0u);s->record=a[0];
        if(a[0]){
            CB_READ(h,0x8646u,a[0],8,type);a[4]=type;
            if(type==0xb0u){CB_READ(h,0x8652u,a[0]+4u,8,length);a[1]=length;CB_READ(h,0x8656u,s->lane+0x12cu,32,target);a[0]+=8u;a[4]=type;CB_CALL(h,0x865cu,target,5,3u);}
            CB_READ(h,0x8662u,0x40068u,32,target);a[0]=s->record;CB_CALL(h,0x8666u,target,5,1u);
        }
        a[0]=s->events^0x8000u;goto done;
    }
    if(event_word&8u){CB_READ(h,0x8876u,0x401a4u,32,target);a[1]=0u;a[2]=0x19de0u;CB_CALL(h,0x8884u,target,5,6u);a[0]=s->events^8u;goto done;}
    CB_READ(h,0x868eu,s->gp+0x94u,8,v);s->task=context;
    if(v==context)s->lane=0u;
    else{CB_READ(h,0x8698u,s->gp+0x98u,8,v);a[0]=0u;s->lane=1u;if(v!=s->task)goto done;}
    address=s->gp+0x94u+(s->lane<<2);CB_READ(h,0x86aeu,address+2u,16,s->connection);
    if(s->events&1u){
        base=0x2000b18cu;s->record=base;s->rom_base=0x40000u;address=base+s->lane*1062u;
        a[1]=s->gp+128u;a[0]=s->connection;a[4]=s->lane<<2;
        CB_READ(h,0x86d4u,address+2u,16,s->span);CB_READ(h,0x86d8u,address+4u,16,s->cursor);CB_READ(h,0x86dcu,s->rom_base+0x13cu,32,target);CB_CALL(h,0x86e0u,target,5,3u);
        if(a[0]!=1u)goto clear_pending;
        s->span=(s->span-s->cursor)&0xffffu;s->cursor=(s->span&0x8000u)?(s->span|0xffff0000u):s->span;
        difference=s->cursor;
        if(difference==0u || (difference&0x8000u))goto clear_pending;
        CB_READ(h,0x86feu,s->rom_base+0xb8u,32,target);a[0]=s->connection;CB_CALL(h,0x8704u,target,5,1u);capacity=(a[0]-3u)&0xffffu;
        a[4]=s->lane<<3;descriptor=0x2000bdf8u+a[4]; /* resolved PCREL 870A */
        v=(s->cursor^0x80000000u)<(capacity^0x80000000u);
        CB_WRITE(h,v?0x8748u:0x871eu,descriptor+2u,16,v?s->span:capacity);
        s->lane*=1062u;s->record+=s->lane;CB_WRITE(h,0x8732u,s->record,8,10u);a[0]=s->task;a[1]=2u;CB_READ(h,0x873au,0x40050u,32,target);CB_CALL(h,0x873cu,target,5,3u);a[0]=s->events^1u;goto done;
clear_pending:
        s->lane*=1062u;s->record+=s->lane;CB_WRITE(h,0x8758u,s->record+2u,16,0u);a[0]=s->events^1u;goto done;
    }
    if(s->events&2u){
        s->span=s->lane*1062u;s->shared_base=0x2000b18cu;s->base_copy=s->shared_base;s->cursor=s->shared_base+s->span;CB_READ(h,0x877au,s->cursor,8,v);
        if(!v){CB_WRITE(h,0x8844u,s->cursor+2u,16,0u);a[0]=s->events^2u;goto done;}
        s->record=0x2000bdf8u+(s->lane<<3);s->rom_base=0x40000u;CB_READ(h,0x8792u,s->rom_base+0x128u,32,target);CB_READ(h,0x8796u,s->record+2u,16,a[2]);a[0]=s->connection;a[1]=27u;a[3]=0u;a[4]=0u;CB_CALL(h,0x87a2u,target,5,31u);
        CB_WRITE(h,0x87a4u,s->record+4u,32,a[0]);
        if(!a[0]){CB_READ(h,0x8834u,s->cursor,8,v);CB_WRITE(h,0x883au,s->cursor,8,v-1u);CB_READ(h,0x883eu,s->rom_base+0x58u,32,target);goto post_retry;}
        CB_READ(h,0x87a8u,s->cursor+4u,16,a[1]);CB_READ(h,0x87acu,s->rom_base+0x4cu,32,target);CB_READ(h,0x87b0u,s->record+2u,16,a[2]);s->span+=6u;a[1]+=s->span;a[1]+=s->shared_base;CB_CALL(h,0x87bau,target,5,6u);
        CB_READ(h,0x87bcu,s->rom_base+0x13cu,32,target);a[1]=s->gp+128u;a[0]=s->connection;CB_CALL(h,0x87c6u,target,5,3u);
        if(!(a[0]&1u))goto dispose;
        CB_READ(h,0x8800u,s->gp+0x2au,16,v);a[1]=s->record;a[2]=0u;CB_WRITE(h,0x8808u,s->record,16,v);CB_READ(h,0x880cu,s->rom_base+0xd4u,32,target);a[0]=s->connection;CB_CALL(h,0x8812u,target,5,7u);
        if(a[0])goto dispose;
        CB_READ(h,0x8816u,s->cursor+4u,16,v);CB_READ(h,0x881au,s->record+2u,16,length);a[4]=length;CB_WRITE(h,0x8824u,s->cursor+4u,16,v+length);a[0]=s->task;a[1]=1u;CB_READ(h,0x8828u,s->rom_base+0x50u,32,target);CB_CALL(h,0x882cu,target,5,3u);a[0]=s->events^2u;goto done;
dispose:
        s->span=0x40000u;CB_READ(h,0x87d0u,s->span+0x12cu,32,target);a[0]=s->record;a[1]=27u;CB_CALL(h,0x87d8u,target,5,3u);s->lane*=1062u;s->lane+=s->base_copy;CB_READ(h,0x87e4u,s->lane,8,v);CB_WRITE(h,0x87eau,s->lane,8,v-1u);CB_READ(h,0x87eeu,s->span+0x58u,32,target);
post_retry:
        a[0]=s->task;a[1]=2u;a[2]=2u;CB_CALL(h,0x87f8u,target,5,7u);a[0]=s->events^2u;goto done;
    }
    a[0]=0u;
    if(s->events&4u){CB_READ(h,0x8858u,0x401a8u,32,target);a[0]=s->connection;a[1]=12u;a[2]=24u;a[3]=0u;a[4]=200u;a[5]=s->task;CB_CALL(h,0x886au,target,6,63u);a[0]=s->events^4u;}
done:
#ifdef CB_HOST
    h->result=a[0];cb_host_frame_leave(h);
#endif
    return;
}
#ifdef CB_HOST
void tsl9_callback_host_8614(cb_host *h,uint32_t context,uint32_t event_word){h->args[0]=context;h->args[1]=event_word;callback_logic(h,context,event_word);}
#else
uint32_t tsl9_callback_native_8614(uint32_t context,uint32_t event_word,uint32_t ambient2,uint32_t ambient3,uint32_t ambient4,uint32_t ambient5,uint32_t ambient6,uint32_t ambient7){
    cb_native h;h.args[0]=context;h.args[1]=event_word;h.args[2]=ambient2;h.args[3]=ambient3;h.args[4]=ambient4;h.args[5]=ambient5;h.args[6]=ambient6;h.args[7]=ambient7;__asm__ volatile("mv %0,gp":"=r"(h.values.gp)::"memory");callback_logic(&h,context,event_word);return h.args[0];
}
#endif
