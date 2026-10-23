package dev.tsl9.morphe;
import java.util.*;
public final class VehicleControlsTests {
    static int checks;static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    static class Rig implements VehicleControls.Listener {
        long now;int cmd;byte[] data;Runnable done;List<Integer> actions=new ArrayList<>();
        VehicleControls v=new VehicleControls(this,()->now);
        public void send(int c,byte[] p,Runnable callback){cmd=c;data=p.clone();done=callback;if(c==0xa7)actions.add(p[0]&255);}
        public void changed(UiMessage m){}public void log(String s){}
        void written(){Runnable r=done;done=null;if(r!=null)r.run();}
        void park(){v.onTelemetry(new byte[]{0,2,0,0});}
        byte[] info(){byte[] b=new byte[76];b[1]=0x32;b[2]=0x41;b[3]=1;for(int i=4;i<18;i++)b[i]=(byte)(i+7);for(int i=18;i<76;i++)b[i]=(byte)(i*3);b[30]&=~0x40;return b;}
        void ready(){v.setAvailable(true);v.onInfo(info());park();}
    }
    public static void main(String[] args){
        Rig r=new Rig();check(!r.v.canOperate(),"disconnected default blocks control");r.v.setAvailable(true);check(!r.v.canOperate(),"normal module info still required");r.ready();
        check(r.v.perform(VehicleControls.Action.LOCK)&&r.cmd==0xa7&&r.data[0]==22,"lock OEM wire command");check(!r.v.perform(VehicleControls.Action.UNLOCK),"no overlapping actions");r.written();check(r.v.perform(VehicleControls.Action.UNLOCK)&&r.data[0]==23,"unlock OEM wire command");r.written();
        check(r.v.beginSeat(VehicleControls.Action.DRIVER_UP)&&r.data[0]==28,"OEM driver up");r.v.stopSeat();check(r.data[0]==16&&r.v.active(),"stop waits for local drain");int n=r.actions.size();r.v.stopSeat();check(r.actions.size()==n,"duplicate release sends only one stop");r.written();check(!r.v.active(),"drained stop releases channel");
        r.v.beginSeat(VehicleControls.Action.PASSENGER_LEFT);check(r.data[0]==12,"OEM passenger left");r.written();r.now+=1001;r.v.tick();check(r.data[0]==16,"hold deadline requests stop");r.written();
        r.v.beginSeat(VehicleControls.Action.DRIVER_DOWN);r.written();r.v.setAvailable(false);r.v.tick();check(r.data[0]==16,"transport/auth/lifecycle unavailability requests stop");r.v.transportLost();check(!r.v.active()&&!r.v.canOperate(),"transport loss clears control state");
        r.ready();r.v.beginSeat(VehicleControls.Action.DRIVER_RIGHT);r.written();byte[] other=r.info();other[4]^=1;int before=r.v.identityEpoch();r.v.onInfo(other);check(r.data[0]==16&&r.v.identityEpoch()>before,"module identity change requests stop");r.written();
        r.ready();r.v.beginSeat(VehicleControls.Action.DRIVER_UP);r.written();r.v.onInfo(new byte[2]);check(!r.v.canOperate()&&r.data[0]==16,"short A0 invalidates mode and requests stop");r.written();
        r.ready();byte[] baseline=r.info();check(!r.v.setBlinkHighBeam(true,false),"lighting layout still explicitly confirmed");r.v.onTelemetry(new byte[4]);check(!r.v.lightingAvailable()&&r.v.canOperate(),"unknown gear only blocks lighting configuration, not direct body control");r.park();
        check(r.v.setBlinkHighBeam(true,true)&&r.cmd==0xa3&&r.data.length==76,"OEM full A3 configuration");byte[] expected=baseline.clone();Arrays.fill(expected,18,24,(byte)0);expected[30]|=0x40;check(Arrays.equals(r.data,expected),"lighting bit mask preserves unrelated configuration");check(!r.v.perform(VehicleControls.Action.LOCK),"configuration excludes direct action");r.written();check(r.cmd==0xa0&&r.v.active(),"A0 query follows config write");r.v.onInfo(expected);check(r.v.lightReadbackConfirmed()&&!r.v.active(),"matching A0 confirms setting");
        r.ready();r.v.setBlinkHighBeam(true,true);r.written();byte[] wrong=expected.clone();wrong[4]^=1;r.v.onInfo(wrong);check(!r.v.lightReadbackConfirmed(),"wrong UID cannot confirm configuration");r.now+=3001;r.v.tick();check(!r.v.active(),"configuration wait is bounded");
        r.ready();r.v.perform(VehicleControls.Action.LOCK);int sent=r.actions.size();r.now+=8001;r.v.tick();check(!r.v.active()&&r.actions.size()==sent,"timed-out direct action is not retried");
        System.out.println("VehicleControlsTests passed: "+checks+" synthetic assertions; no car actuation.");
    }
}
