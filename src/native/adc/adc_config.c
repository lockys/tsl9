#include "adc_config.h"
#include "io.h"

static ml_result stopped(ml_io *io)
{
    ml_result result={io->flow,0,0};return result;
}

ml_result tsl9_adc_config_io(ml_io *io,uint32_t base,uint32_t config)
{
    uint32_t old,bits,v;
    io->flow=ML_CONTINUE;io->effects=0;
    if(!ml_port_read32(io,base+4u,&old))return stopped(io);
    bits=old&UINT32_C(0xe0f0feff);
    if(!ml_port_read32(io,config+24u,&v))return stopped(io);
    bits|=v;
    if(!ml_port_read32(io,config,&v))return stopped(io);
    bits|=v;
    if(!ml_port_read32(io,config+28u,&v))return stopped(io);
    bits|=v;
    if(!ml_port_read32(io,config+4u,&v))return stopped(io);
    bits|=v<<8;
    if(!ml_port_write32(io,base+4u,bits))return stopped(io);

    if(!ml_port_read32(io,base+8u,&old))return stopped(io);
    bits=old&UINT32_C(0xfff1f7fd);
    if(!ml_port_read32(io,config+12u,&v))return stopped(io);
    bits|=v;
    if(!ml_port_read32(io,config+16u,&v))return stopped(io);
    bits|=v;
    if(!ml_port_read32(io,config+8u,&v))return stopped(io);
    bits|=v<<1;
    if(!ml_port_write32(io,base+8u,bits))return stopped(io);

    if(!ml_port_read32(io,base+44u,&old))return stopped(io);
    bits=old&UINT32_C(0xff0fffff);
    if(!ml_port_read8(io,config+20u,&v))return stopped(io);
    bits|=((v-1u)&255u)<<20;
    if(!ml_port_write32(io,base+44u,bits))return stopped(io);
    {
        ml_result result={ML_CONTINUE,base,1};return result;
    }
}
