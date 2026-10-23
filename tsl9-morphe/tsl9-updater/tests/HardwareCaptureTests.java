package dev.tsl9.morphe;

import java.nio.charset.StandardCharsets;
import java.util.*;

/** Synthetic hardware notifications; never uses a radio or real vehicle data. */
public final class HardwareCaptureTests {
    private static int checks;
    private static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    private static void rejects(Runnable r){checks++;try{r.run();}catch(IllegalArgumentException e){return;}throw new AssertionError("expected rejection");}
    public static void main(String[] args){
        long[] clock={100};HardwareCapture c=new HardwareCapture(()->clock[0]);
        check(Arrays.equals(HardwareCapture.canFilter(""),new byte[]{1}),"all CAN subscription original C0[1]");
        check(Arrays.equals(HardwareCapture.canFilter("123, 07E8"),new byte[]{(byte)255,(byte)255,0x23,1,(byte)0xe8,7}),"CAN filter little endian");
        rejects(()->HardwareCapture.canFilter("XYZ"));rejects(()->HardwareCapture.canFilter("123,"));rejects(()->HardwareCapture.canFilter("10000"));
        c.start(HardwareCapture.Mode.BLE,false);byte[] info=new byte[178];Arrays.fill(info,(byte)'Z');info[0]=9;info[1]=1;info[2]=2;info[3]=1;
        c.packet(0xa0,info);String log=c.snapshot();check(log.contains("device_info")&&log.contains("\"hwByte\":9"),"actual device fields retained");
        check(!log.contains("ZZZZ"),"UID/VIN not retained");c.packet(0xa8,"test-password".getBytes(StandardCharsets.UTF_8));check(!c.snapshot().contains("test-password"),"password payload omitted");
        c.packet(0x57,"firmware-private-bytes".getBytes(StandardCharsets.UTF_8));check(!c.snapshot().contains("firmware-private"),"firmware bytes omitted");
        c.stop("manual");int n=c.records();c.packet(0xa0,info);check(c.records()==n,"stopped ignores packets");
        c.start(HardwareCapture.Mode.CAN,false);c.packet(0xc0,new byte[]{1,0x23,0x11,0x22});
        check(c.snapshot().contains("0123")&&!c.snapshot().contains("11 22"),"CAN ID retained, data opt-in");
        c.stop("mode change");c.start(HardwareCapture.Mode.CAN,true);c.packet(0xc0,new byte[]{1,0x23,0x11,0x22});check(c.snapshot().contains("11 22"),"explicit synthetic CAN data retained");
        c.packet(0xc0,new byte[]{7,(byte)0xe8,0x49,2,0x56,0x49,0x4e});check(c.snapshot().contains("diagnostic_identity_redacted"),"diagnostic transport identity masked");
        c.packet(0xc0,new byte[]{0});check(c.snapshot().contains("can_status"),"control reply not fake CAN frame");
        c.stop("mode change");c.start(HardwareCapture.Mode.TEXT,false);byte[] utf="溫度=31\n".getBytes(StandardCharsets.UTF_8);
        c.notification(Arrays.copyOfRange(utf,0,2));c.notification(Arrays.copyOfRange(utf,2,utf.length));check(c.snapshot().contains("溫度=31"),"fragmented UTF8 line");
        c.notification("password=synthetic-secret\nUID=0011223344\nVIN=TEST-PRIVATE\n".getBytes(StandardCharsets.UTF_8));
        check(!c.snapshot().contains("synthetic-secret")&&!c.snapshot().contains("0011223344")&&!c.snapshot().contains("TEST-PRIVATE"),"known secrets redacted across text lines");
        c.notification("device_uid=private-identifier\nrefresh_token=private-refresh\nBLE_MAC=private-mac\n".getBytes(StandardCharsets.UTF_8));
        check(!c.snapshot().contains("private-identifier")&&!c.snapshot().contains("private-refresh")&&!c.snapshot().contains("private-mac"),"prefixed identity and credential keys redacted");
        c.notification("partial".getBytes(StandardCharsets.UTF_8));c.stop("manual");check(c.snapshot().contains("partial"),"last text line flushed on stop");
        c.start(HardwareCapture.Mode.TEXT,false);c.notification(new byte[]{(byte)0xff,0,10});check(c.snapshot().contains("invalid_utf8")&&!c.snapshot().contains("\u0000"),"binary text not forged");
        HardwareCapture limited=new HardwareCapture(()->clock[0],2,4096,5000);limited.start(HardwareCapture.Mode.BLE,false);for(int j=0;j<3;j++)limited.packet(0x45,new byte[0]);check(!limited.active()&&limited.records()==2&&limited.reason().contains("record_limit"),"bounded journal stops capture");
        c.stop("mode change");c.start(HardwareCapture.Mode.CAN,false);clock[0]+=300001;c.tick();check(!c.active()&&c.reason().equals("duration_limit"),"bounded capture time");
        c.start(HardwareCapture.Mode.TEXT,false);c.notification("q\"\\\t\n".getBytes(StandardCharsets.UTF_8));check(c.snapshot().contains("\\\"")&&c.snapshot().contains("\\\\")&&c.snapshot().contains("\\t"),"JSON escape");
        System.out.println("HardwareCaptureTests passed: "+checks+" synthetic assertions; no physical hardware.");
    }
}
