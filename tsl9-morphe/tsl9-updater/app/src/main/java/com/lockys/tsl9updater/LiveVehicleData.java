package com.lockys.tsl9updater;

import java.util.*;

/** Read-only received-data model. Never produces CAN or actuation commands. */
public final class LiveVehicleData {
    public static final int MAX_IDS=256;
    private final OtaSession.Clock clock;
    private final LinkedHashMap<Integer,CanFrame> frames=new LinkedHashMap<>();
    private long canCount;private Snapshot status;private int statusBytes=-1;
    public LiveVehicleData(OtaSession.Clock clock){this.clock=clock;}
    public static final class Snapshot {
        public final long at;public final int bytes,speed,gear,doorBits,lightBits;
        public final Integer batteryPercent;public final Boolean frunkOpen,trunkOpen;
        public final Double odometerKm,cabinC,ambientC,voltage;
        private Snapshot(byte[] p,long now){
            at=now;bytes=p.length;int w=le32(p,0);speed=w&511;gear=w>>>9&7;doorBits=w>>>16&15;
            lightBits=(w>>>20&15)|(w>>>27&16)|(p.length>=5?(p[4]&16)<<1:0);
            int soc=w>>>24&127;batteryPercent=soc<=100?soc:null;
            if(p.length>=8){int w2=le32(p,4);frunkOpen=(w2&2)!=0;trunkOpen=(w2&32)!=0;odometerKm=(w2>>>6)/10.0;}else{frunkOpen=trunkOpen=null;odometerKm=null;}
            // OEM treats the extended block as present only at 33 bytes or longer.
            if(p.length>=33){int climate=le32(p,23);cabinC=(climate>>>21&2047)*0.1-40;ambientC=(p[27]&255)*0.5-40;voltage=(le32(p,28)&4095)*0.002;}else{cabinC=ambientC=voltage=null;}
        }
        public String gearLabel(){return gear==1?"P":gear==2?"R":gear==3?"N":gear==4?"D":"? ("+gear+")";}
    }
    public static final class CanFrame {
        public final int id,length;public final long firstAt,lastAt,count;private final byte[] data;
        private CanFrame(int id,byte[] bytes,long first,long last,long count){this.id=id;data=bytes.clone();length=bytes.length;firstAt=first;lastAt=last;this.count=count;}
        public boolean diagnosticIdentity(){return id==0x7df||(id>=0x7e0&&id<=0x7ef);}
        public Double averageHz(){return count>1&&lastAt>firstAt?(count-1)*1000.0/(lastAt-firstAt):null;}
        public String visibleHex(boolean optIn){if(!optIn||diagnosticIdentity())return null;StringBuilder out=new StringBuilder();for(byte b:data){if(out.length()>0)out.append(' ');out.append(String.format(Locale.ROOT,"%02X",b&255));}return out.toString();}
    }
    private static int le32(byte[] p,int offset){return(p[offset]&255)|(p[offset+1]&255)<<8|(p[offset+2]&255)<<16|(p[offset+3]&255)<<24;}
    public void onStatus(byte[] p){statusBytes=p==null?0:p.length;status=p!=null&&p.length>=4?new Snapshot(p,clock.now()):null;}
    public Snapshot status(){return status;}public int statusBytes(){return statusBytes;}
    public boolean statusFresh(){return status!=null&&ageMs(status.at)<=2500;}
    public long ageMs(long at){return Math.max(0,clock.now()-at);}
    public boolean onCan(byte[] p){
        if(p==null||p.length<2||p.length>10)return false;
        int id=(p[0]&255)<<8|(p[1]&255);long now=clock.now();CanFrame old=frames.remove(id);byte[] data=Arrays.copyOfRange(p,2,p.length);
        frames.put(id,new CanFrame(id,data,old==null?now:old.firstAt,now,old==null?1:old.count+1));canCount++;
        if(frames.size()>MAX_IDS)frames.remove(frames.keySet().iterator().next());return true;
    }
    public long canCount(){return canCount;}public int idCount(){return frames.size();}
    public List<CanFrame> recent(int limit){ArrayList<CanFrame> list=new ArrayList<>(frames.values());Collections.reverse(list);return Collections.unmodifiableList(new ArrayList<>(list.subList(0,Math.min(list.size(),Math.max(0,limit)))));}
    public void clearCan(){frames.clear();canCount=0;}
    public void clear(){clearCan();status=null;statusBytes=-1;}
}
