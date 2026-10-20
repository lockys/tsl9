#include "general_reports.h"
#include <stdio.h>
#include <string.h>
#define A(x) (TF_RAM_BASE+UINT32_C(x))
#define CACHE A(0xc1b4)
static tf_model ram;static gr_model model;static gr_backend backend;static uint8_t image[76800];
static unsigned groups,checks,failures,calls,replies;static uint8_t sent[2][29],sent_known[2][29];static uint16_t handles[2];static uint32_t sources[2];static size_t lengths[2];
static uint32_t stop_site;static int partial,mutate_cache,mutate_record,noop_zero;
#define CHECK(x) do{++checks;if(!(x)){++failures;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void put(uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){ram.ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(8*i));ram.known[a-TF_RAM_BASE+i]=255;}}
static uint32_t read(uint32_t a,unsigned n){unsigned i;uint32_t v=0;for(i=0;i<n;i++)v|=(uint32_t)ram.ram[a-TF_RAM_BASE+i]<<(8*i);return v;}
static void connect(unsigned slot,uint16_t h,uint8_t auth,uint8_t mode){uint32_t a=A(0xc792)+4*slot;put(a,h,2);put(a+2,auth,1);put(a+3,mode,1);}
static gb_flow invoke(void*p,gr_model*m,const gr_request*r,gb_scalar*out){
    size_t i,n=r->buffer_length;(void)p;CHECK(m->memory==&ram);++calls;out->value=0x12345678;out->known=0;
    CHECK(r->known[2]==UINT32_MAX&&r->arguments[2]==n&&r->buffer&&r->buffer_known);
    if(r->callsite==stop_site&&!partial)return GB_HALT;if(r->callsite==stop_site&&partial)n=1;
    if(r->target!=72&&r->target!=76)return GB_HALT;if(r->target==72&&noop_zero)return GB_RETURNED;
    for(i=0;i<n;i++){
        if(r->target==72){r->buffer[i]=(uint8_t)r->arguments[1];r->buffer_known[i]=255;}
        else if(!r->known[1]){CHECK(r->input&&r->input_known);r->buffer[i]=r->input[i];r->buffer_known[i]=r->input_known[i];}
        else {uint32_t a=r->arguments[1]+(uint32_t)i;if(a<TF_RAM_BASE||a>=TF_RAM_BASE+TF_RAM_SIZE)return GB_HALT;r->buffer[i]=ram.ram[a-TF_RAM_BASE];r->buffer_known[i]=ram.known[a-TF_RAM_BASE];}
    }
    if(mutate_cache&&r->target==76&&r->arguments[1]==CACHE+12)put(CACHE+12*11+3,0xee,1);
    return r->callsite==stop_site?GB_HALT:GB_RETURNED;
}
static gb_flow reply(void*p,gr_model*m,const gb_reply_request*r){
    (void)p;CHECK(m->memory==&ram&&r->wrapper_va==0x8cfa&&replies<2);
    if(replies<2){memcpy(sent[replies],r->data,r->length);memcpy(sent_known[replies],r->known,r->length);handles[replies]=r->handle;sources[replies]=r->source_address;lengths[replies]=r->length;}
    ++replies;if(mutate_record&&replies==1){put(A(0xd003),0x99,1);connect(1,9,1,4);}
    return stop_site==0x8cfa?GB_HALT:GB_RETURNED;
}
static void fixture(void){
    unsigned i;memset(&ram,0,sizeof(ram));memset(ram.known,255,sizeof(ram.known));memset(&backend,0,sizeof(backend));memset(sent,0,sizeof(sent));memset(sent_known,0,sizeof(sent_known));
    connect(0,7,1,0);connect(1,65534,0,0);put(A(0xb9d8),1,1);
    for(i=0;i<4;i++)put(CACHE+12+3+i,0x11*(i+1),1);
    for(i=0;i<8;i++)put(CACHE+12*11+3+i,0x51+i,1);
    put(CACHE+12*5+3,0x8c,1);put(CACHE+12*5+4,0x2a,1);put(CACHE+12*5+5,0xbc,1);put(CACHE+12*5+6,0x0d,1);
    for(i=0;i<4;i++)put(CACHE+12*6+5+i,0x61+i,1);
    put(CACHE+12*7+5,0x71,1);put(CACHE+12*7+6,0x72,1);put(CACHE+12*3+8,0x156,2);
    put(CACHE+12*4+2,0xaa,1);for(i=0;i<6;i++)put(CACHE+12*4+3+i,0x31+i,1);put(CACHE+12*4+9,0xcc,1);
    put(A(0xbf62),0x2ab,2);put(A(0xbf5e),0x16b,2);put(A(0xbf60),1,1);put(A(0xbf61),0x65,1);put(A(0xbfa4),0x234567,4);
    for(i=0;i<8;i++)put(A(0xd003)+i,0x81+i,1);put(A(0xd002),0,1);
    calls=replies=0;stop_site=0;partial=mutate_cache=mutate_record=noop_zero=0;backend.invoke=invoke;backend.reply=reply;gr_init(&model,&ram,&backend);
}
static void d0_golden(void){
    static const uint8_t expected[29]={0x11,0x22,0x33,0x44,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x63,0x64,0x61,0x62,0x71,0x72,0xa3,0xca,0xdb,0x56,0xad,0xea,0xda,0xf2,0x59,0xd1,8};
    unsigned i;++groups;fixture();CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_RETURNED);CHECK(calls==7&&replies==1&&lengths[0]==29&&sources[0]==0&&read(A(0xc795),1)==3);
    for(i=0;i<29;i++){CHECK(sent[0][i]==expected[i]);CHECK(sent_known[0][i]==255);}
}
static void d2_correct_record_offset(void){
    unsigned i;++groups;fixture();CHECK(gr_command(&model,7,0xd2,A(0xb9d8),1)==GB_RETURNED);CHECK(calls==2&&replies==1&&lengths[0]==8);
    for(i=0;i<6;i++)CHECK(sent[0][i]==0x31+i);CHECK(sent[0][6]==0&&sent[0][7]==0);CHECK(read(A(0xc795),1)==3);
}
static void command_gates_and_no_length_gate(void){
    ++groups;fixture();put(A(0xb9d8),2,1);CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_RETURNED);CHECK(calls==0&&replies==0&&read(A(0xc795),1)==0);
    fixture();put(A(0xc790),1,1);CHECK(gr_command(&model,7,0xd2,A(0xb9d8),1)==GB_RETURNED);CHECK(read(A(0xc795),1)==3&&calls==0&&replies==0);
    fixture();ram.known[0xc790]=0;CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_HALT);CHECK(read(A(0xc795),1)==3&&calls==0&&model.boundary_va==0x1426a);
    fixture();CHECK(gr_command(&model,7,0xd1,A(0xb9d8),0)==GB_RETURNED);CHECK(read(A(0xc795),1)==4&&calls==0&&replies==0);
    fixture();CHECK(gr_command(&model,7,0xd2,A(0xb9d8),0)==GB_RETURNED);CHECK(replies==1);
}
static void mode_raw_handle_and_slot_priority(void){
    ++groups;fixture();CHECK(gr_mode(&model,7,0x103)==GB_RETURNED);CHECK(read(A(0xc795),1)==3);
    CHECK(gr_mode(&model,0x10007,4)==GB_RETURNED);CHECK(read(A(0xc795),1)==3);
    connect(1,7,1,1);CHECK(gr_mode(&model,7,4)==GB_RETURNED);CHECK(read(A(0xc795),1)==4&&read(A(0xc799),1)==1);
    ram.known[0xc796]=0;CHECK(gr_mode(&model,7,5)==GB_RETURNED);CHECK(read(A(0xc795),1)==5);
    CHECK(gr_mode(&model,8,5)==GB_HALT);CHECK(model.boundary_va==0x139ce);
}
static void d1_live_source_and_gates(void){
    ++groups;fixture();connect(0,7,1,4);mutate_record=1;CHECK(gr_d1(&model,A(0xd000))==GB_RETURNED);CHECK(replies==2&&calls==0&&handles[1]==9&&sources[0]==A(0xd003)&&sources[1]==A(0xd003));
    CHECK(sent[0][0]==0x81&&sent[1][0]==0x99&&lengths[1]==8);
    fixture();connect(0,7,1,4);put(A(0xc790),1,1);CHECK(gr_d1(&model,A(0xfffffffe))==GB_RETURNED);CHECK(replies==0&&calls==0);
    fixture();connect(0,7,0,4);ram.known[0xd003]=0;CHECK(gr_d1(&model,A(0xd000))==GB_RETURNED);CHECK(replies==0);
    fixture();connect(0,7,1,4);ram.known[0xc795]=0;CHECK(gr_d1(&model,A(0xd000))==GB_HALT);CHECK(model.boundary_va==0x13a24&&replies==0);
}
static void cache_masked_fields_and_output_unknown(void){
    ++groups;fixture();ram.known[0xc1b4+12*5]=0;ram.known[0xc1b4+12*5+3]=0xfc;ram.known[0xc1b4+12*5+4]=0x3f;ram.known[0xc1b4+12*5+6]=15;ram.known[0xc1b4+12*5+7]=0;
    ram.known[0xc1b4+12*3+9]=3;ram.known[0xbf63]=3;ram.known[0xbf5f]=1;ram.known[0xbf61]=127;ram.known[0xbfa7]=3;
    CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_RETURNED);CHECK(sent_known[0][18]==255&&sent_known[0][19]==255&&sent_known[0][28]==255);
    fixture();ram.known[0xc1b4+12+3]=127;ram.known[0xc1b4+12*5+4]=0xdf;
    CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_RETURNED);CHECK(sent_known[0][0]==127&&sent_known[0][19]==247&&sent_known[0][18]==255);
}
static void copies_are_not_atomic_or_noop(void){
    ++groups;fixture();mutate_cache=1;CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_RETURNED);CHECK(sent[0][0]==0x11&&sent[0][4]==0xee);
    fixture();backend.invoke=NULL;gr_init(&model,&ram,&backend);CHECK(gr_command(&model,7,0xd2,A(0xb9d8),1)==GB_HALT);CHECK(model.boundary_va==0x14286&&read(A(0xc795),1)==3&&model.known[0]==0);
    fixture();stop_site=0x82c0;partial=1;CHECK(gr_command(&model,7,0xd2,A(0xb9d8),1)==GB_HALT);CHECK(model.stack[12]==0&&model.known[12]==255&&model.known[13]==0&&model.stack[0]==0&&replies==0);
    fixture();stop_site=0x8cfa;CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_HALT);CHECK(model.frame_length==29&&replies==1);
}
static void cache_two_directions_and_wrap(void){
    uint8_t bytes[12],knowns[12];gr_view v;unsigned i;++groups;fixture();for(i=0;i<12;i++){bytes[i]=(uint8_t)(0xa0+i);knowns[i]=255;}knowns[3]=127;
    memset(&v,0,sizeof(v));v.data=bytes;v.known=knowns;v.available=12;
    CHECK(gr_cache_transfer(&model,0,2,&v)==GB_RETURNED);CHECK(read(CACHE+24+3,1)==0xa3&&ram.known[0xc1b4+24+3]==127);
    memset(bytes,0,12);memset(knowns,0,12);CHECK(gr_cache_transfer(&model,7,2,&v)==GB_RETURNED);CHECK(bytes[3]==0xa3&&knowns[3]==127);
    put(CACHE-12,0x1234,2);CHECK(gr_cache_transfer(&model,1,UINT32_MAX,&v)==GB_RETURNED);CHECK(bytes[0]==0x34&&bytes[1]==0x12);
}
static void scalar_known_different_from_return_flow(void){
    gb_scalar result;++groups;fixture();ram.known[0xbf63]=3;CHECK(gr_getter(&model,0xd392,&result)==GB_RETURNED);CHECK(result.value==0x2ab&&(result.known&1023)==1023&&result.known!=UINT32_MAX);
    ram.known[0xbf60]=1;ram.known[0xbf58]=0;CHECK(gr_getter(&model,0xd17c,&result)==GB_RETURNED);CHECK(result.value==2&&result.known==UINT32_MAX);
    put(A(0xbf60),0,1);put(A(0xbf58),0x100,2);CHECK(gr_getter(&model,0xd17c,&result)==GB_RETURNED);CHECK(result.value==1&&result.known==UINT32_MAX);
    ram.known[0xbf60]=0;ram.known[0xbf58]=0;CHECK(gr_getter(&model,0xd17c,&result)==GB_RETURNED);CHECK(result.known==UINT32_C(0xfffffffc));
    CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_RETURNED);CHECK(sent_known[0][23]==0xcf&&sent_known[0][28]==255&&replies==1);
}
static void copied_unknown_and_absent_dlc_check(void){
    ++groups;fixture();ram.known[0xc1b4+12*4+2]=0;CHECK(gr_command(&model,7,0xd2,A(0xb9d8),1)==GB_RETURNED);CHECK(sent_known[0][0]==255&&sent[0][0]==0x31);
    fixture();connect(0,7,1,4);ram.known[0xd003]=127;CHECK(gr_d1(&model,A(0xd000))==GB_RETURNED);CHECK(sent_known[0][0]==127&&sent[0][0]==0x81);
    fixture();noop_zero=1;CHECK(gr_command(&model,7,0xd0,A(0xb9d8),1)==GB_HALT);CHECK(model.boundary_va==0x1430e&&model.frame_length==29&&model.known[12]==0);
}
static void mapped_cache_transfer_and_missing_reply(void){
    gr_view view;unsigned i;++groups;fixture();memset(&view,0,sizeof(view));view.address=A(0xd020);view.available=12;
    CHECK(gr_cache_transfer(&model,1,1,&view)==GB_RETURNED);CHECK(read(A(0xd023),1)==0x11&&model.last_request.known[0]==UINT32_MAX);
    for(i=0;i<12;i++)put(A(0xd020)+i,0x90+i,1);
    CHECK(gr_cache_transfer(&model,0,4,&view)==GB_RETURNED);CHECK(read(CACHE+48+3,1)==0x93&&model.last_request.known[1]==UINT32_MAX);
    fixture();backend.reply=NULL;gr_init(&model,&ram,&backend);CHECK(gr_command(&model,7,0xd2,A(0xb9d8),1)==GB_HALT);CHECK(model.boundary_va==0x142cc&&model.replies==1&&replies==0);
}
static void proved_partial_control_and_actual_sink(void){
    ++groups;fixture();ram.known[0xc792]=ram.known[0xc793]=ram.known[0xc796]=ram.known[0xc797]=0;
    CHECK(gr_mode(&model,0x10007,4)==GB_RETURNED);CHECK(read(A(0xc795),1)==0&&read(A(0xc799),1)==0);
    fixture();connect(0,7,1,0);connect(1,8,1,1);ram.known[0xc792]=254;
    CHECK(gr_mode(&model,8,0x103)==GB_RETURNED);CHECK(read(A(0xc795),1)==0&&read(A(0xc799),1)==3);
    fixture();connect(0,7,1,0);connect(1,7,1,1);ram.known[0xc792]=254;
    CHECK(gr_mode(&model,7,4)==GB_HALT);CHECK(read(A(0xc795),1)==0&&read(A(0xc799),1)==1);
    fixture();put(A(0xb9d8),2,1);ram.known[0xb9d8]=254;
    CHECK(gr_command(&model,7,0xd0,A(0xb9d8),0)==GB_RETURNED);CHECK(calls==0&&replies==0&&read(A(0xc795),1)==0);
    fixture();put(A(0xc790),128,1);ram.known[0xc790]=128;
    CHECK(gr_command(&model,7,0xd2,A(0xb9d8),1)==GB_RETURNED);CHECK(calls==0&&replies==0&&read(A(0xc795),1)==3);
    CHECK(gr_d1(&model,UINT32_C(0xfffffffe))==GB_RETURNED);CHECK(calls==0&&replies==0);
    fixture();connect(0,7,1,3);ram.known[0xc795]=254;connect(1,9,1,4);
    CHECK(gr_d1(&model,A(0xd000))==GB_RETURNED);CHECK(replies==1&&handles[0]==9);
    fixture();connect(0,7,2,4);ram.known[0xc794]=2;
    CHECK(gr_d1(&model,A(0xd000))==GB_RETURNED);CHECK(replies==1&&handles[0]==7);
    fixture();connect(0,7,1,0);ram.known[0xc792]=254;
    CHECK(gr_d1(&model,A(0xd000))==GB_RETURNED);CHECK(calls==0&&replies==0);
    fixture();connect(0,7,1,4);ram.known[0xc792]=254;
    CHECK(gr_d1(&model,A(0xd000))==GB_HALT);CHECK(calls==0&&replies==0&&model.boundary_va==0x13a36);
    fixture();put(A(0xb9d8),1,1);ram.known[0xb9d8]=254;
    CHECK(gr_command(&model,7,0xd1,A(0xb9d8),1)==GB_HALT);CHECK(read(A(0xc795),1)==0);
}
static void source_bindings(void){
    static const struct{uint32_t va;uint8_t b[4];} points[]={
        {0x14292,{0x83,0x47,0x41,2}},{0x14296,{3,0x47,0x31,2}},
        {0x14440,{0xef,0x80,0x3f,0xf5}},{0x139ea,{0x83,0xc7,0xa7,0xda}},
        {0x15048,{0x6f,0xe0,0xff,0x99}}};
    size_t i;unsigned j;++groups;for(i=0;i<sizeof(points)/sizeof(points[0]);i++)for(j=0;j<4;j++)CHECK(image[points[i].va-0x8000+j]==points[i].b[j]);
}
int main(int argc,char**argv){FILE*f;if(argc!=2)return 2;f=fopen(argv[1],"rb");if(!f)return 3;if(fread(image,1,sizeof(image),f)!=sizeof(image)){fclose(f);return 4;}fclose(f);
    d0_golden();d2_correct_record_offset();command_gates_and_no_length_gate();mode_raw_handle_and_slot_priority();d1_live_source_and_gates();cache_masked_fields_and_output_unknown();copies_are_not_atomic_or_noop();cache_two_directions_and_wrap();scalar_known_different_from_return_flow();
    copied_unknown_and_absent_dlc_check();mapped_cache_transfer_and_missing_reply();proved_partial_control_and_actual_sink();source_bindings();
    printf("GENERAL_REPORTS groups=%u checks=%u failures=%u synthetic=true target_executed=false\n",groups,checks,failures);return failures?1:0;}
