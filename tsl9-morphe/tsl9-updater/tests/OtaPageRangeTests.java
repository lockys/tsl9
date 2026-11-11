package dev.tsl9.morphe;

import java.nio.file.*;
import java.util.*;

/** Offline exercise of the actual FirmwareImage and OtaSession, never a BLE transport. */
public final class OtaPageRangeTests {
    static void check(boolean b, String s) { if (!b) throw new AssertionError(s); }
    static final class Harness implements OtaSession.Listener, OtaSession.Clock {
        long now; int cmd; byte[] payload; int sends;
        final OtaSession session = new OtaSession(this, this);
        public long now() { return now; }
        public void send(int c, byte[] p, Runnable written) { cmd=c; payload=p.clone(); sends++; written.run(); }
        public void changed(UiMessage m) {}
        public void log(String s) {}
        void reply(int c, byte[] p) { session.onPacket(c,p); }
        void begin(FirmwareImage image, boolean readback) {
            byte[] uid=new byte[14]; uid[0]=1;
            session.start(image,uid); reply(0x55,new byte[]{0});
            reply(0x53,readback?new byte[]{1,1}:new byte[]{1});
        }
    }
    static int index(byte[] p) { return (p[0]&255)*256+(p[1]&255); }
    static void rejected(byte[] b, FirmwareImage.Format f) {
        try { FirmwareImage.parse(b,f); throw new AssertionError("accepted invalid length/index"); }
        catch (UiException expected) { }
    }
    static void transfer(byte[] data, int count, boolean readback) {
        FirmwareImage img=FirmwareImage.parse(data,FirmwareImage.Format.RAW);
        check(img.pageCount()==count,"count"); Harness h=new Harness(); h.begin(img,readback);
        for(int i=0;i<count;i++) {
            check(h.cmd==0x57 && h.payload.length==1026 && index(h.payload)==i,"W "+i);
            check(Arrays.equals(Arrays.copyOfRange(h.payload,2,1026),Arrays.copyOfRange(data,i*1024,(i+1)*1024)),"content "+i);
            h.reply(0x57,new byte[]{0});
        }
        if(readback) {
            for(int i=0;i<count;i++) {
                check(h.cmd==0x52 && h.payload.length==16 && index(h.payload)==i,"R "+i);
                h.reply(0x52,img.page(i));
            }
            check(h.session.readbackVerified(),"verified");
            check(h.cmd==0x52 && index(h.payload)==count && h.payload.length==16,"tail R");
            h.reply(0x52,new byte[0]);
        }
        check(h.cmd==0x45 && h.payload.length==15,"end");
        h.reply(0x45,new byte[0]); check(h.session.success(),"done");
    }
    public static void main(String[] args) throws Exception {
        byte[] data=Files.readAllBytes(Paths.get(args[0]));
        FirmwareImage original=FirmwareImage.parse(data,FirmwareImage.Format.RAW);
        check(data.length==76800 && original.pageCount()==75,"ID2966 length/pages");
        check(original.sha256.equals("0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667"),"image hash");
        transfer(data,75,true); transfer(data,75,false);
        rejected(Arrays.copyOf(data,data.length-1),FirmwareImage.Format.RAW);
        rejected(new byte[1025],FirmwareImage.Format.PAGED);
        byte[] badIndex=new byte[1026]; badIndex[1]=1; rejected(badIndex,FirmwareImage.Format.PAGED);
        byte[] shortImage=Arrays.copyOf(data,74*1024); transfer(shortImage,74,false);
        byte[] extended=Arrays.copyOf(data,96*1024); transfer(extended,96,false);
        transfer(Arrays.copyOf(data,97*1024),97,false);
        FirmwareImage padded=FirmwareImage.parse(Arrays.copyOf(data,data.length-1),FirmwareImage.Format.RAW_FF_PAD);
        check(padded.pageCount()==75 && padded.paddingBytes==1 && padded.page(74)[1025]==(byte)0xff,"explicit pad");
        Harness h=new Harness(); h.begin(original,true);
        for(int i=0;i<74;i++) h.reply(0x57,new byte[]{0});
        check(index(h.payload)==74,"retry page"); byte[] last=h.payload.clone(); int before=h.sends;
        h.reply(0x57,new byte[0]); check(h.sends==before+1 && Arrays.equals(last,h.payload),"invalid W retry");
        h.now+=1200; h.session.tick(); check(h.sends==before+2 && Arrays.equals(last,h.payload),"timeout W retry");
        h.reply(0x57,new byte[]{0});
        check(h.cmd==0x52 && index(h.payload)==0,"verify start");
        byte[] request=h.payload.clone(); before=h.sends;
        h.reply(0x52,new byte[0]); check(h.sends==before+1 && Arrays.equals(request,h.payload),"short R retry");
        for(int i=0;i<4;i++) h.reply(0x52,new byte[0]);
        check(h.session.failed() && h.sends==before+4,"R max five transmissions");
        Harness w=new Harness(); w.begin(original,false); before=w.sends;
        for(int i=0;i<9;i++) w.reply(0x57,new byte[0]);
        check(w.session.failed() && w.sends==before+8,"W max nine transmissions");
        System.out.println("OtaPageRangeTests PASS: real ID2966, 74/75/96/97 pages, lengths, retries and read tail");
    }
}
