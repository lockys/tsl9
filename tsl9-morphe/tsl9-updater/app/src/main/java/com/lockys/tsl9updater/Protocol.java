package com.lockys.tsl9updater;

import java.util.*;

/** Byte format from original BDB12361... BLE module; no Android dependencies. */
public final class Protocol {
    private Protocol() {}
    public static final class Packet {
        public final int command; public final byte[] payload;
        public Packet(int c,byte[] b){command=c;payload=b.clone();}
    }
    public static byte[] encode(int command,byte[] payload) {
        if(command<0||command>255||payload.length>4096)throw new IllegalArgumentException("invalid frame");
        byte[] frame=new byte[payload.length+6];frame[0]=0x55;frame[1]=0x7f;
        frame[2]=(byte)command;frame[3]=(byte)(payload.length>>>8);frame[4]=(byte)payload.length;
        System.arraycopy(payload,0,frame,5,payload.length);int sum=0;
        for(int j=2;j<frame.length-1;j++)sum+=frame[j]&255;
        frame[frame.length-1]=(byte)sum;return frame;
    }
    public static final class Decoder {
        private int state,command,length,index,sum;private long last=-1000;private byte[] data;
        public void reset(){state=0;index=0;length=0;data=null;sum=0;}
        public List<Packet> push(byte[] chunk,long now){
            if(now-last>=500)reset();last=now;List<Packet> out=new ArrayList<>();
            for(byte value:chunk){int b=value&255;switch(state){
                case 0:if(b==0x55)state=1;break;
                case 1:state=b==0x7f?2:(b==0x55?1:0);break;
                case 2:command=b;sum=b;state=3;break;
                case 3:length=b<<8;sum+=b;state=4;break;
                case 4:length|=b;sum+=b;index=0;if(length>4096){reset();break;}data=new byte[length];state=length==0?6:5;break;
                case 5:data[index++]=value;sum+=b;if(index==length)state=6;break;
                case 6:if((sum&255)==b)out.add(new Packet(command,data));reset();break;
                default:reset();
            }}return out;
        }
    }
}
