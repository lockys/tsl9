package dev.tsl9.morphe;

import java.util.*;
import static dev.tsl9.morphe.UiMessage.m;

/** APP-only OEM OTA wire flow. Original APK app-service.js offsets 0x18c05..0x19a0c. */
public final class OtaSession {
    public interface Listener { void send(int cmd,byte[] payload,Runnable written); void changed(UiMessage detail); void log(String text); }
    public interface Clock { long now(); }
    public enum State { IDLE, PREPARE, BOOT, START, WRITE, VERIFY, END, DONE, FAILED, CANCELLED }
    private final Listener listener;private final Clock clock;
    private State state=State.IDLE;private FirmwareImage image;private byte[] uid;
    private int page,expected,sequence,attempts;private long deadline;private boolean transmitting,readback,verified,oemHw20;
    private byte[] request;private UiMessage requestDetail;
    private Protocol.Packet early;
    public OtaSession(Listener l,Clock c){listener=l;clock=c;}
    public State state(){return state;}public int page(){return page;}public int total(){return image==null?0:image.pageCount();}
    public boolean active(){return state!=State.IDLE&&state!=State.DONE&&state!=State.FAILED&&state!=State.CANCELLED;}
    public boolean waitingBoot(){return state==State.BOOT;}public boolean success(){return state==State.DONE;}
    public boolean failed(){return state==State.FAILED;}public boolean readbackVerified(){return verified;}
    public void start(FirmwareImage img,byte[] deviceUid){
        start(img,deviceUid,false);
    }
    public void start(FirmwareImage img,byte[] deviceUid,boolean confirmedOemHw20){
        if(active())throw new UiException(m("ota_active"));
        if(img==null||deviceUid==null||deviceUid.length!=14)throw new UiException(m("ota_info_required"));
        boolean any=false;for(byte b:deviceUid)any|=b!=0;
        if(!any)throw new UiException(m("ota_empty_uid"));
        image=img;uid=deviceUid.clone();page=0;verified=false;readback=false;oemHw20=confirmedOemHw20;
        listener.log("OTA profile=OEM_APP hw20="+oemHw20+" W/S/E=1200ms maxTx=9 R=1000ms maxTx=5");
        emit(State.PREPARE,0x55,modeUid(),m("ota_prepare"));
    }
    private byte[] modeUid(){byte[] b=new byte[15];b[0]=1;System.arraycopy(uid,0,b,1,14);return b;}
    private void emit(State next,int cmd,byte[] payload,UiMessage detail){
        state=next;expected=cmd;request=payload.clone();requestDetail=detail;attempts=0;transmit();
    }
    private int maxAttempts(){return state==State.PREPARE?1:state==State.VERIFY?5:9;}
    private int ackTimeout(){return state==State.PREPARE?10000:state==State.VERIFY?1000:1200;}
    private void transmit(){
        transmitting=true;early=null;deadline=clock.now()+12000;attempts++;
        int token=++sequence;listener.changed(attempts>1?m("ota_retry",requestDetail,attempts,maxAttempts()):requestDetail);
        listener.log(String.format(Locale.ROOT,"OTA TX cmd=0x%02X page=%d/%d len=%d seq=%d attempt=%d/%d",expected,page,total(),request.length,token,attempts,maxAttempts()));
        if(token!=sequence||!active())return;
        listener.send(expected,request.clone(),()->{
            if(token!=sequence||!active())return;transmitting=false;deadline=clock.now()+ackTimeout();
            if(early!=null){Protocol.Packet packet=early;early=null;onPacket(packet.command,packet.payload);}
        });
    }
    private void retry(UiMessage why){if(attempts>=maxAttempts()){fail(m("ota_limit",why,maxAttempts()));return;}listener.log("OTA RETRY "+why+" page="+page);transmit();}
    public void onPacket(int cmd,byte[] data){
        if(!active()||state==State.BOOT||cmd!=expected)return;
        if(transmitting){if(early==null)early=new Protocol.Packet(cmd,data.clone());return;}
        listener.log(String.format(Locale.ROOT,"OTA RX cmd=0x%02X page=%d/%d len=%d",cmd,page,total(),data.length));
        switch(state){
            case PREPARE:
                if(data.length<1){fail(m("ota_u_invalid"));return;}
                if(data[0]==0)emit(State.START,0x53,modeUid(),m("ota_start"));
                else waitForBoot();
                break;
            case START:
                if(data.length<1||data[0]!=1){fail(m("ota_s_refused"));return;}
                readback=data.length==2&&data[1]==1&&!oemHw20;
                listener.log("OTA S readback="+readback+" policy="+(oemHw20?"confirmed_oem_hw20":"device_reply"));page=0;writePage();break;
            case WRITE:
                if(!((data.length==1&&data[0]==0)||Arrays.equals(data,image.page(page)))){retry(m("ota_w_invalid"));return;}
                if(++page<total())writePage();else if(readback){page=0;readPage();}else end();break;
            case VERIFY:
                // OEM Read() requests index == pageCount once before UpgradeEnd().
                if(page==total()){end();break;}
                if(!Arrays.equals(data,image.page(page))){retry(m("ota_read_mismatch",page));return;}
                if(++page==total())verified=true;readPage();break;
            case END:
                // Original client accepts the E notification; payload semantics are not documented.
                state=State.DONE;sequence++;deadline=0;transmitting=false;request=null;
                listener.changed(verified?m("ota_done_verified"):oemHw20?m("ota_done_hw20"):m("ota_done_no_read"));break;
            default:break;
        }
    }
    private void writePage(){emit(State.WRITE,0x57,image.page(page),m("ota_write_page",page+1,total()));}
    private void readPage(){byte[] b=new byte[16];b[0]=(byte)(page>>>8);b[1]=(byte)page;System.arraycopy(uid,0,b,2,14);emit(State.VERIFY,0x52,b,page==total()?m("ota_read_tail",page):m("ota_read_page",page+1,total()));}
    private void end(){emit(State.END,0x45,modeUid(),m("ota_end"));}
    private void waitForBoot(){state=State.BOOT;sequence++;transmitting=false;early=null;request=null;deadline=clock.now()+30000;listener.changed(m("ota_boot"));}
    public void onDeviceInfo(byte[] info){
        if(!waitingBoot())return;
        if(info.length<18){fail(m("ota_reconnect_short"));return;}
        if(!Arrays.equals(Arrays.copyOfRange(info,4,18),uid)){fail(m("ota_uid_changed"));return;}
        if((info[3]&1)==0)emit(State.START,0x53,modeUid(),m("ota_boot_start"));
    }
    public void tick(){if(!active()||clock.now()<deadline)return;if(transmitting){fail(m("ota_frame_timeout"));return;}if(state==State.PREPARE||state==State.BOOT){fail(m("ota_wait_timeout",state));return;}retry(m("ota_wait_retry",state));}
    public void transportLost(){
        if(!active()||waitingBoot())return;
        // A peripheral ACK can precede Android's final local write callback.
        // These two ACKs deliberately cause a reboot; preserve their evidence.
        Protocol.Packet pending=early;
        if(transmitting&&pending!=null){
            if(state==State.PREPARE&&pending.command==0x55&&pending.payload.length>0&&pending.payload[0]!=0){listener.log("OTA U reboot reply received before disconnect/write callback");waitForBoot();return;}
            if(state==State.END&&pending.command==0x45){sequence++;transmitting=false;early=null;onPacket(pending.command,pending.payload);return;}
        }
        fail(m("ota_connection_lost"));
    }
    public void fail(String why){fail(UiMessage.raw(why));}
    public void fail(UiMessage why){if(!active())return;state=State.FAILED;sequence++;early=null;deadline=0;transmitting=false;request=null;listener.log("OTA STOP "+why);listener.changed(why);}
    public void cancel(String why){cancel(UiMessage.raw(why));}
    public void cancel(UiMessage why){if(!active())return;state=State.CANCELLED;sequence++;early=null;deadline=0;transmitting=false;request=null;listener.log("OTA CANCEL "+why);listener.changed(m("ota_cancelled",why));}
}
