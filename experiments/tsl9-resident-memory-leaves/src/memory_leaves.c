#include "memory_leaves.h"
#include "io.h"
#define ML_GUARD UINT32_C(0x4002420c)

static ml_result stopped(ml_io *io)
{
    ml_result result={io->flow,0,0};return result;
}
static ml_result completed(uint32_t value)
{
    ml_result result={ML_CONTINUE,value,1};return result;
}
static int begin(ml_io *io,uint32_t *saved)
{
    io->flow=ML_CONTINUE;io->effects=0;
    if(!ml_port_read32(io,ML_GUARD,saved))return 0;
    if(!ml_port_write32(io,ML_GUARD,0))return 0;
    return ml_port_fence_i(io);
}

ml_result tsl9_candidate_compare_200004bc(ml_io *io,uint32_t address,uint32_t expected,uint32_t count)
{
    uint32_t saved,byte,end,answer=0;
    if(!begin(io,&saved))return stopped(io);
    if(address && count){
        end=address+count;
        do{
            uint32_t current=address;address+=1u;
            if(!ml_port_read8(io,current,&byte))return stopped(io);
            if((byte&255u)!=expected)goto restore;
        }while(address!=end);
        answer=1;
    }
restore:
    if(!ml_port_write32(io,ML_GUARD,saved))return stopped(io);
    return completed(answer);
}

ml_result tsl9_candidate_fill_2000039c(ml_io *io,uint32_t destination,uint32_t value,uint32_t count)
{
    uint32_t saved,end;
    if(!begin(io,&saved))return stopped(io);
    if(destination && count){
        end=destination+count;
        do{
            uint32_t current=destination;destination+=1u;
            if(!ml_port_write8(io,current,value&255u))return stopped(io);
        }while(destination!=end);
    }
    if(!ml_port_write32(io,ML_GUARD,saved))return stopped(io);
    return completed(destination);
}

ml_result tsl9_candidate_copy_20000332(ml_io *io,uint32_t destination,uint32_t source,uint32_t count)
{
    uint32_t saved,byte,offset=0;
    if(!begin(io,&saved))return stopped(io);
    if(destination && source && count){
        do{
            uint32_t current=destination+offset;
            if(!ml_port_read8(io,source+offset,&byte))return stopped(io);
            offset+=1u;
            if(!ml_port_write8(io,current,byte&255u))return stopped(io);
        }while(offset!=count);
    }
    if(!ml_port_write32(io,ML_GUARD,saved))return stopped(io);
    return completed(destination);
}
