#include "startup_clock.h"
#define FULL UINT32_MAX
static int effect(sc_machine*m,da_flow f,uint32_t site,uint32_t address){
 if(f==DA_RETURNED)return 1;m->flow=f;m->boundary_va=site;m->boundary_address=address;m->needed_mask=0;return 0;
}
static int need(sc_machine*m,da_scalar v,uint32_t mask,uint32_t site,uint32_t address){
 if((v.known&mask)==mask)return 1;m->flow=DA_HALT;m->boundary_va=site;m->boundary_address=address;m->needed_mask=mask;return 0;
}
static int read_s(sc_machine*m,uint32_t a,uint32_t site,da_scalar*out){
 ++m->reads;out->value=out->known=0;
 return effect(m,m->io&&m->io->read?m->io->read(m->io->context,a,4,0,site,out):DA_HALT,site,a);
}
static int write_s(sc_machine*m,uint32_t a,da_scalar v,uint32_t site){
 ++m->writes;return effect(m,m->io&&m->io->write?m->io->write(m->io->context,a,v.value,4,v.known,site):DA_HALT,site,a);
}
static int modify(sc_machine*m,uint32_t a,uint32_t and_mask,uint32_t or_mask,uint32_t read_site,uint32_t write_site){
 da_scalar v;if(!read_s(m,a,read_site,&v))return 0;v.value=(v.value&and_mask)|or_mask;v.known|=~and_mask|or_mask;return write_s(m,a,v,write_site);
}
static int equal_mask(sc_machine*m,da_scalar v,uint32_t expected,uint32_t mask,uint32_t site,uint32_t address,int*out){
 if(((v.value^expected)&v.known&mask)!=0){*out=0;return 1;}
 if(!need(m,v,mask,site,address))return 0;*out=1;return 1;
}
void sc_init(sc_machine*m,const sc_backend*io){
 m->io=io;m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=m->reads=m->writes=m->hse_iterations=m->hse_ready=0;
}
da_flow sc_run(sc_machine*m){
 da_scalar v;int match;uint32_t counter=0;
 if(m->flow==DA_TRANSFER)return m->flow;
 m->flow=DA_RETURNED;m->boundary_va=m->boundary_address=m->needed_mask=m->reads=m->writes=m->hse_iterations=m->hse_ready=0;
 if(!modify(m,SC_CONTROL,FULL,1,0x184a2,0x184ae)||
    !modify(m,SC_CONFIG,UINT32_C(0xf8ff0000),0,0x184b0,0x184b8)||
    !modify(m,SC_CONTROL,UINT32_C(0xfef6ffff),0,0x184ba,0x184c4)||
    !modify(m,SC_CONTROL,UINT32_C(0xfffbffff),0,0x184c6,0x184d0)||
    !modify(m,SC_CONFIG,UINT32_C(0xff80ffff),0,0x184d2,0x184dc))return m->flow;
 v.value=UINT32_C(0x9f0000);v.known=FULL;
 if(!write_s(m,SC_INTERRUPT,v,0x184e2)||!modify(m,SC_CONTROL,FULL,UINT32_C(0x10000),0x184e8,0x184ee))return m->flow;
 do{
  if(!read_s(m,SC_CONTROL,0x184f6,&v))return m->flow;
  ++counter;m->hse_iterations=counter;
  if(!need(m,v,UINT32_C(0x20000),0x18504,SC_CONTROL))return m->flow;
 }while(!(v.value&UINT32_C(0x20000))&&counter!=4096);
 /* The original performs this fresh read even after the4096th failed poll. */
 if(!read_s(m,SC_CONTROL,0x18510,&v)||!need(m,v,UINT32_C(0x20000),0x18516,SC_CONTROL))return m->flow;
 if(!(v.value&UINT32_C(0x20000)))return m->flow;
 m->hse_ready=1;
 /* Two apparently redundant read/write pairs are actual MMIO effects. */
 if(!modify(m,SC_CONFIG,FULL,0,0x1852a,0x18532)||
    !modify(m,SC_CONFIG,FULL,0,0x18534,0x18536)||
    !modify(m,SC_CONFIG,FULL,UINT32_C(0x400),0x18538,0x1853e)||
    !modify(m,SC_CONFIG,UINT32_C(0xffc0ffff),0,0x18540,0x18544)||
    !modify(m,SC_CONFIG,FULL,UINT32_C(0x290000),0x18546,0x1854e)||
    !modify(m,SC_CONTROL,FULL,UINT32_C(0x1000000),0x18550,0x18558))return m->flow;
 do{
  if(!read_s(m,SC_CONTROL,0x1855a,&v)||!need(m,v,UINT32_C(0x2000000),0x18560,SC_CONTROL))return m->flow;
 }while(!(v.value&UINT32_C(0x2000000)));
 if(!modify(m,SC_CONFIG,UINT32_C(0xfffffffc),0,0x18564,0x1856c)||
    !modify(m,SC_CONFIG,FULL,2,0x1856e,0x18574))return m->flow;
 do{
  if(!read_s(m,SC_CONFIG,0x18578,&v)||!equal_mask(m,v,8,12,0x1857c,SC_CONFIG,&match))return m->flow;
 }while(!match);
 return m->flow;
}
#if defined(__riscv) && __riscv_xlen == 32
static da_flow native_read(void*p,uint32_t a,unsigned n,uint32_t mask,uint32_t site,da_scalar*out){
 (void)p;(void)n;(void)mask;(void)site;
 out->value=*(volatile uint32_t*)(uintptr_t)a;out->known=FULL;return DA_RETURNED;
}
static da_flow native_write(void*p,uint32_t a,uint32_t v,unsigned n,uint32_t known,uint32_t site){
 (void)p;(void)n;(void)known;(void)site;
 *(volatile uint32_t*)(uintptr_t)a=v;return DA_RETURNED;
}
static const sc_backend native_backend={0,native_read,native_write};
static uint32_t native_core(void) __asm__("tsl9_sc_native_core");
__attribute__((used,noinline)) static uint32_t native_core(void){
 sc_machine m;sc_init(&m,&native_backend);(void)sc_run(&m);return m.hse_ready;
}
/* Original SystemInit is a leaf that preserves these registers. The C core
   may clobber them; this real ABI shim restores them before ROM handoff. */
__attribute__((naked,used)) void sc_native_init(void){
 __asm__ volatile(
  ".option push\n"
  ".option norelax\n"
  "addi sp,sp,-48\n"
  "sw a0,0(sp)\n"
  "sw a1,4(sp)\n"
  "sw a6,8(sp)\n"
  "sw a7,12(sp)\n"
  "sw t0,16(sp)\n"
  "sw t1,20(sp)\n"
  "sw t2,24(sp)\n"
  "sw t3,28(sp)\n"
  "sw t4,32(sp)\n"
  "sw t5,36(sp)\n"
  "sw t6,40(sp)\n"
  "sw ra,44(sp)\n"
  "call tsl9_sc_native_core\n"
  "li a2,0x20000\n"
  "li a3,0x40021000\n"
  "beqz a0,1f\n"
  "li a4,8\n"
  "li a5,8\n"
  "j 2f\n"
  "1: li a4,0\n"
  "li a5,1\n"
  "2: lw a0,0(sp)\n"
  "lw a1,4(sp)\n"
  "lw a6,8(sp)\n"
  "lw a7,12(sp)\n"
  "lw t0,16(sp)\n"
  "lw t1,20(sp)\n"
  "lw t2,24(sp)\n"
  "lw t3,28(sp)\n"
  "lw t4,32(sp)\n"
  "lw t5,36(sp)\n"
  "lw t6,40(sp)\n"
  "lw ra,44(sp)\n"
  "addi sp,sp,48\n"
  "ret\n"
  ".option pop\n"
 );
}
#endif
