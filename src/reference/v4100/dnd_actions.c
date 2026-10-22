#include "dnd_actions.h"
#define GP UINT32_C(0x20004000)
#define CFG_SLOT (GP+84u)
#define FULL UINT32_MAX
static int accept(da_machine *m,da_flow f,uint32_t site,uint32_t address){
 if(f==DA_RETURNED)return 1;m->flow=f;m->boundary_va=site;m->boundary_address=address;return 0;
}
static int read_scalar(da_machine *m,uint32_t address,unsigned width,uint32_t mask,uint32_t site,da_scalar *out){
 out->value=out->known=0;
 if(!accept(m,m->io.read?m->io.read(m->io.context,address,width,mask,site,out):DA_HALT,site,address))return 0;
 return (out->known&mask)==mask?1:accept(m,DA_HALT,site,address);
}
static int read_value(da_machine *m,uint32_t address,unsigned width,uint32_t mask,uint32_t site,uint32_t *out){
 da_scalar r;int ok=read_scalar(m,address,width,mask,site,&r);*out=r.value;return ok;
}
static int write_scalar(da_machine *m,uint32_t address,da_scalar value,unsigned width,uint32_t site){
 return accept(m,m->io.write?m->io.write(m->io.context,address,value.value,width,value.known,site):DA_HALT,site,address);
}
static int write_width(da_machine *m,uint32_t address,uint32_t value,unsigned width,uint32_t site){
 da_scalar r={value,FULL};return write_scalar(m,address,r,width,site);
}
static int write_value(da_machine *m,uint32_t address,uint32_t value,uint32_t site){return write_width(m,address,value,1,site);}
static int cfg_value(da_machine *m,unsigned offset,uint32_t mask,uint32_t ptrsite,uint32_t site,uint32_t *out){
 uint32_t p;return read_value(m,CFG_SLOT,4,FULL,ptrsite,&p)&&read_value(m,p+offset,1,mask,site,out);
}
static int schedule_scalar(da_machine *m,uint32_t cb,uint32_t delay,uint32_t site,da_scalar *out){
 da_scalar ignored={0,0};if(!out)out=&ignored;out->value=out->known=0;
 return accept(m,m->io.schedule?m->io.schedule(m->io.context,cb,delay,site,out):DA_HALT,site,cb);
}
static int schedule_value(da_machine *m,uint32_t cb,uint32_t delay,uint32_t site){return schedule_scalar(m,cb,delay,site,0);}
static int interval(da_machine *);
static int pulse_build(da_machine *,uint32_t,da_scalar *);
static int report_mode0(da_machine *,da_scalar *);
static int native_interval(da_machine *m){return interval(m);}
static int random_bit(da_machine *m,uint32_t *out){
 da_scalar r={0,0};
 if(!accept(m,m->io.call?m->io.call(m->io.context,DA_ROM,56,0xa1c2,0,0,&r):DA_HALT,0xa1c2,0))return 0;
 if(!(r.known&1))return accept(m,DA_HALT,0xa1c4,0);
 *out=r.value&1;return 1;
}
static int gear_request(da_machine *m){
 return write_value(m,0x2000bf34,1,0xcec8)&&write_value(m,0x2000bf35,3,0xcecc)&&
        write_value(m,0x2000bf36,0,0xced0)&&write_value(m,0x2000bf37,1,0xced4);
}
static int select_pending(da_machine *m){
 uint32_t branch,value,blocked,request;
 if(!read_value(m,GP+188,1,255,0xa192,&branch))return 0;
 if(!branch){
  if(!read_value(m,GP+182,1,255,0xa198,&blocked))return 0;if(blocked)return 1;
  if(!read_value(m,GP+186,1,255,0xa19e,&value))return 0;request=value?3u:1u;
 }else{
  if(!read_value(m,GP+186,1,255,0xa1f8,&value))return 0;
  request=branch==3?(value?10u:12u):(value?11u:9u);
 }
 return write_value(m,0x2000bf0c,request,0xb578);
}
static int mode_one(da_machine *m,uint32_t raw){
 uint32_t priority,count,p,cfg,old,value;
 if(!read_value(m,GP+180,1,255,0xa12c,&priority))return 0;
 if(priority){
  if(!raw)return 1;if(!read_value(m,0x2000bee0,1,255,0xab16,&value))return 0;
  return !value||gear_request(m);
 }
 if(!read_value(m,GP+187,1,255,0xa14c,&count))return 0;
 if(!raw){
  if(!count)return 1;count=(count-1)&255u;
  if(!write_value(m,GP+187,count,0xa1d4))return 0;if(count)return 1;
  if(!read_value(m,GP+186,1,255,0xa1da,&value)||!write_value(m,GP+186,value==0,0xa1e2))return 0;
  return select_pending(m);
 }
 if(count)return 1;
 if(!write_value(m,GP+187,raw,0xa154)||!read_value(m,CFG_SLOT,4,FULL,0xa15c,&p)||
    !read_value(m,p+4,1,192,0xa160,&cfg))return 0;
 switch((cfg>>6)&3){
 case 0:if(!write_value(m,GP+188,0,0xa174))return 0;break;
 case 1:if(!write_value(m,GP+188,1,0xa1b2))return 0;break;
 case 2:
  if(!read_value(m,GP+188,1,255,0xa1aa,&old)||!write_value(m,GP+188,old==0,0xa1b2))return 0;break;
 default:if(!write_value(m,GP+188,3,0xa1b2))return 0;break;
 }
 if(!read_value(m,p+9,1,3,0xa178,&cfg))return 0;
 switch(cfg&3){
 case 0:if(!write_value(m,GP+186,0,0xa18e))return 0;break;
 case 1:if(!write_value(m,GP+186,1,0xa1e2))return 0;break;
 case 2:break;
 default:
  if(!random_bit(m,&value)||!write_value(m,GP+186,value,0xa1c6))return 0;break;
 }
 return select_pending(m);
}
static int alternate_duration(da_machine *m,uint32_t raw){
 if(!raw)raw=1;
 return write_value(m,0x2000bfb4,1,0x106a4)&&schedule_value(m,0x1049a,raw*UINT32_C(1000),0x106b4);
}
static int selector_value(da_machine *m,uint32_t *out){
 uint32_t value;if(!cfg_value(m,5,3,0x81e2,0x81e4,&value))return 0;
 *out=(value&3)+1;return 1;
}
static int gate_two(da_machine *m,uint32_t *out){
 uint32_t value;if(!cfg_value(m,4,8,0x8218,0x821a,&value))return 0;
 *out=0;if(value&8)return 1;
 if(!read_value(m,GP+195,1,255,0x8232,&value))return 0;*out=value<3;return 1;
}
static int action(da_machine *m,uint32_t raw){
 uint32_t mode,selector,gate,cfg,count,delay;
 if(!read_value(m,0x2000bfb1,1,255,0x8298,&mode))return 0;
 if(mode!=1)return alternate_duration(m,raw);
 if(!selector_value(m,&selector))return 0;
 if((selector&1)&&!mode_one(m,raw))return 0;
 if(!(selector&2))return 1;
 if(!gate_two(m,&gate))return 0;if(!gate||!raw)return 1;
 if(!cfg_value(m,3,15,0xa248,0xa24c,&cfg))return 0;if((cfg&15)==15)return 1;
 delay=raw*UINT32_C(1000);
 if(!read_value(m,GP+184,1,3,0xa25e,&count)||!write_value(m,GP+184,(count+1)&3,0xa268)||
    !write_value(m,GP+183,1,0xa272))return 0;
 return schedule_value(m,0x9e8e,delay,0xa284);
}
static int priority_refresh(da_machine *m){
 uint32_t cfg,observed,value=0;
 if(!cfg_value(m,8,16,0x9e98,0x9e9a,&cfg))return 0;
 if(cfg&16){
  if(!read_value(m,0x2000bee0,1,255,0xab16,&observed))return 0;
  if(observed){if(!read_value(m,GP+354,1,1,0x9eb8,&value))return 0;value^=1;}
 }
 return write_value(m,GP+180,value&1,(cfg&16)?0x9ec4u:0x9ea6u);
}
static int priority_reset(da_machine *m){
 uint32_t cfg,observed,alternate;
 if(!write_value(m,GP+180,0,0x9ee2)||!cfg_value(m,8,16,0x9eea,0x9eec,&cfg))return 0;
 if(!(cfg&16))return 1;
 if(!read_value(m,0x2000bee0,1,255,0xab16,&observed))return 0;if(!observed)return 1;
 if(!read_value(m,GP+354,1,255,0x9efe,&alternate))return 0;if(alternate)return 1;
 return schedule_value(m,0x9e94,10000,0x9f1a);
}
static int pending_setter(da_machine *m,uint32_t raw){
 if(((raw-1u)&255u)>17u)return 1;
 if(!native_interval(m))return 0;
 if((raw<=11||raw==18)&&!priority_reset(m))return 0;
 return write_value(m,0x2000bf0c,raw,0xb5ac);
}
/* R25 core: all local calls below use the same RAM/backend instance. */
static int invoke_scalars(da_machine *m,da_kind kind,uint32_t target,uint32_t site,const da_scalar *args,unsigned count,da_scalar *out){
 da_scalar ignored={0,0};if(!out)out=&ignored;out->value=out->known=0;
 return accept(m,m->io.call?m->io.call(m->io.context,kind,target,site,args,count,out):DA_HALT,site,
               kind==DA_MMIO_READ||kind==DA_MMIO_WRITE?target:0);
}
static int invoke_value(da_machine *m,da_kind kind,uint32_t target,uint32_t site,const uint32_t *args,unsigned count,da_scalar *out){
 da_scalar scalars[3];unsigned i;for(i=0;i<count;i++){scalars[i].value=args[i];scalars[i].known=FULL;}
 return invoke_scalars(m,kind,target,site,scalars,count,out);
}
static int rom_values(da_machine *m,uint32_t offset,uint32_t site,uint32_t a0,uint32_t a1,uint32_t a2,unsigned count,da_scalar *out){
 const uint32_t args[3]={a0,a1,a2};return invoke_value(m,DA_ROM,offset,site,args,count,out);
}
static int gate_channel(da_machine *m,uint32_t channel,uint32_t *out){
 uint32_t cfg,value;if(!cfg_value(m,4,8,0x8218,0x821a,&cfg))return 0;
 *out=0;if((cfg&8)||channel>2)return 1;
 if(!read_value(m,GP+193+channel,1,255,0x8232,&value))return 0;*out=value<3;return 1;
}
static int interval(da_machine *m){
 uint32_t enabled,n,cfg,gate,priority,base,mod,task;da_scalar random;
 if(!read_value(m,GP+364,1,255,0x843a,&enabled))return 0;if(!enabled)return 1;
 if(!cfg_value(m,3,15,0x16f5c,0x16f60,&n))return 0;
 if((n&15)==15){
  if(!gate_channel(m,1,&gate))return 0;
  if(gate){
   if(!cfg_value(m,8,16,0x16fde,0x16fe0,&cfg))return 0;if(!(cfg&16))return 1;
   if(!read_value(m,GP+180,1,255,0x9edc,&priority))return 0;if(!priority)return 1;
  }
 }
 if(!cfg_value(m,3,15,0x16f6a,0x16f6c,&n))return 0;n&=15;if(n==15)n=1;
 if(!rom_values(m,56,0x16f80,0,0,0,0,&random))return 0;
 base=n<=1?2000:n==2?3000:(n-2)*5000;mod=n<=1?1001:n==2?2001:5001;
 if(!cfg_value(m,4,1,0x16f94,0x16f96,&cfg))return 0;
 if(cfg&1){if(random.known!=FULL)return accept(m,DA_HALT,0x16f9e,0);base+=random.value%mod;}
 if(!read_value(m,GP+365,1,255,0x16fac,&task)||!rom_values(m,88,0x16fbc,task,1,(base*1000)/625,3,0))return 0;
 if(!read_value(m,GP+365,1,255,0x16fc8,&task))return 0;
 return rom_values(m,88,0x16fd4,task,4,80,3,0);
}
static int feedback_value(da_machine *m,uint32_t raw){
 da_scalar ignored;return pulse_build(m,raw?250u:2u,&ignored);
}
static int cancel_registry(da_machine *m,uint32_t callback,da_scalar *out){
 unsigned i;uint32_t cb,arg,task;
 for(i=0;i<15;i++){
  uint32_t slot=UINT32_C(0x2000be08)+12*i;
  if(!read_value(m,slot+4,4,FULL,0x90a4,&cb))return 0;if(cb!=callback)continue;
  if(!read_value(m,slot+8,4,FULL,0x90b2,&arg))return 0;
  if(arg&&!rom_values(m,104,0x90bc,arg,0,0,1,0))return 0;
  if(!read_value(m,GP+174,1,255,0x90d0,&task))return 0;
  if(!write_width(m,slot+4,0,4,0x90dc)||!write_width(m,slot+8,0,4,0x90e0))return 0;
  return rom_values(m,92,0x90ec,task,(1u<<i)&65535u,0,2,out);
 }
 out->value=1;out->known=FULL;return 1;
}
static int clear_duration(da_machine *m,da_scalar *out){
 return write_value(m,0x2000bfb4,0,0x1049e)&&cancel_registry(m,0x1049a,out);
}
static int enable_value(da_machine *m,uint32_t raw,uint32_t feedback){
 uint32_t eligible,cfg,task;da_scalar ignored;
 if(raw){if(!read_value(m,GP+175,1,255,0x81aa,&eligible))return 0;if(!eligible)return 1;}
 if(!write_value(m,GP+364,raw,0x17056)||!interval(m))return 0;
 if(feedback&&!feedback_value(m,raw))return 0;
 if(raw){
  if(!cfg_value(m,7,7,0x1706c,0x1706e,&cfg))return 0;cfg&=7;if(!cfg)return 1;
  if(!read_value(m,GP+365,1,255,0x17090,&task))return 0;
  return rom_values(m,88,0x17098,task,2,cfg*UINT32_C(960000),3,0);
 }
 if(!read_value(m,GP+365,1,255,0x170b2,&task)||!rom_values(m,92,0x170b6,task,2,0,2,0))return 0;
 if(!read_value(m,GP+365,1,255,0x170bc,&task)||!rom_values(m,92,0x170c0,task,1,0,2,0))return 0;
 return schedule_value(m,0x13b5c,20,0x170d0)&&clear_duration(m,&ignored);
}
static int task_value(da_machine *m,uint32_t events,da_scalar *out){
 uint32_t p,selected,cfg,mode,observed=0;
 if(events&1){
  if(!interval(m)||!read_value(m,CFG_SLOT,4,FULL,0x170fa,&p)||
     !read_value(m,p+8,1,15,0x170fe,&selected)||!read_value(m,p+3,1,15,0x17102,&cfg))return 0;
  selected&=15;
  if((cfg&15)==15){if(!read_value(m,0x2000bfb1,1,255,0x8298,&mode))return 0;if(mode==1&&selected>3)selected=3;}
  if(!action(m,selected))return 0;out->value=events^1u;
 }else if(events&2){
  if(!cfg_value(m,4,16,0x17144,0x17146,&cfg))return 0;
  if((cfg&16)&&!read_value(m,0x2000bee0,1,255,0xab16,&observed))return 0;
  if(!observed&&!enable_value(m,0,1))return 0;out->value=events^2u;
 }else if(events&4){
  da_scalar ignored;if(!report_mode0(m,&ignored))return 0;out->value=events^4u;
 }else out->value=0;
 out->known=FULL;return 1;
}
static int initialize_task(da_machine *m){
 da_scalar registration;uint32_t cfg;
 if(!rom_values(m,72,0x1718a,GP+364,0,1,3,0)||!rom_values(m,128,0x17198,0x170e2,0,0,1,&registration))return 0;
 if((registration.known&255)!=255)return accept(m,DA_HALT,0x1719a,0);
 if(!write_value(m,GP+365,registration.value,0x1719a)||!cfg_value(m,6,1,0x171a2,0x171a4,&cfg))return 0;
 return !(cfg&1)||enable_value(m,1,0);
}

/* R26: local feedback and mode0 report execute on this same backend. */
static int nonzero(da_machine *m,da_scalar value,uint32_t mask,uint32_t site,uint32_t address,int *out){
 if(value.value&value.known&mask){*out=1;return 1;}
 if((value.known&mask)==mask){*out=0;return 1;}
 return accept(m,DA_HALT,site,address);
}
static int mmio_write(da_machine *m,uint32_t address,da_scalar value,uint32_t site){
 da_scalar args[2];args[0].value=value.value&65535u;args[0].known=value.known&65535u;
 args[1].value=16;args[1].known=FULL;return invoke_scalars(m,DA_MMIO_WRITE,address,site,args,2,0);
}
static int mmio_constant(da_machine *m,uint32_t address,uint32_t value,uint32_t site){
 da_scalar r={value,FULL};return mmio_write(m,address,r,site);
}
static int mmio_state(da_machine *m,uint32_t site,da_scalar *out){
 const uint32_t args[1]={16};return invoke_value(m,DA_MMIO_READ,0x40000400,site,args,1,out);
}
static int pulse_stop(da_machine *m){
 da_scalar state;if(!mmio_constant(m,0x4000042c,65535,0x93d2)||!mmio_constant(m,0x4000043c,0,0x93d6)||
    !mmio_state(m,0x93da,&state))return 0;
 state.value&=65534u;state.known=(state.known|1u)&65535u;return mmio_write(m,0x40000400,state,0x93e8);
}
static int pulse_allocate(da_machine *m,uint32_t count,da_scalar *out){
 da_scalar old;int exists;
 if(!read_scalar(m,0x2000becc,4,0,0x93fc,&old)||!nonzero(m,old,FULL,0x9400,0x2000becc,&exists))return 0;
 if(exists){
  if(!invoke_scalars(m,DA_ROM,104,0x9408,&old,1,0)||!write_width(m,0x2000becc,0,4,0x940e)||
     !write_width(m,0x2000bec8,0,4,0x9416)||!pulse_stop(m))return 0;
 }
 return rom_values(m,112,0x9430,count*UINT32_C(6),0,0,1,out);
}
static int pulse_start(da_machine *m){
 uint32_t p;da_scalar cfg,registered,enabled,state;int active;
 if(!read_value(m,CFG_SLOT,4,FULL,0x938c,&p)||!read_scalar(m,p+2,1,0,0x938e,&cfg)||
    !read_scalar(m,0x2000bec0,1,0,0x9396,&registered))return 0;
 enabled.value=cfg.value|registered.value;
 enabled.known=(cfg.known&registered.known)|(cfg.value&cfg.known)|(registered.value&registered.known);
 if(!nonzero(m,enabled,255,0x939c,0x2000bec0,&active))return 0;if(!active)return 1;
 if(!write_value(m,0x2000bec2,0,0x93a2)||!write_value(m,0x2000bec1,0,0x93aa)||
    !write_width(m,0x2000bebc,0,4,0x93b2)||!mmio_constant(m,0x40000424,0,0x93ba)||
    !mmio_state(m,0x93be,&state))return 0;
 state.value=(state.value|1u)&65535u;state.known=(state.known|1u)&65535u;
 return mmio_write(m,0x40000400,state,0x93c6);
}
static int pulse_build(da_machine *m,uint32_t input,da_scalar *out){
 da_scalar pointer;uint32_t i,site;int exists;int large=input>19u;
 if(!pulse_allocate(m,large?2u:input+1u,&pointer)||
    !write_scalar(m,0x2000becc,pointer,4,large?0x94a4u:0x9454u)||
    !nonzero(m,pointer,FULL,large?0x94a8u:0x9458u,0x2000becc,&exists))return 0;
 if(!exists){*out=pointer;return 1;}
 site=large?0x94b0u:input?0x9488u:0x9478u;
 if(pointer.known!=FULL)return accept(m,DA_HALT,site,0x2000becc);
 if(large){
  if(!write_width(m,pointer.value,3000,2,0x94b0)||!write_width(m,pointer.value+2,input,2,0x94b4)||
     !write_width(m,pointer.value+4,0,2,0x94b8)||!write_width(m,pointer.value+6,0,2,0x94bc))return 0;
 }else{
  for(i=0;i<input;i++){
   if(!write_width(m,pointer.value+i*6,3000,2,0x9488)||!write_width(m,pointer.value+i*6+2,40,2,0x948c)||
      !write_width(m,pointer.value+i*6+4,80,2,0x9490))return 0;
  }
  if(!write_width(m,pointer.value+input*6,0,2,0x9478))return 0;
 }
 if(!pulse_start(m))return 0;*out=pointer;return 1;
}
static int clock_value(da_machine *m,da_scalar *out){
 da_scalar raw;if(!rom_values(m,124,0x81ba,0,0,0,0,&raw))return 0;
 if((raw.known&UINT32_C(0x7fffffff))!=UINT32_C(0x7fffffff))return accept(m,DA_HALT,0x81ba,0);
 out->value=(raw.value*UINT32_C(10))>>4;out->known=FULL;return 1;
}
static int report_pending(da_machine *m,da_scalar *out){
 unsigned i;uint32_t h,mode,auth;
 for(i=0;i<2;i++){
  uint32_t a=UINT32_C(0x2000c790)+4*i;
  if(!read_value(m,a+2,2,65535,i?0x13426u:0x13400u,&h))return 0;if(h==65534)continue;
  if(!read_value(m,a+5,1,255,i?0x13434u:0x13412u,&mode))return 0;if(!mode)continue;
  if(!read_value(m,a+4,1,255,i?0x1343eu:0x1341cu,&auth))return 0;if(!auth)continue;
  if(!write_value(m,0x2000c790,1,0x13462)||!schedule_value(m,0x13156,300,0x13466))return 0;
  out->value=1;out->known=FULL;return 1;
 }
 out->value=0;out->known=FULL;return 1;
}
static int report_mode0(da_machine *m,da_scalar *out){
 da_scalar pending,now;uint32_t h,mode,last;unsigned i;int eligible=0;
 if(!report_pending(m,&pending))return 0;
 for(i=0;i<2;i++){
  uint32_t a=UINT32_C(0x2000c790)+4*i;
  if(!read_value(m,a+2,2,65535,i?0x13b86u:0x13b6au,&h))return 0;if(h==65534)continue;
  if(!read_value(m,a+5,1,255,i?0x13b92u:0x13b7cu,&mode))return 0;if(!mode){eligible=1;break;}
 }
 if(!eligible){*out=pending;return 1;}
 if(pending.value)return schedule_scalar(m,0x13160,100,0x13bb2,out);
 if(!clock_value(m,&now)||!read_value(m,GP+344,4,FULL,0x13bbe,&last))return 0;
 if((uint32_t)(now.value-last)<=34u)return schedule_scalar(m,0x13160,35,0x13bb2,out);
 if(!write_width(m,GP+344,now.value,4,0x13bce))return 0;
 {const uint32_t args[1]={0};return invoke_value(m,DA_NATIVE,0x13160,0x13bd6,args,1,out);}
}

void da_init(da_machine *m,const da_backend *io){
 m->io.context=io?io->context:0;m->io.read=io?io->read:0;m->io.write=io?io->write:0;
 m->io.call=io?io->call:0;m->io.schedule=io?io->schedule:0;
 m->flow=DA_RETURNED;m->boundary_va=0;m->boundary_address=0;
}
int da_recognizes(uint32_t entry){
 switch(entry){case 0x81de:case 0x9e8e:case 0x9e94:case 0x9ee2:case 0xa128:case 0xa20e:
 case 0xa212:case 0xb574:case 0xb57e:case 0x10692:
 case 0x81aa:case 0x843a:case 0x8214:case 0x8294:case 0x9edc:case 0xab12:case 0x9770:case 0x1049a:case 0x908e:
 case 0x16f4a:case 0x17024:case 0x17048:case 0x170e2:case 0x17176:
 case 0x9432:case 0x93ee:case 0x9388:case 0x93cc:case 0x13b5c:case 0x133fa:case 0x81b0:case 0x13156:return 1;default:return 0;}
}
da_flow da_run_pair(da_machine *m,uint32_t entry,uint32_t raw,uint32_t a1,da_scalar *out){
 da_scalar ignored={0,0};uint32_t value;
 if(m->flow==DA_TRANSFER)return m->flow;
 m->flow=DA_RETURNED;m->boundary_va=0;m->boundary_address=0;
 if(!out)out=&ignored;out->value=0;out->known=0;
 switch(entry){
 case 0x9432:pulse_build(m,raw,out);break;
 case 0x93ee:pulse_allocate(m,raw,out);break;
 case 0x9388:if(pulse_start(m)){out->value=raw;out->known=FULL;}break;
 case 0x93cc:if(pulse_stop(m)){out->value=raw;out->known=FULL;}break;
 case 0x13b5c:report_mode0(m,out);break;
 case 0x133fa:report_pending(m,out);break;
 case 0x81b0:clock_value(m,out);break;
 case 0x13156:if(write_value(m,0x2000c790,0,0x1315a)){out->value=raw;out->known=FULL;}break;
 case 0x16f4a:interval(m);break;
 case 0x17024:
  if(read_value(m,GP+364,1,255,0x843a,&value)&&value&&read_value(m,GP+365,1,255,0x17038,&value))rom_values(m,80,0x17040,value,1,0,2,out);break;
 case 0x17048:enable_value(m,raw,a1);break;
 case 0x170e2:task_value(m,a1,out);break;
 case 0x17176:initialize_task(m);break;
 case 0x81aa:if(read_value(m,GP+175,1,255,0x81aa,&value)){out->value=value;out->known=FULL;}break;
 case 0x843a:if(read_value(m,GP+364,1,255,0x843a,&value)){out->value=value;out->known=FULL;}break;
 case 0x8214:if(gate_channel(m,raw,&value)){out->value=value;out->known=FULL;}break;
 case 0x8294:if(read_value(m,0x2000bfb1,1,255,0x8298,&value)){out->value=value;out->known=FULL;}break;
 case 0x9edc:if(read_value(m,GP+180,1,255,0x9edc,&value)){out->value=value;out->known=FULL;}break;
 case 0xab12:if(read_value(m,0x2000bee0,1,255,0xab16,&value)){out->value=value;out->known=FULL;}break;
 case 0x9770:feedback_value(m,raw);break;
 case 0x1049a:clear_duration(m,out);break;
 case 0x908e:cancel_registry(m,raw,out);break;
 case 0x81de:if(selector_value(m,&value)){out->value=value;out->known=FULL;}break;
 case 0x9e8e:write_value(m,GP+183,0,0x9e8e);break;
 case 0x9e94:priority_refresh(m);break;
 case 0x9ee2:priority_reset(m);break;
 case 0xa128:mode_one(m,raw);break;
 case 0xa20e:mode_one(m,1);break;
 case 0xa212:action(m,raw);break;
 case 0xb574:write_value(m,0x2000bf0c,raw,0xb578);break;
 case 0xb57e:pending_setter(m,raw);break;
 case 0x10692:alternate_duration(m,raw);break;
 default:accept(m,DA_HALT,entry,0);break;
 }
 return m->flow;
}

da_flow da_run(da_machine *m,uint32_t entry,uint32_t raw,da_scalar *out){return da_run_pair(m,entry,raw,0,out);}
