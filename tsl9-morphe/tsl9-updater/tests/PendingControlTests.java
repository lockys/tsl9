package dev.tsl9.morphe;
import java.util.*;
public final class PendingControlTests {
    static int checks;static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static final class Job {int code;Runnable done;VehicleControls.WriteGuard guard;Job(int c,Runnable r,VehicleControls.WriteGuard g){code=c;done=r;guard=g;}}
    static final class Wire implements VehicleControls.Listener {
        long now;VehicleControls v=new VehicleControls(this,()->now);ArrayDeque<Job> pending=new ArrayDeque<>();ArrayList<Integer> sent=new ArrayList<>();
        public void send(int cmd,byte[] p,Runnable done){pending.add(new Job(p[0]&255,done,null));}
        public void sendGuarded(int cmd,byte[] p,Runnable done,VehicleControls.WriteGuard guard){pending.add(new Job(p[0]&255,done,guard));}
        public void changed(UiMessage m){}public void log(String text){}
        void ready(){byte[] info=new byte[18];info[3]=1;v.onInfo(info);v.setAvailable(true);}
        void drain(){while(!pending.isEmpty()){Job j=pending.poll();if(j.guard==null||j.guard.allow()){sent.add(j.code);j.done.run();}}}
    }
    public static void main(String[] args){
        Wire w=new Wire();w.ready();w.v.perform(VehicleControls.Action.LOCK);w.v.setAvailable(false);w.v.cancel();w.drain();check(w.sent.isEmpty(),"auth or foreground revocation drops queued lock before transmission");
        w.ready();w.v.beginSeat(VehicleControls.Action.DRIVER_LEFT);w.v.stopSeat();w.drain();check(w.sent.equals(Arrays.asList(16)),"release before poll drain cancels queued start but preserves stop");
        w.sent.clear();w.ready();w.v.beginSeat(VehicleControls.Action.PASSENGER_UP);w.v.onInfo(new byte[18]);w.drain();check(w.sent.equals(Arrays.asList(16)),"BOOT transition drops queued seat start");
        w.sent.clear();w.ready();w.v.beginSeat(VehicleControls.Action.DRIVER_UP);w.now+=1001;w.drain();check(w.sent.isEmpty(),"late queued seat start cannot pass software hold deadline");w.v.tick();w.drain();check(w.sent.equals(Arrays.asList(16)),"expired hold still sends stop");
        w.sent.clear();w.ready();w.v.perform(VehicleControls.Action.UNLOCK);w.drain();check(w.sent.equals(Arrays.asList(23)),"valid direct command drains normally without telemetry");
        w.sent.clear();w.ready();w.v.perform(VehicleControls.Action.LOCK);w.v.cancel();w.v.perform(VehicleControls.Action.LOCK);w.drain();check(w.sent.equals(Arrays.asList(22)),"generation separates canceled lock from next lock");
        w.sent.clear();w.ready();w.v.perform(VehicleControls.Action.LOCK);byte[] other=new byte[18];other[3]=1;other[4]=1;w.v.onInfo(other);w.drain();check(w.sent.isEmpty()&&!w.v.active(),"new module identity cancels queued lock before transmission");
        System.out.println("PendingControlTests passed: "+checks+" queue-order assertions; no BLE.");
    }
}
