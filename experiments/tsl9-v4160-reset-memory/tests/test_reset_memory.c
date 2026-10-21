#if defined(_MSC_VER)
#define _CRT_SECURE_NO_WARNINGS
#endif
#include "reset_memory.h"
#include "test_io.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define INIT UINT32_C(0x1ab60)
#define END UINT32_C(0x2000c958)
#define GP UINT32_C(0x20004000)
#define CAP 20000
typedef struct event { char kind;uint32_t address,value,extra; } event;
static event expected[CAP];
static unsigned expected_count,used,checks,cases,groups,gp_used;
static uint32_t gp_samples[3],initial_words[32],source_words[32];
static void require(int okay,const char *message)
{
    ++checks;
    if(!okay){fprintf(stderr,"FAIL: %s\n",message);exit(1);}
}
static void add(char kind,uint32_t address,uint32_t value,uint32_t extra)
{
    require(expected_count<CAP,"bounded synthetic fixture");
    expected[expected_count].kind=kind;expected[expected_count].address=address;
    expected[expected_count].value=value;expected[expected_count++].extra=extra;
}
static void observed(char kind,uint32_t address,uint32_t value,uint32_t extra)
{
    event e;
    require(used<expected_count,"no unexpected or unbounded effect");e=expected[used++];
    require(e.kind==kind,"exact effect order and width");
    require(e.address==address,"exact numeric address or A0");
    require(e.value==value,"exact live value or A1");
    require(e.extra==extra,"exact A2 or effect metadata");
}
uint32_t tsl9_rm_test_gp(void)
{
    uint32_t value;require(gp_used<3,"only three live GP observations");
    value=gp_samples[gp_used++];observed('G',0,value,0);return value;
}
uint32_t tsl9_rm_test_read32(uint32_t address)
{
    uint32_t value;
    require(address>=INIT && address<INIT+128u && (address-INIT)%4u==0u,
            "read only declared synthetic initializer words");
    value=source_words[(address-INIT)/4u];observed('R',address,value,0);return value;
}
void tsl9_rm_test_write32(uint32_t address,uint32_t value)
{
    observed('W',address,value,0);
    if(address>=INIT && address<INIT+128u && (address-INIT)%4u==0u)
        source_words[(address-INIT)/4u]=value;
}
void tsl9_rm_test_outputs(uint32_t a0,uint32_t a1,uint32_t a2)
{
    observed('O',a0,a1,a2);
}
static void scenario(uint32_t first_gp,uint32_t second_gp,uint32_t third_gp)
{
    uint32_t bound=second_gp+128u,start=third_gp+128u,final_clear;
    uint32_t copies=first_gp<bound?(uint32_t)(((uint64_t)bound-first_gp+3u)/4u):0u;
    uint32_t zeros=start<END?(END-start+3u)/4u:0u,i;
    uint32_t alias=first_gp>INIT && first_gp<INIT+128u && (first_gp-INIT)%4u==0u
        ?(first_gp-INIT)/4u:0u;
    ++cases;expected_count=used=gp_used=0;
    gp_samples[0]=first_gp;gp_samples[1]=second_gp;gp_samples[2]=third_gp;
    memcpy(source_words,initial_words,sizeof source_words);
    require(copies<=32u && zeros<=8758u,"bounded terminating test domain");
    require(!copies || (uint64_t)first_gp+(uint64_t)copies*4u<=UINT32_MAX,
            "exclude nonterminating copy wrap domains");
    add('G',0,first_gp,0);add('G',0,second_gp,0);
    for(i=0;i<copies;++i){
        uint32_t value=initial_words[alias?i%alias:i];
        add('R',INIT+i*4u,value,0);add('W',first_gp+i*4u,value,0);
    }
    add('G',0,third_gp,0);
    for(i=0;i<zeros;++i)add('W',start+i*4u,0,0);
    final_clear=start+zeros*4u;
    add('O',final_clear,END,bound);
    tsl9_rebuild_reset_memory_186ba();
    require(used==expected_count && gp_used==3,"complete effects and output registers");
}
static void normal_original_data(void)
{
    ++groups;scenario(GP,GP,GP);
}
static void independent_bounds(void)
{
    uint32_t n,z;
    ++groups;
    for(n=0;n<=32u;++n)for(z=0;z<=8u;++z)
        scenario(UINT32_C(0x30000000),UINT32_C(0x30000000)+n*4u-128u,END-128u-z*4u);
}
static void unsigned_and_skip(void)
{
    ++groups;
    scenario(0x80000000u,0x7fffff7cu,END-128u);
    scenario(0xfffffff4u,0xffffff7cu,END-128u);
    scenario(0xfffffff8u,0xffffff7cu,END-124u);
    scenario(100u,0xffffff80u,END-128u);
    scenario(0x30000000u,0x2fffff82u,END-128u);
    scenario(0x30000001u,0x2fffff86u,END-131u);
}
static void forward_copy_alias(void)
{
    ++groups;scenario(INIT+4u,INIT+4u,END-128u);scenario(INIT-4u,INIT-4u,END-128u);
}
static void zero_residues(void)
{
    uint32_t n,low;
    ++groups;
    for(n=0;n<8u;++n)for(low=0;low<4u;++low)
        scenario(0x40000000u,0u,END-128u-n*4u+low);
}
static void load_initializer(const char *name)
{
    unsigned char bytes[128];unsigned i;FILE *file=fopen(name,"rb");
    require(file!=NULL,"runner-provided original initializer copy exists");
    require(fread(bytes,1,sizeof bytes,file)==sizeof bytes,"exact 128 original initializer bytes");
    require(fgetc(file)==EOF,"no appended initializer bytes");
    require(fclose(file)==0,"initializer file closed");
    for(i=0;i<32u;++i)initial_words[i]=(uint32_t)bytes[i*4u]
        |((uint32_t)bytes[i*4u+1u]<<8)|((uint32_t)bytes[i*4u+2u]<<16)|((uint32_t)bytes[i*4u+3u]<<24);
}
int main(int argc,char **argv)
{
    require(argc==2,"exact local initializer argument");load_initializer(argv[1]);
    normal_original_data();independent_bounds();unsigned_and_skip();forward_copy_alias();zero_residues();
    printf("{\"passed\":true,\"groups\":%u,\"cases\":%u,\"checks\":%u}\n",groups,cases,checks);
    return 0;
}
