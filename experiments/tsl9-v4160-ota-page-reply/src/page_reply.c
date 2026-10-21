#include "page_reply.h"
#include "reply_io.h"

/* ID2966 9B8E..9C0A. Numeric addresses are not host pointers or wire I/O. */
op_return tsl9_ota_page_reply_9b8e(OP_CONTEXT uint32_t connection,uint32_t command,uint32_t index)
{
    uint32_t base,target,buffer,live_index,high,source,ctx,cmd,tail_a1,tail_a2,allocation_size,copy_size,tx_size;
    OP_ENTRY(connection,command,index);
    OP_FRAME_HEAD();
    OP_SET_S2(0x40000u);
    OP_LIVE_S2(base);
    OP_SLOT(0x9b96u,base+0x70u,target);
    OP_FRAME_REST();
    OP_SET_S3(connection);allocation_size=OP_ALLOC_SIZE0();OP_SET_S4(command);OP_SET_S1(index);
    OP_ALLOC(target,allocation_size,command,index,buffer);
    if(buffer==0u) {
        OP_RESTORE_NULL();
        OP_RETURN_NULL(buffer);
    }
    OP_LIVE_S1(live_index);
    high=OP_HEADER_HIGH5(live_index);
    OP_WRITE8(0x9bb6u,buffer+1u,live_index);
    OP_WRITE8(0x9bbau,buffer,high);
    source=OP_SOURCE_HIGH1();
    OP_LIVE_S2(base);
    OP_SLOT(0x9bc2u,base+0x4cu,target);
    source=OP_SOURCE_LOW1(source);
    OP_LIVE_S1(live_index);
    source=OP_SOURCE_ADD1(source,live_index);
    OP_SET_S0(buffer);
    copy_size=OP_COPY_SIZE2();
    source=OP_SOURCE_SHIFT1(source);
    buffer=OP_BUFFER_ADVANCE0(buffer);
    OP_COPY(target,buffer,source,copy_size);
    OP_LIVE_S3(ctx);ctx=OP_ARG0(ctx);
    OP_LIVE_S0(buffer);buffer=OP_ARG2(buffer);
    OP_LIVE_S4(cmd);cmd=OP_ARG1(cmd);
    tx_size=OP_TX_SIZE3();
    OP_TX(ctx,cmd,buffer,tx_size,tail_a1,tail_a2);
    OP_LIVE_S0(buffer);buffer=OP_ARG0(buffer);
    OP_RESTORE_S0();
    OP_LIVE_S2(base);
    OP_FREE_SLOT(0x9be8u,base+0x68u,target);
    OP_RESTORE_TAIL();
    OP_TAIL_RELEASE(target,buffer,tail_a1,tail_a2);
}
