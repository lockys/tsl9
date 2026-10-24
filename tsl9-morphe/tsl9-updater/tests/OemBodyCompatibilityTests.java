package dev.tsl9.morphe;
import java.nio.file.*;
import java.util.*;
/** Differential wire comparison against actual pinned OEM JS methods; synthetic only. */
public final class OemBodyCompatibilityTests {
    private static int checks;
    private static void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    private static byte[] hex(String value){byte[] bytes=new byte[value.length()/2];for(int i=0;i<bytes.length;i++)bytes[i]=(byte)Integer.parseInt(value.substring(i*2,i*2+2),16);return bytes;}
    private static final class Rig implements VehicleControls.Listener {
        int command;byte[] payload;Runnable written;final VehicleControls car=new VehicleControls(this,()->0);
        public void send(int command,byte[] payload,Runnable written){this.command=command;this.payload=payload.clone();this.written=written;}
        public void changed(UiMessage detail){}public void log(String line){}
        void ready(byte[] info){car.setAvailable(true);car.onInfo(info);}
    }
    public static void main(String[] args)throws Exception{
        check(args.length==1,"Pass the offline OEM body trace TSV");
        List<String> lines=Files.readAllLines(Paths.get(args[0]));check(lines.size()==14,"all OEM reference scenarios present");
        for(String line:lines){String[] fields=line.split("\t");String name=fields[0];int command=Integer.parseInt(fields[1]);byte[] expected=hex(fields[2]),frame=hex(fields[3]);
            Rig rig=new Rig();byte[] info=new byte[76];info[0]=6;info[3]=1;info[4]=7;
            if(name.startsWith("light_")){String[] parts=name.split("_");int hw=Integer.parseInt(parts[1]);boolean enabled=parts[2].equals("1");
                info=hex(fields[4]);check(info.length==76&&(info[0]&255)==hw,"canonical OEM input snapshot");
                rig.ready(info);check(!rig.car.telemetryFresh(),"fixture has no B0");check(rig.car.setBlinkHighBeam(enabled,true),"OEM setting must remain available without B0: "+name);
            }else{rig.ready(info);if(name.equals("driver_left")||name.equals("seat_stop")){rig.car.beginSeat(VehicleControls.Action.DRIVER_LEFT);if(name.equals("seat_stop"))rig.car.stopSeat();}
                else rig.car.perform(name.equals("unlock")?VehicleControls.Action.UNLOCK:VehicleControls.Action.LOCK);}
            check(rig.command==command,"OEM command "+name);check(Arrays.equals(rig.payload,expected),"OEM payload "+name);check(Arrays.equals(Protocol.encode(rig.command,rig.payload),frame),"complete OEM BLE frame "+name);
        }
        System.out.println("OemBodyCompatibilityTests passed: "+checks+" synthetic differential assertions; no hardware.");
    }
}
