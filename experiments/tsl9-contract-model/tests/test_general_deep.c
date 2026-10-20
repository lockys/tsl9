#include "general_deep.h"
#include <stdio.h>
#include <string.h>
static tf_model ram;static gd_model deep;static gd_backend io;static uint8_t image[76800];
static unsigned groups,checks,failures,calls,replies;static uint8_t sent[2][76],sent_known[2][76];static uint16_t handles[2];static size_t lengths[2];
static uint32_t raw96,raw_known,stop_site;static int switch_config,switch_slot,partial_copy,switch_after_copy,noop_zero,second_active;static uint8_t metadata[8];
#define R(x) (TF_RAM_BASE+UINT32_C(x))
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));ram.known[a-TF_RAM_BASE+i]=255;}}
static void connect(unsigned i,uint16_t h,uint8_t auth,uint8_t mode){uint32_t a=R(0xc792)+4*i;put(a,h,2);put(a+2,auth,1);put(a+3,mode,1);}
static uint8_t outside(uint32_t a){if(a>=0x08077b00&&a<0x08077b08)return metadata[a-0x08077b00];if(a>=0x1ffff7ec&&a<0x1ffff7f4)return (uint8_t)(a-0x1ffff7ec+1);if(a>=0x1ffff7e8&&a<0x1ffff7ec)return (uint8_t)(a-0x1ffff7e8+0x21);return 0;}
static gb_flow invoke(void *p,gd_model *g,const gd_request *r,gb_scalar *out){size_t i,n;(void)p;CHECK(g->memory==&ram);++calls;out->value=0;out->known=0;
    if(r->kind!=GD_ROM)return GB_HALT;
    if(r->target==96){CHECK(r->argument_count==2&&r->arguments[0]==9&&r->arguments[1]==1);out->value=raw96;out->known=raw_known;if(switch_config)put(R(0x4054),R(0xc500),4);return r->callsite==stop_site?GB_HALT:GB_RETURNED;}
    if(r->target!=72&&r->target!=76)return GB_HALT;
    CHECK(r->buffer&&r->buffer_known&&r->known[0]==0&&r->known[2]==UINT32_MAX&&r->buffer_length==r->arguments[2]);
    n=r->buffer_length;if(r->callsite==stop_site&&!partial_copy)return GB_HALT;if(r->callsite==stop_site&&partial_copy)n=1;if(r->target==72&&noop_zero)return GB_RETURNED;
    for(i=0;i<n;i++){uint32_t a=r->arguments[1]+(uint32_t)i;if(r->target==72){r->buffer[i]=0;r->buffer_known[i]=255;}else if(a>=TF_RAM_BASE&&a<TF_RAM_BASE+TF_RAM_SIZE){r->buffer[i]=ram.ram[a-TF_RAM_BASE];r->buffer_known[i]=ram.known[a-TF_RAM_BASE];}else{r->buffer[i]=outside(a);r->buffer_known[i]=255;}}
    if(r->callsite==0x13398&&switch_after_copy){put(R(0x4054),R(0xc500),4);put(R(0xc792),8,2);}
    return r->callsite==stop_site?GB_HALT:GB_RETURNED;
}
static gb_flow reply(void *p,gd_model *g,const gb_reply_request *r){(void)p;CHECK(g->memory==&ram);CHECK(r->wrapper_va==0x8cfa&&r->source_address==0);CHECK(replies<2);
    if(replies<2){memcpy(sent[replies],r->data,r->length);memcpy(sent_known[replies],r->known,r->length);handles[replies]=r->handle;lengths[replies]=r->length;}++replies;
    if(switch_slot&&replies==1){connect(1,42,0,0);put(R(0xc91c),0,1);}
    if(second_active&&replies==1){connect(1,42,1,1);put(R(0x4050),0,2);ram.known[0x4050]=0;}
    return stop_site==0x8cfa?GB_HALT:GB_RETURNED;
}
static void fixture(void){unsigned i;memset(&ram,0,sizeof(ram));memset(ram.known,255,sizeof(ram.known));memset(&io,0,sizeof(io));memset(sent,0,sizeof(sent));memset(sent_known,0,sizeof(sent_known));
    put(R(0x4054),R(0xc298),4);connect(0,7,1,0);connect(1,65534,0,0);put(R(0x416d),9,1);put(R(0x40c1),1,1);put(R(0x40c2),3,1);put(R(0x40c3),2,1);
    for(i=0;i<16;i++){put(R(0xc298)+i,0xa0+i,1);put(R(0xc2f8)+i,0x60+i,1);put(R(0xc500)+i,0x30+i,1);put(R(0xc560)+i,0x40+i,1);}put(R(0xc29c),0xa4,1);put(R(0xc504),0x34,1);
    for(i=0;i<19;i++)put(R(0xbf44)+i,0x80+i,1);
    metadata[0]=0x12;metadata[1]=0x34;for(i=2;i<8;i++)metadata[i]=(uint8_t)(0x50+i);
    calls=replies=0;raw96=0x1234;raw_known=UINT32_MAX;stop_site=0;switch_config=switch_slot=partial_copy=switch_after_copy=noop_zero=second_active=0;
    io.invoke=invoke;io.reply=reply;gd_init(&deep,&ram,&io);
}
static void a0_fields(void){put(R(0x4116),0x22,1);put(R(0x40c4),3,1);put(R(0x4117),3,1);put(R(0x4164),9,1);put(R(0xbed1),1,1);put(R(0xbf58),0x0102,2);put(R(0xbf5b),1,1);put(R(0xc91c),3,1);put(R(0xbeef),2,1);put(R(0xbf12),2,1);put(R(0xbf26),1,1);put(R(0x416c),2,1);put(R(0xbf99),2,1);put(R(0xbf9e),3,1);put(R(0xbf9b),4,1);put(R(0xbfa0),5,1);put(R(0xbee0),2,1);put(R(0x4115),3,1);put(R(0xbfb1),0xd7,1);}
static void a0_golden(void){static const uint8_t expected[24]={0,0x12,0x34,0xdd,1,2,3,4,5,6,7,8,0x21,0x22,0x23,0x24,1,2,0xbf,0xfe,0x92,0x0b,0x17,5};unsigned i;++groups;fixture();a0_fields();
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(replies==1&&handles[0]==7&&lengths[0]==76);
    for(i=0;i<24;i++)CHECK(sent[0][i]==expected[i]);for(i=0;i<16;i++){CHECK(sent[0][24+i]==0xa0+i);CHECK(sent[0][59+i]==0x60+i);}for(i=0;i<19;i++)CHECK(sent[0][40+i]==0x80+i);CHECK(sent[0][75]==0);
    for(i=0;i<76;i++)CHECK(sent_known[0][i]==255);
}
static void a0_unauthenticated_retains_fields(void){unsigned i;++groups;fixture();a0_fields();switch_slot=1;CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(replies==2&&handles[1]==42&&lengths[1]==76);CHECK(sent[1][3]==1&&sent[1][18]==0&&sent[1][19]==0);
    for(i=20;i<24;i++)CHECK(sent[1][i]==sent[0][i]);for(i=0;i<16;i++){CHECK(sent[1][24+i]==0);CHECK(sent[1][59+i]==0);}CHECK(sent[1][40]==0x80&&sent[1][4]==1);
}
static void a0_preparation_before_gate(void){++groups;fixture();connect(0,65534,0,0);stop_site=0x92b4;CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x92b4&&replies==0);CHECK(calls==3);
    fixture();connect(0,65534,0,0);connect(1,8,1,1);CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(calls==5&&replies==0);
}
static void distinct_callee_stack_prefix(void){++groups;fixture();stop_site=0x9db4;partial_copy=1;CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.dependency_out[0]==0x12&&deep.dependency_known[0]==255);CHECK(deep.known[0]==0&&deep.known[8]==0);
}
static void a0_config_fresh_pointer(void){++groups;fixture();a0_fields();switch_config=1;CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(sent[0][24]==0x30&&sent[0][59]==0x40);}
static void b0_fields(void){unsigned i;connect(0,7,1,1);put(R(0x4050),0x035a,2);put(R(0xbf40),6,1);put(R(0xbed6),2,1);put(R(0xbed7),2,1);put(R(0xbed1),1,1);put(R(0xbf66),1,1);put(R(0xbf68),1,1);put(R(0xbf67),0,1);put(R(0xbf69),1,1);put(R(0xbed9),2,1);put(R(0xbed8),0,1);put(R(0xbedb),2,1);put(R(0xbeda),1,1);put(R(0xbf61),0x65,1);put(R(0xbfae),1,1);put(R(0xbf91),0,1);put(R(0xbf64),1,1);put(R(0xc248),0,2);put(R(0x4115),1,1);put(R(0xbf18),1,1);put(R(0xbf65),1,1);put(R(0xbfa4),0x123456,4);
    for(i=0;i<4;i++)put(R(0x40e8)+i,0x11*(i+1),1);put(R(0xbf41),0xa6,1);put(R(0x4164),9,1);put(R(0xbfac),0x356,2);put(R(0xbfaa),0x6ab,2);put(R(0xbfa8),0x2abc,2);put(R(0xbf60),1,1);put(R(0x4052),1,1);put(R(0xbee9),1,1);for(i=0;i<5;i++)put(R(0x40fc)+i,0x50+i,1);
    put(R(0xbefa),0x2a7,2);put(R(0xbef8),0x5d3,2);put(R(0xbef6),0x634,2);put(R(0xbef4),0x5c,1);put(R(0xbf5e),0x16b,2);put(R(0xbf5c),0xabc,2);put(R(0xbf62),0x2d6,2);put(R(0xbee7),0x15,1);put(R(0xbee6),0xd,1);
}
static void b0_golden(void){static const uint8_t expected[33]={0x5a,0xbd,0x9b,0xe5,0xbf,0x15,0x8d,4,0x11,0x22,0x33,0x44,0xa6,0x56,0x5b,0x35,0xaf,0xea,0x50,0x51,0x52,0x53,0x54,0xa7,0x4e,0x97,0xc6,0x5c,0xbc,0x6a,0xed,0xda,0xda};unsigned i;++groups;fixture();b0_fields();
    CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(replies==1&&handles[0]==7&&lengths[0]==33);for(i=0;i<33;i++){CHECK(sent[0][i]==expected[i]);CHECK(sent_known[0][i]==255);}
}
static void b0_pause_and_construction_order(void){++groups;fixture();b0_fields();put(R(0xc790),1,1);CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(calls==0&&replies==0&&deep.frame_length==0);
    fixture();b0_fields();connect(0,65534,0,0);ram.known[0x4050]=0;CHECK(gd_dispatch(&deep,0x135d4,0)==GB_HALT);CHECK(replies==0&&calls==1);CHECK(deep.boundary_address==R(0x4050));
}
static void output_masks(void){++groups;fixture();a0_fields();ram.known[0x4164]=15;raw_known=0x7ffff;raw96=UINT32_MAX;CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(sent[0][20]==0x31&&sent[0][21]==0);
    fixture();b0_fields();ram.known[0xbfa9]=0x3f;CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(sent[0][16]==0xaf&&sent[0][17]==0xea);
    fixture();a0_fields();raw_known=0x3ffff;CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x16f36&&replies==0);
}
static void unknown_copy_masks(void){++groups;fixture();a0_fields();ram.known[0xbf44]=0;CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(sent_known[0][40]==0&&sent_known[0][39]==255&&sent_known[0][41]==255);}
static void reply_gate_rereads_second_slot(void){++groups;fixture();b0_fields();switch_slot=1;CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(replies==1);}
static void copy_remap_and_reply_handle(void){++groups;fixture();a0_fields();switch_after_copy=1;
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(sent[0][24]==0xa0&&sent[0][59]==0x40&&handles[0]==8);
}
static void scalar_halt_prefix_order(void){++groups;fixture();a0_fields();ram.known[0x4164]=0;
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x13232&&deep.stack[11]==0x4d&&deep.stack[26]==0);
    fixture();a0_fields();ram.known[0xc91c]=1;
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x17f6c&&deep.needed_mask==2&&deep.stack[26]==15);
    fixture();b0_fields();ram.known[0xbf5c]=0;
    CHECK(gd_dispatch(&deep,0x135d4,0)==GB_HALT);CHECK(deep.boundary_va==0xd2aa&&deep.stack[30]==0xc0&&deep.stack[31]==0x5a&&deep.stack[28]==0);
    fixture();b0_fields();ram.known[0xc249]=0x3f;
    CHECK(gd_dispatch(&deep,0x135d4,0)==GB_HALT);CHECK(deep.boundary_va==0x136cc&&deep.stack[4]==1);
}
static void mask_ignored_bits_and_required_bits(void){++groups;fixture();b0_fields();
    ram.known[0x4051]=1;ram.known[0xbf40]=7;ram.known[0xbf61]=127;ram.known[0xbfae]=1;
    ram.known[0xbf64]=1;ram.known[0xc248]=0;ram.known[0xc249]=0x40;ram.known[0x4115]=1;ram.known[0xbf65]=1;
    ram.known[0xbfa7]=3;ram.known[0xbfad]=7;ram.known[0xbfab]=7;ram.known[0xbfa9]=63;
    ram.known[0x4052]=1;ram.known[0xbee9]=1;ram.known[0xbefb]=3;ram.known[0xbef9]=7;ram.known[0xbef7]=7;
    ram.known[0xbf5f]=1;ram.known[0xbf5d]=15;ram.known[0xbf63]=3;ram.known[0xbee7]=31;ram.known[0xbee6]=15;
    CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(replies==1&&sent[0][32]==0xda);
    fixture();b0_fields();ram.known[0xbf5f]=0;
    CHECK(gd_dispatch(&deep,0x135d4,0)==GB_HALT);CHECK(deep.boundary_va==0xd31e&&deep.needed_mask==0x1ff);
}
static void branch_skips_unread_values(void){unsigned s;++groups;
    for(s=7;s<=8;s++){fixture();b0_fields();put(R(0x4164),s,1);ram.known[0xbfaa]=ram.known[0xbfac]=0;
        CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(sent[0][12]==0xa6&&sent[0][13]==0&&sent[0][14]==0&&sent[0][15]==0);}
    fixture();b0_fields();put(R(0xbed8),1,1);ram.known[0xbedb]=0;ram.known[0xbee0]=ram.known[0xbee8]=0;ram.known[0xbf58]=0;
    CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(sent[0][2]==0xfb);
}
static void eligibility_unknown_order(void){++groups;fixture();a0_fields();connect(0,65534,1,0);ram.known[0xc795]=0;
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(calls==5&&replies==0);
    fixture();a0_fields();ram.known[0xc795]=0;CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x131ee&&deep.stack[11]==0);
    fixture();b0_fields();connect(0,7,1,0);ram.known[0xc794]=0;CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(replies==0);
    fixture();b0_fields();ram.known[0xc794]=0;CHECK(gd_dispatch(&deep,0x135d4,0)==GB_HALT);CHECK(deep.boundary_va==0x1392c&&deep.stack[32]==0xda);
}
static void dependency_frontiers(void){++groups;fixture();io.invoke=NULL;gd_init(&deep,&ram,&io);
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x9db4&&deep.boundary_address==76&&calls==0&&deep.calls==1);
    fixture();b0_fields();noop_zero=1;CHECK(gd_dispatch(&deep,0x135d4,0)==GB_HALT);CHECK(deep.boundary_va==0x135fa&&deep.known[0]==0);
    fixture();b0_fields();stop_site=0x1373a;partial_copy=1;CHECK(gd_dispatch(&deep,0x135d4,0)==GB_HALT);
    CHECK(deep.stack[8]==0x11&&deep.stack[9]==0&&deep.stack[12]==0&&deep.boundary_va==0x1373a);
    fixture();a0_fields();io.reply=NULL;gd_init(&deep,&ram,&io);CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x133bc&&deep.replies==1&&replies==0&&deep.stack[32]==0xa0);
    fixture();CHECK(gd_dispatch(&deep,0x13162,0)==GB_HALT);CHECK(!deep.recognized&&deep.boundary_va==0x13162&&calls==0);
}
static void config_bit_and_gate_mask(void){++groups;fixture();a0_fields();put(R(0xc29c),8,1);ram.known[0xc29c]=8;
    ram.known[0x40c1]=ram.known[0x40c2]=ram.known[0x40c3]=0;
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(sent[0][23]==0&&sent_known[0][28]==8);
    fixture();a0_fields();ram.known[0xc29c]=247;
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_HALT);CHECK(deep.boundary_va==0x821a&&deep.stack[27]==0xfe);
}
static void first_unauth_slot_skips_deep_fields(void){unsigned i;++groups;fixture();a0_fields();connect(0,7,0,0);
    ram.known[0x4054]=ram.known[0x4116]=ram.known[0x416d]=0;
    CHECK(gd_dispatch(&deep,0x13160,0)==GB_RETURNED);CHECK(calls==7&&replies==1&&sent[0][3]==1);
    for(i=18;i<40;i++)CHECK(sent[0][i]==0);for(i=59;i<76;i++)CHECK(sent[0][i]==0);CHECK(sent[0][4]==1&&sent[0][40]==0x80);
}
static void b0_frame_built_once_with_live_gates(void){unsigned i;++groups;fixture();b0_fields();second_active=1;
    CHECK(gd_dispatch(&deep,0x135d4,0)==GB_RETURNED);CHECK(replies==2&&handles[1]==42&&calls==3);
    for(i=0;i<33;i++)CHECK(sent[1][i]==sent[0][i]);CHECK(ram.known[0x4050]==0);
}
static void timer_low19_minimal_output_dependency(void){uint32_t samples[]={0,1,15,16,1234,0x3ffff,0x40000,0x7ffff};size_t i;uint32_t top;++groups;
    for(i=0;i<sizeof(samples)/sizeof(samples[0]);i++){
        uint16_t base=(uint16_t)((samples[i]*UINT32_C(10)>>4)+50);
        for(top=0;top<8192;top++){uint32_t raw=samples[i]|(top<<19);uint16_t result=(uint16_t)((raw*UINT32_C(10)>>4)+50);CHECK(result==base);}
    }
    CHECK((((samples[6]*10>>4)+50)&65535)!=50);
}
static void source_byte_binding(void){static const struct{uint32_t va;uint8_t n,b[4];} items[]={
    {0x13178,4,{0xef,0x60,0x7f,0xc2}},{0x131fe,4,{0xa3,0x0b,0x61,1}},
    {0x133de,4,{0x23,0x13,1,2}},{0x133bc,4,{0xef,0x50,0xff,0x93}},
    {0x135dc,4,{0x63,0x91,7,0x38}},{0x136cc,4,{0x83,0xd7,7,0xb8}},
    {0x13868,4,{0xef,0x90,0x3f,0xab}},{0x13896,4,{0xef,0x90,0x1f,0xa1}},
    {0x13944,4,{0xef,0x50,0x6f,0xbb}},{0xffee,4,{0x63,0x7c,0xf7,0}}};
    size_t i;unsigned j;++groups;for(i=0;i<sizeof(items)/sizeof(items[0]);i++)for(j=0;j<items[i].n;j++)CHECK(image[items[i].va-0x8000+j]==items[i].b[j]);
}
int main(int argc,char **argv){FILE *f;if(argc!=2)return 2;f=fopen(argv[1],"rb");if(!f)return 3;if(fread(image,1,sizeof(image),f)!=sizeof(image)){fclose(f);return 4;}fclose(f);
    a0_golden();a0_unauthenticated_retains_fields();a0_preparation_before_gate();distinct_callee_stack_prefix();a0_config_fresh_pointer();b0_golden();b0_pause_and_construction_order();output_masks();unknown_copy_masks();reply_gate_rereads_second_slot();
    copy_remap_and_reply_handle();scalar_halt_prefix_order();mask_ignored_bits_and_required_bits();branch_skips_unread_values();eligibility_unknown_order();dependency_frontiers();config_bit_and_gate_mask();source_byte_binding();
    first_unauth_slot_skips_deep_fields();b0_frame_built_once_with_live_gates();timer_low19_minimal_output_dependency();
    printf("GENERAL_DEEP groups=%u checks=%u failures=%u synthetic=true target_executed=false\n",groups,checks,failures);return failures?1:0;}
