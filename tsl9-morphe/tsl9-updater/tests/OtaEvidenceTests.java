package dev.tsl9.morphe;
import java.io.File;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;

public class OtaEvidenceTests {
    static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception{
        File file=Files.createTempFile("ota-evidence-", ".log").toFile();
        try {
            OtaEvidence evidence=new OtaEvidence(file);
            String hash="a".repeat(64);
            evidence.accept("OTA IMAGE format=RAW bytes=1024 pages=1 padding=0 sha256="+hash+" transferSha256="+hash);
            evidence.accept("OTA TX cmd=0x57 page=0/1 len=1026 seq=3 attempt=1/9");
            evidence.accept("OTA RX cmd=0x52 page=0/1 len=1026");
            evidence.accept("OTA WRITE accepted page=0 total=1");
            evidence.accept("OTA VERIFY matched page=0 total=1");
            evidence.accept("OTA RETRY ota_read_mismatch[0] page=0");
            evidence.accept("OTA S readback=true policy=device_reply");
            evidence.accept("OTA RESULT eReplyReceived=true readbackVerified=true restartVerified=false");
            evidence.accept("OTA STOP secret-UID-123456789");
            evidence.accept("CAN RX fake-private-data");
            evidence.accept("A0 validated len=76 hwByte=0 btVersionByte=16 appVersionByte=16 normalMode=true");
            String saved=Files.readString(file.toPath(),StandardCharsets.UTF_8);
            check(saved.contains("sha256="+hash)&&saved.contains("cmd=0x57")&&saved.contains("readback=true"),"OTA facts persisted");
            check(saved.contains("readbackVerified=true restartVerified=false"),"readback remains distinct from restart");
            check(saved.contains("VERIFY matched page=0")&&saved.contains("reason=ota_read_mismatch page=0"),"explicit match and bounded reason");
            check(!saved.contains("secret")&&!saved.contains("fake-private"),"no untrusted diagnostic content");
            check(saved.contains("identity_and_update_phase_unverified"),"A0 evidence not treated as confirmed identity or post-update state");
            OtaEvidence reopened=new OtaEvidence(file);
            check(reopened.snapshot().contains("cmd=0x52"),"survives reopening");
            reopened.accept("OTA IMAGE format=RAW bytes=1024 pages=1 padding=0 sha256="+hash+" transferSha256="+hash);
            check(!reopened.snapshot().contains("cmd=0x52"),"new OTA starts new evidence");
            System.out.println("OtaEvidenceTests passed");
        } finally {Files.deleteIfExists(file.toPath());}
    }
}
