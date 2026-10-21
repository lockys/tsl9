#include "native_clock.h"
#include "test_io.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define GPA UINT32_C(0x20004000)
#define GPB UINT32_C(0x20005000)
#define GPC UINT32_C(0x20006000)
#define GPD UINT32_C(0x20007000)
#define RCC UINT32_C(0x40021004)
#define EXTEN UINT32_C(0x40023800)
typedef struct event {char kind;uint32_t address,value;} event;
typedef struct word {uint32_t address,value;} word;
static event events[40];static unsigned count,checks,groups,gp_reads;
static word words[8];static unsigned word_count;
static uint32_t gp,rcc[8],exten;static unsigned rcc_count,rcc_used,exten_reads;
static uint8_t shift_byte;static uint32_t table_address;
static int gp_mode,derive_mode;static unsigned clock_stores;
static void check(int okay,const char *message){
    ++checks;if(!okay){fprintf(stderr,"FAIL: %s\n",message);exit(1);}
}
static void record(char kind,uint32_t address,uint32_t value){
    check(count<40,"bounded synthetic trace");events[count].kind=kind;
    events[count].address=address;events[count++].value=value;
}
static void put_word(uint32_t address,uint32_t value){
    unsigned i;for(i=0;i<word_count;++i)if(words[i].address==address){words[i].value=value;return;}
    check(word_count<8,"bounded synthetic word map");words[word_count].address=address;
    words[word_count++].value=value;
}
static uint32_t get_word(uint32_t address){
    unsigned i;for(i=0;i<word_count;++i)if(words[i].address==address)return words[i].value;
    check(0,"no invented value for unmapped RAM");return 0;
}
static void reset(void){
    count=gp_reads=word_count=rcc_count=rcc_used=exten_reads=clock_stores=0;
    gp=GPA;exten=0;shift_byte=0;table_address=GPA+64;gp_mode=derive_mode=0;
    memset(events,0,sizeof events);memset(words,0,sizeof words);memset(rcc,0,sizeof rcc);
}
uint32_t tsl9_nc_test_gp(void){++gp_reads;record('G',0,gp);return gp;}
uint32_t tsl9_nc_test_read32(uint32_t address){
    uint32_t value;
    if(address==RCC){check(rcc_used<rcc_count,"one queued sample per fresh RCC read");value=rcc[rcc_used++];}
    else if(address==EXTEN){++exten_reads;value=exten;}
    else{
        check(address==gp+108,"live GP for global word read");value=get_word(address);
    }
    record('R',address,value);
    if(address!=RCC && address!=EXTEN){
        if(gp_mode==1)gp=GPD;
        if(gp_mode==2)gp=GPB;
    }
    return value;
}
uint8_t tsl9_nc_test_read8(uint32_t address){
    check(!derive_mode,"derived fields do not reload a byte");
    check(address==table_address,"live GP and fresh index for table read");
    record('r',address,shift_byte);if(gp_mode==1)gp=GPC;return shift_byte;
}
void tsl9_nc_test_write32(uint32_t address,uint32_t value){
    check(address==gp+108,"live GP for global word store");
    record('W',address,value);put_word(address,value);++clock_stores;
    if(gp_mode==1 && clock_stores==1)gp=GPB;
}
void tsl9_nc_test_write8(uint32_t address,uint8_t value){
    check(derive_mode && address==gp+382,"live GP and byte output width");
    record('b',address,value);
    /* A byte-store boundary can change the environment. The quotient remains
     * a held value; subsequent code must not reload this byte or clock word. */
    if(gp_mode==2){gp=GPC;put_word(GPC+108,0xffffffffu);}
}
void tsl9_nc_test_write16(uint32_t address,uint16_t value){
    check(derive_mode && address==gp+380,"live GP and halfword output width");
    record('h',address,value);
}
static void same(unsigned i,char kind,uint32_t address,uint32_t value){
    check(i<count,"effect exists");check(events[i].kind==kind,"effect kind/order");
    check(events[i].address==address,"effect exact address");check(events[i].value==value,"effect exact value");
}
static void query_tail(unsigned i,uint32_t base,uint32_t divisor_cfg){
    same(i++,'G',0,GPA);same(i++,'W',GPA+108,base);
    same(i++,'R',RCC,divisor_cfg);same(i++,'G',0,GPA);
    same(i++,'r',table_address,shift_byte);same(i++,'G',0,GPA);
    same(i++,'R',GPA+108,base);same(i++,'G',0,GPA);
    same(i++,'W',GPA+108,base>>(shift_byte&31u));
    check(count==i && gp_reads==4 && rcc_used==rcc_count,"complete query trace");
}
static void direct_sources(void){
    static const uint32_t selectors[]={0,4,12};unsigned s;
    ++groups;
    for(s=0;s<3;++s){
        uint32_t base=selectors[s]==4?32000000u:8000000u;
        reset();rcc[0]=selectors[s]|0x80000000u;rcc[1]=0xf0;rcc_count=2;
        table_address=GPA+64+15;shift_byte=2;
        tsl9_rebuild_clock_query_18834();same(0,'R',RCC,rcc[0]);query_tail(1,base,rcc[1]);
        check(exten_reads==0,"direct sources do not read EXTEN");
    }
}
static void pll_sources(void){
    unsigned n,source;
    ++groups;
    for(n=0;n<16;++n)for(source=0;source<5;++source){
        uint32_t multiplier=n+2u,base;unsigned j=3,read_end;
        reset();if(multiplier==17)multiplier=18;
        rcc[0]=8;rcc[1]=(n<<18)|0x10000u;
        rcc[2]=source<2?0u:0x10000u;
        if(source<2){base=source?8000000u:4000000u;exten=source?16u:0u;}
        else if(source==2){base=16000000u;rcc[j++]=0xc00000u;}
        else{base=source==3?8000000u:4000000u;rcc[j++]=0x800000u;rcc[j++]=source==3?0u:0x20000u;}
        rcc[j++]=0;rcc_count=j;
        tsl9_rebuild_clock_query_18834();
        same(0,'R',RCC,rcc[0]);same(1,'R',RCC,rcc[1]);same(2,'R',RCC,rcc[2]);
        read_end=3;
        if(source<2){same(read_end++,'R',EXTEN,exten);check(exten_reads==1,"fresh internal-source control read");}
        else{
            same(read_end++,'R',RCC,rcc[3]);
            if(source>2)same(read_end++,'R',RCC,rcc[4]);
            check(exten_reads==0,"external path does not sample EXTEN");
        }
        query_tail(read_end,multiplier*base,0);
    }
}
static void shifts_and_indices(void){
    unsigned index,shift;
    ++groups;
    for(index=0;index<16;++index)for(shift=0;shift<256;++shift){
        reset();rcc[0]=0;rcc[1]=index<<4;rcc_count=2;
        table_address=GPA+64+index;shift_byte=(uint8_t)shift;
        tsl9_rebuild_clock_query_18834();query_tail(1,8000000,rcc[1]);
    }
}
static void fresh_gp_and_global(void){
    ++groups;reset();gp_mode=1;rcc[0]=4;rcc[1]=0x70;rcc_count=2;
    table_address=GPB+64+7;shift_byte=33;put_word(GPC+108,0x80000000u);
    tsl9_rebuild_clock_query_18834();
    same(0,'R',RCC,4);same(1,'G',0,GPA);same(2,'W',GPA+108,32000000);
    same(3,'R',RCC,0x70);same(4,'G',0,GPB);same(5,'r',table_address,33);
    same(6,'G',0,GPC);same(7,'R',GPC+108,0x80000000u);
    same(8,'G',0,GPD);same(9,'W',GPD+108,0x40000000u);
    check(count==10 && gp_reads==4,"four distinct live GP observations");
    check(get_word(GPA+108)==32000000 && get_word(GPC+108)==0x80000000u,"separate global identities preserved");
}
static void derived_case(uint32_t value){
    uint32_t low=(value/8000000u)&255u;
    reset();derive_mode=1;put_word(GPA+108,value);tsl9_rebuild_clock_fields_1973c();
    same(0,'G',0,GPA);same(1,'R',GPA+108,value);same(2,'G',0,GPA);
    same(3,'b',GPA+382,low);same(4,'G',0,GPA);same(5,'h',GPA+380,(low*1000u)&65535u);
    check(count==6 && gp_reads==3 && rcc_used==0,"only derived source effects");
}
static void division_boundaries(void){
    uint32_t quotient;
    ++groups;
    for(quotient=0;quotient<=536;++quotient){
        uint64_t start=(uint64_t)quotient*8000000u,end=(uint64_t)(quotient+1u)*8000000u-1u;
        if(end>UINT32_MAX)end=UINT32_MAX;
        derived_case((uint32_t)start);derived_case((uint32_t)end);
    }
    derived_case(0x80000000u);derived_case(UINT32_MAX);
}
static void derived_live_gp(void){
    uint32_t value=UINT32_MAX,low=(value/8000000u)&255u;
    ++groups;reset();derive_mode=1;gp_mode=2;put_word(GPA+108,value);
    tsl9_rebuild_clock_fields_1973c();
    same(0,'G',0,GPA);same(1,'R',GPA+108,value);same(2,'G',0,GPB);
    same(3,'b',GPB+382,low);same(4,'G',0,GPC);same(5,'h',GPC+380,(low*1000u)&65535u);
    check(count==6 && gp_reads==3,"derived three GP sites and held truncated quotient");
}
int main(void){
    direct_sources();pll_sources();shifts_and_indices();fresh_gp_and_global();division_boundaries();derived_live_gp();
    printf("{\"passed\":true,\"groups\":%u,\"checks\":%u}\n",groups,checks);return 0;
}
