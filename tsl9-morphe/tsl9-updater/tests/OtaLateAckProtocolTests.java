package dev.tsl9.morphe;

import java.util.*;

/** Offline session and production frame codec; this is not an Android GATT test. */
public final class OtaLateAckProtocolTests {
    static void check(boolean b, String s) { if (!b) throw new AssertionError(s); }
    static final class Harness implements OtaSession.Listener, OtaSession.Clock {
        long time; int command, sends; byte[] payload; Runnable done;
        final Protocol.Decoder decoder = new Protocol.Decoder();
        final OtaSession session = new OtaSession(this, this);
        final List<String> events = new ArrayList<>();
        public long now() { return time; }
        public void changed(UiMessage m) { }
        public void log(String s) { }
        public void send(int c, byte[] p, Runnable d) {
            command=c; payload=p.clone(); done=d; sends++;
            // Exercise production encoding and decoding on outgoing requests as well.
            Protocol.Decoder out = new Protocol.Decoder();
            List<Protocol.Packet> packets=out.push(Protocol.encode(c,p),time);
            check(packets.size()==1 && packets.get(0).command==c && Arrays.equals(p,packets.get(0).payload),"outgoing frame");
            events.add("send "+c+" page="+session.page());
        }
        void complete() { Runnable r=done; events.add("callback "+command+" page="+session.page()); r.run(); }
        void reply(int c, byte[] p) {
            byte[] frame=Protocol.encode(c,p); int cut=3;
            check(decoder.push(Arrays.copyOfRange(frame,0,cut),time).isEmpty(),"partial frame");
            List<Protocol.Packet> packets=decoder.push(Arrays.copyOfRange(frame,cut,frame.length),time);
            check(packets.size()==1 && Arrays.equals(p,packets.get(0).payload),"reply frame");
            events.add("reply "+c+" len="+p.length+" page="+session.page());
            session.onPacket(packets.get(0).command,packets.get(0).payload);
        }
        void start(FirmwareImage image, byte[] uid) {
            session.start(image,uid); complete(); reply(0x55,new byte[]{0});
            complete(); reply(0x53,new byte[]{1});
        }
    }
    static Harness oldPageOne(FirmwareImage image, byte[] uid) {
        Harness h=new Harness(); h.start(image,uid);
        h.complete(); h.reply(0x57,new byte[]{0});
        check(h.session.page()==1,"old page 1");
        h.complete(); h.events.add("disconnect"); h.session.transportLost();
        check(h.session.failed(),"disconnect fails");
        h.start(image,uid); check(h.session.page()==0,"new page 0");
        return h;
    }
    public static void main(String[] args) {
        byte[] bytes=new byte[2048]; Arrays.fill(bytes,0,1024,(byte)0x35); Arrays.fill(bytes,1024,2048,(byte)0x76);
        FirmwareImage image=FirmwareImage.parse(bytes,FirmwareImage.Format.RAW);
        byte[] uid=new byte[14]; uid[0]=1;
        for (boolean early : new boolean[]{true,false}) {
            Harness h=oldPageOne(image,uid);
            if (!early) h.complete();
            h.reply(0x57,new byte[]{0}); // synthetic status-only ACK, no page identity
            check(h.session.page()==0 || !early,"early reply buffered");
            if (early) { check(h.session.page()==0,"not advanced before callback"); h.complete(); }
            check(h.session.page()==1 && h.command==0x57,"stale status ACK advances new page");
            System.out.println((early?"before":"after")+" callback: "+h.events);
        }
        Harness h=oldPageOne(image,uid); h.complete(); int sent=h.sends;
        h.reply(0x57,image.page(1)); // synthetic full echo includes page index 00 01
        check(h.session.page()==0 && h.sends==sent+1 && Arrays.equals(h.payload,image.page(0)),"different-page echo retries");
        h.complete(); h.reply(0x57,image.page(0));
        check(h.session.page()==1,"matching full echo accepted");
        // A stale echo for the same page remains indistinguishable on restart.
        h=oldPageOne(image,uid); h.complete(); h.reply(0x57,image.page(0));
        check(h.session.page()==1,"same-page echo advances");
        h=oldPageOne(image,uid); h.complete(); sent=h.sends; h.reply(0x57,new byte[0]);
        check(h.session.page()==0 && h.sends==sent+1,"empty W reply retries, not accepted");
        System.out.println("OtaLateAckProtocolTests PASS");
    }
}
