package dev.tsl9.morphe;
import java.util.*;
/** User-requested direct body control: no profile checkbox or gear/speed dependency. */
public final class DirectControlTests {
    static int checks;static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static class Rig implements VehicleControls.Listener {
        long now;final List<Integer> actions=new ArrayList<>();Runnable written;VehicleControls v=new VehicleControls(this,()->now);
        public void send(int cmd,byte[] p,Runnable done){if(cmd==0xa7)actions.add(p[0]&255);written=done;}
        public void changed(UiMessage value){}public void log(String text){}
        void ready(){byte[] info=new byte[18];info[3]=1;v.onInfo(info);v.setAvailable(true);}
        void drain(){Runnable r=written;written=null;if(r!=null)r.run();}
    }
    public static void main(String[] args){
        Rig r=new Rig();r.ready();check(r.v.canOperate(),"connected normal module permits direct control without checkbox, UID or telemetry");
        check(r.v.perform(VehicleControls.Action.LOCK)&&r.actions.equals(Arrays.asList(22)),"direct lock sends original A7 code22");r.drain();
        check(r.v.perform(VehicleControls.Action.UNLOCK)&&r.actions.get(1)==23,"direct unlock sends code23");r.drain();
        r.v.onTelemetry(new byte[4]);check(r.v.gear()==0&&r.v.canOperate(),"unknown gear stays unknown but does not block direct body controls");
        r.v.onTelemetry(new byte[]{1,8,0,0});check(r.v.canOperate(),"gear and speed are monitoring-only for direct body controls");r.now=10000;check(r.v.canOperate(),"stale telemetry does not gate direct body controls");
        check(r.v.beginSeat(VehicleControls.Action.DRIVER_LEFT)&&r.actions.get(2)==26,"seat starts without status confirmation");r.drain();r.now+=1000;r.v.tick();check(r.actions.get(3)==16&&r.v.active(),"one second requests stop and waits for local drain");r.drain();
        r.v.beginSeat(VehicleControls.Action.PASSENGER_UP);r.drain();r.v.onTelemetry(new byte[0]);r.v.tick();check(r.v.moving(),"missing telemetry does not cancel a manual hold before timeout");r.v.stopSeat();check(r.actions.get(r.actions.size()-1)==16,"release still sends stop");r.drain();
        r.v.setAvailable(false);check(!r.v.perform(VehicleControls.Action.LOCK),"transport/auth/capture/OTA unavailable still blocks actions");
        r.ready();byte[] boot=new byte[18];r.v.onInfo(boot);check(!r.v.beginSeat(VehicleControls.Action.DRIVER_UP),"BOOT mode still blocks actuation");
        System.out.println("DirectControlTests passed: "+checks+" synthetic assertions; no hardware actuation.");
    }
}
