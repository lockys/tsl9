#include "general_helpers.h"
#include <string.h>
#define AUTH UINT32_C(0x2000c790)
#define REG UINT32_C(0x2000be08)
#define PAT UINT32_C(0x2000bebc)
#define FULL UINT32_MAX
static int actions_body_pair(gh_model *,uint32_t,uint32_t,uint32_t,gb_scalar *);
static int halt(gh_model *m,uint32_t va,uint32_t address){m->flow=GB_HALT;m->boundary_va=va;m->boundary_address=address;return 0;}
static int returned(gh_model*m,gb_flow flow,uint32_t va,uint32_t address){if(flow==GB_RETURNED)return 1;if(flow==GB_TRANSFER){m->flow=flow;return 0;}return halt(m,va,address);}
static int inside(uint32_t a,unsigned n){return n<=TF_RAM_SIZE&&a>=TF_RAM_BASE&&a<=TF_RAM_BASE+TF_RAM_SIZE-n;}
static int load(gh_model *m,uint32_t a,unsigned n,uint32_t need,uint32_t *v,uint32_t site){unsigned i;uint32_t k=0;*v=0;
    if(!inside(a,n))return halt(m,site,a);
    for(i=0;i<n;i++){*v|=(uint32_t)m->memory->ram[a-TF_RAM_BASE+i]<<(8*i);k|=(uint32_t)m->memory->known[a-TF_RAM_BASE+i]<<(8*i);}
    return (k&need)==need?1:halt(m,site,a);
}
static int store(gh_model *m,uint32_t a,uint32_t v,unsigned n,uint32_t site){unsigned i;
    if(!inside(a,n))return halt(m,site,a);
    for(i=0;i<n;i++){m->memory->ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));m->memory->known[a-TF_RAM_BASE+i]=255;}return 1;
}
static int request(gh_model *m,gh_kind kind,uint32_t target,uint32_t site,
                   const uint32_t *a,unsigned argc,unsigned width,gb_scalar *out){unsigned i;gb_scalar ignored={0,0};gh_request r;
    memset(&r,0,sizeof(r));r.kind=kind;r.target=target;r.callsite=site;r.argument_count=argc;r.width=width;
    for(i=0;i<argc;i++){r.arguments[i]=a[i];r.known[i]=width==2?65535u:FULL;}
    m->last_request=r;++m->calls;if(!out)out=&ignored;out->value=0;out->known=0;
    return returned(m,m->backend.invoke?m->backend.invoke(m->backend.context,m,&r,out):GB_HALT,site,kind==GH_MMIO_READ||kind==GH_MMIO_WRITE?target:0);
}
static int need(gh_model *m,const gb_scalar *v,uint32_t mask,uint32_t site,uint32_t address){return (v->known&mask)==mask?1:halt(m,site,address);}
static int schedule(gh_model *m,uint32_t cb,uint32_t delay,uint32_t site,gb_scalar *out){gb_scalar ignored={0,0};gh_request r;
    if(!out)out=&ignored;out->value=0;out->known=0;memset(&r,0,sizeof(r));r.kind=GH_NATIVE;r.target=0x9102;r.callsite=site;r.argument_count=4;
    r.arguments[0]=cb;r.arguments[1]=0;r.arguments[2]=delay;r.arguments[3]=0;r.known[0]=r.known[1]=r.known[2]=r.known[3]=FULL;m->last_request=r;++m->schedules;
    return returned(m,m->backend.schedule?m->backend.schedule(m->backend.context,m,cb,0,delay,0,out):GB_HALT,site,cb);
}
static int reply_af2(gh_model *m,uint16_t handle,uint32_t site){const uint8_t value=2,known=255;gb_reply_request r;gh_request call;
    memset(&r,0,sizeof(r));r.wrapper_va=0x13d7a;r.source_address=0;r.handle=handle;r.command=0xaf;r.data=&value;r.known=&known;r.length=1;
    memset(&call,0,sizeof(call));call.kind=GH_NATIVE;call.target=r.wrapper_va;call.callsite=site;call.argument_count=3;
    call.arguments[0]=handle;call.arguments[1]=0xaf;call.arguments[2]=2;call.known[0]=call.known[1]=call.known[2]=FULL;m->last_request=call;++m->replies;
    return returned(m,m->backend.reply?m->backend.reply(m->backend.context,m,&r):GB_HALT,r.wrapper_va,0);
}
static int clock_value(gh_model *m,gb_scalar *out){return actions_body_pair(m,0x81b0,0,0,out);}
static int cancel(gh_model *m,uint32_t callback,gb_scalar *out){return actions_body_pair(m,0x908e,callback,0,out);}
static int pending(gh_model *m,gb_scalar *out){return actions_body_pair(m,0x133fa,0,0,out);}
static int deep_builder(gh_model *m,uint32_t target,uint32_t site,gb_scalar *out){const uint32_t args[1]={0};return request(m,GH_NATIVE,target,site,args,1,0,out);}
static int mode0(gh_model *m,gb_scalar *out){return actions_body_pair(m,0x13b5c,0,0,out);}
static int mode1(gh_model *m,uint32_t argument,gb_scalar *out){gb_scalar now;uint32_t h,mode,auth,last;int eligible=0;unsigned i;
    for(i=0;i<2;i++){
        uint32_t a=AUTH+4*i;
        if(!load(m,a+2,2,65535,&h,i?0x13a8e:0x13a68))return 0;if(h==65534)continue;
        if(!load(m,a+5,1,255,&mode,i?0x13a9a:0x13a7a))return 0;if(mode!=1)continue;
        if(!load(m,a+4,1,255,&auth,i?0x13aa4:0x13a84))return 0;if(auth){eligible=1;break;}
    }
    if(!eligible){out->value=argument;out->known=FULL;return 1;}
    if(!clock_value(m,&now)||!load(m,TF_GP+340,4,FULL,&last,0x13aba))return 0;
    if((uint32_t)(now.value-last)<=34)return schedule(m,0x135d4,35,0x13aea,out);
    if(!store(m,TF_GP+340,now.value,4,0x13aca))return 0;
    return deep_builder(m,0x135d4,0x13ad2,out);
}
static int pattern_allocate(gh_model *m,uint32_t count,gb_scalar *out){
 /* Legacy saved/error builders still consume a fully resolved pointer. */
 return actions_body_pair(m,0x93ee,count,0,out)&&need(m,out,FULL,0x9430,0);
}
static int pattern_submit(gh_model *m,uint32_t argument,gb_scalar *out){return actions_body_pair(m,0x9388,argument,0,out);}
static int pattern_build(gh_model *m,int postsave,gb_scalar *out){gb_scalar allocated;uint32_t p;unsigned i;
    static const uint16_t saved_values[7]={1165,130,0,1465,150,0,0};
    static const unsigned saved_order[7]={0,1,3,2,4,5,6};
    static const uint32_t saved_site[7]={0x9602,0x960a,0x9612,0x961c,0x9620,0x9624,0x9628};
    static const uint16_t error_values[7]={435,80,80,435,130,0,0};
    static const unsigned error_order[7]={0,3,1,2,4,5,6};
    static const uint32_t error_site[7]={0x94fc,0x9504,0x950e,0x9512,0x9516,0x951a,0x951e};
    if(!pattern_allocate(m,3,&allocated))return 0;p=allocated.value;
    if(!store(m,PAT+16,p,4,postsave?0x95f8:0x94f2))return 0;
    if(!p){*out=allocated;return 1;}
    for(i=0;i<7;i++){
        unsigned index=postsave?saved_order[i]:error_order[i];
        uint16_t v=postsave?saved_values[index]:error_values[index];
        if(!store(m,p+2*index,v,2,postsave?saved_site[i]:error_site[i]))return 0;
    }
    return pattern_submit(m,p,out);
}
static int recognized(uint32_t va){if(da_recognizes(va))return 1;switch(va){case 0x908e:case 0x13be8:case 0x13d9c:case 0x95ec:case 0x13a62:case 0x13b5c:case 0x133fa:case 0x13156:case 0x81aa:case 0x81b0:case 0x93ee:case 0x93cc:case 0x9388:case 0x94e6:return 1;default:return 0;}}
static int body(gh_model *,uint32_t,uint32_t,gb_scalar *);
static int register_body(gh_model *m,uint32_t cb,uint32_t a1,uint16_t a2,gb_scalar *out){const uint32_t args[3]={0,a1,a2};
    if(!store(m,PAT+4,1,1,0x94d8)||!store(m,PAT+8,a2,2,0x94dc)||!store(m,PAT+12,a1,4,0x94e0))return 0;
    return recognized(cb)?body(m,cb,0,out):request(m,GH_NATIVE,cb,0x94e4,args,3,0,out);
}
static int activation_report(gh_model *m,gb_scalar *out){unsigned i;uint32_t h,mode,auth;
    for(i=0;i<2;i++){
        uint32_t a=AUTH+4*i;
        if(!load(m,a+2,2,65535,&h,i?0x13ddc:0x13da8))return 0;if(h==65534)continue;
        if(!load(m,a+5,1,255,&mode,i?0x13de8:0x13dba))return 0;if(mode)continue;
        if(!load(m,a+4,1,255,&auth,i?0x13df2:0x13dc4))return 0;if(!auth)continue;
        /* Re-read handle after gates, matching native13DCE/13DFC load. */
        if(!load(m,a+2,2,65535,&h,i?0x13dfc:0x13dce)||!reply_af2(m,(uint16_t)h,i?0x13e06:0x13dd8))return 0;
    }
    return register_body(m,0x94e6,0,1,out);
}
/* R24 adapter: the exact same freestanding action source is also compiled
   alone for RV32. Its callbacks retain this host model's knowledge boundary. */
static da_flow action_flow(gb_flow f){return f==GB_RETURNED?DA_RETURNED:f==GB_TRANSFER?DA_TRANSFER:DA_HALT;}
static da_flow action_read(void *p,uint32_t address,unsigned width,uint32_t mask,uint32_t site,da_scalar *out){
 gh_model *m=(gh_model *)p;unsigned i;out->value=out->known=0;
 if(!load(m,address,width,mask,&out->value,site))return action_flow(m->flow);
 for(i=0;i<width;i++)out->known|=(uint32_t)m->memory->known[address-TF_RAM_BASE+i]<<(8*i);return DA_RETURNED;
}
static da_flow action_write(void *p,uint32_t address,uint32_t value,unsigned width,uint32_t known,uint32_t site){
 gh_model *m=(gh_model *)p;unsigned i;if(!inside(address,width)){halt(m,site,address);return DA_HALT;}
 for(i=0;i<width;i++){m->memory->ram[address-TF_RAM_BASE+i]=(uint8_t)(value>>(8*i));m->memory->known[address-TF_RAM_BASE+i]=(uint8_t)(known>>(8*i));}return DA_RETURNED;
}
static da_flow action_call(void *p,da_kind kind,uint32_t target,uint32_t site,const da_scalar *args,unsigned count,da_scalar *out){
 gh_model *m=(gh_model *)p;gb_scalar value={0,0};gh_request r;unsigned i;int ok;
 memset(&r,0,sizeof(r));r.target=target;r.callsite=site;r.kind=kind==DA_ROM?GH_ROM:GH_NATIVE;r.argument_count=count;
 if(kind==DA_MMIO_READ||kind==DA_MMIO_WRITE){
  unsigned width_index=kind==DA_MMIO_READ?0:1;
  if(count!=width_index+1||args[width_index].known!=FULL||args[width_index].value!=16){halt(m,site,target);return DA_HALT;}
  r.kind=kind==DA_MMIO_READ?GH_MMIO_READ:GH_MMIO_WRITE;r.width=2;r.argument_count=width_index;
 }
 for(i=0;i<r.argument_count;i++){r.arguments[i]=args[i].value;r.known[i]=args[i].known;if(r.width==2){r.arguments[i]&=65535;r.known[i]&=65535;}}
 m->last_request=r;++m->calls;
 ok=returned(m,m->backend.invoke?m->backend.invoke(m->backend.context,m,&r,&value):GB_HALT,site,r.width?target:0);
 out->value=value.value;out->known=value.known;return ok?DA_RETURNED:action_flow(m->flow);
}
static da_flow action_schedule(void *p,uint32_t callback,uint32_t ticks,uint32_t site,da_scalar *out){
 gh_model *m=(gh_model *)p;gb_scalar value={0,0};int ok=schedule(m,callback,ticks,site,&value);
 out->value=value.value;out->known=value.known;return ok?DA_RETURNED:action_flow(m->flow);
}
static int actions_body_pair(gh_model *m,uint32_t entry,uint32_t raw,uint32_t a1,gb_scalar *out){
 da_machine machine;da_backend io;da_scalar result;da_flow f;
 io.context=m;io.read=action_read;io.write=action_write;io.call=action_call;io.schedule=action_schedule;
 da_init(&machine,&io);f=da_run_pair(&machine,entry,raw,a1,&result);
 out->value=result.value;out->known=result.known;
 if(f!=DA_RETURNED){
  /* Keep a deeper modeled report/pattern failure rather than replacing
     that evidence with the freestanding module's declared callee edge. */
  if(m->flow==GB_RETURNED||!m->boundary_va){m->boundary_va=machine.boundary_va;m->boundary_address=machine.boundary_address;}
  m->flow=f==DA_TRANSFER?GB_TRANSFER:GB_HALT;return 0;
 }
 return 1;
}

static int body(gh_model *m,uint32_t entry,uint32_t argument,gb_scalar *out){gb_scalar ignored;uint32_t eligible;
    if(da_recognizes(entry))return actions_body_pair(m,entry,argument,0,out);
    switch(entry){
    case 0x133fa:return pending(m,out);
    case 0x13b5c:return mode0(m,out);
    case 0x13156:if(!store(m,AUTH,0,1,0x1315a))return 0;out->value=argument;out->known=FULL;return 1;
    case 0x13a62:return mode1(m,argument,out);
    case 0x13d9c:return activation_report(m,out);
    case 0x95ec:return pattern_build(m,1,out);
    case 0x94e6:return pattern_build(m,0,out);
    case 0x9388:return pattern_submit(m,argument,out);
    case 0x93cc:return actions_body_pair(m,entry,argument,0,out);
    case 0x93ee:return pattern_allocate(m,argument,out);
    case 0x81b0:return clock_value(m,out);
    case 0x13be8:
        if(!cancel(m,0x13be8,&ignored)||!mode0(m,&ignored)||!load(m,TF_GP+175,1,255,&eligible,0x81aa))return 0;
        if(!eligible)return schedule(m,0x13d9c,300,0x13c18,out);
        out->value=eligible;out->known=FULL;return 1;
    default:return halt(m,entry,0);
    }
}
void gh_init(gh_model *m,tf_model *ram,const gh_backend *io){memset(m,0,sizeof(*m));m->memory=ram;if(io)m->backend=*io;m->flow=GB_RETURNED;}
gb_flow gh_dispatch_pair(gh_model *m,uint32_t entry,uint32_t arg,uint32_t a1,gb_scalar *out){if(m->flow==GB_TRANSFER)return m->flow;gb_scalar ignored={0,0};m->entry=entry;m->argument=arg;m->recognized=(uint8_t)(recognized(entry));m->flow=GB_RETURNED;m->boundary_va=m->boundary_address=0;
    if(!out)out=&ignored;out->value=0;out->known=0;
    if(!m->memory)halt(m,entry,0);else if(da_recognizes(entry))actions_body_pair(m,entry,arg,a1,out);else body(m,entry,arg,out);return m->flow;
}
gb_flow gh_dispatch(gh_model *m,uint32_t entry,uint32_t arg,gb_scalar *out){return gh_dispatch_pair(m,entry,arg,0,out);}
gb_flow gh_pattern_register(gh_model *m,uint32_t cb,uint32_t value_a1,uint16_t value_a2,gb_scalar *out){if(m->flow==GB_TRANSFER)return m->flow;gb_scalar ignored={0,0};m->entry=0x94cc;m->argument=cb;m->recognized=1;m->flow=GB_RETURNED;m->boundary_va=m->boundary_address=0;
    if(!out)out=&ignored;out->value=0;out->known=0;
    if(!m->memory)halt(m,0x94cc,0);else register_body(m,cb,value_a1,value_a2,out);return m->flow;
}
