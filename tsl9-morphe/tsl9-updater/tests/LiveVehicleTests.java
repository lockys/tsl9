package dev.tsl9.morphe;
import java.util.*;
public final class LiveVehicleTests {
    private static int checks;private static void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    private static void put(byte[] p,int i,int n){for(int b=0;b<4;b++)p[i+b]=(byte)(n>>>(8*b));}
    public static void main(String[] args){
        long[] now={100};LiveVehicleData live=new LiveVehicleData(()->now[0]);
        check(live.status()==null&&!live.statusFresh(),"no synthetic default vehicle values");
        byte[] basic=new byte[4];put(basic,0,(75<<24)|(3<<16)|512);live.onStatus(basic);LiveVehicleData.Snapshot s=live.status();
        check(s.gear==1&&s.speed==0&&s.gearLabel().equals("P"),"B0 bit fields decoded");check(s.batteryPercent==75&&s.doorBits==3,"SOC and raw door mask");
        check(s.odometerKm==null&&s.frunkOpen==null&&s.voltage==null,"short reply has no fabricated optional fields");basic[0]=33;check(s.speed==0,"snapshot owns decoded values");
        byte[] extended=new byte[33];put(extended,0,(88<<24)|512);put(extended,4,(12345<<6)|34);put(extended,23,650<<21);extended[27]=(byte)130;put(extended,28,6500&4095);live.onStatus(extended);s=live.status();
        check(s.odometerKm==1234.5&&s.frunkOpen&&s.trunkOpen,"OEM odometer km and trunk flags");check(Math.abs(s.cabinC-25)<.001&&s.ambientC==25,"OEM extended temperature formulas");check(Math.abs(s.voltage-((6500&4095)*.002))<.0001,"OEM voltage conversion without assigning an unverified measurement point");
        live.onStatus(new byte[]{0,2,0,0});check(live.status().cabinC==null,"new short reply clears older extended values");now[0]+=2501;check(!live.statusFresh(),"old status explicitly stale");live.onStatus(new byte[3]);check(live.status()==null&&live.statusBytes()==3,"incomplete status invalidates displayed values");
        check(!live.onCan(new byte[1])&&!live.onCan(new byte[11])&&live.canCount()==0,"C0 subscription echo and invalid DLC ignored");
        byte[] frame={1,0x18,0x55,0x66};live.onCan(frame);frame[2]=0;LiveVehicleData.CanFrame f=live.recent(1).get(0);
        check(f.id==0x118&&f.length==2&&f.count==1&&f.averageHz()==null,"CAN identity DLC count; single frame rate unknown");check(f.visibleHex(false)==null&&"55 66".equals(f.visibleHex(true)),"CAN bytes opt-in and copied");
        now[0]+=100;live.onCan(new byte[]{1,0x18,0x77});f=live.recent(1).get(0);check(f.count==2&&f.averageHz()==10&&"77".equals(f.visibleHex(true)),"latest CAN values and mean rate");
        live.onCan(new byte[]{7,(byte)0xe8,0x12});f=live.recent(1).get(0);check(f.diagnosticIdentity()&&f.visibleHex(true)==null,"diagnostic identity payload stays redacted");
        live.clearCan();for(int i=0;i<300;i++)live.onCan(new byte[]{(byte)(i>>>8),(byte)i,1});check(live.idCount()==256&&live.canCount()==300,"bounded map retains total received count");check(live.recent(50).size()==50&&live.recent(1).get(0).id==299,"latest 50 display order");
        live.clear();check(live.canCount()==0&&live.idCount()==0&&live.status()==null&&live.statusBytes()==-1,"disconnect clears live source data");
        live.onStatus(new byte[4]);check(live.status().gearLabel().contains("0")&&!live.status().gearLabel().equals("P"),"unknown module gear displayed with raw code instead of relabeling P");
        System.out.println("LiveVehicleTests passed: "+checks+" synthetic assertions; no hardware meanings inferred from CAN IDs.");
    }
}
