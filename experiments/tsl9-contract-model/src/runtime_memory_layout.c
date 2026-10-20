#include "runtime_memory_layout.h"
#include <string.h>
/* Normalized instruction bytes are code metadata, never called as code. */
static const unsigned char rml_shape[148]={
 0x97,0x01,0x00,0x00,0x93,0x81,0x01,0x00,0x17,0x01,0x00,0x00,
 0x13,0x01,0x01,0x00,0x17,0x05,0x00,0x00,0x13,0x05,0x05,0x00,
 0x93,0x85,0x01,0x00,0x13,0x86,0x01,0x00,0x63,0xfa,0xc5,0x00,
 0x83,0x22,0x05,0x00,0x23,0xa0,0x55,0x00,0x11,0x05,0x91,0x05,
 0xe3,0xea,0xc5,0xfe,0x13,0x85,0x01,0x00,0x97,0x05,0x00,0x00,
 0x93,0x85,0x05,0x00,0x63,0x77,0xb5,0x00,0x23,0x20,0x05,0x00,
 0x11,0x05,0xe3,0x6d,0xb5,0xfe,0xfd,0x42,0x73,0x90,0x02,0xbc,
 0x8d,0x42,0x73,0x90,0x42,0x80,0xb7,0x22,0x00,0x00,0x93,0x82,
 0x82,0x88,0x73,0xa0,0x02,0x30,0x97,0x02,0x00,0x00,0x93,0x82,
 0x02,0x00,0x93,0xe2,0x32,0x00,0x73,0x90,0x52,0x30,0xef,0x00,
 0x00,0x00,0x97,0x02,0x00,0x00,0x93,0x82,0x02,0x00,0x73,0x90,
 0x12,0x34,0x6f,0x00,0x00,0x00,0x73,0x00,0x20,0x30,0x73,0x00,
 0x20,0x30,0x01,0xa0
};
static const unsigned char rml_mask[148]={
 0xff,0x0f,0x00,0x00,0xff,0xff,0x0f,0x00,0xff,0x0f,0x00,0x00,
 0xff,0xff,0x0f,0x00,0xff,0x0f,0x00,0x00,0xff,0xff,0x0f,0x00,
 0xff,0xff,0xff,0xff,0xff,0xff,0x0f,0x00,0xff,0xff,0xff,0xff,
 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,
 0xff,0xff,0xff,0xff,0xff,0xff,0x0f,0x00,0xff,0x0f,0x00,0x00,
 0xff,0xff,0x0f,0x00,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,
 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,
 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,
 0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x0f,0x00,0x00,0xff,0xff,
 0x0f,0x00,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0x0f,
 0x00,0x00,0xff,0x0f,0x00,0x00,0xff,0xff,0x0f,0x00,0xff,0xff,
 0xff,0xff,0xff,0x0f,0x00,0x00,0xff,0xff,0xff,0xff,0xff,0xff,
 0xff,0xff,0xff,0xff
};
static uint32_t word(const unsigned char *p){
 return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static uint32_t sext12(uint32_t x){
 x&=UINT32_C(0xfff);return (x&UINT32_C(0x800))?x|UINT32_C(0xfffff000):x;
}
static uint32_t pair(const unsigned char *p,uint32_t pc,unsigned off){
 return pc+(uint32_t)off+(word(p+off)&UINT32_C(0xfffff000))+sext12(word(p+off+4)>>20);
}
static uint32_t jump(const unsigned char *p,uint32_t pc,unsigned off){
 uint32_t x=word(p+off),v=((x>>31)&1u)<<20|((x>>21)&1023u)<<1|
  ((x>>20)&1u)<<11|((x>>12)&255u)<<12;
 if(v&UINT32_C(0x100000))v|=UINT32_C(0xffe00000);
 return pc+(uint32_t)off+v;
}
static int inside(uint32_t x,uint32_t n,uint32_t lo,uint32_t length){
 uint64_t end=(uint64_t)x+n,lim=(uint64_t)lo+length;
 return x>=lo&&end<=lim&&end<=UINT32_MAX&&lim<=UINT32_MAX;
}
rml_status rml_decode_reset(const unsigned char *p,size_t n,uint32_t reset,
 uint32_t image_base,uint32_t image_bytes,rml_layout *out){
 rml_layout v;size_t i;
 if(out)memset(out,0,sizeof(*out));
 if(!p||!out||n!=148u)return RML_BAD_ARGUMENT;
 if(!inside(reset,148u,image_base,image_bytes))return RML_OUTSIDE_IMAGE;
 for(i=0;i<148u;i++)if((p[i]&rml_mask[i])!=rml_shape[i])return RML_BAD_PATTERN;
 memset(&v,0,sizeof(v));v.reset=reset;v.gp=pair(p,reset,0u);v.sp=pair(p,reset,8u);
 v.data_load=pair(p,reset,16u);v.data_start=v.gp;
 v.data_end=v.gp+sext12(word(p+28)>>20);
 v.bss_start=v.gp+sext12(word(p+52)>>20);v.bss_end=pair(p,reset,56u);
 v.vector=pair(p,reset,102u);v.mtvec_value=v.vector|3u;
 v.clock_entry=jump(p,reset,118u);v.runtime_entry=pair(p,reset,122u);
 v.rom_entry=jump(p,reset,134u);
 if((v.gp|v.sp|v.data_load|v.data_end|v.bss_start|v.bss_end|v.vector)&3u)return RML_BAD_LAYOUT;
 if(v.data_end<v.data_start||v.bss_end<v.bss_start||
    v.data_end!=v.bss_start||v.sp<v.bss_end)return RML_BAD_LAYOUT;
 v.data_bytes=v.data_end-v.data_start;v.bss_bytes=v.bss_end-v.bss_start;
 v.numeric_gap_to_sp=v.sp-v.bss_end;
 if(!inside(v.data_load,v.data_bytes,image_base,image_bytes)||
    !inside(v.vector,328u,image_base,image_bytes)||
    (v.clock_entry&1u)||(v.runtime_entry&1u)||
    !inside(v.clock_entry,2u,image_base,image_bytes)||
    !inside(v.runtime_entry,2u,image_base,image_bytes))return RML_OUTSIDE_IMAGE;
 *out=v;return RML_OK;
}
rml_range rml_classify_range(const rml_layout *p,uint32_t start,uint32_t size){
 uint64_t end=(uint64_t)start+size;
 if(!size)return RML_RANGE_EMPTY;
 if(end>UINT32_MAX)return RML_RANGE_WRAP;
 if(!p)return RML_RANGE_OUTSIDE;
 if(start>=p->data_start&&end<=p->data_end)return RML_RANGE_DATA;
 if(start>=p->bss_start&&end<=p->bss_end)return RML_RANGE_BSS;
 if(start<p->bss_end&&end>p->data_start)return RML_RANGE_CROSSES;
 return RML_RANGE_OUTSIDE;
}
rml_status rml_observe_witness(const rml_layout *p,const rml_witness *w,
 rml_witness_report *out){
 rml_witness_report v;int64_t sum;
 if(out)memset(out,0,sizeof(*out));
 if(!p||!w||!out)return RML_BAD_ARGUMENT;
 if(w->gp_relative>1u||(!w->gp_relative&&w->gp_offset))return RML_BAD_ARGUMENT;
 switch(w->use){
 case RML_WITNESS_ADDRESS:if(w->bytes)return RML_BAD_ARGUMENT;break;
 case RML_WITNESS_READ:case RML_WITNESS_WRITE:
  if(w->bytes!=1u&&w->bytes!=2u&&w->bytes!=4u)return RML_BAD_ARGUMENT;break;
 case RML_WITNESS_POINTER_LOAD:if(w->bytes!=4u)return RML_BAD_ARGUMENT;break;
 case RML_WITNESS_SPAN:if(!w->bytes)return RML_BAD_ARGUMENT;break;
 default:return RML_BAD_ARGUMENT;
 }
 if(((p->gp|p->sp|p->data_start|p->data_end|p->bss_start|p->bss_end)&3u)||
    p->data_start!=p->gp||p->data_start>p->data_end||
    p->data_end!=p->bss_start||p->bss_start>p->bss_end||p->sp<p->bss_end||
    p->data_bytes!=p->data_end-p->data_start||
    p->bss_bytes!=p->bss_end-p->bss_start)return RML_BAD_LAYOUT;
 sum=(int64_t)p->gp+(int64_t)w->gp_offset;
 if(w->gp_relative&&(uint32_t)sum!=w->address)return RML_BAD_LAYOUT;
 memset(&v,0,sizeof(v));v.address=w->address;v.bytes=w->bytes;
 v.point_region=rml_classify_range(p,w->address,1u);
 v.window_region=rml_classify_range(p,w->address,w->bytes);
 v.gp_wrapped=w->gp_relative&&(sum<0||sum>(int64_t)UINT32_MAX);
 v.pointer_provider_required=w->use==RML_WITNESS_POINTER_LOAD;
 v.reset_copy_covers_window=v.window_region==RML_RANGE_DATA;
 v.reset_zero_covers_window=v.window_region==RML_RANGE_BSS;
 *out=v;return RML_OK;
}
