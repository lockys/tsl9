#include "adc_config.h"
#include "../../tsl9-resident-memory-leaves/src/io.h"
/* Only these three typed synthetic ports are part of this model. */
static int reserve(ml_io *io)
{
    if(io->flow!=ML_CONTINUE)return 0;
    if(io->effects>=io->diagnostic_budget){io->flow=ML_UNKNOWN;return 0;}
    io->effects+=1u;return 1;
}
int ml_port_read8(ml_io *io,uint32_t address,uint32_t *out)
{
    if(!reserve(io))return 0;
    if(!io->read8){io->flow=ML_UNKNOWN;return 0;}
    io->flow=io->read8(io->user,address,out);
    if(io->flow==ML_CONTINUE)*out&=255u;
    return io->flow==ML_CONTINUE;
}
int ml_port_read32(ml_io *io,uint32_t address,uint32_t *out)
{
    if(!reserve(io))return 0;
    if(!io->read32){io->flow=ML_UNKNOWN;return 0;}
    io->flow=io->read32(io->user,address,out);return io->flow==ML_CONTINUE;
}
int ml_port_write32(ml_io *io,uint32_t address,uint32_t value)
{
    if(!reserve(io))return 0;
    if(!io->write32){io->flow=ML_UNKNOWN;return 0;}
    io->flow=io->write32(io->user,address,value);return io->flow==ML_CONTINUE;
}
