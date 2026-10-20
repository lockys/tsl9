#include "tsl9_contract.h"
#include "general_reports.h"
#include <stdio.h>
#include <string.h>
#define XFER TC_TRANSFER
#define XFER_OUT TC_TRANSFERRED
#define GB_XFER GB_TRANSFER
static tc_model core;static tf_model memory;static gb_model general;static gr_model reports;
static unsigned groups,checks,failures,programs,reads,replies,calls;static tc_flow tc_result;static gb_flow gb_result;
#define CHECK(x) do{checks++;if(!(x)){failures++;printf("FAIL line=%d %s\n",__LINE__,#x);}}while(0)
static void group(const char*s){groups++;printf("GROUP %s\n",s);}
static tc_flow program(void*p,uint32_t a,const uint8_t*d,const uint8_t*k){(void)p;(void)a;(void)d;(void)k;programs++;return tc_result;}
static void read_bytes(void*p,uint32_t a,uint8_t*d,uint8_t*k,size_t n){(void)p;(void)a;reads++;memset(d,0,n);memset(k,255,n);}
static tc_flow wrapper(void*p,tc_model*m){(void)p;(void)m;replies++;return tc_result;}
static gb_flow invoke(void*p,gb_model*m,const gb_request*q,gb_scalar*out){(void)p;(void)m;(void)q;calls++;out->value=out->known=0;return gb_result;}
static gb_flow reply(void*p,gb_model*m,const gb_reply_request*q){(void)p;(void)m;(void)q;replies++;return gb_result;}
static gb_flow gr_invoke(void*p,gr_model*m,const gr_request*q,gb_scalar*out){(void)p;(void)m;(void)q;calls++;out->value=out->known=0;return gb_result;}
static gb_flow gr_reply(void*p,gr_model*m,const gb_reply_request*q){(void)p;(void)m;(void)q;replies++;return gb_result;}
static void put(unsigned off,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){memory.ram[off+i]=(uint8_t)(v>>(8*i));memory.known[off+i]=255;}}
static void fresh(void){tc_backend tc;gb_backend gb;gr_backend gr;memset(&tc,0,sizeof(tc));tc.program256=program;tc.read=read_bytes;tc.gatt_wrapper=wrapper;tc.uart_wrapper=wrapper;tc_init(&core,TC_RUNTIME,&tc);core.alloc_ok=core.link_ok=core.uart_ready=TC_YES;
 memset(&memory,0,sizeof(memory));memset(memory.known,255,sizeof(memory.known));put(0xc792,7,2);put(0xc794,1,1);put(0xc796,65534,2);put(0x40af,1,1);put(0xb9d8,1,1);
 memset(&gb,0,sizeof(gb));gb.invoke=invoke;gb.reply=reply;gb_init(&general,&memory,&gb);memset(&gr,0,sizeof(gr));gr.invoke=gr_invoke;gr.reply=gr_reply;gr_init(&reports,&memory,&gr);programs=reads=replies=calls=0;tc_result=TC_RETURNED;gb_result=GB_RETURNED;}
static void core_flash(void){uint8_t d[1026],k[1026];uint32_t command_count;group("Known page helper transfer stays distinct from unknown and blocks later commands");fresh();memset(d,0,sizeof(d));memset(k,255,sizeof(k));core.active=1;tc_result=XFER;tc_gatt_command(&core,'W',d,k,1026,0);CHECK(programs==1&&reads==0&&replies==0);CHECK(core.outcome==XFER_OUT&&core.interpretation_halted==0&&core.stalled==0);command_count=core.command_count;tc_gatt_command(&core,'S',d,k,0,0);CHECK(core.command_count==command_count&&core.outcome==XFER_OUT&&core.active==1);
 fresh();d[0]=d[1]=0;k[0]=k[1]=255;core.active=1;tc_result=TC_FLOW_UNKNOWN;tc_gatt_command(&core,'W',d,k,1026,0);CHECK(core.outcome==TC_INDETERMINATE&&programs==1&&replies==0);}
static void metadata_transfer(void){group("Metadata helper known transfer has distinct result and no later retry/read");fresh();tc_result=XFER;CHECK(tc_metadata_select(&core,2)==-3);CHECK(core.outcome==XFER_OUT&&programs==1&&reads==1);CHECK(tc_metadata_select(&core,1)==-3);CHECK(programs==1&&reads==1);tc_metadata_initialize(&core);CHECK(programs==1&&reads==1&&core.outcome==XFER_OUT);}
static void wrapper_transfer(void){uint8_t d=3,k=255;group("GATT and UART wrapper declared transfer stops native suffix without false unknown");fresh();tc_result=XFER;CHECK(tc_gatt_reply(&core,0xaa,&d,&k,1)==0);CHECK(replies==1&&core.outcome==XFER_OUT&&core.interpretation_halted==0);CHECK(tc_gatt_reply(&core,0xaa,&d,&k,1)==0);CHECK(replies==1);
 fresh();core.image=TC_BOOT;core.uart.command='I';tc_result=XFER;tc_uart_command(&core);CHECK(replies==1&&core.uart_session==0&&core.outcome==XFER_OUT&&core.interpretation_halted==0);}
static void parser_transfer(void){uint8_t wire[7]={0x55,0x7f,'G',0,0,'G',0x55};group("Known nonreturn preserves parser checksum-call state and ignores following bytes");fresh();core.image=TC_BOOT;tc_result=XFER;tc_receive(&core,TC_UART,wire,sizeof(wire),1);CHECK(core.command_count==1&&replies==1);CHECK(core.outcome==XFER_OUT&&core.uart.state==6);tc_receive(&core,TC_UART,wire,sizeof(wire),9000);CHECK(core.command_count==1&&replies==1&&core.uart.state==6&&core.uart.last_clock==1);}
static void general_invoke_transfer(void){group("GB native call flow preserves declared transfer and actual prefix");fresh();gb_result=GB_XFER;CHECK(gb_dispatch(&general,7,0xa1,0x2000b9d8,1)==GB_XFER);CHECK(calls==1&&replies==0&&general.last_request.target==0x17048);fresh();gb_result=GB_HALT;CHECK(gb_dispatch(&general,7,0xa1,0x2000b9d8,1)==GB_HALT);CHECK(calls==1&&general.boundary_va==0x17048);}
static void general_reply_transfer(void){group("GB reply transfer does not become HALT");fresh();gb_result=GB_XFER;CHECK(gb_dispatch(&general,7,0xa2,0x2000b9d8,1)==GB_XFER);CHECK(calls==1&&replies==0);fresh();put(0xb9d8,0,1);gb_result=GB_XFER;CHECK(gb_dispatch(&general,7,0xa2,0x2000b9d8,1)==GB_XFER);CHECK(replies==1&&calls==0);}
static void report_transfer(void){group("GR primitive and reply transfer preserve path outcome and stop next slot");fresh();gb_result=GB_XFER;CHECK(gr_command(&reports,7,0xd2,0x2000b9d8,1)==GB_XFER);CHECK(calls==1&&replies==0&&memory.ram[0xc795]==3);fresh();put(0xc795,4,1);gb_result=GB_XFER;CHECK(gr_d1(&reports,0x2000c600)==GB_XFER);CHECK(replies==1&&calls==0);}
int main(void){core_flash();metadata_transfer();wrapper_transfer();parser_transfer();general_invoke_transfer();general_reply_transfer();report_transfer();printf("FLOW_RESULT groups=%u checks=%u failures=%u original_executed=no hardware=no\n",groups,checks,failures);return failures?1:0;}
