#include "gatt_runtime.h"
#include <stdio.h>
#include <string.h>
#define BASE UINT32_C(0x20000000)
#define GP (BASE+0x4000u)
#define ATTR (BASE+0x5000u)
#define UUID (BASE+0x5100u)
#define SERVICE (BASE+0x5200u)
#define INPUT (BASE+0x6000u)
static gr_machine m;static gr_backend io;
static uint8_t ram[65536],known[65536],scratch[84],sk[84],dep[8],dk[8],adv,ak;
static uint16_t mtu,mk;static const gr_gatt_binding*saved;static const br_role_binding*saved_role;
static unsigned groups,checks,failures,registers,clocks,dispatches,cccd,legacy,life;
static da_flow dispatch_flow,register_flow,life_flow;
#define CK(x) do{++checks;if(!(x)){++failures;if(failures<12)printf("FAIL line=%u expression=%s\n",(unsigned)__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){for(unsigned i=0;i<n;i++){ram[a-BASE+i]=(uint8_t)(v>>(i*8));known[a-BASE+i]=255;}}
static uint32_t get(uint32_t a,unsigned n){uint32_t v=0;for(unsigned i=0;i<n;i++)v|=(uint32_t)ram[a-BASE+i]<<(i*8);return v;}
static da_flow rd(void*p,uint32_t a,unsigned n,uint32_t need,uint32_t site,da_scalar*out){
 (void)need;(void)site;CK(p==ram);if(a<BASE||a-BASE>sizeof(ram)-n)return DA_HALT;out->value=out->known=0;
 for(unsigned i=0;i<n;i++){out->value|=(uint32_t)ram[a-BASE+i]<<(i*8);out->known|=(uint32_t)known[a-BASE+i]<<(i*8);}return DA_RETURNED;
}
static da_flow wr(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t k,uint32_t site){
 (void)site;CK(p==ram);if(a<BASE||a-BASE>sizeof(ram)-n)return DA_HALT;put(a,v,n);for(unsigned i=0;i<n;i++)known[a-BASE+i]=(uint8_t)(k>>(i*8));return DA_RETURNED;
}
static da_flow core(void*p,da_kind kind,uint32_t target,uint32_t site,const da_scalar*args,unsigned n,da_scalar*out){
 (void)args;CK(p==ram);if(kind!=DA_ROM||target!=124||site!=0x81ba||n)return DA_HALT;
 ++clocks;out->value=1600;out->known=UINT32_MAX;return DA_RETURNED;
}
static da_flow gatt(void*p,const gp_request*r,da_scalar*out){
 CK(p==ram);if(r->kind==GP_NATIVE&&r->target==0x13e6a){++dispatches;CK(r->arguments[1].value==0x19&&r->arguments[3].value==0);out->value=7;out->known=0xff;return dispatch_flow;}
 if(r->kind==GP_ROM&&r->target==324){++cccd;CK(r->arguments[4].value==0xfedcba98&&r->arguments[5].value==1);out->value=0xabcdef;out->known=0xff00ff;return DA_RETURNED;}
 ++legacy;return DA_HALT;
}
static da_flow reg(void*p,const gr_registration_request*r,const gr_gatt_binding*b,da_scalar*out){
 CK(p==ram);++registers;CK(r->target==304&&r->callsite==0x8fa4&&r->argument_count==4);
 CK(r->arguments[0].value==GP&&r->arguments[1].value==4&&r->arguments[2].value==16&&r->arguments[3].value==0&&r->arguments[3].known==0);
 CK(b&&b->context==&m&&b->original_table_va==0x19a94);saved=b;out->value=0x9876;out->known=0xffff;return register_flow;
}
static da_flow role(void*p,const bt_request*r,const br_role_binding*b,bt_result*out){
 CK(p==ram);CK(r->target==420&&r->arguments[2].known==0&&b->context==&m.role);saved_role=b;out->scalar.value=out->scalar.known=0;out->memory_effects=0;return DA_RETURNED;
}
static da_flow lifecycle(void*p,const bl_request*r,da_scalar*out){
 CK(p==ram);++life;CK(r->target==80&&r->callsite==0x8aaa);out->value=0;out->known=UINT32_MAX;return life_flow;
}
static bt_source view(uint32_t a){bt_source s={BT_MAPPED,0,0,0,0};s.address=a;return s;}
static void reset(void){
 rp_storage a={scratch,sk,84},b={dep,dk,8};bl_storage c={&adv,&ak,&mtu,&mk};
 memset(ram,0,sizeof(ram));memset(known,255,sizeof(known));memset(&io,0,sizeof(io));
 registers=clocks=dispatches=cccd=legacy=life=0;dispatch_flow=register_flow=life_flow=DA_RETURNED;saved=0;saved_role=0;
 put(ATTR,2,1);put(ATTR+4,UUID,4);put(ATTR+10,0x27,2);put(UUID,0xfef1,2);put(SERVICE,0xfef1,2);put(GP+36,SERVICE,4);put(GP+42,0x27,2);put(GP+168,1000,4);
 put(GP+158,65534,2);put(GP+162,65534,2);put(GP+175,0x5a,1);put(GP+156,3,1);
 put(INPUT,0x55,1);put(INPUT+1,0x7f,1);put(INPUT+2,0x19,1);put(INPUT+5,0x19,1);
 io.role.runtime.core.context=ram;io.role.runtime.core.read=rd;io.role.runtime.core.write=wr;io.role.runtime.core.call=core;
 io.role.role_start=role;io.role.lifecycle_invoke=lifecycle;io.gatt_invoke=gatt;io.register_attributes=reg;
 gr_init(&m,&io,a,b,c);
}
static da_flow receive(da_scalar*out){bt_source a=view(ATTR),s=view(INPUT);return gr_write(&m,0xf1234567,&a,&s,6,0xfedcba98,out);}
static void registration(void){
 da_scalar out;bt_source a,s;const gr_callbacks*table;++groups;reset();
 CK(gr_register_attributes(&m,&out)==DA_RETURNED&&registers==1&&out.value==0x9876&&out.known==0xffff);
 CK(saved&&saved->callbacks&&saved->callbacks->write&&!saved->callbacks->reserved0&&!saved->callbacks->reserved2);if(!saved||!saved->callbacks||!saved->callbacks->write)return;
 table=saved->callbacks;a=view(ATTR);s=view(INPUT);CK(saved->callbacks->write(saved->context,0xf1234567,&a,&s,6,0xfedcba98,&out)==DA_RETURNED);
 CK(dispatches==1&&clocks==1&&legacy==0&&get(GP+164,1)==0);CK(saved->callbacks==table&&saved->context==&m);
 CK(gr_register_attributes(&m,&out)==DA_RETURNED&&saved->callbacks==table);
 reset();io.register_attributes=0;CK(gr_register_attributes(&m,&out)==DA_HALT);CK(m.boundary_va==0x8fa4&&m.boundary_address==304&&legacy==0);
}
static void shared(void){
 da_scalar out;++groups;reset();CK(gr_run_pair(&m,0x81aa,0,0,&out)==DA_RETURNED);CK(out.value==0x5a);
 put(GP+175,0x23,1);CK(gr_run_pair(&m,0x81aa,0,0,&out)==DA_RETURNED&&out.value==0x23);
 CK(receive(&out)==DA_RETURNED&&dispatches==1&&clocks==1&&legacy==0);
 CK(gr_state(&m,1,0,&out)==DA_RETURNED&&out.value==1);CK(gr_parameters(&m,7,18,0,200,&out)==DA_RETURNED&&out.value==7);
 reset();io.role.runtime.core.call=0;CK(receive(&out)==DA_HALT);CK(m.boundary_va==0x81ba&&dispatches==0&&legacy==0);
 reset();put(UUID,0x2902,2);CK(receive(&out)==DA_RETURNED&&cccd==1&&clocks==0&&out.value==0xabcdef&&out.known==0xff00ff);
}
static void stops(void){
 da_scalar out;unsigned calls;bt_source a,s;++groups;
 reset();dispatch_flow=DA_HALT;CK(receive(&out)==DA_HALT&&get(GP+164,1)==6&&m.boundary_va==0x8cec);dispatch_flow=DA_RETURNED;
 put(GP+164,0,1);CK(receive(&out)==DA_RETURNED&&dispatches==2);
 reset();CK(gr_events(&m,9,8,&out)==DA_RETURNED&&saved_role);dispatch_flow=DA_TRANSFER;CK(receive(&out)==DA_TRANSFER);calls=dispatches;
 if(saved_role)CK(saved_role->callbacks->state_changed(saved_role->context,1,0,&out)==DA_TRANSFER);
 CK(receive(&out)==DA_TRANSFER&&dispatches==calls);CK(gr_register_attributes(&m,&out)==DA_TRANSFER&&registers==0);
 reset();register_flow=DA_TRANSFER;CK(gr_register_attributes(&m,&out)==DA_TRANSFER);CK(receive(&out)==DA_TRANSFER&&clocks==0);
 reset();CK(gr_events(&m,9,8,&out)==DA_RETURNED&&saved_role);CK(gr_register_attributes(&m,&out)==DA_RETURNED&&saved);
 if(!saved_role||!saved||!saved->callbacks||!saved->callbacks->write)return;
 put(INPUT+2,5,1);put(INPUT+10,7,2);s=view(INPUT);life_flow=DA_TRANSFER;
 CK(saved_role->callbacks->state_changed(saved_role->context,4,&s,&out)==DA_TRANSFER);CK(get(GP+158,2)==7&&life==1);
 a=view(ATTR);CK(saved->callbacks->write(saved->context,7,&a,&s,0,0,&out)==DA_TRANSFER);CK(clocks==0&&m.boundary_va==0x8aaa);
}
int main(void){registration();shared();stops();printf("GATT_RUNTIME_RESULT groups=%u checks=%u failures=%u synthetic=true target_executed=false\n",groups,checks,failures);return failures?1:0;}
