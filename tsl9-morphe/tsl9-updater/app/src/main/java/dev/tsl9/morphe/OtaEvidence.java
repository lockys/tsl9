package dev.tsl9.morphe;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.regex.Pattern;

/** Private, bounded update evidence. Accept only explicitly structured, non-payload fields. */
final class OtaEvidence {
    private static final long MAX = 512L * 1024;
    private static final Pattern IMAGE = Pattern.compile("OTA IMAGE format=[A-Z_]+ bytes=[0-9]+ pages=[0-9]+ padding=[0-9]+ sha256=[0-9a-f]{64} transferSha256=[0-9a-f]{64}");
    private static final Pattern PACKET = Pattern.compile("OTA (TX|RX) cmd=0x[0-9A-F]{2} page=[0-9]+/[0-9]+ len=[0-9]+(?: seq=[0-9]+ attempt=[0-9]+/[0-9]+)?");
    private static final Pattern POLICY = Pattern.compile("OTA S readback=(true|false) policy=(confirmed_oem_hw20|device_reply)");
    private static final Pattern RESULT = Pattern.compile("OTA RESULT eReplyReceived=true readbackVerified=(true|false) restartVerified=false");
    private static final Pattern PAGE = Pattern.compile("OTA (WRITE accepted|VERIFY matched) page=[0-9]+ total=[0-9]+");
    private static final Pattern REASON = Pattern.compile("ota_[a-z0-9_]+");
    private static final Pattern RETRY_PAGE = Pattern.compile(" page=([0-9]+)$");
    private static final Pattern INFO = Pattern.compile("A0 validated len=[0-9]+ hwByte=[0-9]+ btVersionByte=[0-9]+ appVersionByte=[0-9]+ normalMode=(true|false)");
    private static final Pattern STATE = Pattern.compile("STATE (PREPARE|BOOT|START|WRITE|VERIFY|END|DONE|FAILED|CANCELLED) .*");
    private final File file;
    OtaEvidence(File file){this.file=file;}
    void accept(String line) throws IOException {
        boolean start=IMAGE.matcher(line).matches();
        String safe;
        if(start||PACKET.matcher(line).matches()||POLICY.matcher(line).matches()||RESULT.matcher(line).matches()||PAGE.matcher(line).matches()) safe=line;
        else if(STATE.matcher(line).matches()) safe="OTA STATE="+line.substring(6).split(" ",2)[0];
        else if(line.startsWith("OTA RETRY ")||line.startsWith("OTA STOP ")) {java.util.regex.Matcher reason=REASON.matcher(line);java.util.regex.Matcher page=RETRY_PAGE.matcher(line);safe=(line.startsWith("OTA RETRY ")?"OTA RETRY":"OTA STOP")+(reason.find()?" reason="+reason.group():" reason=redacted")+(page.find()?" page="+page.group(1):"");}
        else if(line.startsWith("OTA CANCEL ")) safe="OTA CANCEL detail_redacted";
        else if(INFO.matcher(line).matches()) safe="OBSERVED_A0 identity_and_update_phase_unverified "+line;
        else return;
        if(!start&&!file.exists())return;
        byte[] data=("epochMs="+System.currentTimeMillis()+" "+safe+"\n").getBytes(StandardCharsets.UTF_8);
        if(!start && file.length()+data.length>MAX)throw new IOException("OTA evidence limit reached");
        try(FileOutputStream out=new FileOutputStream(file,!start)){out.write(data);}
    }
    String snapshot() throws IOException {
        if(!file.exists())return "";
        if(file.length()>MAX)throw new IOException("OTA evidence exceeds limit");
        try(FileInputStream in=new FileInputStream(file);ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1){if(out.size()+n>MAX)throw new IOException("OTA evidence exceeds limit");out.write(b,0,n);}return new String(out.toByteArray(),StandardCharsets.UTF_8);
        }
    }
}
