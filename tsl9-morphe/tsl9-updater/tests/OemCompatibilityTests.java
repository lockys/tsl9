package dev.tsl9.morphe;
import java.util.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.lang.reflect.*;

/** Compare wire payloads against the original APK's actual JS, not a second hand-written oracle. */
public final class OemCompatibilityTests {
    static int checks;static void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    static String hash(byte[] b)throws Exception{StringBuilder s=new StringBuilder();for(byte v:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format(Locale.ROOT,"%02x",v&255));return s.toString();}
    static byte[] uid(){byte[] u=new byte[14];Arrays.fill(u,(byte)7);return u;}
    static final class Rig implements OtaSession.Listener{
        long now;int cmd;byte[] data;Runnable sent;final List<String> trace=new ArrayList<>();final OtaSession ota=new OtaSession(this,()->now);
        public void changed(UiMessage x){}public void log(String x){}
        public void send(int c,byte[] b,Runnable done){cmd=c;data=b.clone();sent=done;try{trace.add(c+"\t"+b.length+"\t"+hash(b));}catch(Exception e){throw new RuntimeException(e);}}
        void drain(){if(sent!=null){Runnable r=sent;sent=null;r.run();}}
        void reply(int c,byte[] b){drain();ota.onPacket(c,b);}
        void start(FirmwareImage image,boolean hw20)throws Exception{
            if(hw20){try{OtaSession.class.getMethod("start",FirmwareImage.class,byte[].class,boolean.class).invoke(ota,image,uid(),true);return;}catch(NoSuchMethodException absent){/* Baseline has no profile; compare its behavior too. */}}
            ota.start(image,uid());
        }
        void timeout(int interval){drain();now+=interval;ota.tick();}
    }
    public static void main(String[] args)throws Exception{
        Map<String,List<String>> expected=new LinkedHashMap<>();Map<String,String> states=new HashMap<>();
        for(String line:Files.readAllLines(Paths.get(args[0]))){String[] a=line.split("\t");if(a[0].equals("#state")){states.put(a[1],a[2]);expected.put(a[1],new ArrayList<>());}else expected.get(a[0]).add(a[1]+"\t"+a[2]+"\t"+a[3]);}
        for(String name:expected.keySet()){
            byte[] raw=name.equals("userRaw")?Files.readAllBytes(Paths.get(args[1])):new byte[name.equals("readback")?2048:1024];if(!name.equals("userRaw"))for(int i=0;i<raw.length;i++)raw[i]=(byte)(i*13);FirmwareImage image=FirmwareImage.parse(raw,FirmwareImage.Format.RAW);Rig r=new Rig();r.start(image,name.equals("hw20"));
            r.reply(0x55,new byte[]{(byte)(name.equals("boot")?1:name.equals("nonzeroU")?2:0)});
            if(r.ota.waitingBoot()){byte[] info=new byte[18];System.arraycopy(uid(),0,info,4,14);r.ota.onDeviceInfo(info);}
            if(name.equals("startTimeout")){for(int i=0;i<12&&r.ota.active();i++)r.timeout(1200);}
            else{
                boolean read=name.equals("readback")||name.equals("readMismatch")||name.equals("hw20");r.reply(0x53,name.equals("extraS")?new byte[]{1,1,0}:read?new byte[]{1,1}:new byte[]{1});
                if(name.equals("writeTimeout")){for(int i=0;i<12&&r.ota.active();i++)r.timeout(1200);}
                else{
                    if(name.equals("writeBad")){r.reply(0x57,new byte[]{1});byte[] corrupt=image.page(0);corrupt[10]^=1;r.reply(0x57,corrupt);}
                    for(int i=0;i<image.pageCount();i++)r.reply(0x57,i==1?image.page(i):new byte[]{0});
                    if(name.equals("readMismatch")){byte[] corrupt=image.page(0);corrupt[10]^=1;for(int i=0;i<5;i++)r.reply(0x52,corrupt);}
                    else{
                        if(name.equals("readback")){for(int i=0;i<image.pageCount();i++)r.reply(0x52,image.page(i));r.reply(0x52,new byte[0]);}
                        if(name.equals("endTimeout")){for(int i=0;i<12&&r.ota.active();i++)r.timeout(1200);}else r.reply(0x45,new byte[0]);
                    }
                }
            }
            check(r.trace.equals(expected.get(name)),"OEM wire sequence mismatch: "+name+" expected="+expected.get(name).size()+" actual="+r.trace.size());
            check(states.get(name).equals("failed")?r.ota.failed():r.ota.success(),"OEM terminal state mismatch: "+name);
        }
        byte[] raw=new byte[1024];FirmwareImage image=FirmwareImage.parse(raw,FirmwareImage.Format.RAW);Rig slow=new Rig();slow.start(image,false);slow.reply(0x55,new byte[]{0});slow.reply(0x53,new byte[]{1});int before=slow.trace.size();slow.now=1200;slow.ota.tick();check(slow.trace.size()==before,"do not overlap slow GATT frame with protocol retry");slow.drain();slow.now+=1199;slow.ota.tick();check(slow.trace.size()==before,"OEM W timer waits full 1200ms after drain");slow.now++;slow.ota.tick();check(slow.trace.size()==before+1,"OEM W retransmits same page at 1200ms");
        Rig silent=new Rig();silent.start(image,false);silent.reply(0x55,new byte[]{0});silent.reply(0x53,new byte[]{1,1});silent.reply(0x57,new byte[]{0});for(int i=0;i<5;i++)silent.timeout(1000);check(silent.ota.failed(),"silent R has bounded retry budget instead of original infinite poll");
        Rig cancel=new Rig();cancel.start(image,false);cancel.reply(0x55,new byte[]{0});int n=cancel.trace.size();cancel.ota.cancel("synthetic");cancel.drain();cancel.now=60000;cancel.ota.tick();cancel.ota.onPacket(0x53,new byte[]{1});check(cancel.trace.size()==n,"cancel prevents retry and late callback sends");
        System.out.println("OemCompatibilityTests passed: "+checks+" assertions / "+expected.size()+" original-JS differential scenarios; synthetic only.");
    }
}
