#define main legacy_general_ble_main
#include "test_general_ble.c"
#undef main
int main(void){unsigned i;fixture();put(0x2000b9d8,1,1);for(i=0;i<12;i++)put(0x2000c1b4+4*12+i,0x2e+i,1);CHECK(run(0xd2,1)==GB_RETURNED);CHECK(last_reply.command==0xd2&&last_reply.length==8);for(i=0;i<6;i++)CHECK(reply_data[i]==0x31+i&&reply_known[i]==255);CHECK(reply_data[6]==0&&reply_data[7]==0);printf("REPORTS_COUNTEREXAMPLE_RESULT groups=1 checks=%u failures=%u original_executed=no hardware=no\n",checks,failures);return failures?1:0;}
