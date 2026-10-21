/* Reuse the immutable independent memory trace, not the parent's fixture. */
#include "clock_registers.h"
#include "register_test_io.h"
#define main previous_independent_main
#define tsl9_rebuild_clock_query_18834 observed_query
#define tsl9_rebuild_clock_fields_1973c observed_fields
#define tsl9_nc_test_gp tsl9_ca_test_gp
#define tsl9_nc_test_read32 tsl9_ca_test_read32
#define tsl9_nc_test_read8 tsl9_ca_test_read8
#define tsl9_nc_test_write32 tsl9_ca_test_write32
#define tsl9_nc_test_write8 tsl9_ca_test_write8
#define tsl9_nc_test_write16 tsl9_ca_test_write16
#include "../../tsl9-v4160-native-clock-2026-10-21/code-review/test_independent.c"
#undef main
#undef tsl9_rebuild_clock_query_18834
#undef tsl9_rebuild_clock_fields_1973c

static unsigned a2_writes,query_commits,field_commits;
static uint32_t final_a2,final_a3,final_a4,final_a5;

void tsl9_ca_test_set_a2(uint32_t value)
{
    ++a2_writes;final_a2=value;
    require(value==0xc00000u,"source external A2 literal");
    require(observed==4 && expected[3].kind=='r'
            && expected[3].address==0x40021004u,
            "A2 committed after the fourth fresh config read");
}
void tsl9_ca_test_query_outputs(uint32_t a3,uint32_t a4,uint32_t a5)
{
    ++query_commits;final_a3=a3;final_a4=a4;final_a5=a5;
    require(observed==planned,"query residues committed after final live store");
}
void tsl9_ca_test_field_outputs(uint32_t a4,uint32_t a5)
{
    ++field_commits;final_a4=a4;final_a5=a5;
    require(observed==planned,"field residues committed after halfword store");
}
void observed_query(void)
{
    const uint32_t selector=expected[0].value&12u;
    uint32_t a3,shift=0;unsigned external=0,i;
    if(selector==4u)a3=4u;
    else if(selector!=8u)a3=8u;
    else if(!(expected[2].value&0x10000u))a3=17u;
    else {
        external=1;
        if((expected[3].value&0xc00000u)==0xc00000u)a3=0x40021000u;
        else a3=expected[4].value<<14;
    }
    for(i=0;i<planned;++i)if(expected[i].kind=='b')shift=expected[i].value;
    a2_writes=query_commits=field_commits=0;final_a2=0x13579bdfu;
    final_a3=final_a4=final_a5=0xdeadbeefu;
    tsl9_rebuild_clock_query_registers_18834();
    require(a2_writes==external,"A2 write exists only on external source branch");
    require(final_a2==(external?0xc00000u:0x13579bdfu),"no stale A2 restoration on untouched paths");
    require(query_commits==1 && field_commits==0,"exactly one query register commitment");
    require(final_a3==a3,"path-dependent A3 survives into later unresolved callback");
    require(final_a4==shift,"A4 retains full unsigned table byte");
    require(final_a5==expected[planned-1].value,"A5 retains full final shifted scalar word");
}
void observed_fields(void)
{
    const uint32_t scalar=expected[1].value;
    const uint32_t product=((scalar/8000000u)&255u)*1000u;
    a2_writes=query_commits=field_commits=0;
    final_a2=0xabcdef01u;final_a4=final_a5=0xdeadbeefu;
    tsl9_rebuild_clock_fields_registers_1973c();
    require(a2_writes==0 && final_a2==0xabcdef01u,"field body leaves A2 untouched");
    require(field_commits==1 && query_commits==0,"exactly one field register commitment");
    require(final_a4==1000u,"field A4 literal remains1000");
    require(final_a5==product,"field A5 retains full product despite halfword store");
}
int main(void)
{
    return previous_independent_main();
}
