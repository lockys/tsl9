#if defined(_MSC_VER)
#define _CRT_SECURE_NO_WARNINGS
#endif
#include "reset_memory.h"
#include "test_io.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SOURCE UINT32_C(0x1ab60)
#define END UINT32_C(0x2000c958)
#define CAP 18000u
typedef struct effect {char kind;uint32_t address,value,extra;} effect;
static effect plan[CAP];
static uint32_t samples[3];
static unsigned planned,seen,gp_reads,groups,cases,checks;
static unsigned char initial[128],predicted[128],actual[128];
static void require(int ok,const char *message)
{
    ++checks;if(!ok){fprintf(stderr,"FAIL %s, case %u, effect %u\n",message,cases,seen);exit(1);}
}
static uint32_t word(const unsigned char *bytes,uint32_t address)
{
    uint32_t k=address-SOURCE;
    require(address>=SOURCE && k<=124u && k%4u==0u,"bounded source-data request");
    return (uint32_t)bytes[k]|((uint32_t)bytes[k+1u]<<8)
        |((uint32_t)bytes[k+2u]<<16)|((uint32_t)bytes[k+3u]<<24);
}
static void bytes_write(unsigned char *bytes,uint32_t address,uint32_t value)
{
    unsigned i;
    for(i=0;i<4u;++i){
        uint32_t location=address+i;
        if(location>=SOURCE && location-SOURCE<128u)
            bytes[location-SOURCE]=(unsigned char)(value>>(8u*i));
    }
}
static void add(char kind,uint32_t address,uint32_t value,uint32_t extra)
{
    require(planned<CAP,"bounded oracle storage");
    plan[planned].kind=kind;plan[planned].address=address;
    plan[planned].value=value;plan[planned++].extra=extra;
}
static void effect_is(char kind,uint32_t address,uint32_t value,uint32_t extra)
{
    effect e;require(seen<planned,"unexpected effect or loop bound failure");e=plan[seen++];
    require(e.kind==kind,"event order");require(e.address==address,"numeric address or A0");
    require(e.value==value,"sampled value or A1");require(e.extra==extra,"GP index or A2");
}
uint32_t tsl9_rm_test_gp(void)
{
    uint32_t v;require(gp_reads<3u,"exactly three GP requests");v=samples[gp_reads];
    effect_is('G',0,v,gp_reads);++gp_reads;return v;
}
uint32_t tsl9_rm_test_read32(uint32_t address)
{
    uint32_t v=word(actual,address);effect_is('R',address,v,0);return v;
}
void tsl9_rm_test_write32(uint32_t address,uint32_t value)
{
    effect_is('W',address,value,0);bytes_write(actual,address,value);
}
void tsl9_rm_test_outputs(uint32_t a0,uint32_t a1,uint32_t a2)
{
    effect_is('O',a0,a1,a2);
}
static void scenario(uint32_t d,uint32_t second_gp,uint32_t third_gp)
{
    uint32_t e=second_gp+128u,z=third_gp+128u,n=0,q=0,i;
    ++cases;planned=seen=gp_reads=0;
    samples[0]=d;samples[1]=second_gp;samples[2]=third_gp;
    memcpy(predicted,initial,128);memcpy(actual,initial,128);
    if(d<e){
        uint64_t count=((uint64_t)e-d+3u)/4u;
        require(count<=32u && (uint64_t)d+count*4u<=UINT32_MAX,"bounded terminating copy domain");
        n=(uint32_t)count;
    }
    if(z<END)q=(END-z+3u)/4u;
    require(q<=8758u,"bounded zero domain");
    add('G',0,d,0);add('G',0,second_gp,1);
    for(i=0;i<n;++i){
        uint32_t value=word(predicted,SOURCE+i*4u);
        add('R',SOURCE+i*4u,value,0);add('W',d+i*4u,value,0);
        bytes_write(predicted,d+i*4u,value);
    }
    add('G',0,third_gp,2);
    for(i=0;i<q;++i){add('W',z+i*4u,0,0);bytes_write(predicted,z+i*4u,0);}
    add('O',z+q*4u,END,e);
    tsl9_rebuild_reset_memory_186ba();
    require(gp_reads==3u && seen==planned,"all planned effects consumed");
    require(memcmp(actual,predicted,128)==0,"forward-copy live byte memory");
}
static void copy_lengths(void)
{
    unsigned n,z;++groups;
    for(n=0;n<=32u;++n)for(z=0;z<=12u;++z)
        scenario(0x31000000u,0x31000000u+n*4u-128u,END-128u-z*4u);
}
static void independent_GP_and_unsigned(void)
{
    ++groups;
    scenario(0x20004000u,0x20004000u,0x20004000u);
    scenario(0x80000000u,0x7fffff80u,END-128u);
    scenario(0x80000000u,0x7fffff7cu,END-128u);
    scenario(0x80000000u,0x7fffff84u,END-128u);
    scenario(0x7ffffffcu,0x7fffff84u,END-128u);
    scenario(0xfffffff8u,0xffffff7cu,END-128u);
    scenario(0x100u,0xffffff80u,END-128u);
    scenario(0xffffffffu,0xffffff7fu,END-124u);
    scenario(0xfffffff0u,0xffffff78u,END-120u);
}
static void forward_overlap(void)
{
    unsigned gap;++groups;
    for(gap=1;gap<=8u;++gap){
        scenario(SOURCE+gap*4u,SOURCE+gap*4u-128u+32u*4u,END-128u);
        scenario(SOURCE-gap*4u,SOURCE-gap*4u-128u+32u*4u,END-128u);
    }
}
static void numeric_unaligned_fakes(void)
{
    unsigned low,n;++groups;
    for(low=0;low<4u;++low)for(n=0;n<9u;++n){
        scenario(0x31000000u+low,0x31000000u+low+n*4u-128u,END-128u-16u+low);
        scenario(SOURCE+1u+low,SOURCE+1u+low+17u-128u,END-128u);
    }
}
static void boundary_residues(void)
{
    unsigned low;++groups;
    for(low=0;low<4u;++low){
        scenario(END,END-128u,END-128u+low);
        scenario(END,END-127u,END-128u-1u-low);
        scenario(0x30000000u,0x30000000u-128u,END-128u-7u+low);
    }
}
int main(int argc,char **argv)
{
    FILE *input;
    require(argc==2,"one exact original-data path");input=fopen(argv[1],"rb");
    require(input!=NULL,"original data readable");
    require(fseek(input,0x12b60L,SEEK_SET)==0,"initializer offset");
    require(fread(initial,1,128,input)==128u,"exact initializer128 bytes read as data");
    require(fclose(input)==0,"data file close");
    copy_lengths();independent_GP_and_unsigned();forward_overlap();numeric_unaligned_fakes();boundary_residues();
    printf("{\"passed\":true,\"groups\":%u,\"cases\":%u,\"checks\":%u}\n",groups,cases,checks);
    return 0;
}
