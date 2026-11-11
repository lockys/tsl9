package dev.tsl9.morphe;

import java.util.Arrays;

/** Synthetic same-connection schedules against the real session and codec, not Android GATT. */
public final class OtaSameConnectionLateAckTests {
    public static void main(String[] args) {
        byte[] bytes = new byte[2048];
        Arrays.fill(bytes, 0, 1024, (byte) 0x35);
        Arrays.fill(bytes, 1024, 2048, (byte) 0x76);
        FirmwareImage image = FirmwareImage.parse(bytes, FirmwareImage.Format.RAW);
        byte[] uid = new byte[14]; uid[0] = 1;
        for (boolean beforeRetryCallback : new boolean[]{true, false}) {
            OtaLateAckProtocolTests.Harness h = new OtaLateAckProtocolTests.Harness();
            h.start(image, uid);
            Runnable oldCallback = h.done;
            h.complete(); // W0's local completion starts its ACK deadline
            h.time += 1200;
            int count = h.sends;
            h.session.tick(); // W0 retransmission, still the same session/connection
            OtaLateAckProtocolTests.check(h.sends == count + 1 && h.session.page() == 0, "W0 retried");
            oldCallback.run(); // token from the previous attempt must not complete the retry
            OtaLateAckProtocolTests.check(h.session.page() == 0, "old callback ignored");
            if (!beforeRetryCallback) h.complete();
            h.reply(0x57, new byte[]{0}); // synthetic delayed W0 status response
            if (beforeRetryCallback) {
                OtaLateAckProtocolTests.check(h.session.page() == 0, "buffered until retry completion");
                h.complete();
            }
            OtaLateAckProtocolTests.check(h.session.page() == 1, "W0 reply advances to W1");
            h.complete();
            h.reply(0x57, new byte[]{0}); // synthetic second W0 response, arriving while W1 waits
            OtaLateAckProtocolTests.check(h.session.page() == 2 && h.command == 0x45,
                    "unidentified delayed W0 response advances W1 to END");
            System.out.println((beforeRetryCallback ? "early" : "late") + " retry reply: " + h.events);
        }
        System.out.println("OtaSameConnectionLateAckTests PASS (synthetic schedules)");
    }
}
