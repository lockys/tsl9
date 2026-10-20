#include "boot_ram.h"
#include <string.h>
void br_init(br_model *m,tf_model *p,const br_backend *b){memset(m,0,sizeof(*m));m->memory=p;if(b)m->backend=*b;}
static int stop(br_model *m,uint32_t va,uint32_t a){m->flow=BR_HALT;m->boundary_va=va;m->boundary_address=a;return 0;}
static void put(br_model *m,uint32_t a,uint32_t v,unsigned n){unsigned i;for(i=0;i<n;i++){m->memory->ram[a-TF_RAM_BASE+i]=(uint8_t)(v>>(i*8));m->memory->known[a-TF_RAM_BASE+i]=255;}}
static int get(br_model *m,uint32_t a,unsigned n,uint32_t va,uint32_t *v){unsigned i;*v=0;for(i=0;i<n;i++){if(m->memory->known[a-TF_RAM_BASE+i]!=255)return stop(m,va,a+i);*v|=(uint32_t)m->memory->ram[a-TF_RAM_BASE+i]<<(i*8);}return 1;}
static int rom(br_model *m,unsigned off,unsigned slot,uint32_t ticks){uint32_t task;int r;m->last_ticks=ticks;m->last_rom_offset=off;++m->requests;if(!get(m,0x2000408a,1,0x1afa,&task))return TF_UNKNOWN;r=m->backend.rom_status?m->backend.rom_status(m->backend.context,off,(uint8_t)task,(uint16_t)(1u<<slot),ticks):TF_UNKNOWN;if(r==TF_UNKNOWN)stop(m,0x1afa,0x40000u+off);return r;}
static int released(br_model*m,br_flow f,uint32_t va,uint32_t a){if(f==BR_RETURNED)return 1;if(f==BR_TRANSFER){m->flow=f;return 0;}return stop(m,va,a);}
static int release(br_model *m,uint32_t argument){if(argument){++m->free_calls;if(!released(m,m->backend.free_argument?m->backend.free_argument(m->backend.context,argument):BR_HALT,0x1b8a,argument))return 0;}return 1;}
br_flow br_cold_start(br_model *m,const uint8_t *b,size_t n){if(m->flow==BR_TRANSFER)return m->flow;
    m->flow=BR_RETURNED;
    if(!b || n<0x2ef8){stop(m,0x2be8,0x3e90);return m->flow;}
    memcpy(m->memory->ram+0x4000,b+0x2e90,104);memset(m->memory->known+0x4000,255,104);
    memset(m->memory->ram+0x4068,0,0x99a0-0x4068);memset(m->memory->known+0x4068,255,0x99a0-0x4068);
    return m->flow;
}
int br_schedule(br_model *m,uint32_t cb,uint32_t mode,uint32_t delay,uint32_t argument){if(m->flow==BR_TRANSFER)return TF_UNKNOWN;
    unsigned i,chosen=15;int matched=0;uint32_t old,a,ticks;int result;m->flow=BR_RETURNED;
    if(delay==0)for(i=0;i<15;i++){
        a=BR_REGISTRY+12u*i;if(!get(m,a+4,4,0x1b18,&old))return TF_UNKNOWN;
        if(old==0){put(m,a+4,cb,4);put(m,a,0,1);put(m,a+8,argument,4);return rom(m,80,i,0);}
    }
    for(i=0;i<15;i++){a=BR_REGISTRY+12u*i;if(!get(m,a+4,4,0x1b72,&old))return TF_UNKNOWN;if(old==cb){chosen=i;matched=1;break;}}
    if(chosen==15)for(i=0;i<15;i++){a=BR_REGISTRY+12u*i;if(!get(m,a+4,4,0x1be0,&old))return TF_UNKNOWN;if(old==0){chosen=i;put(m,a+4,cb,4);break;}}
    if(chosen==15)return 1;
    a=BR_REGISTRY+12u*chosen;
    if(matched){if(!get(m,a+8,4,0x1b80,&old)||!release(m,old))return TF_UNKNOWN;}
    put(m,a,mode,1);put(m,a+8,argument,4);ticks=(delay*UINT32_C(1000))/625u;
    result=rom(m,mode?556u:88u,chosen,ticks);
    return result==TF_UNKNOWN?TF_UNKNOWN:(mode?result:result==0);
}
int br_stop_startup(br_model *m){if(m->flow==BR_TRANSFER)return TF_UNKNOWN;
    uint32_t task;int result;m->flow=BR_RETURNED;
    if(!get(m,0x2000408d,1,0x2518,&task))return TF_UNKNOWN;
    ++m->requests;m->last_rom_offset=92;m->last_ticks=0;
    result=m->backend.rom_status?m->backend.rom_status(m->backend.context,92,(uint8_t)task,2,0):TF_UNKNOWN;
    if(result==TF_UNKNOWN)stop(m,0x251c,0x4005c);
    return result;
}
uint16_t br_dispatch(br_model *m,uint16_t events){if(m->flow==BR_TRANSFER)return events;
    unsigned i;uint32_t a,cb,arg,mode;m->flow=BR_RETURNED;
    for(i=0;i<15;i++)if(events&(1u<<i)){
        a=BR_REGISTRY+12u*i;if(!get(m,a+4,4,0x1a8a,&cb))return events;
        if(cb){if(!get(m,a,1,0x1a8e,&mode)||!get(m,a+8,4,0x1a92,&arg))return events;
            if(mode==0){put(m,a+4,0,4);put(m,a+8,0,4);}
            ++m->callback_calls;
            if(!released(m,m->backend.callback?m->backend.callback(m->backend.context,m,cb,arg):BR_HALT,cb,arg))return events;
        }
        return (uint16_t)(events^(1u<<i));
    }
    return 0;
}
size_t br_uart_receive(br_model *m,const uint8_t *bytes,size_t n,uint32_t now){if(m->flow==BR_TRANSFER)return 0;
    size_t i;uint32_t previous,state,sum,length,count,command;uint8_t byte;
    m->flow=BR_RETURNED;
    for(i=0;i<n;i++){
        /* Native UART ISR checks clock only after the peripheral reports a byte. */
        if(!get(m,0x20004090,4,0x2642,&previous))return i;
        if((uint32_t)(now-previous)>2999){
            memset(m->memory->ram+0x9594,0,1036);memset(m->memory->known+0x9594,255,1036);
        }
        put(m,0x20004090,now,4);
        if(!get(m,BR_UART+1033,1,0x2670,&state))return i;
        byte=bytes[i];
        switch(state){
        case 0:put(m,BR_UART+1033,byte==0x55?1u:0u,1);break;
        case 1:
            if(byte==0x7f){put(m,BR_UART+1033,2,1);put(m,BR_UART+1031,0,1);}
            else put(m,BR_UART+1033,0,1);
            break;
        case 2:
            put(m,BR_UART+1033,3,1);put(m,BR_UART+1030,byte,1);
            if(!get(m,BR_UART+1031,1,0x26d0,&sum))return i+1;
            put(m,BR_UART+1031,sum+byte,1);break;
        case 3:
            put(m,BR_UART+1033,4,1);put(m,BR_UART+1026,(uint32_t)byte*256,2);
            if(!get(m,BR_UART+1031,1,0x26d0,&sum))return i+1;
            put(m,BR_UART+1031,sum+byte,1);break;
        case 4:
            put(m,BR_UART+1028,0,2);
            if(!get(m,BR_UART+1026,2,0x270a,&length))return i;
            length|=byte;put(m,BR_UART+1026,length,2);put(m,BR_UART+1033,length>1026?0u:(length==0?6u:5u),1);
            if(!get(m,BR_UART+1031,1,0x273e,&sum))return i+1;
            put(m,BR_UART+1031,sum+byte,1);break;
        case 5:
            if(!get(m,BR_UART+1028,2,0x274e,&count))return i;
            if(count>1025){put(m,BR_UART+1033,0,1);break;}
            put(m,BR_UART+count,byte,1);put(m,BR_UART+1028,count+1,2);
            if(!get(m,BR_UART+1026,2,0x2774,&length))return i+1;
            if(count+1>=length)put(m,BR_UART+1033,6,1);
            if(!get(m,BR_UART+1031,1,0x273e,&sum))return i+1;
            put(m,BR_UART+1031,sum+byte,1);break;
        case 6:
            if(!get(m,BR_UART+1031,1,0x2788,&sum))return i;
            if(sum==byte){
                if(!get(m,BR_UART+1030,1,0x2790,&command)||!get(m,BR_UART+1026,2,0x270a,&length))return i;
                if(command=='I'||command=='S'||command=='W'||command=='E'||command=='G'||command=='R'){
                    ++m->uart_commands;
                    if(!released(m,m->backend.uart_command?m->backend.uart_command(m->backend.context,m,(uint8_t)command,BR_UART,(uint16_t)length):BR_HALT,0x27b2,BR_UART))return i;
                }
            }
            put(m,BR_UART+1033,0,1);break;
        default:put(m,BR_UART+1033,0,1);break;
        }
    }
    return n;
}
