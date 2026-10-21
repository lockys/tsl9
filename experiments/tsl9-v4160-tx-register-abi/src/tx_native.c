#include "tx_native.h"
#include "tx_io.h"

/* ID2966 8A56..8B6E. These are numeric device addresses, never host pointers. */
tx_return tsl9_ota_tx_8a56(TX_CONTEXT uint32_t context,uint32_t command,uint32_t source,uint32_t length)
{
    uint32_t limit,gp,handle,target,argument,result=context,lane,connection,invalid,accepted,ambient2=source,ambient3=length;
    uint32_t record,base,packet,n,low,high,cmd,checksum,index,payload,byte,out,tail_argument,task,magic;
    TX_ENTRY(context,command,source,length);
    limit=TX_LIMIT5();
    if(length>limit)TX_RETURN_LARGE(context);
    TX_FRAME();
    TX_GP(gp);TX_READ16(0x8a6au,gp+0x96u,handle,"a4");
    TX_SET_S2(context);TX_SET_S0(length);TX_SET_S1(source);TX_SET_S3(command);
    if(handle==context) {
        invalid=TX_INVALID5();
        if(handle!=invalid) {
            TX_GATE_SLOT(0x8a86u,target);
            TX_GP(gp);argument=TX_ARG1(gp+128u);
            TX_GATE(0x8a8eu,target,context,argument,ambient2,ambient3,result);
            accepted=TX_ACCEPT5();
            if(TX_EXPECT(result==accepted,0)) {lane=TX_LANE2(0u);goto selected;}
        }
    }
    TX_GP(gp);TX_READ16(0x8a96u,gp+0x9au,handle,"a5");
    TX_LIVE_S2(connection);
    if(handle!=connection) {TX_RESTORE_FAILURE();TX_RETURN_FAILURE(result);}
    invalid=TX_INVALID5();
    TX_LIVE_S2(connection);
    if(connection==invalid) {TX_RESTORE_FAILURE();TX_RETURN_FAILURE(result);}
    TX_GATE_SLOT(0x8aaau,target);
    TX_GP(gp);argument=TX_ARG1(gp+128u);TX_LIVE_S2(connection);connection=TX_ARG0(connection);
    TX_GATE(0x8ab4u,target,connection,argument,ambient2,ambient3,result);
    accepted=TX_ACCEPT5();
    lane=TX_LANE2(1u);
    if(TX_EXPECT(result!=accepted,1)) {TX_RESTORE_FAILURE();TX_RETURN_FAILURE(result);}
selected:
    record=TX_RECORD5(lane);
    base=TX_STORAGE3();
    magic=TX_MAGIC4();TX_LIVE_S0(n);low=TX_ARG1(n&255u);
    packet=TX_PACKET5(record,base);
    TX_WRITE16(0x8aecu,packet,magic);
    TX_WRITE8(0x8af0u,packet+4u,low);
    high=TX_HIGH4(n);
    TX_LIVE_S3(cmd);low=TX_ARG1(low+cmd);
    TX_WRITE8(0x8afau,packet+3u,high);
    checksum=TX_SUM4(high,low);
    TX_WRITE8(0x8b00u,packet+2u,cmd);
    checksum=TX_MASK4(checksum);
    index=TX_ARG1(0u);
    for(;;) {
        TX_LIVE_S0(n);
        if(TX_INDEX0(index)>=n)break;
        TX_BUDGET();
        TX_LIVE_S1(payload);payload=TX_ARG0(payload+index);
        TX_READ8(0x8b56u,payload,byte,"a0");
        out=TX_ARG6(packet+index);
        index=TX_ARG1(index+1u);
        checksum=TX_ARG4(checksum+byte);
        TX_WRITE8(0x8b62u,out+5u,byte);
        checksum=TX_MASK4(checksum);
    }
    record=TX_ARG5(packet+n);
    TX_WRITE8(0x8b16u,record+5u,checksum);
    record=TX_RECORD5(lane);
    n=TX_LENGTH_S0(n);
    lane=TX_LANE2(lane<<2);
    TX_RESTORE_HEAD();
    argument=TX_ARG1(1u);
    record=TX_ARG5(record+base);
    TX_WRITE16(0x8b32u,record+2u,n);
    TX_WRITE16(0x8b36u,record+4u,0u);
    TX_GP(gp);tail_argument=TX_LANE2(lane+gp+0x94u);
    TX_RESTORE_S0();
    TX_TAIL_SLOT(0x8b46u,target);
    TX_READ8(0x8b4au,tail_argument,task,"a0");
    TX_POP_FRAME();
    TX_TAIL(target,task,argument,tail_argument,base);
}
