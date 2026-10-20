#include "ram_bridge.h"
#include <string.h>
static gb_flow general_invoke(void *,gb_model *,const gb_request *,gb_scalar *);
static void general_read(void *,uint32_t,uint8_t *,uint8_t *,size_t);
static gb_flow general_reply(void *,gb_model *,const gb_reply_request *);
static gb_flow report_command(void *,gb_model *,uint16_t,uint8_t,uint32_t,uint16_t);
static gb_flow general_schedule(void *,gb_model *,uint32_t,uint32_t,uint32_t,uint32_t,gb_scalar *);
static void bind_startup(ta_model *);
static void bind_kernel(ta_model *);
static gb_flow helper_invoke(void *,gh_model *,const gh_request *,gb_scalar *);
static int dnd_helper_entry(uint32_t va){return va==0x16f4a||va==0x17024||va==0x17048||va==0x170e2||va==0x17176;}
static int native_entry(tc_image image,uint32_t callback,nc_callback *entry){
    if(image==TC_RUNTIME){switch(callback){case 0x8e12:*entry=NC_RUNTIME_DISCONNECT;return 1;case 0x99c6:*entry=NC_RUNTIME_RESET;return 1;case 0x9dfa:*entry=NC_RUNTIME_BOOT_REQUEST;return 1;default:return 0;}}
    switch(callback){case 0x192c:*entry=NC_BOOT_DISCONNECT;return 1;case 0x20e2:*entry=NC_BOOT_JUMP;return 1;case 0x1ff6:*entry=NC_BOOT_RESET;return 1;default:return 0;}
}
static int helper_entry(uint32_t va){if(da_recognizes(va)&&!dnd_helper_entry(va))return 1;switch(va){case 0x908e:case 0x13be8:case 0x13d9c:case 0x95ec:case 0x13a62:case 0x13b5c:case 0x133fa:case 0x13156:case 0x81aa:case 0x81b0:case 0x93ee:case 0x93cc:case 0x9388:case 0x94e6:case 0x17024:case 0x1049a:case 0x843a:case 0x8214:case 0x8294:case 0x9edc:case 0xab12:case 0x9770:return 1;default:return 0;}}
static void export_uart(ta_model *);
static void import_uart(ta_model *);
static void export_call_state(ta_model *);
static void import_call_state(ta_model *);
static void transfer(ta_model*m){m->transferred=1;m->halted=1;m->ota.transferred=1;m->ota.outcome=TC_TRANSFERRED;}
typedef struct {
    uint32_t state,clock,command,sum,length,received,payload,active;
} parser_map;
static parser_map layout(const ta_model *m) {
    parser_map p;
    if(m->ota.image==TC_BOOT) {
        p.state=0x20004080;p.clock=0x20004084;p.command=0x20004088;
        p.sum=0x20004089;p.length=0x20004070;p.received=0x2000406e;
        p.payload=0x200090aa;p.active=0x2000408b;
    } else {
        p.state=0x200040a4;p.clock=0x200040a8;p.command=0x200040ac;
        p.sum=0x200040ad;p.length=0x20004096;p.received=0x20004092;
        p.payload=0x2000b9d8;p.active=0x200040b1;
    }
    return p;
}
static void unresolved(ta_model *m,uint32_t a) {
    ++m->unresolved;m->last_unknown_address=a;
}
static void put(ta_model *m,uint32_t a,uint32_t v,unsigned n) {
    unsigned i;
    for(i=0;i<n;i++) {
        m->memory.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));
        m->memory.known[a-TF_RAM_BASE+i]=255;
    }
}
static int get(ta_model *m,uint32_t a,unsigned n,uint32_t *v) {
    unsigned i;*v=0;
    for(i=0;i<n;i++) {
        if(m->memory.known[a-TF_RAM_BASE+i]!=255){unresolved(m,a+i);return 0;}
        *v|=(uint32_t)m->memory.ram[a-TF_RAM_BASE+i]<<(8*i);
    }
    return 1;
}
static void import_active(ta_model *m) {
    parser_map p=layout(m);size_t i=p.active-TF_RAM_BASE;
    m->ota.active=m->memory.ram[i];m->ota.active_mask=m->memory.known[i];
}
static void export_active(ta_model *m) {
    parser_map p=layout(m);size_t i=p.active-TF_RAM_BASE;
    m->memory.ram[i]=m->ota.active;m->memory.known[i]=m->ota.active_mask;
}
static uint32_t slot_address(const ta_model *m,unsigned i) {
    return m->ota.image==TC_BOOT?0x200090a4u:0x2000b18cu+1062u*i;
}
static void possible_reply(ta_model *m,unsigned i) {
    uint32_t a=slot_address(m,i);
    /* Coarse sound join of refusal and accepted-builder writes. Values remain
       placeholders; these are not known poststate bytes. +0/+1 remain untouched. */
    memset(m->memory.known+a-TF_RAM_BASE+2,0,4);
    memset(m->memory.known+a-TF_RAM_BASE+6,0,m->ota.reply_frame_length);
}
static void unknown_reply(ta_model *m,unsigned first) {
    unsigned i,count=m->ota.image==TC_BOOT?1u:2u;
    for(i=first;i<count;i++)possible_reply(m,i);
    unresolved(m,slot_address(m,first));
    m->ota.reply_queued=TC_UNKNOWN;m->ota.outcome=TC_INDETERMINATE;
}
static void commit_reply(ta_model *m) {
    unsigned i,count=m->ota.image==TC_BOOT?1u:2u;
    uint32_t handle_address=m->ota.image==TC_BOOT?0x2000407eu:0x2000409eu;
    uint32_t query_address=m->ota.image==TC_BOOT?0x20004068u:0x20004088u;
    uint32_t task_address=m->ota.image==TC_BOOT?0x2000407cu:0x2000409cu;
    uint32_t handle,a,task;int accepted,posted;
    if(m->ota.reply_length>1039){m->ota.reply_queued=TC_NO;return;}
    if(m->ota.reply_length && m->ota.alloc_ok!=TC_YES) {
        if(m->ota.alloc_ok==TC_UNKNOWN)unknown_reply(m,0);
        else m->ota.reply_queued=TC_NO;
        return;
    }
    for(i=0;i<count;i++) {
        if(!get(m,handle_address+4*i,2,&handle)){unknown_reply(m,i);return;}
        if(handle!=m->handle || handle==0xfffe)continue;
        accepted=m->link.connection_status?
            m->link.connection_status(m->link.context,m->handle,query_address):TF_UNKNOWN;
        if(accepted==TF_UNKNOWN){unknown_reply(m,i);return;}
        if(accepted!=1)continue;
        a=slot_address(m,i);
        memcpy(m->memory.ram+a-TF_RAM_BASE+6,m->ota.reply_frame,m->ota.reply_frame_length);
        memcpy(m->memory.known+a-TF_RAM_BASE+6,m->ota.reply_frame_mask,m->ota.reply_frame_length);
        put(m,a+2,(uint32_t)m->ota.reply_frame_length,2);put(m,a+4,0,2);
        ++m->replies_committed;m->ota.reply_queued=TC_YES;
        /* Native ignores ROM+80's result. A committed slot is not a transmitted
           packet and is not a hardware/application acknowledgement. */
        if(get(m,task_address+4*i,1,&task)) {
            posted=m->memory.backend.rom_status?
                m->memory.backend.rom_status(m->memory.backend.context,80,(uint8_t)task,1,0):TF_UNKNOWN;
            if(posted==TF_UNKNOWN)unresolved(m,0x40050);
            if(posted==TF_UNKNOWN && m->candidate)m->halted=1;
        }
        return;
    }
    m->ota.reply_queued=TC_NO;
}
static int reply_byte_source(ta_model*m,uint32_t pointer,size_t i,uint8_t*v,uint8_t*k){
    uint32_t a=pointer?pointer:m->reply_source_address;
    if(a){a+=(uint32_t)i;
        if(a>=TF_RAM_BASE&&a-TF_RAM_BASE<TF_RAM_SIZE){*v=m->memory.ram[a-TF_RAM_BASE];*k=m->memory.known[a-TF_RAM_BASE];return 1;}
        if(m->memory.runtime&&a>=0x8000&&a-0x8000<m->memory.runtime_length){*v=m->memory.runtime[a-0x8000];*k=255;return 1;}
        if(m->external_general.read||m->external.read){general_read(m,a,v,k,1);return 1;}
        unresolved(m,a);m->halted=1;return 0;
    }
    if(m->reply_source_data||m->reply_source_known){
        if(!m->reply_source_data||!m->reply_source_known||i>=m->reply_source_available){unresolved(m,0);m->halted=1;return 0;}
        *v=m->reply_source_data[i];*k=m->reply_source_known[i];return 1;
    }
    /* No borrowed descriptor: the core's complete synchronous value contract. */
    if(m->reply_wrapper_va==0x8cfa&&i>=m->reply_source_available){unresolved(m,0);m->halted=1;return 0;}
    *v=m->ota.reply_data[i];*k=m->ota.reply_mask[i];return 1;
}
static tc_flow native_reply_builder(ta_model*m,tc_model*core,uint32_t pointer){
    unsigned i,count=core->image==TC_BOOT?1u:2u;uint32_t h,task,a,base;
    uint32_t handles=core->image==TC_BOOT?0x2000407eu:0x2000409eu;
    uint32_t query=core->image==TC_BOOT?0x20004068u:0x20004088u;
    uint32_t tasks=core->image==TC_BOOT?0x2000407cu:0x2000409cu;
    size_t j;int accepted,posted;uint8_t value,known_byte,sum,mask=255;
    core->reply_queued=TC_NO;if(core->reply_length>1039)return TC_RETURNED;
    for(i=0;i<count;i++){
        if(!get(m,handles+4*i,2,&h)){m->halted=1;return TC_FLOW_UNKNOWN;}
        if(h!=m->handle||h==65534)continue;
        accepted=m->link.connection_status?m->link.connection_status(m->link.context,m->handle,query):TF_UNKNOWN;
        if(m->transferred||core->transferred)return TC_TRANSFER;
        if(accepted==TF_UNKNOWN){unresolved(m,0x4013c);m->halted=1;return TC_FLOW_UNKNOWN;}
        if(accepted!=1)continue;
        a=slot_address(m,i);base=a+6;
        /* 8D90/94/9E/A4 and BOOT185C/68/74/7E precede every source LBU. */
        put(m,base,0x7f55,2);
        if(core->image==TC_BOOT){put(m,base+2,core->reply_command,1);put(m,base+4,(uint32_t)core->reply_length,1);put(m,base+3,(uint32_t)(core->reply_length>>8),1);}
        else {put(m,base+4,(uint32_t)core->reply_length,1);put(m,base+3,(uint32_t)(core->reply_length>>8),1);put(m,base+2,core->reply_command,1);}
        sum=(uint8_t)(core->reply_command+(core->reply_length>>8)+(core->reply_length&255u));
        for(j=0;j<core->reply_length;j++){
            if(!reply_byte_source(m,pointer,j,&value,&known_byte))return TC_FLOW_UNKNOWN;
            m->memory.ram[base-TF_RAM_BASE+5+j]=value;m->memory.known[base-TF_RAM_BASE+5+j]=known_byte;
            core->reply_data[j]=value;core->reply_mask[j]=known_byte;core->reply_frame[5+j]=value;core->reply_frame_mask[5+j]=known_byte;
            sum=(uint8_t)(sum+value);if(known_byte!=255)mask=0;
        }
        m->memory.ram[base-TF_RAM_BASE+5+j]=sum;m->memory.known[base-TF_RAM_BASE+5+j]=mask;
        core->reply_frame[5+j]=sum;core->reply_frame_mask[5+j]=mask;
        put(m,a+2,(uint32_t)core->reply_length+6,2);put(m,a+4,0,2);
        ++m->replies_committed;core->reply_queued=TC_YES;
        if(!get(m,tasks+4*i,1,&task)){m->halted=1;return TC_FLOW_UNKNOWN;}
        posted=m->memory.backend.rom_status?m->memory.backend.rom_status(m->memory.backend.context,80,(uint8_t)task,1,0):TF_UNKNOWN;
        if(m->transferred||core->transferred)return TC_TRANSFER;
        if(posted==TF_UNKNOWN){unresolved(m,0x40050);m->halted=1;return TC_FLOW_UNKNOWN;}
        return TC_RETURNED; /* Native tailcall's scalar result is ignored by callers. */
    }return TC_RETURNED;
}
static tc_flow candidate_reply_body(void *p,tc_model *core) {
    ta_model *m=(ta_model *)p;uint32_t pointer=0,status=0;size_t i;tc_flow flow;
    if(!m->candidate){commit_reply(m);return TC_RETURNED;}
    /* 13960/13D7A/13CAC and BOOT29CE wrappers allocate/copy before8CFA/1848.
       Direct8CFA reports/debug do not touch the heap. Core OTA keeps its existing
       explicit copy-wrapper contract (wrapperVA0). */
    if(core->reply_length&&m->reply_wrapper_va!=0x8cfa){
        if(!rc_msg_allocate(m->candidate,(uint16_t)core->reply_length,&pointer)){
            unresolved(m,m->candidate->last_unknown_address);m->halted=1;return TC_FLOW_UNKNOWN;
        }
        if(!pointer){core->reply_queued=TC_NO;return TC_RETURNED;}
        if(!m->memory.backend.memory_contracts){unresolved(m,0x4004c);m->halted=1;return TC_FLOW_UNKNOWN;}
        if(pointer<TF_RAM_BASE||pointer-TF_RAM_BASE>TF_RAM_SIZE||core->reply_length>TF_RAM_SIZE-(pointer-TF_RAM_BASE)){
            unresolved(m,pointer);m->halted=1;return TC_FLOW_UNKNOWN;
        }
        for(i=0;i<core->reply_length;i++){
            uint8_t value,known_byte;if(!reply_byte_source(m,0,i,&value,&known_byte))return TC_FLOW_UNKNOWN;
            m->memory.ram[pointer-TF_RAM_BASE+i]=value;m->memory.known[pointer-TF_RAM_BASE+i]=known_byte;
        }
    }
    flow=native_reply_builder(m,core,pointer);if(flow!=TC_RETURNED)return flow;
    if(pointer&&!rc_msg_deallocate(m->candidate,pointer,&status)){
        unresolved(m,m->candidate->last_unknown_address);m->halted=1;return TC_FLOW_UNKNOWN;
    }
    return TC_RETURNED; /* Copy wrapper ignores the deallocation scalar. */
}
static tc_flow candidate_reply(void *p,tc_model *core) {
    ta_model *m=(ta_model *)p;tc_flow flow;
    /* Commit this command's earlier active write before any allocator/link
       callback; import callback changes before later staging observations. */
    export_active(m);flow=candidate_reply_body(p,core);import_active(m);return flow;
}
static void external_read(void *p,uint32_t a,uint8_t *d,uint8_t *k,size_t n) {
    ta_model *m=(ta_model *)p;export_call_state(m);
    if(m->external.read)m->external.read(m->external.context,a,d,k,n);
    import_call_state(m);
    if(m->ota.interpretation_halted)memset(k,0,n);
}
static tc_flow external_program(void *p,uint32_t a,const uint8_t *d,const uint8_t *k) {
    ta_model *m=(ta_model *)p;tc_flow f=TC_FLOW_UNKNOWN;export_call_state(m);
    if(m->flash_enabled){fp_source source;fp_flow flow;uintptr_t ptr=(uintptr_t)d,ram=(uintptr_t)m->memory.ram,uart=(uintptr_t)m->ota.uart.data;memset(&source,0,sizeof(source));source.kind=FP_VALUE_VIEW;source.data=d;source.known=k;source.available=256;if(ptr>=ram&&ptr-ram<=TF_RAM_SIZE-256){source.kind=FP_ADDRESS;source.address=TF_RAM_BASE+(uint32_t)(ptr-ram);}else if(m->transport==TC_UART&&ptr>=uart&&ptr-uart<=sizeof(m->ota.uart.data)-256){source.kind=FP_ADDRESS;source.address=UINT32_C(0x20009594)+(uint32_t)(ptr-uart);}flow=ta_program_page(m,a,&source);f=flow==FP_RETURNED?TC_RETURNED:flow==FP_TRANSFER?TC_TRANSFER:TC_FLOW_UNKNOWN;}
    else if(m->external.program256)f=m->external.program256(m->external.context,a,d,k);
    import_call_state(m);if(f==TC_TRANSFER||m->transferred){transfer(m);return TC_TRANSFER;}return m->ota.interpretation_halted?TC_FLOW_UNKNOWN:f;
}
static void external_copy(void *p,uint8_t *d,uint8_t *k,const uint8_t *s,const uint8_t *sk,size_t n) {
    ta_model *m=(ta_model *)p;export_call_state(m);
    if(m->external.rom_copy)m->external.rom_copy(m->external.context,d,k,s,sk,n);
    import_call_state(m);
}
static void on_event(void *p,const tc_event *source) {
    ta_model *m=(ta_model *)p;tc_event e=*source;export_call_state(m);
    if(e.kind==TC_EV_REPLY) {
        if(m->transport==TC_GATT){e.result=m->ota.reply_queued;}
    } else if(e.kind==TC_EV_SCHEDULE) {
        if(m->transport==TC_UART) {
            uint32_t task;
            if(get(m,0x2000408d,1,&task)){
                int r=m->memory.backend.rom_status?m->memory.backend.rom_status(m->memory.backend.context,88,(uint8_t)task,(uint16_t)e.address,(uint32_t)e.length):TF_UNKNOWN;
                m->last_schedule_result=r;e.result=r==TF_UNKNOWN?TC_UNKNOWN:(r==1?TC_YES:TC_NO);
            }
        } else if(m->ota.image==TC_RUNTIME) {
            /* Source event.argument is the original native delay; event.length
               is already converted. Do not convert the latter a second time. */
            m->last_schedule_result=tf_schedule(&m->memory,e.va,0,e.argument,e.address);
            e.result=m->last_schedule_result==TF_UNKNOWN?TC_UNKNOWN:
                (m->last_schedule_result==0?TC_YES:TC_NO);
        } else {
            m->last_schedule_result=br_schedule(&m->boot,e.va,0,e.argument,e.address);
            e.result=m->last_schedule_result==TF_UNKNOWN?TC_UNKNOWN:(m->last_schedule_result==0?TC_YES:TC_NO);
        }
    } else if(e.kind==TC_EV_CANCEL_STARTUP) {
        if(br_stop_startup(&m->boot)==TF_UNKNOWN){unresolved(m,0x251c);m->halted=1;m->ota.interpretation_halted=1;}
    }
    if(m->boot.flow==BR_TRANSFER){transfer(m);}else if(e.kind==TC_EV_SCHEDULE&&m->last_schedule_result==TF_UNKNOWN){m->halted=1;m->ota.interpretation_halted=1;m->ota.outcome=TC_INDETERMINATE;}
    if(m->external.event)m->external.event(m->external.context,&e);
    import_call_state(m);
}
static int feature_rom(void *p,unsigned off,uint8_t task,uint16_t events,uint32_t ticks) {
    ta_model *m=(ta_model *)p;
    if(m->candidate)return rc_rom_status(m->candidate,off,task,events,ticks);
    return m->external_features.rom_status?
        m->external_features.rom_status(m->external_features.context,off,task,events,ticks):TF_UNKNOWN;
}
static int feature_free(void *p,uint32_t pointer) {
    ta_model *m=(ta_model *)p;uint32_t status;
    if(m->candidate)return rc_msg_deallocate(m->candidate,pointer,&status)?1:TF_UNKNOWN;
    return m->external_features.free_argument?m->external_features.free_argument(m->external_features.context,pointer):TF_UNKNOWN;
}
static int feature_tx(void *p,const tf_frame *f) {
    ta_model *m=(ta_model *)p;
    return m->external_features.tx?m->external_features.tx(m->external_features.context,f):TF_UNKNOWN;
}
static void feature_delivery(void *p,tf_model *ram,uint32_t callback,uint32_t argument) {
    ta_model *m=(ta_model *)p;
    if(m->ota.image==TC_RUNTIME && (callback==0x8e12 || callback==0x9dfa || callback==0x99c6))
        ta_deliver_ota(m,callback,argument);
    if(m->external_features.delivery)
        m->external_features.delivery(m->external_features.context,ram,callback,argument);
}
void ta_init(ta_model *m,tc_image image,const uint8_t *b,size_t n,const tc_backend *io,const tf_backend *features,const ta_link_backend *link) {
    tc_backend bridge;tf_backend feature_bridge;
    memset(m,0,sizeof(*m));if(io)m->external=*io;if(link)m->link=*link;
    if(features)m->external_features=*features;
    memset(&feature_bridge,0,sizeof(feature_bridge));feature_bridge.context=m;
    feature_bridge.rom_status=feature_rom;feature_bridge.tx=feature_tx;
    feature_bridge.delivery=feature_delivery;
    feature_bridge.free_argument=feature_free;
    feature_bridge.memory_contracts=m->external_features.memory_contracts;
    if(image==TC_RUNTIME)tf_init(&m->memory,b,n,&feature_bridge);
    else m->memory.backend=feature_bridge;
    memset(&bridge,0,sizeof(bridge));bridge.context=m;
    bridge.read=external_read;bridge.program256=external_program;
    if(io && io->rom_copy)bridge.rom_copy=external_copy;
    bridge.event=on_event;
    bridge.gatt_wrapper=candidate_reply;
    tc_init(&m->ota,image,&bridge);
    /* Actual native link/slot selection occurs in on_event, not a synthetic
       claim that every reply passes the connection query. */
    m->ota.link_ok=TC_YES;m->last_schedule_result=TF_UNKNOWN;import_active(m);
    m->transport=TC_GATT;
    ta_set_general_backend(m,NULL);
    ta_set_helper_backend(m,NULL);bind_startup(m);
    ta_set_native_backend(m,NULL);
    ta_set_deep_backend(m,NULL);
    ta_set_reports_backend(m,NULL);
    ta_set_spi_backend(m,NULL);
    fp_init(&m->flash,&m->memory,image==TC_BOOT?FP_BOOT:FP_RUNTIME,NULL);ta_set_receive_backend(m,NULL);
}
size_t ta_receive(ta_model *m,uint16_t h,const uint8_t *b,size_t n,uint32_t now) {
    parser_map p=layout(m);uint32_t previous,state,sum,length,received,command;
    size_t i;uint8_t byte;
    if(m->transferred||m->ota.transferred){m->halted=1;return 0;}m->handle=h;m->halted=0;
    m->reply_source_address=0;
    m->transport=TC_GATT;
    if(m->ota.stalled || m->ota.interpretation_halted){m->halted=1;return 0;}
    if(get(m,p.clock,4,&previous)) {
        if((uint32_t)(now-previous)>299)put(m,p.state,0,1);
    } else {
        /* A zero parser state has the same value on both timeout branches. */
        if(m->memory.known[p.state-TF_RAM_BASE]!=255 || m->memory.ram[p.state-TF_RAM_BASE]!=0)
            m->memory.known[p.state-TF_RAM_BASE]=0;
    }
    put(m,p.clock,now,4); /* Unconditional native store, even for empty input. */
    for(i=0;i<n;i++) {
        if(!get(m,p.state,1,&state)){m->halted=1;return i;}
        byte=b[i];
        switch(state) {
        case 0:put(m,p.state,byte==0x55?1u:0u,1);break;
        case 1:
            if(byte==0x7f){put(m,p.state,2,1);put(m,p.sum,0,1);}
            else put(m,p.state,0,1);
            break;
        case 2:
            put(m,p.state,3,1);put(m,p.command,byte,1);
            if(!get(m,p.sum,1,&sum)){m->halted=1;return i+1;}
            put(m,p.sum,sum+byte,1);break;
        case 3:
            put(m,p.state,4,1);put(m,p.length,(uint32_t)byte*256,2);
            if(!get(m,p.sum,1,&sum)){m->halted=1;return i+1;}
            put(m,p.sum,sum+byte,1);break;
        case 4:
            put(m,p.received,0,2);
            if(!get(m,p.length,2,&length)){m->halted=1;return i;}
            length|=byte;put(m,p.length,length,2);
            put(m,p.state,length>1040?0u:(length==0?6u:5u),1);
            if(!get(m,p.sum,1,&sum)){m->halted=1;return i+1;}
            put(m,p.sum,sum+byte,1);break;
        case 5:
            if(!get(m,p.received,2,&received)){m->halted=1;return i;}
            if(received>=1040){put(m,p.state,0,1);break;}
            put(m,p.received,received+1,2);put(m,p.payload+received,byte,1);
            if(!get(m,p.length,2,&length)){m->halted=1;return i+1;}
            if(received+1>=length)put(m,p.state,6,1);
            if(!get(m,p.sum,1,&sum)){m->halted=1;return i+1;}
            put(m,p.sum,sum+byte,1);
            break;
        case 6:
            if(!get(m,p.sum,1,&sum)){m->halted=1;return i;}
            if(sum==byte) {
                if(!get(m,p.length,2,&length)||!get(m,p.command,1,&command)){m->halted=1;return i;}
                if(m->ota.image==TC_RUNTIME){
                    if(command!='U'&&command!='S'&&command!='W'&&command!='E')++m->ota.command_count;
                    {gb_flow flow=gb_dispatch(&m->general,h,(uint8_t)command,p.payload,(uint16_t)length);if(flow!=GB_RETURNED){
                        if(flow==GB_TRANSFER)transfer(m);else {unresolved(m,m->general.boundary_address);m->ota.outcome=TC_INDETERMINATE;m->halted=1;}return i;
                    }}
                } else {
                    import_active(m);
                    m->reply_source_address=command=='S'?p.payload:0;
                    tc_gatt_command(&m->ota,(uint8_t)command,m->memory.ram+p.payload-TF_RAM_BASE,
                        m->memory.known+p.payload-TF_RAM_BASE,(uint16_t)length,2u);
                    m->reply_source_address=0;
                    export_active(m);
                }
                if(m->halted)return i;
                if(m->ota.stalled){m->halted=1;return i+1;}
            }
            put(m,p.state,0,1); /* Callback/alias effects precede this store. */
            break;
        default:put(m,p.state,0,1);break;
        }
    }
    return n;
}
void ta_deliver_ota(ta_model *m,uint32_t c,uint32_t a) {if(m->transferred||m->ota.transferred)return;
    import_active(m);tc_deliver_callback(&m->ota,c,a);export_active(m);
}
uint16_t ta_dispatch_runtime(ta_model *m,uint16_t events) {
    if(m->ota.image!=TC_RUNTIME){unresolved(m,0x200094cc);m->halted=1;return events;}
    if(m->halted || m->ota.interpretation_halted)return events;
    {
        unsigned i;uint32_t callback=0,argument=0,mode=0,address;gb_scalar out;nc_callback native;
        for(i=0;i<15;i++)if(events&(1u<<i)){
            address=TF_REGISTRY+12u*i;
            if(!get(m,address+4,4,&callback)){m->halted=1;return events;}
            if(callback && (!get(m,address,1,&mode)||!get(m,address+8,4,&argument))){m->halted=1;return events;}
            if(callback&&native_entry(m->ota.image,callback,&native)){
                if(!mode){put(m,address+4,0,4);put(m,address+8,0,4);}
                if(ta_dispatch_native(m,callback,argument)!=NC_RETURNED)return events;
                return (uint16_t)(events^(1u<<i));
            }
            if(callback && (helper_entry(callback)||callback==0x13160||callback==0x135d4)){
                if(!get(m,address,1,&mode)||!get(m,address+8,4,&argument)){m->halted=1;return events;}
                if(!mode){put(m,address+4,0,4);put(m,address+8,0,4);}
                if(helper_entry(callback)){
                    {gb_flow f=gh_dispatch(&m->helpers,callback,argument,&out);if(f!=GB_RETURNED){if(f==GB_TRANSFER)transfer(m);else {unresolved(m,m->helpers.boundary_address);m->halted=1;}return events;}}
                }else{
                    if(ta_dispatch_deep(m,callback,argument)!=GB_RETURNED)return events;
                }
                return (uint16_t)(events^(1u<<i));
            }
            break;
        }
    }
    {
        uint32_t before=m->memory.unknown_effects;uint16_t returned=tf_dispatch(&m->memory,events);
        /* These three old OTA callbacks only expose request effects. Their
           manual API keeps that narrow contract; SystemProcess below cannot
           promote an unresolved request to a confirmed handler return. */
        if(m->memory.unknown_effects!=before && m->memory.last_callback!=0x8e12 && m->memory.last_callback!=0x9dfa && m->memory.last_callback!=0x99c6){m->halted=1;return events;}
        return returned;
    }
}
static int span(uint32_t address,size_t n){return address>=TF_RAM_BASE && address<=TF_RAM_BASE+TF_RAM_SIZE && n<=TF_RAM_BASE+TF_RAM_SIZE-address;}
static void export_uart(ta_model *m){
    tc_parser *p=&m->ota.uart;
    memcpy(m->memory.ram+0x9594,p->data,1026);memcpy(m->memory.known+0x9594,p->mask,1026);
    put(m,0x20009996,p->length,2);put(m,0x20009998,p->received,2);
    put(m,0x2000999a,p->command,1);m->memory.ram[0x999b]=p->sum;m->memory.known[0x999b]=p->sum_mask;put(m,0x2000999d,p->state,1);
    m->memory.ram[0x999c]=m->ota.uart_session;m->memory.known[0x999c]=m->ota.uart_session_mask;
    m->memory.ram[0x999e]=m->ota.uart_key;m->memory.known[0x999e]=m->ota.uart_key_mask;
    m->memory.ram[0x999f]=m->ota.uart_sum;m->memory.known[0x999f]=m->ota.uart_sum_mask;
    put(m,0x2000408c,m->ota.stay,1);
}
static void import_uart(ta_model *m){
    tc_parser *p=&m->ota.uart;uint32_t v;int complete=1;
    memcpy(p->data,m->memory.ram+0x9594,1026);memcpy(p->mask,m->memory.known+0x9594,1026);
    if(get(m,0x20009996,2,&v))p->length=(uint16_t)v;else complete=0;
    if(get(m,0x20009998,2,&v))p->received=(uint16_t)v;else complete=0;
    if(get(m,0x2000999a,1,&v))p->command=(uint8_t)v;else complete=0;
    p->sum=m->memory.ram[0x999b];p->sum_mask=m->memory.known[0x999b];
    if(get(m,0x2000999d,1,&v))p->state=(uint8_t)v;else complete=0;
    m->ota.uart_session=m->memory.ram[0x999c];m->ota.uart_session_mask=m->memory.known[0x999c];
    m->ota.uart_key=m->memory.ram[0x999e];m->ota.uart_key_mask=m->memory.known[0x999e];
    m->ota.uart_sum=m->memory.ram[0x999f];m->ota.uart_sum_mask=m->memory.known[0x999f];
    if(get(m,0x2000408c,1,&v))m->ota.stay=(uint8_t)v;else complete=0;
    if(!complete){m->halted=1;m->ota.interpretation_halted=1;m->ota.outcome=TC_INDETERMINATE;}
}
static void export_call_state(ta_model *m){export_active(m);if(m->transport==TC_UART && !m->ota.interpretation_halted)export_uart(m);}
static void import_call_state(ta_model *m){import_active(m);if(m->transport==TC_UART)import_uart(m);}
static gb_flow invoke_external(ta_model *m,gb_model *g,const gb_request *r,gb_scalar *v){
    return m->external_general.invoke?m->external_general.invoke(m->external_general.context,g,r,v):GB_HALT;
}
static gb_flow general_invoke(void *p,gb_model *g,const gb_request *r,gb_scalar *v){
    ta_model *m=(ta_model *)p;uint32_t address,result;size_t i,n;uint8_t value,known;
    if(r->kind==GB_NATIVE_HELPER&&dnd_helper_entry(r->target)){
        unsigned expected=(r->target==0x17048||r->target==0x170e2)?2u:0u;
        if(r->argument_count!=expected)return GB_HALT;
        for(i=0;i<expected;i++)if(r->known[i]!=UINT32_MAX)return GB_HALT;
        return ta_dispatch_dnd(m,r->target,expected?r->arguments[0]:0,expected?r->arguments[1]:0,v);
    }
    if(r->kind==GB_NATIVE_HELPER && r->target==0x9bac){
        if(r->argument_count!=4 || !span(r->arguments[2],1040))return GB_HALT;
        for(i=0;i<4;i++)if(r->known[i]!=UINT32_MAX)return GB_HALT;
        import_active(m);
        m->reply_source_address=r->arguments[1]=='S'?r->arguments[2]:0;
        tc_gatt_command(&m->ota,(uint8_t)r->arguments[1],m->memory.ram+r->arguments[2]-TF_RAM_BASE,
            m->memory.known+r->arguments[2]-TF_RAM_BASE,(uint16_t)r->arguments[3],r->arguments[2]&3u);
        m->reply_source_address=0;
        export_active(m);v->value=0;v->known=UINT32_MAX;
        return m->transferred||m->ota.transferred?GB_TRANSFER:m->ota.stalled||m->halted||m->ota.outcome==TC_INDETERMINATE?GB_HALT:GB_RETURNED;
    }
    if(r->kind==GB_NATIVE_HELPER && r->target==0x829e && r->argument_count==3 && r->buffer_length==12){
        gr_view view;if(r->known[0]!=UINT32_MAX||r->known[1]!=UINT32_MAX||!r->buffer||!r->buffer_known)return GB_HALT;memset(&view,0,sizeof(view));view.address=r->known[2]==UINT32_MAX?r->arguments[2]:0;view.data=r->buffer;view.known=r->buffer_known;view.available=12;v->value=0;v->known=0;return gr_cache_transfer(&m->reports,r->arguments[0],r->arguments[1],&view);
    }
    if(r->kind==GB_NATIVE_HELPER&&(r->target==SC_ROUTE_SEND||r->target==SC_ROUTE_FILTERS)){
        sc_arguments a;sc_flow flow;memset(&a,0,sizeof(a));if(!r->buffer||!r->buffer_known||r->argument_count>4)return GB_HALT;for(i=0;i<r->argument_count;i++){if(r->known[i]!=UINT32_MAX&&!(r->target==SC_ROUTE_SEND&&i==0)&&!(r->target==SC_ROUTE_FILTERS&&i==1))return GB_HALT;a.registers[i]=r->arguments[i];}a.buffer.kind=SC_VIEW;a.buffer.data=r->buffer;a.buffer.known=r->buffer_known;a.buffer.available=(uint32_t)r->buffer_length;flow=ta_dispatch_spi(m,r->target,&a);v->value=0;v->known=0;return flow==SC_RETURNED?GB_RETURNED:flow==SC_TRANSFER?GB_TRANSFER:GB_HALT;
    }
    if(r->kind==GB_NATIVE_HELPER && helper_entry(r->target)){
        if(r->argument_count && r->known[0]!=UINT32_MAX)return GB_HALT;
        return gh_dispatch(&m->helpers,r->target,r->argument_count?r->arguments[0]:0,v);
    }
    if(r->kind==GB_NATIVE_HELPER && r->target==0x94cc && r->argument_count==3){
        for(i=0;i<3;i++)if(r->known[i]!=UINT32_MAX)return GB_HALT;
        return gh_pattern_register(&m->helpers,r->arguments[0],r->arguments[1],(uint16_t)r->arguments[2],v);
    }
    if(r->kind==GB_NATIVE_HELPER && r->target==0x1d54 && m->ota.image==TC_BOOT){
        if(!m->startup_enabled && m->external_general.invoke)return invoke_external(m,g,r,v);
        if(r->argument_count!=1 || r->known[0]!=UINT32_MAX)return GB_HALT;
        if(bs_pattern(&m->startup,r->arguments[0])!=BS_RETURNED)return GB_HALT;
        v->value=0;v->known=0;return GB_RETURNED;
    }
    if(r->kind==GB_ROM_ALLOC && m->candidate){
        if(r->known[0]!=UINT32_MAX || !rc_msg_allocate_register(m->candidate,r->arguments[0],&address))return GB_HALT;
        v->value=address;v->known=UINT32_MAX;return GB_RETURNED;
    }
    if(r->kind==GB_ROM_FREE && m->candidate){
        if(r->known[0]!=UINT32_MAX || !rc_msg_deallocate(m->candidate,r->arguments[0],&result))return GB_HALT;
        v->value=result;v->known=UINT32_MAX;return GB_RETURNED;
    }
    if(r->kind==GB_ROM_ZERO && m->memory.backend.memory_contracts){
        if(!r->buffer || !r->buffer_known || r->known[1]!=UINT32_MAX)return GB_HALT;
        memset(r->buffer,(uint8_t)r->arguments[1],r->buffer_length);memset(r->buffer_known,255,r->buffer_length);
        v->value=0;v->known=UINT32_MAX;return GB_RETURNED;
    }
    if(r->kind==GB_ROM_COPY && m->memory.backend.memory_contracts){
        if(r->known[1]!=UINT32_MAX || r->known[2]!=UINT32_MAX)return GB_HALT;
        n=r->arguments[2];
        if(m->candidate && (r->arguments[1]==0 || (!r->buffer && r->known[0]==UINT32_MAX && r->arguments[0]==0) || n==0)){
            /* Fixed candidate leaves incidental a0=entry dst; declared API is
               void. An abstract OUT buffer's native address remains unknown. */
            v->value=r->arguments[0];v->known=r->known[0];return GB_RETURNED;
        }
        if(r->buffer){
            if(!r->buffer_known || r->buffer_length!=n)return GB_HALT;
            if(!span(r->arguments[1],n) && !m->external_general.read && !m->external.read)return GB_HALT;
            general_read(m,r->arguments[1],r->buffer,r->buffer_known,n);
            v->value=r->arguments[0];v->known=m->candidate?r->known[0]:0;return GB_RETURNED;
        }
        if(r->known[0]!=UINT32_MAX || !span(r->arguments[0],n))return GB_HALT;
        if(!span(r->arguments[1],n) && !m->external_general.read && !m->external.read)return GB_HALT;
        for(i=0;i<n;i++){
            address=r->arguments[1]+(uint32_t)i;value=known=0;
            if(span(address,1)){value=m->memory.ram[address-TF_RAM_BASE];known=m->memory.known[address-TF_RAM_BASE];}
            else general_read(m,address,&value,&known,1);
            address=r->arguments[0]+(uint32_t)i;
            m->memory.ram[address-TF_RAM_BASE]=value;m->memory.known[address-TF_RAM_BASE]=known;
        }
        v->value=r->arguments[0];v->known=m->candidate?r->known[0]:0;return GB_RETURNED;
    }
    return invoke_external(m,g,r,v);
}
static gb_flow reply_view(ta_model*m,const gb_reply_request*r,size_t available){
    uint8_t data[1040],known[1040];size_t n;
    const uint8_t *old_data=m->reply_source_data,*old_known=m->reply_source_known;
    size_t old_available=m->reply_source_available;uint32_t old_address=m->reply_source_address,old_wrapper=m->reply_wrapper_va;
    if(m->transferred||m->ota.transferred)return GB_TRANSFER;
    if(r->length>sizeof(data)||(!r->data&&available)||(!r->known&&available))return GB_HALT;
    m->handle=r->handle;m->transport=TC_GATT;import_active(m);
    m->reply_source_address=r->source_address;m->reply_source_data=r->source_address?NULL:r->data;
    m->reply_source_known=r->known;m->reply_source_available=available;m->reply_wrapper_va=r->wrapper_va;
    if(r->source_address){
        memset(data,0,r->length);memset(known,0,r->length);
        /* Staging is diagnostic. Native source reads remain after link selection
           and header writes, including when the mapped span is unrepresented. */
        if(span(r->source_address,r->length)){memcpy(data,m->memory.ram+r->source_address-TF_RAM_BASE,r->length);memcpy(known,m->memory.known+r->source_address-TF_RAM_BASE,r->length);}
        (void)tc_gatt_reply(&m->ota,r->command,data,known,r->length);
    }else if(available<r->length){
        /* Safe host staging only. Native builder reads the borrowed bytes live
           and stops at the first unrepresented byte after its actual TX prefix. */
        memset(data,0,r->length);memset(known,0,r->length);n=available;
        if(n){memcpy(data,r->data,n);memcpy(known,r->known,n);}
        (void)tc_gatt_reply(&m->ota,r->command,data,known,r->length);
    }else (void)tc_gatt_reply(&m->ota,r->command,r->data,r->known,r->length);
    m->reply_source_address=old_address;m->reply_source_data=old_data;
    m->reply_source_known=old_known;m->reply_source_available=old_available;m->reply_wrapper_va=old_wrapper;
    if(m->ota.transferred){transfer(m);return GB_TRANSFER;}
    return m->ota.stalled||m->ota.interpretation_halted||m->halted?GB_HALT:GB_RETURNED;
}
static gb_flow general_reply(void*p,gb_model*g,const gb_reply_request*r){(void)g;return reply_view((ta_model*)p,r,r->bounded?r->available:r->length);}
static gb_flow general_schedule(void *p,gb_model *g,uint32_t cb,uint32_t mode,uint32_t delay,uint32_t argument,gb_scalar *v){
    ta_model *m=(ta_model *)p;int result;(void)g;
    result=tf_schedule(&m->memory,cb,mode,delay,argument);m->last_schedule_result=result;
    v->value=(uint32_t)result;v->known=result==TF_UNKNOWN?0:UINT32_MAX;
    return m->transferred||m->ota.transferred?GB_TRANSFER:result==TF_UNKNOWN?GB_HALT:GB_RETURNED;
}
static void general_read(void *p,uint32_t a,uint8_t *d,uint8_t *k,size_t n){
    ta_model *m=(ta_model *)p;if(span(a,n)){memcpy(d,m->memory.ram+a-TF_RAM_BASE,n);memcpy(k,m->memory.known+a-TF_RAM_BASE,n);}
    else if(m->external_general.read)m->external_general.read(m->external_general.context,a,d,k,n);
    else if(m->external.read)m->external.read(m->external.context,a,d,k,n);
    else {memset(d,0,n);memset(k,0,n);}
}
static br_flow boot_free(void *p,uint32_t pointer){
    ta_model *m=(ta_model *)p;gb_request r;gb_scalar v;
    memset(&r,0,sizeof(r));r.kind=GB_ROM_FREE;r.target=104;r.callsite=0x1b8a;
    r.argument_count=1;r.arguments[0]=pointer;r.known[0]=UINT32_MAX;
    {gb_flow f=general_invoke(m,&m->general,&r,&v);return f==GB_RETURNED?BR_RETURNED:f==GB_TRANSFER?BR_TRANSFER:BR_HALT;}
}
static br_flow boot_callback(void *p,br_model *b,uint32_t cb,uint32_t argument){
    ta_model *m=(ta_model *)p;(void)b;m->transport=TC_GATT;
    {nc_flow f=ta_dispatch_native(m,cb,argument);return f==NC_RETURNED?BR_RETURNED:f==NC_TRANSFER?BR_TRANSFER:BR_HALT;}
}
static br_flow boot_uart_command(void *p,br_model *b,uint8_t command,uint32_t address,uint16_t length){
    ta_model *m=(ta_model *)p;uint32_t stay,task;gb_request r;gb_scalar result;(void)b;(void)address;(void)length;
    m->transport=TC_UART;
    if(!get(m,0x2000408c,1,&stay))return BR_HALT;
    if(command=='I' && !stay){
        if(m->startup_enabled){
            {bs_flow f=bs_stay(&m->startup);if(f!=BS_RETURNED)return f==BS_TRANSFER?BR_TRANSFER:BR_HALT;}
        }else{
        put(m,0x2000408c,1,1);
        if(br_stop_startup(&m->boot)==TF_UNKNOWN)return BR_HALT;
        if(!get(m,0x2000408d,1,&task))return BR_HALT;
        if(feature_rom(m,80,(uint8_t)task,1,0)==TF_UNKNOWN)return BR_HALT;
        memset(&r,0,sizeof(r));r.kind=GB_NATIVE_HELPER;r.target=0x1d54;r.callsite=0x253e;
        r.argument_count=1;r.arguments[0]=3;r.known[0]=UINT32_MAX;
        {gb_flow f=general_invoke(m,&m->general,&r,&result);if(f!=GB_RETURNED)return f==GB_TRANSFER?BR_TRANSFER:BR_HALT;}
        }
    }
    import_uart(m);import_active(m);if(m->ota.interpretation_halted)return BR_HALT;
    tc_uart_command(&m->ota);export_call_state(m);
    if(m->ota.transferred||m->transferred){transfer(m);return BR_TRANSFER;}return m->ota.stalled||m->ota.outcome==TC_INDETERMINATE?BR_HALT:BR_RETURNED;
}
void ta_set_general_backend(ta_model *m,const gb_backend *source){
    gb_backend b;br_backend boot;
    memset(&m->external_general,0,sizeof(m->external_general));if(source)m->external_general=*source;
    memset(&b,0,sizeof(b));b.context=m;b.invoke=general_invoke;b.reply=general_reply;b.schedule=general_schedule;b.read=general_read;b.report_command=report_command;
    gb_init(&m->general,&m->memory,&b);
    memset(&boot,0,sizeof(boot));boot.context=m;boot.rom_status=feature_rom;boot.free_argument=boot_free;
    boot.callback=boot_callback;boot.uart_command=boot_uart_command;br_init(&m->boot,&m->memory,&boot);
}
int ta_attach_candidate(ta_model *m,rc_adapter *a){
    if(!a || a->memory!=&m->memory || a->profile!=RC_WCH_64BE955_V130)return 0;
    m->candidate=a;
    if(!bs_attach_candidate(&m->startup,a))return 0;
    bind_kernel(m);return m->kernel.flow==RK_RETURNED;
}
br_flow ta_boot_cold_start(ta_model *m,const uint8_t *source,size_t length){if(m->transferred||m->ota.transferred)return BR_TRANSFER;
    br_flow flow;if(m->ota.image!=TC_BOOT)return BR_HALT;
    flow=br_cold_start(&m->boot,source,length);import_active(m);return flow;
}
size_t ta_receive_uart(ta_model *m,const uint8_t *bytes,size_t n,uint32_t now){
    size_t used;if(m->transferred||m->ota.transferred||m->ota.image!=TC_BOOT || m->ota.stalled || m->ota.interpretation_halted){m->halted=1;return 0;}
    m->transport=TC_UART;used=br_uart_receive(&m->boot,bytes,n,now);
    if(m->boot.flow==BR_TRANSFER)transfer(m);else m->halted=m->boot.flow==BR_HALT;m->transport=TC_GATT;return used;
}
uint16_t ta_dispatch_boot(ta_model *m,uint16_t events){if(m->transferred||m->ota.transferred)return events;
    if(m->ota.image!=TC_BOOT){m->halted=1;return events;}
    m->callback_return_boundary=0;
    return br_dispatch(&m->boot,events);
}
static gb_flow helper_invoke(void *p,gh_model *h,const gh_request *r,gb_scalar *v){
    ta_model *m=(ta_model *)p;uint32_t value;int status;(void)h;
    if(r->kind==GH_ROM&&r->callsite>=0x16f4a&&r->callsite<0x171c2){
        /* Typed core provider takes precedence; no fallback after its HALT.
           In particular rawFFFFFFFF from ROM128 is not TF_UNKNOWN. */
        if(m->external_helpers.invoke)return m->external_helpers.invoke(m->external_helpers.context,h,r,v);
        if((r->target==88&&r->argument_count==3)||((r->target==80||r->target==92)&&r->argument_count==2)){
            status=feature_rom(m,r->target,(uint8_t)r->arguments[0],(uint16_t)r->arguments[1],r->argument_count==3?r->arguments[2]:0);
            if(status==TF_UNKNOWN)return GB_HALT;v->value=(uint32_t)status;v->known=UINT32_MAX;return GB_RETURNED;
        }
        return GB_HALT;
    }
    if(r->callsite>=0x9388&&r->callsite<0x94cc&&m->external_receive.invoke&&
       ((r->kind==GH_ROM&&(r->target==104||r->target==112))||r->kind==GH_MMIO_READ||r->kind==GH_MMIO_WRITE)){
        /* The shared native body exposes primitives, without calling CR's
           separate pulse algorithm or inventing known argument bits. */
        cr_request q;cr_result out;cr_flow f;unsigned i;memset(&q,0,sizeof(q));memset(&out,0,sizeof(out));
        q.va=r->callsite;q.count=r->argument_count;
        for(i=0;i<q.count;i++){q.arguments[i]=r->arguments[i];q.argument_known[i]=r->known[i];}
        if(r->kind==GH_ROM){q.operation=r->target==112?CR_ALLOC:CR_FREE;q.slot=r->target;q.target=0x40000+r->target;}
        else{q.operation=r->kind==GH_MMIO_READ?CR_MMIO_READ:CR_MMIO_WRITE;q.target=r->target;q.width=r->width*8u;
             if(r->argument_count){q.value=r->arguments[0];q.known=r->known[0];}q.count=0;}
        f=m->external_receive.invoke(m->external_receive.context,&m->receive,&q,&out);
        v->value=out.value;v->known=out.known;return f==CR_RETURNED?GB_RETURNED:f==CR_TRANSFER?GB_TRANSFER:GB_HALT;
    }
    if(r->kind==GH_NATIVE&&(r->target==0x13160||r->target==0x135d4)){
        if(r->argument_count&&r->known[0]!=UINT32_MAX)return GB_HALT;
        v->value=0;v->known=0;return ta_dispatch_deep(m,r->target,r->argument_count?r->arguments[0]:0);
    }
    if(r->kind==GH_ROM && m->candidate){
        if(r->target==104 && r->argument_count==1){if(!rc_msg_deallocate(m->candidate,r->arguments[0],&value))return GB_HALT;v->value=value;v->known=UINT32_MAX;return GB_RETURNED;}
        if(r->target==112 && r->argument_count==1){if(!rc_msg_allocate_register(m->candidate,r->arguments[0],&value))return GB_HALT;v->value=value;v->known=UINT32_MAX;return GB_RETURNED;}
        if(r->target==124 && r->argument_count==0){if(!rc_clock_get(m->candidate,&value))return GB_HALT;v->value=value;v->known=UINT32_MAX;return GB_RETURNED;}
    }
    if(r->kind==GH_ROM && r->target==92 && r->argument_count==2){
        status=feature_rom(m,92,(uint8_t)r->arguments[0],(uint16_t)r->arguments[1],0);
        if(status==TF_UNKNOWN)return GB_HALT;v->value=(uint32_t)status;v->known=UINT32_MAX;return GB_RETURNED;
    }
    return m->external_helpers.invoke?m->external_helpers.invoke(m->external_helpers.context,h,r,v):GB_HALT;
}
static gb_flow helper_reply(void *p,gh_model *h,const gb_reply_request *r){ta_model *m=(ta_model *)p;(void)h;return general_reply(m,&m->general,r);}
static gb_flow helper_schedule(void *p,gh_model *h,uint32_t callback,uint32_t mode,uint32_t delay,uint32_t argument,gb_scalar *v){ta_model *m=(ta_model *)p;(void)h;return general_schedule(m,&m->general,callback,mode,delay,argument,v);}
void ta_set_helper_backend(ta_model *m,const gh_backend *external){gh_backend b;memset(&m->external_helpers,0,sizeof(m->external_helpers));if(external)m->external_helpers=*external;memset(&b,0,sizeof(b));b.context=m;b.invoke=helper_invoke;b.reply=helper_reply;b.schedule=helper_schedule;gh_init(&m->helpers,&m->memory,&b);}
gb_flow ta_dispatch_dnd(ta_model *m,uint32_t entry,uint32_t a0,uint32_t a1,gb_scalar *out){gb_flow f;
    if(m->transferred||m->ota.transferred)return GB_TRANSFER;
    if(m->ota.image!=TC_RUNTIME||!dnd_helper_entry(entry)){unresolved(m,entry);m->halted=1;return GB_HALT;}
    f=gh_dispatch_pair(&m->helpers,entry,a0,a1,out);
    if(f==GB_TRANSFER)transfer(m);else if(f==GB_HALT){unresolved(m,m->helpers.boundary_address);m->halted=1;}
    return f;
}
static int startup_allocate(void *p,uint32_t n,uint32_t *out){ta_model *m=(ta_model *)p;if(m->external_startup.msg_allocate)return m->external_startup.msg_allocate(m->external_startup.context,n,out);return 0;}
static int startup_free(void *p,uint32_t pointer){ta_model *m=(ta_model *)p;if(m->external_startup.msg_deallocate)return m->external_startup.msg_deallocate(m->external_startup.context,pointer);return 0;}
static bs_flow startup_hal(void *p,bs_model *b,const bs_request *r,bs_result *out){
    ta_model *m=(ta_model *)p;uint32_t clock;
    if(r->operation==BS_CLOCK && m->candidate){
        /* Fresh BOOT11A2: ROM124 -> low32 multiply10 -> logical shift4. */
        if(!rc_clock_get(m->candidate,&clock))return BS_HALT;
        out->value=(clock*UINT32_C(10))>>4;out->known=UINT32_MAX;return BS_RETURNED;
    }
    return m->external_startup.hal?m->external_startup.hal(m->external_startup.context,b,r,out):BS_HALT;
}
static void bind_startup(ta_model *m){bs_backend b;memset(&b,0,sizeof(b));b.context=m;b.msg_allocate=startup_allocate;b.msg_deallocate=startup_free;b.rom_status=feature_rom;b.hal=startup_hal;bs_init(&m->startup,&m->memory,&b);if(m->candidate)(void)bs_attach_candidate(&m->startup,m->candidate);}
static tc_flow candidate_uart_reply(void *p,tc_model *core){
    ta_model *m=(ta_model *)p;bs_uart_view view;bs_flow flow;
    if(m->ota.image!=TC_BOOT||core->reply_length>UINT32_MAX)return TC_FLOW_UNKNOWN;
    view.data=core->reply_data;view.known=core->reply_mask;view.available=(uint32_t)sizeof(core->reply_data);
    export_call_state(m);flow=bs_uart_reply_view(&m->startup,core->reply_command,&view,(uint32_t)core->reply_length);import_call_state(m);
    if(flow==BS_TRANSFER){transfer(m);return TC_TRANSFER;}if(flow!=BS_RETURNED||core->interpretation_halted){m->halted=1;unresolved(m,m->startup.boundary_address);core->reply_queued=TC_UNKNOWN;return TC_FLOW_UNKNOWN;}
    core->reply_queued=TC_YES;return TC_RETURNED;
}
void ta_set_startup_backend(ta_model *m,const bs_backend *external){memset(&m->external_startup,0,sizeof(m->external_startup));if(external)m->external_startup=*external;m->startup_enabled=1;bind_startup(m);m->ota.backend.uart_wrapper=m->ota.image==TC_BOOT?candidate_uart_reply:NULL;}
bs_flow ta_dispatch_startup(ta_model *m,uint16_t events,uint16_t *out){if(m->transferred||m->ota.transferred)return BS_TRANSFER;bs_flow flow;if(m->ota.image!=TC_BOOT)return BS_HALT;flow=bs_startup_dispatch(&m->startup,events,out);if(flow!=BS_RETURNED){m->halted=1;if(flow==BS_TRANSFER)transfer(m);else if(flow==BS_HALT)unresolved(m,m->startup.boundary_address);}return flow;}
bs_flow ta_pattern_irq(ta_model *m){if(m->transferred||m->ota.transferred)return BS_TRANSFER;bs_flow flow;if(m->ota.image!=TC_BOOT)return BS_HALT;flow=bs_pattern_irq(&m->startup);if(flow!=BS_RETURNED){m->halted=1;if(flow==BS_TRANSFER)transfer(m);else unresolved(m,m->startup.boundary_address);}return flow;}
static rk_flow kernel_invoke(void *p,rk_model *k,const rk_request *r,rk_result *out){
    ta_model *m=(ta_model *)p;uint16_t returned;uint32_t before;bs_flow flow;
    if(r->kind==RK_TASK_HANDLER && r->count==2){
        if(r->target==0x170e2&&m->ota.image==TC_RUNTIME){gb_scalar value;gb_flow f=ta_dispatch_dnd(m,0x170e2,r->arguments[0],r->arguments[1],&value);if(f==GB_TRANSFER)return RK_TRANSFER;if(f!=GB_RETURNED||(value.known&65535)!=65535)return RK_HALT;out->value=value.value;out->known=value.known;return RK_RETURNED;}
        if(r->target==SC_TASK&&m->ota.image==TC_RUNTIME){sc_arguments a;sc_flow f;memset(&a,0,sizeof(a));a.registers[0]=r->arguments[0];a.registers[1]=r->arguments[1];f=ta_dispatch_spi(m,SC_TASK,&a);if(f==SC_TRANSFER)return RK_TRANSFER;if(f!=SC_RETURNED||!m->spi.result_defined||(m->spi.result_known&65535)!=65535)return RK_HALT;out->value=m->spi.result;out->known=m->spi.result_known;return RK_RETURNED;}
        if(r->target==0x8ff8 && m->ota.image==TC_RUNTIME){before=m->memory.unknown_effects;returned=ta_dispatch_runtime(m,(uint16_t)r->arguments[1]);if(m->transferred||m->ota.transferred||m->native_callbacks.flow==NC_TRANSFER)return RK_TRANSFER;if(m->halted || m->ota.interpretation_halted || m->memory.unknown_effects!=before){m->halted=1;return RK_HALT;}out->value=returned;out->known=UINT32_MAX;return RK_RETURNED;}
        if(r->target==0x1a64 && m->ota.image==TC_BOOT){returned=ta_dispatch_boot(m,(uint16_t)r->arguments[1]);if(m->transferred||m->ota.transferred||m->native_callbacks.flow==NC_TRANSFER)return RK_TRANSFER;if(m->boot.flow==BR_HALT)return RK_HALT;out->value=returned;out->known=UINT32_MAX;return RK_RETURNED;}
        if(r->target==0x24a8 && m->ota.image==TC_BOOT){flow=ta_dispatch_startup(m,(uint16_t)r->arguments[1],&returned);if(flow==BS_TRANSFER)return RK_TRANSFER;if(flow!=BS_RETURNED)return RK_HALT;out->value=returned;out->known=UINT32_MAX;return RK_RETURNED;}
    }
    return m->external_kernel.invoke?m->external_kernel.invoke(m->external_kernel.context,k,r,out):RK_HALT;
}
static void bind_kernel(ta_model *m){rk_backend b;b.context=m;b.invoke=kernel_invoke;if(m->candidate)(void)rk_attach(&m->kernel,m->candidate,&b);}
void ta_set_kernel_backend(ta_model *m,const rk_backend *external){memset(&m->external_kernel,0,sizeof(m->external_kernel));if(external)m->external_kernel=*external;bind_kernel(m);}
rk_flow ta_system_process(ta_model *m){rk_flow flow;if(m->transferred||m->ota.transferred)return RK_TRANSFER;if(!m->candidate||m->halted||m->ota.interpretation_halted)return RK_HALT;flow=rk_system_process(&m->kernel);if(flow!=RK_RETURNED){m->halted=1;if(flow==RK_TRANSFER)transfer(m);else if(flow==RK_HALT)unresolved(m,m->kernel.unknown_address);}return flow;}
rk_flow ta_msg_receive(ta_model *m,uint8_t task,uint32_t *out){rk_flow flow;if(!m->candidate)return RK_HALT;flow=rk_msg_receive(&m->kernel,task,out);if(flow!=RK_RETURNED){m->halted=1;unresolved(m,m->kernel.unknown_address);}return flow;}
static nc_flow native_invoke(void *p,nc_model *n,const nc_request *r,nc_result *out){
    ta_model *m=(ta_model *)p;uint32_t value;(void)n;
    if(m->flash_enabled&&r->kind==NC_FLASH_CALL){fp_source source;fp_flow flow;memset(&source,0,sizeof(source));source.kind=FP_VALUE_VIEW;source.data=r->data;source.known=r->known;source.available=r->length;flow=fp_dispatch_helper(&m->flash,r->target,r->count?r->arguments[0]:0,r->source==NC_VALUE_VIEW?&source:NULL);return flow==FP_RETURNED?NC_RETURNED:flow==FP_TRANSFER?NC_TRANSFER:NC_HALT;}
    if(m->external_native.invoke)return m->external_native.invoke(m->external_native.context,n,r,out);
    if(!m->candidate||m->candidate->profile!=RC_WCH_64BE955_V130||m->candidate->fault)return NC_HALT;
    if(r->kind==NC_ROM_SCALAR&&r->slot==124&&m->candidate){if(!rc_clock_get(m->candidate,&value))return NC_HALT;out->value=value;out->known=UINT32_MAX;return NC_RETURNED;}
    if(r->kind==NC_ROM_COPY&&r->slot==76&&m->candidate&&r->destination==NC_VALUE_VIEW&&r->length<=sizeof(out->data)){
        out->length=r->length;
        if(r->source==NC_VALUE_VIEW){memcpy(out->data,r->data,r->length);memcpy(out->bytes_known,r->known,r->length);return NC_RETURNED;}
        if(r->source==NC_ADDRESS){
            if(!r->source_address){memset(out->bytes_known,0,r->length);return NC_RETURNED;}
            if(span(r->source_address,r->length)){memcpy(out->data,m->memory.ram+r->source_address-TF_RAM_BASE,r->length);memcpy(out->bytes_known,m->memory.known+r->source_address-TF_RAM_BASE,r->length);return NC_RETURNED;}
            if(m->external.read){m->external.read(m->external.context,r->source_address,out->data,out->bytes_known,r->length);return NC_RETURNED;}
        }
    }
    return NC_HALT;
}
void ta_set_native_backend(ta_model *m,const nc_backend *external){nc_backend b;memset(&m->external_native,0,sizeof(m->external_native));if(external)m->external_native=*external;memset(&b,0,sizeof(b));b.context=m;b.invoke=native_invoke;nc_init(&m->native_callbacks,&m->memory,&b);}
nc_flow ta_dispatch_native(ta_model *m,uint32_t callback,uint32_t argument){if(m->transferred||m->ota.transferred)return NC_TRANSFER;
    nc_callback entry;nc_flow flow;if(!native_entry(m->ota.image,callback,&entry)){m->halted=1;unresolved(m,callback);return NC_HALT;}
    flow=nc_run(&m->native_callbacks,entry,argument);import_active(m);m->callback_return_boundary=flow==NC_HALT?callback:0;
    if(flow!=NC_RETURNED){m->halted=1;if(flow==NC_TRANSFER)transfer(m);else if(flow==NC_HALT)unresolved(m,m->native_callbacks.unknown_address);}
    return flow;
}
static gb_flow deep_invoke(void *p,gd_model *d,const gd_request *r,gb_scalar *out){
    ta_model *m=(ta_model *)p;uint32_t value,source,offset;(void)d;out->value=0;out->known=0;
    if(m->external_deep.invoke)return m->external_deep.invoke(m->external_deep.context,d,r,out);
    if(r->kind!=GD_ROM||!m->candidate||m->candidate->profile!=RC_WCH_64BE955_V130||m->candidate->fault)return GB_HALT;
    if(r->target==96&&r->argument_count==2&&r->known[0]==UINT32_MAX&&r->known[1]==UINT32_MAX){
        if(!rc_timer_remaining(m->candidate,r->arguments[0],(uint16_t)r->arguments[1],&value))return GB_HALT;out->value=value;out->known=UINT32_MAX;return GB_RETURNED;
    }
    if((r->target!=72&&r->target!=76)||r->argument_count!=3||!r->buffer||!r->buffer_known||r->known[1]!=UINT32_MAX||r->known[2]!=UINT32_MAX||r->buffer_length!=r->arguments[2])return GB_HALT;
    if(r->target==72){memset(r->buffer,(uint8_t)r->arguments[1],r->buffer_length);memset(r->buffer_known,255,r->buffer_length);return GB_RETURNED;}
    source=r->arguments[1];if(!source||!r->buffer_length)return GB_RETURNED;
    if(span(source,r->buffer_length)){memcpy(r->buffer,m->memory.ram+source-TF_RAM_BASE,r->buffer_length);memcpy(r->buffer_known,m->memory.known+source-TF_RAM_BASE,r->buffer_length);return GB_RETURNED;}
    offset=source>=0x08000000&&source<0x08080000?source-0x08000000:source;
    if(m->ota.image==TC_RUNTIME&&m->memory.runtime&&offset>=0x8000&&offset-0x8000<=m->memory.runtime_length&&r->buffer_length<=m->memory.runtime_length-(offset-0x8000)){
        memcpy(r->buffer,m->memory.runtime+offset-0x8000,r->buffer_length);memset(r->buffer_known,255,r->buffer_length);return GB_RETURNED;
    }
    if(m->external_general.read){m->external_general.read(m->external_general.context,source,r->buffer,r->buffer_known,r->buffer_length);return GB_RETURNED;}
    if(m->external.read){m->external.read(m->external.context,source,r->buffer,r->buffer_known,r->buffer_length);return GB_RETURNED;}
    return GB_HALT;
}
static gb_flow deep_reply(void *p,gd_model *d,const gb_reply_request *r){ta_model *m=(ta_model *)p;if(m->external_deep.reply)return m->external_deep.reply(m->external_deep.context,d,r);return general_reply(m,&m->general,r);}
void ta_set_deep_backend(ta_model *m,const gd_backend *external){gd_backend b;memset(&m->external_deep,0,sizeof(m->external_deep));if(external)m->external_deep=*external;memset(&b,0,sizeof(b));b.context=m;b.invoke=deep_invoke;b.reply=deep_reply;gd_init(&m->deep,&m->memory,&b);}
gb_flow ta_dispatch_deep(ta_model *m,uint32_t entry,uint32_t argument){if(m->transferred||m->ota.transferred)return GB_TRANSFER;gb_flow flow;if(m->ota.image!=TC_RUNTIME){m->halted=1;unresolved(m,entry);return GB_HALT;}flow=gd_dispatch(&m->deep,entry,argument);if(flow!=GB_RETURNED){m->halted=1;if(flow==GB_TRANSFER)transfer(m);else unresolved(m,m->deep.boundary_address);}return flow;}
static gb_flow reports_invoke(void *p,gr_model *g,const gr_request *r,gb_scalar *out){
    ta_model *m=(ta_model *)p;uint32_t source;size_t i;(void)g;out->value=0;out->known=0;
    if(m->external_reports.invoke)return m->external_reports.invoke(m->external_reports.context,g,r,out);
    if(!m->candidate||m->candidate->profile!=RC_WCH_64BE955_V130||m->candidate->fault||!m->memory.backend.memory_contracts)return GB_HALT;
    if(!r->buffer||!r->buffer_known||r->known[2]!=UINT32_MAX||r->buffer_length!=r->arguments[2])return GB_HALT;
    if(r->target==72){memset(r->buffer,0,r->buffer_length);memset(r->buffer_known,255,r->buffer_length);return GB_RETURNED;}
    if(r->target!=76)return GB_HALT;
    if(r->known[1]!=UINT32_MAX){if(!r->input||!r->input_known)return GB_HALT;for(i=0;i<r->buffer_length;i++){r->buffer[i]=r->input[i];r->buffer_known[i]=r->input_known[i];}return GB_RETURNED;}
    source=r->arguments[1];if(!source||!r->buffer_length)return GB_RETURNED;
    if(span(source,r->buffer_length)){for(i=0;i<r->buffer_length;i++){r->buffer[i]=m->memory.ram[source-TF_RAM_BASE+i];r->buffer_known[i]=m->memory.known[source-TF_RAM_BASE+i];}return GB_RETURNED;}
    if(m->external_general.read){m->external_general.read(m->external_general.context,source,r->buffer,r->buffer_known,r->buffer_length);return GB_RETURNED;}
    if(m->external.read){m->external.read(m->external.context,source,r->buffer,r->buffer_known,r->buffer_length);return GB_RETURNED;}
    return GB_HALT;
}
static gb_flow reports_reply(void *p,gr_model *g,const gb_reply_request *r){ta_model *m=(ta_model *)p;if(m->external_reports.reply)return m->external_reports.reply(m->external_reports.context,g,r);return general_reply(m,&m->general,r);}
void ta_set_reports_backend(ta_model *m,const gr_backend *external){gr_backend b;memset(&m->external_reports,0,sizeof(m->external_reports));if(external)m->external_reports=*external;memset(&b,0,sizeof(b));b.context=m;b.invoke=reports_invoke;b.reply=reports_reply;gr_init(&m->reports,&m->memory,&b);}
static gb_flow report_command(void *p,gb_model *g,uint16_t h,uint8_t cmd,uint32_t address,uint16_t length){ta_model *m=(ta_model *)p;gb_flow flow=gr_command(&m->reports,h,cmd,address,length);if(flow!=GB_RETURNED){g->boundary_va=m->reports.boundary_va;g->boundary_address=m->reports.boundary_address;}return flow;}
gb_flow ta_dispatch_report_d1(ta_model *m,uint32_t address){if(m->transferred||m->ota.transferred)return GB_TRANSFER;gb_flow flow;if(m->ota.image!=TC_RUNTIME){m->halted=1;unresolved(m,address);return GB_HALT;}flow=gr_d1(&m->reports,address);if(flow!=GB_RETURNED){m->halted=1;if(flow==GB_TRANSFER)transfer(m);else unresolved(m,m->reports.boundary_address);}return flow;}
static fp_flow flash_invoke(void *p,fp_model *f,const fp_request *r,fp_scalar *out){ta_model *m=(ta_model *)p;return m->external_flash.invoke?m->external_flash.invoke(m->external_flash.context,f,r,out):FP_HALT;}
void ta_set_flash_backend(ta_model *m,const fp_backend *external){fp_backend b;memset(&m->external_flash,0,sizeof(m->external_flash));if(external)m->external_flash=*external;memset(&b,0,sizeof(b));b.context=m;b.invoke=flash_invoke;fp_init(&m->flash,&m->memory,m->ota.image==TC_BOOT?FP_BOOT:FP_RUNTIME,&b);m->flash_enabled=1;}
fp_flow ta_program_page(ta_model *m,uint32_t address,const fp_source *source){if(m->transferred||m->ota.transferred)return FP_TRANSFER;fp_flow flow=fp_program_page(&m->flash,address,source);if(flow!=FP_RETURNED){m->halted=1;if(flow==FP_TRANSFER)transfer(m);else if(flow==FP_HALT)unresolved(m,m->flash.boundary_address);}return flow;}
static int spi_byte_read(ta_model *m,const sc_buffer *b,uint32_t i,uint8_t *v,uint8_t *k){uint32_t address;if(b->kind==SC_VIEW){if(!b->data||!b->known||i>=b->available)return 0;*v=b->data[i];*k=b->known[i];return 1;}if(b->kind!=SC_RAM)return 0;address=b->address+i;if(span(address,1)){*v=m->memory.ram[address-TF_RAM_BASE];*k=m->memory.known[address-TF_RAM_BASE];return 1;}if(m->external.read){m->external.read(m->external.context,address,v,k,1);return 1;}return 0;}
static int spi_byte_write(ta_model *m,const sc_buffer *b,uint32_t i,uint8_t v,uint8_t k){uint32_t address;if(b->kind==SC_VIEW){if(!b->data||!b->known||i>=b->available)return 0;b->data[i]=v;b->known[i]=k;return 1;}if(b->kind!=SC_RAM)return 0;address=b->address+i;if(!span(address,1))return 0;m->memory.ram[address-TF_RAM_BASE]=v;m->memory.known[address-TF_RAM_BASE]=k;return 1;}
static sc_flow spi_invoke(void *p,sc_model *s,const sc_request *r,sc_result *out){
    ta_model *m=(ta_model *)p;uint32_t value=0,i;uint8_t task=0,v,k;int ok=0;
    if(m->external_spi.invoke)return m->external_spi.invoke(m->external_spi.context,s,r,out);
    if(!m->candidate||m->candidate->profile!=RC_WCH_64BE955_V130||m->candidate->fault)return SC_HALT;
    if(r->operation==SC_ROM_COPY||r->operation==SC_ROM_MEMSET){
        if(!m->memory.backend.memory_contracts)return SC_HALT;
        if((r->source.kind==SC_RAM&&!r->source.address)||(r->destination.kind==SC_RAM&&!r->destination.address)||!r->length){out->memory_effects=1;return SC_RETURNED;}
        for(i=0;i<r->length;i++){
            if(r->operation==SC_ROM_COPY){if(!spi_byte_read(m,&r->source,i,&v,&k))return SC_HALT;}
            else{v=(uint8_t)r->arguments[0];k=255;}
            if(!spi_byte_write(m,&r->destination,i,v,k))return SC_HALT;
        }
        out->memory_effects=1;return SC_RETURNED;
    }
    if(r->operation!=SC_ROM_CALL)return SC_HALT;
    if(r->count>3)return SC_HALT;
    for(i=0;i<r->count;i++)if(r->argument_known[i]!=UINT32_MAX)return SC_HALT;
    if(r->slot==128&&r->count==1){ok=rc_task_register(m->candidate,r->arguments[0],&task);value=task;}
    else if(r->slot==124&&r->count==0)ok=rc_clock_get(m->candidate,&value);
    else if(r->slot==80&&r->count==2)ok=rc_set_event(m->candidate,r->arguments[0],(uint16_t)r->arguments[1],&value);
    else if(r->slot==84&&r->count==2)ok=rc_clear_event(m->candidate,r->arguments[0],(uint16_t)r->arguments[1],&value);
    else if(r->slot==88&&r->count==3)ok=rc_timer_start(m->candidate,r->arguments[0],(uint16_t)r->arguments[1],r->arguments[2],&value);
    else if(r->slot==92&&r->count==2)ok=rc_timer_stop(m->candidate,r->arguments[0],(uint16_t)r->arguments[1],&value);
    else if(r->slot==556&&r->count==3)ok=rc_timer_reload(m->candidate,r->arguments[0],(uint16_t)r->arguments[1],r->arguments[2],&value);
    if(!ok)return SC_HALT;out->value=value;out->known=UINT32_MAX;return SC_RETURNED;
}
void ta_set_spi_backend(ta_model *m,const sc_backend *external){sc_backend b;memset(&m->external_spi,0,sizeof(m->external_spi));if(external)m->external_spi=*external;memset(&b,0,sizeof(b));b.context=m;b.invoke=spi_invoke;sc_init(&m->spi,&m->memory,&b);}
sc_flow ta_dispatch_spi(ta_model *m,uint32_t entry,const sc_arguments *arguments){if(m->transferred||m->ota.transferred)return SC_TRANSFER;sc_flow flow;if(m->ota.image!=TC_RUNTIME){m->halted=1;unresolved(m,entry);return SC_HALT;}flow=sc_run(&m->spi,entry,arguments);if(flow!=SC_RETURNED){m->halted=1;if(flow==SC_TRANSFER)transfer(m);else if(flow==SC_HALT)unresolved(m,m->spi.unknown_address);}return flow;}
static int receive_read(ta_model*m,const cr_buffer*b,uint32_t i,uint8_t*v,uint8_t*k){
    uint32_t a,offset;if(b->kind==CR_VIEW){if(!b->data||!b->known||i>=b->available)return 0;*v=b->data[i];*k=b->known[i];return 1;}
    if(b->kind!=CR_RAM)return 0;a=b->address+i;
    if(span(a,1)){*v=m->memory.ram[a-TF_RAM_BASE];*k=m->memory.known[a-TF_RAM_BASE];return 1;}
    offset=a>=0x08000000&&a<0x08080000?a-0x08000000:a;
    if(m->memory.runtime&&offset>=0x8000&&offset-0x8000<m->memory.runtime_length){*v=m->memory.runtime[offset-0x8000];*k=255;return 1;}
    if(m->external_general.read||m->external.read){general_read(m,a,v,k,1);return 1;}return 0;
}
static int receive_write(ta_model*m,const cr_buffer*b,uint32_t i,uint8_t v,uint8_t k){
    uint32_t a;if(b->kind==CR_VIEW){if(!b->data||!b->known||i>=b->available)return 0;b->data[i]=v;b->known[i]=k;return 1;}
    if(b->kind!=CR_RAM)return 0;a=b->address+i;if(!span(a,1))return 0;m->memory.ram[a-TF_RAM_BASE]=v;m->memory.known[a-TF_RAM_BASE]=k;return 1;
}
static cr_flow receive_gb(gb_flow f){return f==GB_RETURNED?CR_RETURNED:f==GB_TRANSFER?CR_TRANSFER:CR_HALT;}
cr_flow ta_receive_primitive(ta_model*m,const cr_request*q,cr_result*out){
    uint32_t i,p=0,status=0;uint8_t v,k;gb_reply_request reply;gr_view view;sc_arguments args;sc_flow f;
    if(!m||!q||!out)return CR_HALT;memset(out,0,sizeof(*out));if(m->transferred||m->ota.transferred)return CR_TRANSFER;
    if(q->operation==CR_SCHEDULE){
        int result;
        if(m->ota.image!=TC_RUNTIME||q->target!=0x9102||q->count!=4)return CR_HALT;
        for(i=0;i<4;i++)if(q->argument_known[i]!=UINT32_MAX)return CR_HALT;
        result=tf_schedule(&m->memory,q->arguments[0],q->arguments[1],q->arguments[2],q->arguments[3]);m->last_schedule_result=result;
        if(m->transferred||m->ota.transferred)return CR_TRANSFER;
        if(result==TF_UNKNOWN)return CR_HALT;
        out->value=(uint32_t)result;out->known=UINT32_MAX;return CR_RETURNED;
    }
    if(q->operation==CR_GENERAL_CALL){
        gb_scalar ignored;gb_flow flow;
        if(q->target!=0x13a62||q->count!=1)return CR_HALT;
        /*13A62 never dereferences its incoming a0; a borrowed native SP remains
          unknown in the request. Its incidental return scalar is not exposed. */
        memset(&ignored,0,sizeof(ignored));flow=gh_dispatch(&m->helpers,q->target,q->arguments[0],&ignored);
        return receive_gb(flow);
    }
    if(q->operation==CR_REPLY){
        if(q->count!=4||q->argument_known[0]!=UINT32_MAX||q->argument_known[1]!=UINT32_MAX||q->argument_known[3]!=UINT32_MAX||q->arguments[3]>1040)return CR_HALT;
        memset(&reply,0,sizeof(reply));reply.wrapper_va=0x8cfa;reply.handle=(uint16_t)q->arguments[0];reply.command=(uint8_t)q->arguments[1];reply.length=q->arguments[3];
        if(q->source.kind==CR_RAM){reply.source_address=q->source.address;return receive_gb(reply_view(m,&reply,0));}
        if(q->source.kind!=CR_VIEW)return CR_HALT;reply.data=q->source.data;reply.known=q->source.known;return receive_gb(reply_view(m,&reply,q->source.available));
    }
    if(q->operation==CR_D1_TAIL){
        memset(&view,0,sizeof(view));if(q->source.kind==CR_RAM)view.address=q->source.address;
        else if(q->source.kind==CR_VIEW){view.data=q->source.data;view.known=q->source.known;view.available=q->source.available;}else return CR_HALT;
        return receive_gb(gr_d1_view(&m->reports,&view));
    }
    if(q->operation==CR_NATIVE_CALL){
        if((q->target!=SC_ROUTE_SEND&&q->target!=SC_ROUTE_FILTERS)||q->count>4)return CR_HALT;memset(&args,0,sizeof(args));
        for(i=0;i<q->count;i++){if(q->argument_known[i]!=UINT32_MAX&&!((q->target==SC_ROUTE_SEND&&i==0)||(q->target==SC_ROUTE_FILTERS&&i==1)))return CR_HALT;args.registers[i]=q->arguments[i];}
        if(q->source.kind==CR_RAM){args.buffer.kind=SC_RAM;args.buffer.address=q->source.address;}else if(q->source.kind==CR_VIEW){args.buffer.kind=SC_VIEW;args.buffer.data=q->source.data;args.buffer.known=q->source.known;args.buffer.available=q->source.available;}else return CR_HALT;
        f=ta_dispatch_spi(m,q->target,&args);return f==SC_RETURNED?CR_RETURNED:f==SC_TRANSFER?CR_TRANSFER:CR_HALT;
    }
    if(!m->candidate||m->candidate->profile!=RC_WCH_64BE955_V130||m->candidate->fault)return CR_HALT;
    if(q->operation==CR_COPY){
        if(!m->memory.backend.memory_contracts||q->slot!=76)return CR_HALT;
        if((q->source.kind==CR_RAM&&!q->source.address)||(q->destination.kind==CR_RAM&&!q->destination.address)||(q->argument_known[2]==UINT32_MAX&&!q->length)){out->memory_effects=1;return CR_RETURNED;}
        if(q->argument_known[2]!=UINT32_MAX)return CR_HALT;
        for(i=0;i<q->length;i++){if(!receive_read(m,&q->source,i,&v,&k)||!receive_write(m,&q->destination,i,v,k))return CR_HALT;}
        out->memory_effects=1;return CR_RETURNED;
    }
    if(q->operation==CR_ALLOC){if(q->count!=1||q->argument_known[0]!=UINT32_MAX||!rc_msg_allocate_register(m->candidate,q->arguments[0],&p))return CR_HALT;out->value=p;out->known=UINT32_MAX;return CR_RETURNED;}
    if(q->operation==CR_FREE){if(q->count!=1||q->argument_known[0]!=UINT32_MAX||!rc_msg_deallocate(m->candidate,q->arguments[0],&status))return CR_HALT;out->value=status;out->known=UINT32_MAX;return CR_RETURNED;}
    return CR_HALT; /* CSR and MMIO require an explicitly supplied provider. */
}
static cr_flow receive_invoke(void*p,cr_model*c,const cr_request*q,cr_result*out){ta_model*m=(ta_model*)p;return m->external_receive.invoke?m->external_receive.invoke(m->external_receive.context,c,q,out):ta_receive_primitive(m,q,out);}
void ta_set_receive_backend(ta_model*m,const cr_backend*external){cr_backend b;memset(&m->external_receive,0,sizeof(m->external_receive));if(external)m->external_receive=*external;memset(&b,0,sizeof(b));b.context=m;b.invoke=receive_invoke;cr_init(&m->receive,&m->memory,&b);}
cr_flow ta_dispatch_receive(ta_model*m,uint32_t entry,const cr_arguments*args){cr_flow f;if(m->transferred||m->ota.transferred)return CR_TRANSFER;if(m->ota.image!=TC_RUNTIME){m->halted=1;unresolved(m,entry);return CR_HALT;}f=cr_run(&m->receive,entry,args);if(f==CR_TRANSFER)transfer(m);else if(f==CR_HALT){m->halted=1;unresolved(m,m->receive.boundary_address);}return f;}
gb_flow ta_dispatch_report_d1_view(ta_model*m,const gr_view*record){gb_flow f;if(m->transferred||m->ota.transferred)return GB_TRANSFER;if(m->ota.image!=TC_RUNTIME){m->halted=1;unresolved(m,0x139e6);return GB_HALT;}f=gr_d1_view(&m->reports,record);if(f==GB_TRANSFER)transfer(m);else if(f==GB_HALT){m->halted=1;unresolved(m,m->reports.boundary_address);}return f;}
int ta_resume_activation(ta_model*m){
    if(!m->transferred&&!m->ota.transferred)return 0;m->transferred=0;(void)tc_resume_activation(&m->ota);m->halted=m->ota.interpretation_halted!=0;
    if(m->general.flow==GB_TRANSFER)m->general.flow=GB_RETURNED;if(m->helpers.flow==GB_TRANSFER)m->helpers.flow=GB_RETURNED;
    if(m->deep.flow==GB_TRANSFER)m->deep.flow=GB_RETURNED;if(m->reports.flow==GB_TRANSFER)m->reports.flow=GB_RETURNED;
    if(m->boot.flow==BR_TRANSFER)m->boot.flow=BR_RETURNED;if(m->startup.flow==BS_TRANSFER)m->startup.flow=BS_RETURNED;
    if(m->native_callbacks.flow==NC_TRANSFER)m->native_callbacks.flow=NC_RETURNED;if(m->kernel.flow==RK_TRANSFER)m->kernel.flow=RK_RETURNED;
    if(m->flash.flow==FP_TRANSFER)m->flash.flow=FP_RETURNED;if(m->spi.flow==SC_TRANSFER)sc_resume(&m->spi);if(m->receive.flow==CR_TRANSFER)cr_resume(&m->receive);return 1;
}
