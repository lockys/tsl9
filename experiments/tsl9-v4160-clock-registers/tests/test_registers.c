/* Reuse the unchanged prior memory-effect fixtures, adding independently
 * source-derived register-output expectations at every reconstructed call.
 * This is high-level C testing, not an instruction decoder or ISA emulator. */
#include "clock_registers.h"
#include "register_test_io.h"
#define main memory_fixture_main
#define tsl9_rebuild_clock_query_18834 checked_query
#define tsl9_rebuild_clock_fields_1973c checked_fields
#define tsl9_nc_test_gp tsl9_ca_test_gp
#define tsl9_nc_test_read32 tsl9_ca_test_read32
#define tsl9_nc_test_read8 tsl9_ca_test_read8
#define tsl9_nc_test_write32 tsl9_ca_test_write32
#define tsl9_nc_test_write8 tsl9_ca_test_write8
#define tsl9_nc_test_write16 tsl9_ca_test_write16
#include "../../tsl9-v4160-native-clock/tests/test_native_clock.c"
#undef main
#undef tsl9_rebuild_clock_query_18834
#undef tsl9_rebuild_clock_fields_1973c
static unsigned marker_count,query_outputs,field_outputs;
static uint32_t returned_a3,returned_a4,returned_a5;

void tsl9_ca_test_set_a2(uint32_t value)
{
    ++marker_count;
    check(value==0xc00000u,"source external-PLL A2 value");
    check(rcc_used==4 && count>0 && events[count-1].kind=='R'
          && events[count-1].address==RCC,"A2 assignment follows fresh external RCC read");
}
void tsl9_ca_test_query_outputs(uint32_t a3,uint32_t a4,uint32_t a5)
{
    ++query_outputs;returned_a3=a3;returned_a4=a4;returned_a5=a5;
}
void tsl9_ca_test_field_outputs(uint32_t a4,uint32_t a5)
{
    ++field_outputs;returned_a4=a4;returned_a5=a5;
}
void checked_query(void)
{
    uint32_t selector=rcc[0]&12u,expected_a3;
    unsigned external=selector==8u && (rcc[2]&0x10000u)!=0u;
    marker_count=query_outputs=field_outputs=0;
    tsl9_rebuild_clock_query_registers_18834();
    if(selector==4u)expected_a3=4u;
    else if(selector!=8u)expected_a3=8u;
    else if(!external)expected_a3=17u;
    else if((rcc[3]&0xc00000u)==0xc00000u)expected_a3=RCC-4u;
    else expected_a3=rcc[4]<<14;
    check(marker_count==external,"A2 is assigned only on external PLL path");
    check(query_outputs==1 && field_outputs==0,"one query return-register commitment");
    check(returned_a3==expected_a3,"query A3 path residue reaches later callback");
    check(returned_a4==shift_byte,"query A4 is unsigned live table byte");
    check(count>0 && events[count-1].kind=='W'
          && returned_a5==events[count-1].value,"query A5 is full final scalar");
}
void checked_fields(void)
{
    const uint32_t frequency=get_word(gp+108u);
    const uint32_t expected_product=((frequency/8000000u)&255u)*1000u;
    marker_count=query_outputs=field_outputs=0;
    tsl9_rebuild_clock_fields_registers_1973c();
    check(marker_count==0 && query_outputs==0 && field_outputs==1,"only field return-register commitment");
    check(returned_a4==1000u,"field A4 original multiplier residue");
    check(returned_a5==expected_product,"field A5 retains full product before halfword truncation");
}
int main(void)
{
    return memory_fixture_main();
}
