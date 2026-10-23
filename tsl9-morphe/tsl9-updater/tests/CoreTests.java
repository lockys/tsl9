package dev.tsl9.morphe;

import java.util.*;

/** Standalone JVM behavior tests; no Android, BLE radio or network. */
public class CoreTests {
    static int checks;
    static void check(boolean ok, String why) { checks++; if(!ok) throw new AssertionError(why); }
    static void rejects(Runnable r) { checks++; try { r.run(); } catch(IllegalArgumentException e) { return; } throw new AssertionError("expected rejection"); }
    static byte[] uid() { byte[] b=new byte[14]; Arrays.fill(b,(byte)7); return b; }
    static class Rig implements OtaSession.Listener {
        long now; OtaSession s=new OtaSession(this,()->now); int cmd; byte[] data; Runnable sent; int sends;
        public void send(int c,byte[] b,Runnable done) {cmd=c;data=b;sent=done;sends++;}
        public void changed(UiMessage detail) {}
        public void log(String text) {}
        void done(){Runnable r=sent;sent=null;r.run();}
        void reply(int c,byte[] b){s.onPacket(c,b);}
        void prepare(FirmwareImage i){s.start(i,uid());check(cmd==0x55,"prepare U");done();reply(0x55,new byte[]{0});check(cmd==0x53,"start S");done();}
    }
    public static void main(String[] args) throws Exception {
        byte[] payload={1,2,3}; byte[] frame=Protocol.encode(0x57,payload);
        check(Arrays.equals(frame,new byte[]{0x55,0x7f,0x57,0,3,1,2,3,0x60}),"framing checksum golden");
        Protocol.Decoder d=new Protocol.Decoder();
        check(d.push(Arrays.copyOfRange(frame,0,4),0).size()==0,"partial header");
        List<Protocol.Packet> packets=d.push(Arrays.copyOfRange(frame,4,frame.length),10);
        check(packets.size()==1&&Arrays.equals(packets.get(0).payload,payload),"fragment reassembly");
        frame[frame.length-1]^=1;check(d.push(frame,20).isEmpty(),"bad checksum discarded");
        byte[] valid=Protocol.encode(0x45,new byte[0]);check(d.push(valid,25).get(0).payload.length==0,"empty ACK");
        d.push(new byte[]{0x55,0x7f,1,0,2,3},30);
        check(d.push(valid,600).size()==1,"stale fragment expires");
        d.push(new byte[]{0x55,0x7f,1,0x7f,(byte)0xff},700);
        check(d.push(valid,710).size()==1,"oversized frame discarded");
        byte[] raw=new byte[2048];for(int j=0;j<raw.length;j++)raw[j]=(byte)(j*13);
        FirmwareImage image=FirmwareImage.parse(raw,FirmwareImage.Format.RAW);
        check(image.pageCount()==2,"two raw pages");check(image.page(1).length==1026&&image.page(1)[1]==1,"page header");
        check(Arrays.equals(Arrays.copyOfRange(image.page(1),2,1026),Arrays.copyOfRange(raw,1024,2048)),"no firmware edits");
        byte[] paged=new byte[2052];System.arraycopy(image.page(0),0,paged,0,1026);System.arraycopy(image.page(1),0,paged,1026,1026);
        check(FirmwareImage.parse(paged,FirmwareImage.Format.PAGED).sha256.length()==64,"SHA256");
        rejects(()->FirmwareImage.parse(new byte[0],FirmwareImage.Format.PAGED));
        rejects(()->FirmwareImage.parse(new byte[1025],FirmwareImage.Format.RAW));
        rejects(()->FirmwareImage.parse(new byte[1027],FirmwareImage.Format.PAGED));
        byte[] wrong=paged.clone();wrong[1027]=3;rejects(()->FirmwareImage.parse(wrong,FirmwareImage.Format.PAGED));
        rejects(()->FirmwareImage.parse(new byte[257*1024],FirmwareImage.Format.RAW));
        byte[] custom=new byte[1025];Arrays.fill(custom,(byte)0x42);custom[1024]=0x37;
        FirmwareImage padded=FirmwareImage.parse(custom,FirmwareImage.Format.RAW_FF_PAD);
        check(padded.pageCount()==2&&padded.paddingBytes==1023,"explicit custom raw FF padding");
        check(padded.page(1)[2]==0x37&&padded.page(1)[3]==(byte)0xff&&padded.page(1)[1025]==(byte)0xff,"custom content preserved, only tail padded");
        check(!padded.sha256.equals(padded.transferSha256),"original and transmitted payload hashes distinguished");
        byte[] patched=raw.clone();patched[200]^=0x7f;FirmwareImage own=FirmwareImage.parse(patched,FirmwareImage.Format.RAW);
        check(own.page(0)[202]==patched[200]&&!own.sha256.equals(image.sha256),"modified user bin not rejected by factory whitelist");
        Rig r=new Rig();rejects(()->r.s.start(image,new byte[14]));rejects(()->r.s.start(image,new byte[13]));
        r.prepare(image);r.reply(0x53,new byte[]{1,1});check(r.cmd==0x57,"first page W");
        r.done();r.reply(0x45,new byte[0]);check(r.s.page()==0,"out of order ignored");
        r.reply(0x57,new byte[]{0});check(r.s.page()==1,"ACK advances one page");r.done();r.reply(0x57,image.page(1));
        check(r.cmd==0x52,"readback after writes");r.done();r.reply(0x52,image.page(0));r.done();r.reply(0x52,image.page(1));
        check(r.cmd==0x52&&r.data[1]==2,"OEM terminal read uses pageCount index");r.done();r.reply(0x52,new byte[0]);
        check(r.cmd==0x45&&!r.s.success(),"end sent not success");r.done();r.reply(0x45,new byte[0]);
        check(r.s.success()&&r.s.readbackVerified(),"device end ACK + readback success");
        Rig noRead=new Rig();noRead.prepare(image);noRead.reply(0x53,new byte[]{1});noRead.done();noRead.reply(0x57,new byte[]{0});noRead.done();noRead.reply(0x57,new byte[]{0});noRead.done();noRead.reply(0x45,new byte[0]);
        check(noRead.s.success()&&!noRead.s.readbackVerified(),"no false verify claim");
        Rig bad=new Rig();bad.prepare(image);bad.reply(0x53,new byte[]{0});check(bad.s.failed(),"wrong APP mode rejected");
        Rig retry=new Rig();retry.prepare(image);retry.reply(0x53,new byte[]{1});retry.done();int sends=retry.sends;retry.now=1200;retry.s.tick();
        check(!retry.s.failed()&&retry.sends==sends+1&&retry.s.page()==0,"OEM timeout retries current page");
        for(int j=0;j<8;j++){retry.done();retry.now+=1200;retry.s.tick();}check(retry.s.failed(),"OEM write retry budget is finite");
        Rig cancelled=new Rig();cancelled.prepare(image);cancelled.s.cancel("test");int n=cancelled.sends;cancelled.reply(0x53,new byte[]{1});check(cancelled.sends==n,"cancel ignores delayed reply");
        Rig boot=new Rig();boot.s.start(image,uid());boot.done();boot.reply(0x55,new byte[]{1});check(boot.s.waitingBoot(),"wait reboot");
        byte[] info=new byte[18];System.arraycopy(uid(),0,info,4,14);boot.s.onDeviceInfo(info);check(boot.cmd==0x53,"same UID boot resumes S");
        Rig different=new Rig();different.s.start(image,uid());different.done();different.reply(0x55,new byte[]{1});byte[] other=info.clone();other[4]++;different.s.onDeviceInfo(other);check(different.s.failed(),"other device cannot receive firmware");
        Rig mismatch=new Rig();mismatch.prepare(image);mismatch.reply(0x53,new byte[]{1,1});mismatch.done();mismatch.reply(0x57,new byte[]{0});mismatch.done();mismatch.reply(0x57,new byte[]{0});byte[] corrupt=image.page(0);corrupt[10]^=1;for(int j=0;j<5;j++){mismatch.done();mismatch.reply(0x52,corrupt);}check(mismatch.s.failed(),"repeated readback mismatch blocks E");
        Rig early=new Rig();early.s.start(image,uid());early.reply(0x55,new byte[]{0});check(early.cmd==0x55,"early ack deferred until write drained");early.done();check(early.cmd==0x53,"deferred ack consumed");
        Rig rebootEarly=new Rig();rebootEarly.s.start(image,uid());rebootEarly.reply(0x55,new byte[]{1});rebootEarly.s.transportLost();
        check(rebootEarly.s.waitingBoot()&&!rebootEarly.s.failed(),"early U reboot ACK survives disconnect before write callback");rebootEarly.done();check(rebootEarly.cmd==0x55,"stale U callback cannot send S while disconnected");rebootEarly.s.onDeviceInfo(info);check(rebootEarly.cmd==0x53,"early reboot resumes only after same UID boot A0");
        Rig endEarly=new Rig();endEarly.prepare(image);endEarly.reply(0x53,new byte[]{1});endEarly.done();endEarly.reply(0x57,new byte[]{0});endEarly.done();endEarly.reply(0x57,new byte[]{0});endEarly.reply(0x45,new byte[0]);check(!endEarly.s.success(),"early E stays pending until transport boundary");endEarly.s.transportLost();check(endEarly.s.success(),"received E survives disconnect before final write callback");int endSends=endEarly.sends;endEarly.done();check(endEarly.s.success()&&endEarly.sends==endSends,"late E write callback cannot restart finished session");
        Rig pageEarly=new Rig();pageEarly.prepare(image);pageEarly.reply(0x53,new byte[]{1});pageEarly.reply(0x57,new byte[]{0});pageEarly.s.transportLost();check(pageEarly.s.failed(),"early W ACK does not allow automatic resume after disconnect");
        Rig zeroEarly=new Rig();zeroEarly.s.start(image,uid());zeroEarly.reply(0x55,new byte[]{0});zeroEarly.s.transportLost();check(zeroEarly.s.failed(),"only nonzero U permits reboot recovery after early ACK");
        Rig endNoAck=new Rig();endNoAck.prepare(image);endNoAck.reply(0x53,new byte[]{1});endNoAck.done();endNoAck.reply(0x57,new byte[]{0});endNoAck.done();endNoAck.reply(0x57,new byte[]{0});endNoAck.s.transportLost();check(endNoAck.s.failed(),"disconnect without E reply never claims completion");
        if(args.length==2){
            byte[] factoryPaged=java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(args[0]));
            byte[] factoryRaw=java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(args[1]));
            FirmwareImage a=FirmwareImage.parse(factoryPaged,FirmwareImage.Format.PAGED),b=FirmwareImage.parse(factoryRaw,FirmwareImage.Format.RAW);
            check(a.pageCount()==b.pageCount(),"factory page count equality");
            for(int j=0;j<a.pageCount();j++)check(Arrays.equals(a.page(j),b.page(j)),"factory raw-to-page exact bytes "+j);
            System.out.println("Factory-reference format check passed: "+a.pageCount()+" pages; files read only, not bundled or flashed.");
        }
        System.out.println("CoreTests passed: "+checks+" assertions; local protocol/format tests only, no hardware.");
    }
}
