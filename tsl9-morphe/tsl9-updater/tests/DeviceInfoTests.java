package dev.tsl9.morphe;
public final class DeviceInfoTests {
    private static int checks;
    static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    public static void main(String[] args){
        byte[] reply=new byte[76];reply[0]=7;reply[1]=0x32;reply[2]=0x41;reply[3]=1;
        DeviceInfoSnapshot info=DeviceInfoSnapshot.parse(reply,1234);
        check(info.hardwareByte==7&&info.bluetoothByte==0x32&&info.applicationByte==0x41,"A0 field offsets from OEM getinfo");
        check(info.bluetoothPrefix().equals("3.2")&&info.applicationPrefix().equals("4.1"),"OEM high-byte hex version prefix");
        check(!info.revisionKnown(),"A0 does not supply server-sourced low-byte revision");
        check(info.normalMode&&info.receivedAt==1234&&info.replyBytes==76,"mode and receipt time");
        reply[2]=0;check(info.applicationByte==0x41,"snapshot cannot change with notification buffer");
        reply[1]=(byte)0xaf;reply[3]=0;info=DeviceInfoSnapshot.parse(reply,2345);
        check(info.bluetoothPrefix().equals("A.F")&&!info.normalMode,"unsigned byte and bootloader mode");
        check(DeviceInfoSnapshot.parse(new byte[18],0).replyBytes==18,"bootloader A0 minimum length");
        for(byte[] invalid:new byte[][]{null,new byte[17]}){try{DeviceInfoSnapshot.parse(invalid,0);throw new AssertionError("short A0 accepted");}catch(IllegalArgumentException expected){checks++;}}
        System.out.println("DeviceInfoTests passed: "+checks+" assertions; synthetic A0 only.");
    }
}
