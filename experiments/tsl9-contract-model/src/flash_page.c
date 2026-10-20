#include "flash_page.h"
#include <string.h>
static uint32_t site(const fp_model *m,uint32_t boot){return m->image==FP_RUNTIME?boot+UINT32_C(0x15c02):boot;}
static int halt(fp_model *m,uint32_t va,uint32_t address,uint32_t needed,fp_boundary_kind why){m->flow=FP_HALT;m->boundary_va=va;m->boundary_address=address;m->needed_mask=needed;m->boundary_kind=why;return 0;}
static int invoke(fp_model *m,fp_kind kind,uint32_t va,uint32_t address,uint32_t value,uint32_t known,fp_scalar *out){
 fp_request q;fp_scalar result;fp_flow flow;memset(&q,0,sizeof(q));memset(&result,0,sizeof(result));q.kind=kind;q.va=va;q.address=address;q.value=value;q.known=known;q.width=32;q.offset=m->source_offset;
 m->last_request=q;m->operations++;
 if(!m->backend.invoke)return halt(m,va,address,0,FP_PRIMITIVE_UNRESOLVED);
 flow=m->backend.invoke(m->backend.context,m,&q,&result);
 if(flow==FP_TRANSFER){m->flow=flow;return 0;}
 if(flow!=FP_RETURNED)return halt(m,va,address,0,FP_PRIMITIVE_UNRESOLVED);
 if(out)*out=result;return 1;
}
static int write_reg(fp_model *m,uint32_t va,uint32_t address,uint32_t value,uint32_t known){return invoke(m,FP_WRITE_REGISTER,site(m,va),address,value,known,NULL);}
static int change_ctrl(fp_model *m,uint32_t read_va,uint32_t write_va,uint32_t force,uint32_t clear){
 fp_scalar v;if(!invoke(m,FP_READ_REGISTER,site(m,read_va),0x40022010,0,0,&v))return 0;
 return write_reg(m,write_va,0x40022010,(v.value|force)&~clear,v.known|force|clear);
}
static int wait_clear(fp_model *m,uint32_t va,uint32_t mask){
 uint32_t i;fp_scalar v;
 for(i=0;i<m->spin_budget;i++){
  if(!invoke(m,FP_READ_REGISTER,site(m,va),0x4002200c,0,0,&v))return 0;
  if((v.known&mask)!=mask)return halt(m,site(m,va),0x4002200c,mask,FP_CONDITION_UNKNOWN);
  if(!(v.value&mask))return 1;
 }
 return halt(m,site(m,va),0x4002200c,mask,FP_SPIN_BUDGET);
}
static int span(uint32_t address){return address>=TF_RAM_BASE&&address-TF_RAM_BASE<=TF_RAM_SIZE-4;}
static int source_word(fp_model *m,const fp_source *source,fp_scalar *out){
 unsigned i;uint32_t address;out->value=out->known=0;
 if(!source)return halt(m,site(m,0x3070),0,m->source_offset,FP_SOURCE_UNBACKED);
 if(source->kind==FP_VALUE_VIEW){
  if(!source->data||source->available<m->source_offset||source->available-m->source_offset<4)return halt(m,site(m,0x3070),0,0,FP_SOURCE_UNBACKED);
  for(i=0;i<4;i++){out->value|=(uint32_t)source->data[m->source_offset+i]<<(i*8);if(source->known)out->known|=(uint32_t)source->known[m->source_offset+i]<<(i*8);}return 1;
 }
 address=source->address+m->source_offset;
 if(m->memory&&span(address)&&!(address&3u)){
  for(i=0;i<4;i++){out->value|=(uint32_t)m->memory->ram[address-TF_RAM_BASE+i]<<(i*8);out->known|=(uint32_t)m->memory->known[address-TF_RAM_BASE+i]<<(i*8);}return 1;
 }
 return invoke(m,FP_SOURCE_READ,site(m,0x3070),address,0,0,out);
}
static int store_word(fp_model *m,const fp_scalar *v){
 unsigned i;uint32_t address=m->destination+m->source_offset;
 if(m->memory&&span(address)){
  for(i=0;i<4;i++){m->memory->ram[address-TF_RAM_BASE+i]=(uint8_t)(v->value>>(i*8));m->memory->known[address-TF_RAM_BASE+i]=(uint8_t)(v->known>>(i*8));}return 1;
 }
 return invoke(m,FP_WORD_STORE,site(m,0x3078),address,v->value,v->known,NULL);
}
void fp_init(fp_model *m,tf_model *memory,fp_image image,const fp_backend *b){memset(m,0,sizeof(*m));m->memory=memory;m->image=image;if(b)m->backend=*b;m->spin_budget=65536;}
static int unlock(fp_model *m){return write_reg(m,0x2ffa,0x40022004,0x45670123,UINT32_MAX)&&write_reg(m,0x3000,0x40022004,0xcdef89ab,UINT32_MAX)&&write_reg(m,0x3002,0x40022024,0x45670123,UINT32_MAX)&&write_reg(m,0x3004,0x40022024,0xcdef89ab,UINT32_MAX);}
static int erase(fp_model *m){return change_ctrl(m,0x301a,0x3026,0x20000,0)&&write_reg(m,0x3028,0x40022014,m->destination,UINT32_MAX)&&change_ctrl(m,0x302a,0x3030,64,0)&&wait_clear(m,0x3032,1)&&change_ctrl(m,0x3038,0x3040,0,0x20000);}
static int program(fp_model *m,const fp_source *source){
 fp_scalar v;
 if(!change_ctrl(m,0x3048,0x3052,0x10000,0)||!wait_clear(m,0x3054,1)||!wait_clear(m,0x305e,2))return 0;
 for(m->source_offset=0;m->source_offset<256;m->source_offset+=4){if(!source_word(m,source,&v)||!store_word(m,&v))return 0;m->words_written++;if(!wait_clear(m,0x307c,2))return 0;}
 return change_ctrl(m,0x3088,0x3090,0x200000,0)&&wait_clear(m,0x3096,1)&&change_ctrl(m,0x309c,0x30a4,0,0x10000);
}
static void begin(fp_model *m,uint32_t address){m->flow=FP_RETURNED;m->boundary_kind=FP_NO_BOUNDARY;m->boundary_va=m->boundary_address=m->needed_mask=0;m->raw_destination=address;m->destination=address&UINT32_C(0xffffff00);m->source_offset=m->words_written=m->operations=0;memset(&m->last_request,0,sizeof(m->last_request));}
fp_flow fp_dispatch_helper(fp_model *m,uint32_t entry,uint32_t address,const fp_source *source){
 uint32_t boot_entry=m->image==FP_RUNTIME?entry-UINT32_C(0x15c02):entry;begin(m,address);
 switch(boot_entry){
 case 0x2fe2:(void)write_reg(m,0x2fe6,0x4002200c,address,UINT32_MAX);break;
 case 0x2fea:(void)unlock(m);break;
 case 0x3008:(void)change_ctrl(m,0x300c,0x3012,0x8000,0);break;
 case 0x3016:(void)erase(m);break;
 case 0x3044:(void)program(m,source);break;
 default:(void)halt(m,entry,entry,0,FP_PRIMITIVE_UNRESOLVED);break;
 }
 return m->flow;
}
fp_flow fp_program_page(fp_model *m,uint32_t address,const fp_source *source){
 uint32_t clear_site=m->image==FP_RUNTIME?0x9b7c:0x20f6,set_site=m->image==FP_RUNTIME?0x9b9e:0x2118;
 begin(m,address);
 if(!invoke(m,FP_CSR_CLEAR,clear_site,0x800,136,UINT32_MAX,NULL))return m->flow;
 if(!unlock(m)||!write_reg(m,0x2fe6,0x4002200c,49,UINT32_MAX)||!erase(m)||!program(m,source)||!change_ctrl(m,0x300c,0x3012,0x8000,0))return m->flow;
 if(!invoke(m,FP_CSR_SET,set_site,0x800,136,UINT32_MAX,NULL))return m->flow;
 return m->flow;
}
