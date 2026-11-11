package dev.tsl9.morphe;

import java.util.*;

/** Host-only fault injection; the fake receiver is not a BOOT emulator. */
public final class OtaInterruptedWriteTests {
    static void check(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
    static final class Link implements OtaSession.Listener, OtaSession.Clock {
        long now; int cmd, sends; byte[] payload; Runnable written;
        final OtaSession session = new OtaSession(this, this);
        public long now() { return now; }
        public void changed(UiMessage message) { }
        public void log(String message) { }
        public void send(int cmd, byte[] payload, Runnable written) {
            this.cmd=cmd; this.payload=payload.clone(); this.written=written; sends++;
        }
        void complete() { written.run(); }
        void reply(int cmd, byte[] payload) { session.onPacket(cmd, payload); }
        void start(FirmwareImage image, byte[] uid) {
            session.start(image,uid); complete(); reply(0x55,new byte[]{0});
            complete(); reply(0x53,new byte[]{1});
        }
    }
    public static void main(String[] args) {
        byte[] bytes=new byte[2048]; Arrays.fill(bytes,0,1024,(byte)0x35); Arrays.fill(bytes,1024,2048,(byte)0x76);
        FirmwareImage image=FirmwareImage.parse(bytes,FirmwareImage.Format.RAW);
        byte[] uid=new byte[14]; uid[0]=1;
        Link link=new Link(); link.start(image,uid);
        check(link.session.state()==OtaSession.State.WRITE && link.session.page()==0 && link.cmd==0x57,"first W");
        byte[] first=link.payload.clone(); link.complete(); link.reply(0x57,new byte[]{0});
        check(link.session.page()==1 && link.cmd==0x57,"second W");
        byte[] second=link.payload.clone(); Runnable lateCallback=link.written;
        // Receiver might have committed page 1, but its ACK and local callback are lost.
        link.session.transportLost(); int stoppedSends=link.sends;
        check(link.session.failed() && !link.session.success() && !link.session.readbackVerified(),"loss fails closed");
        lateCallback.run(); link.reply(0x57,new byte[]{0}); link.now+=30000; link.session.tick();
        check(link.session.failed() && link.sends==stoppedSends,"late callback/ACK cannot finish failed session");
        // Explicit new session, not resume: a stale callback from the previous session must be inert.
        link.session.start(image,uid); check(link.cmd==0x55,"restart U");
        lateCallback.run(); link.complete(); link.reply(0x55,new byte[]{0});
        check(link.cmd==0x53,"restart S"); link.complete(); link.reply(0x53,new byte[]{1});
        check(link.session.page()==0 && link.cmd==0x57 && Arrays.equals(first,link.payload),"restart begins at page zero");
        link.complete(); link.reply(0x57,new byte[]{0});
        check(link.session.page()==1 && Arrays.equals(second,link.payload),"restart replays second page");
        link.complete(); link.reply(0x57,new byte[]{0});
        check(link.session.state()==OtaSession.State.END && link.cmd==0x45 && !link.session.success(),"E required");
        link.complete(); link.reply(0x45,new byte[0]);
        check(link.session.success() && !link.session.readbackVerified(),"success is transport completion, not readback");
        System.out.println("OtaInterruptedWriteTests PASS");
    }
}
