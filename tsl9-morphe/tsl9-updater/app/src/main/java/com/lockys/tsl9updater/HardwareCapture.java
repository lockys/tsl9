package com.lockys.tsl9updater;
import static com.lockys.tsl9updater.UiMessage.m;

import java.io.*;
import java.nio.*;
import java.nio.charset.*;
import java.util.*;
import java.util.regex.Pattern;

/** Local hardware-origin journal, separate from phone-side GATT debugging. */
public final class HardwareCapture {
    public enum Mode { BLE, CAN, TEXT }
    private final OtaSession.Clock clock;
    private final int maxRecords,maxChars;private final long maxDuration;
    private final StringBuilder rows=new StringBuilder();private final ByteArrayOutputStream textLine=new ByteArrayOutputStream();
    private Mode mode=Mode.BLE;private boolean active,includeCanData;private long started;private int records;private String reason="not_started";
    private boolean textOverflow;
    private static final Pattern SECRET=Pattern.compile("(?i)(?<![a-z0-9])(password|passwd|pwd|token|secret|authorization|api[_ -]?key|uid|uuid|vin|mac|ble[_ -]?key|ssid)(?![a-z0-9])|密碼|金鑰|憑證|車架");
    private static final char[] HEX="0123456789ABCDEF".toCharArray();
    public HardwareCapture(OtaSession.Clock clock){this(clock,10000,512*1024,300000);}
    public HardwareCapture(OtaSession.Clock clock,int count,int chars,long duration){this.clock=clock;maxRecords=count;maxChars=chars;maxDuration=duration;}
    public boolean active(){return active;}public Mode mode(){return mode;}public int records(){return records;}public String reason(){return reason;}
    public void start(Mode next,boolean includeBytes){
        if(active)throw new UiException(m("capture_active"));if(next==null)throw new UiException(m("capture_missing"));
        mode=next;includeCanData=includeBytes;started=clock.now();rows.setLength(0);textLine.reset();textOverflow=false;records=0;reason="recording";active=true;
    }
    public static byte[] canFilter(String text){
        if(text==null||text.trim().isEmpty())return new byte[]{1};
        String[] ids=text.trim().split(",",-1);if(ids.length>16)throw new UiException(m("can_limit"));
        byte[] out=new byte[2+ids.length*2];out[0]=(byte)255;out[1]=(byte)255;
        for(int j=0;j<ids.length;j++){
            String id=ids[j].trim();if(!id.matches("[0-9a-fA-F]{3,4}"))throw new UiException(m("can_invalid"));
            int n=Integer.parseInt(id,16);out[2+j*2]=(byte)n;out[3+j*2]=(byte)(n>>>8);
        }return out;
    }
    public void packet(int cmd,byte[] payload){
        tick();if(!active||mode==Mode.TEXT)return;
        String prefix="\"cmd\":"+cmd+",\"length\":"+payload.length;
        if(cmd==0xa0&&payload.length>=18){
            append("device_info",prefix+",\"hwByte\":"+(payload[0]&255)+",\"bootByte\":"+(payload[1]&255)+",\"appByte\":"+(payload[2]&255)+",\"normalMode\":"+((payload[3]&1)!=0)+",\"identity\":\"redacted\"");
        }else if(cmd==0xc0&&mode==Mode.CAN){
            if(payload.length<2||payload.length>10){append("can_status",prefix+",\"payload\":\"redacted\"");return;}
            int id=(payload[0]&255)<<8|(payload[1]&255);String data="redacted";
            if(includeCanData){
                // Standard OBD/diagnostic transport may carry VIN/identity across packets.
                data=(id>=0x7e0&&id<=0x7ef)||id==0x7df?"diagnostic_identity_redacted":hex(payload,2);
            }
            append("can_rx",prefix+",\"id\":"+quote(hex(payload,0).substring(0,5).replace(" ",""))+",\"dataLength\":"+(payload.length-2)+",\"data\":"+quote(data));
        }else append(cmd==0xa8?"auth_status":"ble_reply",prefix+",\"payload\":\"redacted\"");
    }
    public void notification(byte[] chunk){
        tick();if(!active||mode!=Mode.TEXT)return;
        for(byte b:chunk){
            if(!active)return;
            if(b==10){flushText();textOverflow=false;}
            else if(textLine.size()<4096&&!textOverflow)textLine.write(b);
            else if(!textOverflow){textLine.reset();textOverflow=true;append("text_truncated","\"reason\":\"line_limit\"");}
        }
    }
    private void flushText(){
        if(textOverflow){textLine.reset();return;}byte[] bytes=textLine.toByteArray();textLine.reset();if(bytes.length==0)return;
        try{
            String line=StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString();
            if(line.endsWith("\r"))line=line.substring(0,line.length()-1);
            for(int j=0;j<line.length();j++)if(line.charAt(j)<32&&line.charAt(j)!='\t'){append("invalid_text","\"reason\":\"binary_control_bytes\"");return;}
            append("firmware_text","\"text\":"+quote(SECRET.matcher(line).find()?"[sensitive line redacted]":line));
        }catch(CharacterCodingException e){append("invalid_utf8","\"length\":"+bytes.length);}
    }
    private void append(String kind,String fields){
        String row="{\"elapsedMs\":"+Math.max(0,clock.now()-started)+",\"source\":\"hardware_rx\",\"kind\":"+quote(kind)+","+fields+"}\n";
        if(records>=maxRecords){active=false;reason="record_limit";return;}
        if(rows.length()+row.length()>maxChars){active=false;reason="size_limit";return;}
        rows.append(row);records++;
    }
    public void tick(){if(active&&clock.now()-started>=maxDuration)stop("duration_limit");}
    public void stop(String why){if(!active)return;if(mode==Mode.TEXT)flushText();active=false;if(reason.equals("recording"))reason=why;}
    public String snapshot(){return "{\"schema\":\"tsl9-hardware-log-v1\",\"mode\":"+quote(mode.name())+",\"reason\":"+quote(reason)+",\"records\":"+records+",\"startedElapsedMs\":"+started+",\"includeCanData\":"+includeCanData+"}\n"+rows;}
    public String preview(){String s=rows.toString();return s.substring(Math.max(0,s.length()-6000));}
    private static String hex(byte[] bytes,int from){StringBuilder b=new StringBuilder();for(int j=from;j<bytes.length;j++){if(j>from)b.append(' ');int v=bytes[j]&255;b.append(HEX[v>>>4]).append(HEX[v&15]);}return b.toString();}
    private static String quote(String text){StringBuilder b=new StringBuilder("\"");for(int j=0;j<text.length();j++){char c=text.charAt(j);switch(c){case '"':b.append("\\\"");break;case '\\':b.append("\\\\");break;case '\n':b.append("\\n");break;case '\r':b.append("\\r");break;case '\t':b.append("\\t");break;default:if(c<32)b.append(String.format(Locale.ROOT,"\\u%04x",(int)c));else b.append(c);}}return b.append('"').toString();}
}
