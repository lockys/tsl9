package dev.tsl9.morphe;
import java.util.*;
import static dev.tsl9.morphe.UiMessage.m;
/** Bounded OEM body controls. No raw CAN API, motion replay, or automatic actuation retries. */
public final class VehicleControls {
    public interface WriteGuard {boolean allow();}
    public interface Listener {
        void send(int command,byte[] payload,Runnable written);void changed(UiMessage detail);void log(String text);
        default void sendGuarded(int command,byte[] payload,Runnable written,WriteGuard guard){if(guard.allow())send(command,payload,written);}
    }
    public enum Action {
        LOCK(22,false),UNLOCK(23,false),
        DRIVER_LEFT(26,true),DRIVER_RIGHT(27,true),DRIVER_UP(28,true),DRIVER_DOWN(29,true),
        PASSENGER_LEFT(12,true),PASSENGER_RIGHT(13,true),PASSENGER_UP(14,true),PASSENGER_DOWN(15,true);
        public final int code;public final boolean seat;Action(int code,boolean seat){this.code=code;this.seat=seat;}
    }
    private enum Phase {IDLE,ONESHOT,MOVING,STOPPING,CONFIG_WRITE,CONFIG_CONFIRM}
    public enum Gate {READY,UNAVAILABLE,INFO,BOOT,ACTIVE}
    public enum LightGate {READY,CONTROL,CONFIG_LENGTH,IDENTITY,HARDWARE,STALE}
    private final Listener listener;private final OtaSession.Clock clock;
    private Phase phase=Phase.IDLE;private boolean available,hasTelemetry,lightVerified;private int identityEpoch;
    private long telemetryAt,infoAt,deadline;private int speed,gear,sequence,telemetryBytes=-1;private byte[] info,expectedConfig;
    public VehicleControls(Listener l,OtaSession.Clock c){listener=l;clock=c;}
    public void setAvailable(boolean value){available=value;}
    public int identityEpoch(){return identityEpoch;}
    public boolean active(){return phase!=Phase.IDLE;}
    public boolean moving(){return phase==Phase.MOVING;}
    public boolean lightReadbackConfirmed(){return lightVerified;}
    public int speed(){return speed;}public int gear(){return gear;}
    public boolean telemetryFresh(){long age=clock.now()-telemetryAt;return hasTelemetry&&age>=0&&age<=2500;}
    public int telemetryBytes(){return telemetryBytes;}
    private Gate eligibilityGate(){
        if(!available)return Gate.UNAVAILABLE;if(info==null||info.length<18)return Gate.INFO;if((info[3]&1)==0)return Gate.BOOT;return Gate.READY;
    }
    public Gate gate(){return active()?Gate.ACTIVE:eligibilityGate();}
    private boolean eligible(){return eligibilityGate()==Gate.READY;}
    public boolean canOperate(){return !active()&&eligible();}
    public void onTelemetry(byte[] data){
        telemetryBytes=data==null?0:data.length;
        // Both fields occupy the first complete LE32. Remaining gauge fields are optional here.
        if(data==null||data.length<4){hasTelemetry=false;return;}
        int word=(data[0]&255)|(data[1]&255)<<8|(data[2]&255)<<16|(data[3]&255)<<24;
        speed=word&511;gear=word>>>9&7;telemetryAt=clock.now();hasTelemetry=true;
    }
    /** Accepts A0 device information only; A3 echoes are not readback evidence. */
    public void onInfo(byte[] data){
        if(data==null||data.length<18){info=null;identityEpoch++;lightVerified=false;tick();return;}
        boolean changed=info==null;
        if(info!=null){for(int i=0;i<18;i++)if(i!=3&&info[i]!=data[i]){changed=true;break;}}
        if(changed){identityEpoch++;lightVerified=false;}
        info=data.clone();infoAt=clock.now();
        if(changed&&moving())stopSeat();
        if(changed&&phase==Phase.ONESHOT)finish(m("car_action_unconfirmed"));
        tick();
        if(phase==Phase.CONFIG_CONFIRM&&configMatches(data)){lightVerified=true;finish(m("car_light_verified"));}
    }
    public LightGate lightingGate(){
        if(!canOperate())return LightGate.CONTROL;if(info.length!=76)return LightGate.CONFIG_LENGTH;
        boolean uid=false;for(int i=4;i<18;i++)uid|=info[i]!=0;if(!uid)return LightGate.IDENTITY;
        int hw=info[0]&255;if(hw!=0&&hw!=3&&hw!=5&&hw!=6&&hw!=8&&hw!=19)return LightGate.HARDWARE;
        long age=clock.now()-infoAt;return age<0||age>10000?LightGate.STALE:LightGate.READY;
    }
    public boolean lightingAvailable(){return lightingGate()==LightGate.READY;}
    public boolean blinkHighBeam(){return info!=null&&info.length==76&&(info[30]&0x40)!=0;}
    public boolean perform(Action action){
        if(action==null||action.seat||!canOperate())return false;
        phase=Phase.ONESHOT;deadline=clock.now()+8000;int token=++sequence;
        listener.changed(m("car_sending"));listener.log("CAR DIRECT action="+action+" code="+action.code+" telemetryRequired=false checkboxRequired=false retry=none");
        if(token!=sequence||phase!=Phase.ONESHOT)return false;
        listener.sendGuarded(0xa7,new byte[]{(byte)action.code},()->{if(token==sequence&&phase==Phase.ONESHOT){listener.log("CAR DIRECT frame_drained action="+action+" code="+action.code+" vehicleExecution=unconfirmed");finish(m(action==Action.UNLOCK?"car_unlock_sent":"car_sent_unconfirmed"));}},()->token==sequence&&phase==Phase.ONESHOT&&eligible()&&clock.now()<deadline);return true;
    }
    public void onControlReply(byte[] payload){
        StringBuilder raw=new StringBuilder();if(payload!=null)for(int i=0;i<Math.min(2,payload.length);i++){if(i>0)raw.append(' ');raw.append(String.format(Locale.ROOT,"%02X",payload[i]&255));}
        listener.log("CAR OEM A7 reply len="+(payload==null?0:payload.length)+" firstBytes="+raw+" interpretation=raw-only vehicleExecution=unconfirmed");
    }
    public boolean beginSeat(Action action){
        if(action==null||!action.seat||!canOperate())return false;
        phase=Phase.MOVING;deadline=clock.now()+1000;int token=++sequence;
        listener.changed(m("car_seat_moving"));listener.log("CAR SEAT start action="+action+" code="+action.code+" maxHoldMs=1000");
        if(token!=sequence||phase!=Phase.MOVING)return false;
        listener.sendGuarded(0xa7,new byte[]{(byte)action.code},()->{if(token==sequence)listener.log("CAR SEAT start frame drained");},()->token==sequence&&phase==Phase.MOVING&&eligible()&&clock.now()<deadline);return true;
    }
    public void stopSeat(){
        if(phase!=Phase.MOVING)return;
        phase=Phase.STOPPING;deadline=clock.now()+8000;int token=++sequence;
        listener.changed(m("car_seat_stopping"));listener.log("CAR SEAT stop code=16");
        listener.send(0xa7,new byte[]{16},()->{if(token==sequence&&phase==Phase.STOPPING)finish(m("car_stop_sent"));});
    }
    public boolean setBlinkHighBeam(boolean enabled,boolean layoutConfirmed){
        if(!layoutConfirmed||!lightingAvailable())return false;
        lightVerified=false;expectedConfig=info.clone();Arrays.fill(expectedConfig,18,24,(byte)0);
        expectedConfig[30]=(byte)((expectedConfig[30]&~0x40)|(enabled?0x40:0));
        phase=Phase.CONFIG_WRITE;deadline=clock.now()+8000;int token=++sequence;
        listener.changed(m("car_light_writing"));listener.log("CAR CONFIG A3 blinkHighBeam="+enabled+" bytes=76 payload=redacted retry=none");
        if(token!=sequence||phase!=Phase.CONFIG_WRITE)return false;
        listener.send(0xa3,expectedConfig.clone(),()->{
            if(token!=sequence||phase!=Phase.CONFIG_WRITE)return;
            phase=Phase.CONFIG_CONFIRM;deadline=clock.now()+3000;listener.changed(m("car_light_readback"));
            if(token==sequence&&phase==Phase.CONFIG_CONFIRM)listener.send(0xa0,new byte[0],()->{});
        });return true;
    }
    private boolean configMatches(byte[] data){
        if(expectedConfig==null||data.length!=expectedConfig.length)return false;
        for(int i=0;i<data.length;i++)if((i<18||i>=24)&&data[i]!=expectedConfig[i])return false;
        return true;
    }
    public void tick(){
        if(phase==Phase.MOVING){if(clock.now()>=deadline||!eligible())stopSeat();return;}
        if(phase==Phase.ONESHOT&&!eligible()){finish(m("car_action_unconfirmed"));return;}
        if(active()&&clock.now()>=deadline)finish(m(phase==Phase.STOPPING?"car_stop_unconfirmed":phase==Phase.CONFIG_CONFIRM||phase==Phase.CONFIG_WRITE?"car_light_unconfirmed":"car_action_unconfirmed"));
    }
    public void cancel(){
        if(phase==Phase.MOVING){stopSeat();return;}
        if(phase==Phase.STOPPING)return;
        if(active())finish(m("car_action_unconfirmed"));
    }
    public void transportLost(){available=false;hasTelemetry=false;telemetryBytes=-1;identityEpoch++;info=null;expectedConfig=null;lightVerified=false;if(active())finish(m("car_connection_lost"));else sequence++;}
    private void finish(UiMessage detail){phase=Phase.IDLE;sequence++;expectedConfig=null;listener.changed(detail);}
}
