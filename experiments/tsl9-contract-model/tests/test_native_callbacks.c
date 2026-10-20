#include "native_callbacks.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static tf_model memory;static nc_model model;
static uint8_t runtime[76800],boot[12288],metadata[8];
static unsigned checks,failures,groups,requests,disconnects,copy_reads,copy_writes,programs,csr_clears,csr_sets;
static uint32_t reset_register,clock_sequence[16],clock_n,clock_index,spi_status,spi_data,last_jump,fail_target,last_reset;
static int metadata_persist,metadata_known,mutate_second,scalar_unknown,reset_returns;
static nc_flow jump_flow;
typedef struct {nc_kind kind;uint32_t va,target,value;unsigned width,length;} logged;
static logged logs[8192];
#define A(x) (TF_RAM_BASE+UINT32_C(x))
#define CHECK(x) do{checks++;if(!(x)){failures++;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void group(const char *s){groups++;printf("GROUP %s\n",s);}
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){memory.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));memory.known[a-TF_RAM_BASE+i]=255;}}
static nc_flow provider(void *p,nc_model *m,const nc_request *r,nc_result *out){
    unsigned i;(void)p;CHECK(m==&model);memset(out,0,sizeof(*out));out->known=scalar_unknown?0:UINT32_MAX;
    if(requests<8192){logs[requests].kind=r->kind;logs[requests].va=r->va;logs[requests].target=r->target;logs[requests].value=r->count?r->arguments[0]:0;logs[requests].width=r->width;logs[requests].length=r->length;}requests++;
    if(fail_target&&r->target==fail_target)return NC_HALT;
    if(r->kind==NC_ROM_DISCONNECT){disconnects++;CHECK(r->slot==380&&r->count==1);if(mutate_second){put(A(0x40a2),0xfffe,2);mutate_second=0;}return NC_RETURNED;}
    if(r->kind==NC_MMIO_READ){if(r->target==0x40021010)out->value=reset_register;else if(r->target==0x40013008)out->value=spi_status;else if(r->target==0x4001300c)out->value=spi_data;return NC_RETURNED;}
    if(r->kind==NC_MMIO_WRITE){if(r->target==0x40021010)reset_register=r->arguments[0];if(r->target==0xe000e048)last_reset=r->arguments[0];return NC_RETURNED;}
    if(r->kind==NC_ROM_SCALAR){CHECK(r->slot==124);out->value=clock_index<clock_n?clock_sequence[clock_index++]:0;return NC_RETURNED;}
    if(r->kind==NC_ROM_COPY){
        CHECK(r->slot==76&&r->length==8&&r->destination==NC_VALUE_VIEW);
        out->length=8;
        if(r->source==NC_ADDRESS){CHECK(r->source_address==0x08077b00);copy_reads++;for(i=0;i<8;i++){out->data[i]=metadata[i];out->bytes_known[i]=(uint8_t)((!metadata_known&&i==4)?0:255);}}
        else{CHECK(r->source==NC_VALUE_VIEW);copy_writes++;for(i=0;i<8;i++){out->data[i]=r->data[i];out->bytes_known[i]=r->known[i];}}
        return NC_RETURNED;
    }
    if(r->kind==NC_FLASH_CALL){if(r->target==0x18c46){programs++;CHECK(r->length==256&&r->source==NC_VALUE_VIEW&&r->arguments[0]==0x08077b00);CHECK(r->data[4]==1);for(i=0;i<8;i++)CHECK(r->known[i]==255);for(i=8;i<256;i++)CHECK(r->known[i]==0);if(metadata_persist)memcpy(metadata,r->data,8);}return NC_RETURNED;}
    if(r->kind==NC_CSR_CLEAR){csr_clears++;CHECK(r->target==0x800&&r->arguments[0]==136);return NC_RETURNED;}
    if(r->kind==NC_CSR_SET){csr_sets++;CHECK(r->target==0x800&&r->arguments[0]==136);return NC_RETURNED;}
    if(r->kind==NC_JUMP){last_jump=r->arguments[0];return jump_flow;}
    if(r->kind==NC_RESET_WAIT)return reset_returns?NC_RETURNED:NC_TRANSFER;
    return NC_HALT;
}
static void fresh(void){nc_backend b;memset(&memory,0,sizeof(memory));memset(memory.known,255,sizeof(memory.known));memset(metadata,0,sizeof(metadata));b.context=NULL;b.invoke=provider;nc_init(&model,&memory,&b);requests=disconnects=copy_reads=copy_writes=programs=csr_clears=csr_sets=0;reset_register=0x11020304;clock_n=clock_index=fail_target=last_jump=last_reset=0;spi_status=3;spi_data=128;metadata_persist=metadata_known=1;mutate_second=scalar_unknown=reset_returns=0;jump_flow=NC_TRANSFER;put(A(0x409e),0xfffe,2);put(A(0x40a2),0xfffe,2);put(A(0x407e),0xfffe,2);}
static void test_disconnects(void){group("dual/single live handles, sentinel and ignored scalar distinct flow");fresh();CHECK(nc_run(&model,NC_RUNTIME_DISCONNECT,0)==NC_RETURNED&&requests==0);fresh();put(A(0x409e),3,2);put(A(0x40a2),4,2);scalar_unknown=1;CHECK(nc_run(&model,NC_RUNTIME_DISCONNECT,0)==NC_RETURNED&&disconnects==2);CHECK(logs[0].value==3&&logs[1].value==4);fresh();put(A(0x409e),3,2);put(A(0x40a2),4,2);mutate_second=1;CHECK(nc_run(&model,NC_RUNTIME_DISCONNECT,0)==NC_RETURNED&&disconnects==1);fresh();put(A(0x407e),9,2);CHECK(nc_run(&model,NC_BOOT_DISCONNECT,0)==NC_RETURNED&&disconnects==1&&logs[0].value==9);fresh();put(A(0x409e),3,2);memory.known[0x40a2]=0;CHECK(nc_run(&model,NC_RUNTIME_DISCONNECT,0)==NC_HALT&&disconnects==1);fresh();put(A(0x407e),9,2);model.backend.invoke=NULL;CHECK(nc_run(&model,NC_BOOT_DISCONNECT,0)==NC_HALT&&requests==0);}
static void test_jump_reset(void){group("BOOT jump carries raw a0 and reset never confirms return");fresh();CHECK(nc_run(&model,NC_BOOT_JUMP,0x12345678)==NC_TRANSFER);CHECK(last_jump==0x12345678&&logs[0].target==0x8000);fresh();jump_flow=NC_RETURNED;CHECK(nc_run(&model,NC_BOOT_JUMP,0)==NC_RETURNED);fresh();CHECK(nc_run(&model,NC_BOOT_RESET,0)==NC_TRANSFER);CHECK(csr_clears==1&&last_reset==0xbeef0080&&requests==3);CHECK(logs[1].width==32&&logs[1].target==0xe000e048);fresh();reset_returns=1;CHECK(nc_run(&model,NC_BOOT_RESET,0)==NC_HALT&&last_reset==0xbeef0080);fresh();fail_target=0xe000e048;CHECK(nc_run(&model,NC_BOOT_RESET,0)==NC_HALT&&csr_clears==1&&last_reset==0);}
static void test_runtime_reset(void){group("Runtime reset GPIO/SPI/clock prefixes fully interpreted before CSR/reset");fresh();CHECK(nc_run(&model,NC_RUNTIME_RESET,0)==NC_TRANSFER);CHECK(reset_register==0x11020304&&last_reset==0xbeef0080&&csr_clears==1);CHECK(requests>30&&logs[0].target==0x40021010&&logs[1].value==0x13020304);fresh();fail_target=0x40013008;CHECK(nc_run(&model,NC_RUNTIME_RESET,0)==NC_HALT);CHECK(reset_register==0x11020304&&csr_clears==0&&last_reset==0);fresh();spi_data=0;clock_n=4;clock_sequence[0]=0;clock_sequence[1]=5;clock_sequence[2]=0;clock_sequence[3]=5;CHECK(nc_run(&model,NC_RUNTIME_RESET,0)==NC_TRANSFER&&last_reset==0xbeef0080);fresh();scalar_unknown=1;CHECK(nc_run(&model,NC_RUNTIME_RESET,0)==NC_HALT&&requests==1);}
static void test_metadata(void){group("metadata byte4 retry preserves unknown stack tail and ignored helper status");fresh();metadata[4]=1;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_TRANSFER);CHECK(copy_reads==1&&programs==0&&copy_writes==0);fresh();metadata[0]=0x31;metadata[7]=0x47;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_TRANSFER);CHECK(copy_reads==2&&copy_writes==1&&programs==1&&metadata[4]==1);CHECK(metadata[0]==0x31&&metadata[7]==0x47&&csr_sets==1&&csr_clears==2);fresh();metadata_persist=0;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_TRANSFER);CHECK(copy_reads==5&&copy_writes==5&&programs==5&&last_reset==0xbeef0080);fresh();metadata_known=0;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_HALT&&copy_reads==1&&programs==0&&csr_clears==0);fresh();fail_target=0x18c18;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_HALT);CHECK(copy_reads==1&&copy_writes==1&&csr_clears==1&&csr_sets==0&&last_reset==0);}
static void test_timeouts(void){group("native255 SPI retry and host spin guard are different boundaries");fresh();spi_status=0;clock_n=4;clock_sequence[0]=0;clock_sequence[1]=5;clock_sequence[2]=0;clock_sequence[3]=5;CHECK(nc_run(&model,NC_RUNTIME_RESET,0)==NC_TRANSFER&&last_reset==0xbeef0080);CHECK(requests>500);fresh();spi_data=0;model.spin_budget=2;CHECK(nc_run(&model,NC_RUNTIME_RESET,0)==NC_HALT&&last_reset==0&&csr_clears==0);CHECK(model.unknown_va==0x16bc4);}
static void test_diagnostic_reuse(void){group("failed new metadata attempt cannot reuse old completed scalar");fresh();metadata[4]=1;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_TRANSFER&&model.metadata_status_known==1&&model.metadata_status==0);nc_resume(&model);metadata_known=0;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_HALT);CHECK(model.metadata_status_known==0);fresh();metadata_persist=0;CHECK(nc_run(&model,NC_RUNTIME_BOOT_REQUEST,0)==NC_TRANSFER&&model.metadata_status_known==1&&model.metadata_status==1);}
static void test_sources(void){group("fresh literal six-body original fixtures");CHECK(runtime[0xe12]==0xc1&&runtime[0xe62]==0x82);CHECK(runtime[0x19ee]==0x73&&runtime[0x1a00]==0x01);CHECK(runtime[0x1dfa]==0x41&&runtime[0x1e08]==0x7d);CHECK(boot[0x92c]==0xc1&&boot[0x942]==0x82);CHECK(boot[0x10e2]==0x21&&boot[0x10e4]==0x02);CHECK(boot[0xffa]==0x73&&boot[0x100c]==0x01);}
static int input(const char *p,uint8_t *b,size_t n){FILE *f=fopen(p,"rb");int ok=f&&fread(b,1,n,f)==n;if(f)fclose(f);return ok;}
int main(int argc,char **argv){if(argc!=3||!input(argv[1],runtime,sizeof(runtime))||!input(argv[2],boot,sizeof(boot)))return 2;test_disconnects();test_jump_reset();test_runtime_reset();test_metadata();test_timeouts();test_diagnostic_reuse();test_sources();printf("NATIVE_CALLBACKS_RESULT groups=%u checks=%u failures=%u original_executed=no hardware=no\n",groups,checks,failures);return failures?1:0;}
