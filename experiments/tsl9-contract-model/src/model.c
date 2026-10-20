#include "tsl9_contract.h"
#include <string.h>

static void event(tc_model *m,tc_event_kind kind,uint32_t va,uint32_t address,
                  uint32_t argument,size_t length,tc_truth result) {
    tc_event e;e.kind=kind;e.va=va;e.address=address;e.argument=argument;e.length=length;e.result=result;
    if(m->backend.event)m->backend.event(m->backend.context,&e);
}
static void begin(tc_model *m) {
    m->outcome=TC_SILENT;m->reply_command=0;m->reply_length=0;
    m->reply_frame_length=0;m->reply_queued=TC_NO;
}
static tc_truth equal(const uint8_t *a,const uint8_t *am,const uint8_t *b,const uint8_t *bm,size_t n) {
    size_t i;tc_truth result=TC_YES;
    for(i=0;i<n;++i) {
        uint8_t common=(uint8_t)(am[i]&bm[i]);
        if(((a[i]^b[i])&common)!=0)return TC_NO;
        if(common!=255)result=TC_UNKNOWN;
    }
    return result;
}
static tc_truth equals_byte(uint8_t a,uint8_t mask,uint8_t b) {
    const uint8_t full=255;return equal(&a,&mask,&b,&full,1);
}
static void read_bytes(tc_model *m,uint32_t address,uint8_t *d,uint8_t *mask,size_t n,uint32_t va) {
    memset(d,0,n);memset(mask,0,n);
    if(m->backend.read)m->backend.read(m->backend.context,address,d,mask,n);
    event(m,TC_EV_READ,va,address,0,n,TC_UNKNOWN);
}
static tc_flow program(tc_model *m,uint32_t address,const uint8_t *d,const uint8_t *mask) {
    tc_flow flow=TC_FLOW_UNKNOWN;
    /* Native wrapper masks CSR0x800 by136, writes status49, erases and programs256;
       there is no checked Flash-status result. Only helper return/stall is modeled. */
    if(m->backend.program256)flow=m->backend.program256(m->backend.context,address,d,mask);
    event(m,TC_EV_PROGRAM,m->image==TC_BOOT?0x20E6u:0x9B6Cu,address,(uint32_t)flow,256,TC_UNKNOWN);
    if(flow==TC_BUSY) {m->outcome=TC_STALLED;m->stalled=1;}
    else if(flow==TC_TRANSFER){m->transferred=1;m->outcome=TC_TRANSFERRED;}
    else if(flow==TC_FLOW_UNKNOWN)m->outcome=TC_INDETERMINATE;
    return flow;
}
static int schedule(tc_model *m,uint32_t callback,uint32_t argument,uint32_t delay,tc_transport transport) {
    tc_truth accepted=TC_UNKNOWN;
    uint32_t ticks=transport==TC_GATT?delay*1000u/625u:delay;
    if(m->backend.schedule)accepted=m->backend.schedule(m->backend.context,callback,argument,ticks);
    /* argument field is original delay; address is stored callback argument/event. */
    event(m,TC_EV_SCHEDULE,callback,argument,delay,ticks,accepted);
    return !m->interpretation_halted&&!m->transferred;
}
static void reply_frame(tc_model *m) {
    size_t i;uint8_t sum=(uint8_t)(m->reply_command+(m->reply_length>>8)+(m->reply_length&255u));
    uint8_t known=255;
    m->reply_frame[0]=0x55;m->reply_frame[1]=0x7F;m->reply_frame[2]=m->reply_command;
    m->reply_frame[3]=(uint8_t)(m->reply_length>>8);m->reply_frame[4]=(uint8_t)m->reply_length;
    memset(m->reply_frame_mask,255,5);
    for(i=0;i<m->reply_length;++i) {
        m->reply_frame[i+5]=m->reply_data[i];m->reply_frame_mask[i+5]=m->reply_mask[i];
        sum=(uint8_t)(sum+m->reply_data[i]);if(m->reply_mask[i]!=255)known=0;
    }
    m->reply_frame[m->reply_length+5]=sum;m->reply_frame_mask[m->reply_length+5]=known;
    m->reply_frame_length=m->reply_length+6;
}
static int reply(tc_model *m,tc_transport transport,uint8_t command,
                 const uint8_t *d,const uint8_t *mask,size_t n) {
    tc_truth queued=TC_YES;
    m->reply_command=command;m->reply_length=n;
    if(n) { memcpy(m->reply_data,d,n);memcpy(m->reply_mask,mask,n); }
    reply_frame(m);
    if(transport==TC_GATT) {
        if(n && m->alloc_ok!=TC_YES)queued=m->alloc_ok;
        else if(n>1039)queued=TC_NO;
        else queued=m->link_ok;
    } else queued=m->uart_ready;
    if(transport==TC_UART && !m->backend.uart_wrapper && queued==TC_YES){
        /* The completed 23E8 wrapper shares the RX checksum at 2000999B.
           uart_ready is a declared scalar-return contract; partial polling
           prefixes and live MMIO require the separate BS UART body. */
        m->uart.sum=m->reply_frame[n+5];m->uart.sum_mask=m->reply_frame_mask[n+5];
    }
    m->reply_queued=queued;m->outcome=queued==TC_UNKNOWN?TC_INDETERMINATE:TC_REPLY;
    if(transport==TC_GATT && m->backend.gatt_wrapper) {
        tc_flow flow=m->backend.gatt_wrapper(m->backend.context,m);
        if(flow!=TC_RETURNED) {
            if(flow==TC_TRANSFER){m->transferred=1;m->outcome=TC_TRANSFERRED;}
            else {m->interpretation_halted=1;m->outcome=TC_INDETERMINATE;}
            return 0;
        }
        queued=m->reply_queued;
        m->outcome=queued==TC_UNKNOWN?TC_INDETERMINATE:TC_REPLY;
    }
    if(transport==TC_UART && m->backend.uart_wrapper){
        tc_flow flow=m->backend.uart_wrapper(m->backend.context,m);
        if(flow!=TC_RETURNED){if(flow==TC_TRANSFER){m->transferred=1;m->outcome=TC_TRANSFERRED;}else {m->interpretation_halted=1;m->outcome=TC_INDETERMINATE;}return 0;}
        queued=m->reply_queued;m->outcome=queued==TC_UNKNOWN?TC_INDETERMINATE:TC_REPLY;
    }
    event(m,TC_EV_REPLY,transport==TC_GATT?(m->image==TC_BOOT?0x1848u:0x8CFAu):0x23E8u,
          command,0,n,queued);
    if(transport==TC_UART && queued!=TC_YES) {
        /* uart_ready NO denotes status-bit polling that has not returned. */
        m->outcome=queued==TC_NO?TC_STALLED:TC_INDETERMINATE;
        if(queued==TC_NO)m->stalled=1;
        return 0;
    }
    return 1;
}
static int ack_uart(tc_model *m) {
    const uint8_t data=0x41,mask=255;return reply(m,TC_UART,'K',&data,&mask,1);
}
int tc_gatt_reply(tc_model *m,uint8_t command,const uint8_t *d,const uint8_t *mask,size_t n) {
    if(m->transferred){m->outcome=TC_TRANSFERRED;return 0;}
    if(m->interpretation_halted){m->outcome=TC_INDETERMINATE;return 0;}
    if(n>1040){m->outcome=TC_INDETERMINATE;return 0;}
    begin(m);return reply(m,TC_GATT,command,d,mask,n);
}
void tc_init(tc_model *m,tc_image image,const tc_backend *b) {
    memset(m,0,sizeof(*m));m->image=image;if(b)m->backend=*b;
    m->alloc_ok=TC_UNKNOWN;m->link_ok=TC_UNKNOWN;m->uart_ready=TC_UNKNOWN;m->general_auth=TC_UNKNOWN;
    m->active_mask=255;m->uart_session_mask=255;m->uart_key_mask=255;m->uart_sum_mask=255;
    m->gatt.sum_mask=255;m->uart.sum_mask=255;
    memset(m->gatt.mask,255,sizeof(m->gatt.mask));memset(m->uart.mask,255,sizeof(m->uart.mask));
    m->metadata_result=-1;begin(m);
}
void tc_identity(tc_model *m,const uint8_t *d,const uint8_t *mask) {
    memcpy(m->identity,d,14);memcpy(m->identity_mask,mask,14);
}
int tc_resume_activation(tc_model*m){if(!m->transferred)return 0;m->transferred=0;m->outcome=m->interpretation_halted?TC_INDETERMINATE:m->stalled?TC_STALLED:TC_SILENT;return 1;}
static tc_flow metadata_write(tc_model *m,const uint8_t *record,const uint8_t *record_mask) {
    uint8_t bytes[256],mask[256];
    /* Zero is only a storage placeholder. The 248-byte mask remains unknown. */
    memset(bytes,0,sizeof(bytes));memset(mask,0,sizeof(mask));
    memcpy(bytes,record,8);memcpy(mask,record_mask,8);
    return program(m,0x08077B00u,bytes,mask);
}
int tc_metadata_select(tc_model *m,uint8_t selector) {
    unsigned i;uint8_t bytes[8],mask[8];
    if(m->transferred){m->outcome=TC_TRANSFERRED;m->metadata_result=-3;return -3;}
    if(m->stalled) {m->outcome=TC_STALLED;return -2;}
    for(i=0;i<5;++i) {
        tc_truth same;
        read_bytes(m,0x08077B00u,bytes,mask,8,m->image==TC_BOOT?0x214Eu:0x9D9Eu);
        same=equals_byte(bytes[4],mask[4],selector);
        if(same==TC_YES) { m->metadata_result=0;return 0; }
        if(same==TC_UNKNOWN) { m->outcome=TC_INDETERMINATE;m->metadata_result=-1;return -1; }
        bytes[4]=selector;mask[4]=255;
        if(metadata_write(m,bytes,mask)!=TC_RETURNED) {
            m->metadata_result=m->transferred?-3:m->outcome==TC_STALLED?-2:-1;return m->metadata_result;
        }
    }
    /* No sixth read. This does not determine whether the fifth write persisted. */
    m->metadata_result=1;return 1;
}
void tc_metadata_initialize(tc_model *m) {
    uint8_t d[8],mask[8];tc_truth a,b;
    if(m->transferred){m->outcome=TC_TRANSFERRED;return;}
    if(m->stalled) {m->outcome=TC_STALLED;return;}
    begin(m);m->active=0;m->active_mask=255;
    read_bytes(m,0x08077B00u,d,mask,8,m->image==TC_BOOT?0x214Eu:0x9D9Eu);
    if(m->image==TC_BOOT) {
        a=equals_byte(d[0],mask[0],16);
        if(a==TC_UNKNOWN) {m->outcome=TC_INDETERMINATE;return;}
        if(a==TC_NO) {d[0]=16;mask[0]=255;(void)metadata_write(m,d,mask);}
    } else {
        a=equals_byte(d[1],mask[1],16);b=equals_byte(d[4],mask[4],0);
        if(a==TC_NO || b==TC_NO) {
            d[1]=16;d[4]=0;mask[1]=255;mask[4]=255;
            if(metadata_write(m,d,mask)!=TC_RETURNED)return;
        } else if(a==TC_UNKNOWN || b==TC_UNKNOWN) {m->outcome=TC_INDETERMINATE;return;}
        event(m,TC_EV_ELIGIBILITY_REFRESH,0x935Cu,0,0,0,TC_UNKNOWN);
    }
}
static tc_truth token(tc_model *m,const uint8_t *d,const uint8_t *mask,uint16_t n) {
    if((uint8_t)(n-1)!=14)return TC_NO;
    return equal(d+1,mask+1,m->identity,m->identity_mask,14);
}
static tc_truth write_page(tc_model *m,uint32_t address,const uint8_t *d,const uint8_t *mask,
                           tc_transport transport) {
    unsigned off;uint8_t read[4],read_mask[4];tc_truth same;
    uint32_t va=transport==TC_UART?0x29BEu:(m->image==TC_BOOT?0x228Au:0x9C76u);
    for(off=0;off<1024;off+=256) if(program(m,address+off,d+off,mask+off)!=TC_RETURNED)return TC_UNKNOWN;
    for(off=0;off<1024;off+=4) {
        read_bytes(m,address+off,read,read_mask,4,va);
        same=equal(d+off,mask+off,read,read_mask,4);
        if(same==TC_NO)return TC_NO;
        if(same==TC_UNKNOWN) {m->outcome=TC_INDETERMINATE;return TC_UNKNOWN;}
    }
    return TC_YES;
}
void tc_gatt_command(tc_model *m,uint8_t command,uint8_t *d,uint8_t *mask,uint16_t n,unsigned alignment) {
    tc_truth good,target;
    if(m->transferred){m->outcome=TC_TRANSFERRED;return;}
    if(m->interpretation_halted){m->outcome=TC_INDETERMINATE;return;}
    if(m->stalled) {m->outcome=TC_STALLED;return;}
    begin(m);++m->command_count;
    if(n>1040) {m->outcome=TC_INDETERMINATE;return;} /* Impossible through observed parser. */
    if(command=='U') {
        uint8_t result=(uint8_t)(m->image==TC_RUNTIME),full=255;
        m->active=0;m->active_mask=255;good=token(m,d,mask,n);
        if(good==TC_NO)return;
        if(good==TC_UNKNOWN) {m->outcome=TC_INDETERMINATE;return;}
        if(m->image==TC_RUNTIME) {
            target=equals_byte(d[0],mask[0],1);
            if(target==TC_YES) {if(!schedule(m,0x8E12,0,200,TC_GATT))return;if(!schedule(m,0x9DFA,0,400,TC_GATT))return;}
            else if(target==TC_UNKNOWN) {m->outcome=TC_INDETERMINATE;return;}
        }
        (void)reply(m,TC_GATT,'U',&result,&full,1);
    } else if(command=='S') {
        good=token(m,d,mask,n);target=equals_byte(d[0],mask[0],m->image==TC_BOOT?1:0);
        if(good==TC_NO || target==TC_NO) {m->active=0;m->active_mask=255;d[0]=255;mask[0]=255;}
        else if(good==TC_UNKNOWN || target==TC_UNKNOWN) {m->active_mask=0;m->outcome=TC_INDETERMINATE;return;}
        else {
            m->active=1;m->active_mask=255;
            if(m->image==TC_BOOT) {
                int meta;
                event(m,TC_EV_CANCEL_STARTUP,0x250Eu,2,0,0,TC_UNKNOWN);
                if(m->interpretation_halted){m->outcome=TC_INDETERMINATE;return;}
                meta=tc_metadata_select(m,2);if(meta<0)return;
            }
        }
        (void)reply(m,TC_GATT,'S',d,mask,n);
    } else if(command=='W') {
        uint16_t page;uint32_t address;const uint8_t *source=d+2,*source_mask=mask+2;
        uint8_t aligned[1024],aligned_mask[1024];
        if(m->active_mask!=255) {m->outcome=TC_INDETERMINATE;return;}
        if(!m->active || n!=1026)return;
        if(mask[0]!=255 || mask[1]!=255) {m->outcome=TC_INDETERMINATE;return;}
        page=(uint16_t)((uint16_t)d[0]*256u+d[1]);
        if(page>(m->image==TC_BOOT?95u:27u))return;
        address=(m->image==TC_BOOT?0x08008000u:0x08001000u)+(uint32_t)page*1024u;
        if(((alignment+2)&3u)!=0) {
            unsigned i,misalignment=(alignment+2)&3u;
            int delta=2-(int)misalignment;
            memset(aligned,0,sizeof(aligned));memset(aligned_mask,0,sizeof(aligned_mask));
            if(m->backend.rom_copy)m->backend.rom_copy(m->backend.context,aligned,aligned_mask,source,source_mask,1024);
            event(m,TC_EV_ROM_COPY,0x4004Cu,0,(alignment+2)&3u,1024,m->backend.rom_copy?TC_YES:TC_UNKNOWN);
            /* Preserve native lower-address overlap effects in the retained RX buffer.
               A prefix before payload[0] is outside this API's represented storage. */
            for(i=0;i<1024;++i) {
                int index=(int)i+delta;
                if(index>=0) {d[index]=aligned[i];mask[index]=aligned_mask[i];}
            }
            source=aligned;source_mask=aligned_mask;
        }
        if(write_page(m,address,source,source_mask,TC_GATT)==TC_YES)(void)reply(m,TC_GATT,'W',NULL,NULL,0);
    } else if(command=='E') {
        if(m->active_mask!=255) {m->outcome=TC_INDETERMINATE;return;}
        if(!m->active)return;
        m->active=0;m->active_mask=255;
        if(!schedule(m,m->image==TC_BOOT?0x192Cu:0x8E12u,0,200,TC_GATT))return;
        if(!schedule(m,m->image==TC_BOOT?0x20E2u:0x99C6u,0,400,TC_GATT))return;
        (void)reply(m,TC_GATT,'E',NULL,NULL,0);
    } else if(command=='R') {
        /* R's observed return is conditional on all general link/auth gates passing.
           Auth failure effects live outside the OTA core; never invent a Flash read. */
        if(m->image==TC_RUNTIME && m->general_auth!=TC_YES)m->outcome=TC_INDETERMINATE;
    } else m->outcome=TC_INDETERMINATE; /* Unimplemented native commands are not silent claims. */
}
void tc_uart_command(tc_model *m) {
    tc_parser *p=&m->uart;uint8_t *d=p->data,*mask=p->mask;tc_truth good;
    if(m->transferred){m->outcome=TC_TRANSFERRED;return;}
    if(m->interpretation_halted){m->outcome=TC_INDETERMINATE;return;}
    begin(m);++m->command_count;
    if(p->command=='I') {
        uint8_t record[8],record_mask[8],data[15],dm[15],sum=0,sum_mask=255;unsigned i;
        if(!m->stay) {m->stay=1;event(m,TC_EV_STAY,0x251Eu,0,0,0,TC_UNKNOWN);}
        read_bytes(m,0x08077B00u,record,record_mask,8,0x214E);
        memcpy(data,m->identity,12);memcpy(dm,m->identity_mask,12);
        data[12]=record[1];dm[12]=record_mask[1];data[13]=4;data[14]=0;dm[13]=255;dm[14]=255;
        for(i=0;i<15;++i) {sum=(uint8_t)(sum+data[i]);if(dm[i]!=255)sum_mask=0;}
        m->uart_key=sum;m->uart_key_mask=sum_mask;
        if(!reply(m,TC_UART,'I',data,dm,15))return;
        /* Native281A/281E/2824 reread the shared key and caller payload
           after23E8 returns. UART/HAL can have changed either live source. */
        m->uart_key=(uint8_t)((m->uart_key^m->reply_data[1])+m->reply_data[2]);
        m->uart_key_mask=(m->uart_key_mask==255 && m->reply_mask[1]==255 && m->reply_mask[2]==255)?255:0;
        m->uart_session=1;m->uart_session_mask=255;
    } else if(p->command=='S') {
        uint8_t full=255;
        if(m->uart_session_mask!=255) {m->outcome=TC_INDETERMINATE;return;}
        if(m->uart_session!=1)return;
        good=equal(d,mask,&m->uart_key,&m->uart_key_mask,1);
        if(good==TC_NO)return;
        if(good==TC_UNKNOWN) {m->uart_session_mask=0;m->outcome=TC_INDETERMINATE;return;}
        m->uart_session=2;m->uart_sum=0;m->uart_sum_mask=full;
        m->uart_key=(uint8_t)((m->uart_key^m->identity[2])+m->identity[3]);
        m->uart_key_mask=(m->uart_key_mask==255 && m->identity_mask[2]==255 && m->identity_mask[3]==255)?255:0;
        if(tc_metadata_select(m,2)<0)return;
        (void)ack_uart(m);
    } else if(p->command=='W') {
        uint16_t page;uint32_t address;unsigned i;uint8_t sum=m->uart_sum,sum_mask=m->uart_sum_mask;
        if(m->uart_session_mask!=255) {m->outcome=TC_INDETERMINATE;return;}
        if(m->uart_session!=2)return;
        if(mask[0]!=255 || mask[1]!=255) {m->outcome=TC_INDETERMINATE;return;}
        page=(uint16_t)((uint16_t)d[0]*256u+d[1]);if(page>95)return;
        address=0x08008000u+(uint32_t)page*1024u;
        /* Forward overlap: input buffer[i+2], output buffer[i]; retains bytes1024/1025. */
        for(i=0;i<1024;++i) {
            d[i]=(uint8_t)(d[i+2]^(uint8_t)(m->uart_key+i));
            mask[i]=m->uart_key_mask==255?mask[i+2]:0;
            sum=(uint8_t)(sum+d[i]);if(mask[i]!=255)sum_mask=0;
        }
        m->uart_sum=sum;m->uart_sum_mask=sum_mask;
        if(write_page(m,address,d,mask,TC_UART)==TC_YES)(void)ack_uart(m);
    } else if(p->command=='E') {
        uint8_t expected=(uint8_t)(m->uart_key^m->uart_sum);
        uint8_t expected_mask=(uint8_t)(m->uart_key_mask&m->uart_sum_mask);
        if(m->uart_session_mask!=255) {m->outcome=TC_INDETERMINATE;return;}
        if(m->uart_session!=2)return;
        good=equal(d,mask,&expected,&expected_mask,1);
        if(good==TC_NO)return;
        if(good==TC_UNKNOWN) {m->uart_session_mask=0;m->outcome=TC_INDETERMINATE;return;}
        m->uart_session=3;
        if(ack_uart(m))(void)schedule(m,0x24A8,2,48,TC_UART);
    } else if(p->command=='G' || p->command=='R') {
        if(ack_uart(m))(void)schedule(m,0x24A8,p->command=='G'?2u:4u,48,TC_UART);
    }
}
void tc_receive(tc_model *m,tc_transport transport,const uint8_t *bytes,size_t n,uint32_t clock) {
    tc_parser *p=transport==TC_GATT?&m->gatt:&m->uart;size_t i;uint16_t limit=transport==TC_GATT?1040:1026;
    uint32_t gap=transport==TC_GATT?299u:2999u;
    if(m->transferred){m->outcome=TC_TRANSFERRED;return;}
    if(m->stalled) {m->outcome=TC_STALLED;return;}
    if(transport==TC_UART && m->image!=TC_BOOT) {m->outcome=TC_INDETERMINATE;return;}
    if(p->clock_set && (uint32_t)(clock-p->last_clock)>gap) {
        if(transport==TC_GATT)p->state=0;
        else {
            memset(p,0,sizeof(*p));memset(p->mask,255,sizeof(p->mask));
            p->sum_mask=255;
            m->uart_session=0;m->uart_key=0;m->uart_sum=0;
            m->uart_session_mask=255;m->uart_key_mask=255;m->uart_sum_mask=255;
        }
    }
    p->last_clock=clock;p->clock_set=1;
    for(i=0;i<n;++i) {
        uint8_t b=bytes[i];
        switch(p->state) {
        case 0:p->state=b==0x55?1:0;break;
        case 1:if(b==0x7F) {p->state=2;p->sum=0;p->sum_mask=255;}else p->state=0;break;
        case 2:p->command=b;p->sum=(uint8_t)(p->sum+b);p->state=3;break;
        case 3:p->length=(uint16_t)((uint16_t)b*256u);p->sum=(uint8_t)(p->sum+b);p->state=4;break;
        case 4:
            p->length=(uint16_t)(p->length|b);p->received=0;p->sum=(uint8_t)(p->sum+b);
            p->state=p->length>limit?0:(p->length==0?6:5);break;
        case 5:
            if(p->received>=limit) {p->state=0;break;}
            p->data[p->received]=b;p->mask[p->received]=255;++p->received;
            p->sum=(uint8_t)(p->sum+b);if(p->received>=p->length)p->state=6;break;
        case 6:
            if(p->sum_mask!=255){m->outcome=TC_INDETERMINATE;m->interpretation_halted=1;return;}
            if(p->sum==b) {
                if(transport==TC_GATT)tc_gatt_command(m,p->command,p->data,p->mask,p->length,m->image==TC_BOOT?2u:0u);
                else tc_uart_command(m);
            }
            if(m->transferred)return;
            p->state=0;break;
        default:p->state=0;break;
        }
        if(m->outcome==TC_STALLED)return;
    }
}
void tc_deliver_callback(tc_model *m,uint32_t callback,uint32_t argument) {
    if(m->transferred){m->outcome=TC_TRANSFERRED;return;}
    if(m->stalled) {m->outcome=TC_STALLED;return;}
    if(callback==0x9DFA) {
        if(tc_metadata_select(m,1)<0)return;
        event(m,TC_EV_RESET_REQUEST,0x99C6,0xE000E048,0xBEEF0080,4,TC_UNKNOWN);
    } else if(callback==0x192C || callback==0x8E12) {
        event(m,TC_EV_DISCONNECT_REQUEST,callback,0,argument,0,TC_UNKNOWN);
    } else if(callback==0x20E2 || (callback==0x24A8 && argument==2)) {
        event(m,TC_EV_JUMP_REQUEST,0x20E2,0x8000,0,0,TC_UNKNOWN);
    } else if(callback==0x99C6 || callback==0x1FF6 || (callback==0x24A8 && argument==4)) {
        event(m,TC_EV_RESET_REQUEST,callback==0x24A8?0x1FF6u:callback,0xE000E048,0xBEEF0080,4,TC_UNKNOWN);
    } else m->outcome=TC_INDETERMINATE;
}
