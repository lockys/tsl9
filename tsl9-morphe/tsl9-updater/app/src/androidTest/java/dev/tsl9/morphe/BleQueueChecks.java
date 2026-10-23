package dev.tsl9.morphe;
import java.lang.reflect.*;
import java.util.*;

/** Runs the actual BleClient pending-write pruner while its transport remains closed. */
final class BleQueueChecks {
    private final MainActivity activity;private int checks;
    BleQueueChecks(MainActivity a){activity=a;}
    private Object get(Object target,String field)throws Exception{Field f=target.getClass().getDeclaredField(field);f.setAccessible(true);return f.get(target);}
    private void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    @SuppressWarnings("unchecked") int run()throws Exception{
        BleClient client=(BleClient)get(activity,"ble");ArrayDeque<Object> queue=(ArrayDeque<Object>)get(client,"queue");check(!client.ready()&&queue.isEmpty(),"queue test starts with closed transport");
        Class<?> write=Class.forName("dev.tsl9.morphe.BleClient$Write");Constructor<?> ctor=write.getDeclaredConstructor(int.class,byte[].class,Runnable.class,VehicleControls.WriteGuard.class);ctor.setAccessible(true);Method next=BleClient.class.getDeclaredMethod("writeNext");next.setAccessible(true);
        long[] now={0};VehicleControls.Listener wire=new VehicleControls.Listener(){
            public void send(int cmd,byte[] p,Runnable done){sendGuarded(cmd,p,done,null);}
            public void sendGuarded(int cmd,byte[] p,Runnable done,VehicleControls.WriteGuard guard){try{queue.add(ctor.newInstance(cmd,Protocol.encode(cmd,p),done,guard));}catch(Exception e){throw new RuntimeException(e);}}
            public void changed(UiMessage value){}public void log(String text){}
        };
        VehicleControls v=new VehicleControls(wire,()->now[0]);byte[] info=new byte[18];info[3]=1;v.onInfo(info);v.setAvailable(true);
        try{
            v.perform(VehicleControls.Action.LOCK);v.cancel();wire.send(0xa0,new byte[0],()->{});next.invoke(client);check(queue.size()==1&&(Integer)get(queue.peek(),"cmd")==0xa0,"real BLE queue drops canceled lock while preserving read");queue.clear();
            v.beginSeat(VehicleControls.Action.DRIVER_LEFT);v.stopSeat();next.invoke(client);check(queue.size()==1&&Arrays.equals((byte[])get(queue.peek(),"frame"),Protocol.encode(0xa7,new byte[]{16})),"real BLE queue removes released start but retains stop frame");queue.clear();v.transportLost();v.onInfo(info);v.setAvailable(true);
            v.perform(VehicleControls.Action.UNLOCK);Object valid=queue.peek();next.invoke(client);check(queue.size()==1&&queue.peek()==valid,"valid pending command is retained without touching GATT");queue.clear();v.cancel();
            v.beginSeat(VehicleControls.Action.DRIVER_UP);now[0]=1001;next.invoke(client);check(queue.isEmpty(),"real BLE queue rejects late seat start before first chunk");v.tick();next.invoke(client);check(queue.size()==1&&get(queue.peek(),"guard")==null,"timed stop remains unconditional");
        }finally{queue.clear();}
        return checks;
    }
}
