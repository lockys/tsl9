package dev.tsl9.morphe;
import android.widget.*;
import java.lang.reflect.*;
/** Tests the real Activity packet bridge and dashboard with synthetic packets; no BLE. */
final class LiveUiChecks {
    private final MainActivity a;private int checks;
    LiveUiChecks(MainActivity a){this.a=a;}
    private Object get(Object target,String name)throws Exception{Field f=target.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(target);}
    private void call(Object target,String name)throws Exception{Method m=target.getClass().getDeclaredMethod(name);m.setAccessible(true);m.invoke(target);}
    private void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    int run()throws Exception{
        TabHost tabs=(TabHost)get(a,"tabs");LivePanel panel=(LivePanel)get(a,"livePanel");LiveVehicleData data=(LiveVehicleData)get(a,"liveData");
        try{
            tabs.setCurrentTabByTag("live");check(tabs.getTabWidget().getTabCount()==3&&tabs.getCurrentTabTag().equals("live"),"third read-only live tab opens");
            check(!((Button)get(panel,"query")).isEnabled()&&!((Button)get(panel,"start")).isEnabled(),"disconnected live queries and subscription disabled");
            check(((TextView)get(panel,"gearValue")).getText().toString().equals("—"),"disconnected metric never uses mock gear");
            CheckBox bytes=(CheckBox)get(panel,"showBytes");check(!bytes.isChecked(),"raw CAN display defaults redacted");
            a.packet(new Protocol.Packet(0xb0,new byte[]{0,2,0,75}));a.packet(new Protocol.Packet(0xc0,new byte[]{1,0x18,0x55,0x66}));call(panel,"render");
            check(data.status()!=null&&data.status().gear==1&&data.status().batteryPercent==75,"B0 Activity bridge updates latest vehicle model");
            check(data.canCount()==1&&data.idCount()==1,"C0 Activity bridge updates live CAN independently of recording");
            String vehicle=((TextView)get(panel,"vehicle")).getText().toString();check(vehicle.contains("75%")&&vehicle.contains("P"),"native dashboard renders decoded received values");
            check(((TextView)get(panel,"socValue")).getText().toString().equals("75%"),"metric tile uses actual synthetic B0 value, not mockup value");
            a.packet(new Protocol.Packet(0xb0,new byte[]{0,0,0,75}));call(panel,"render");check(((TextView)get(panel,"gearValue")).getText().toString().equals(a.getString(R.string.ui_gear_unknown)),"unknown raw gear is visibly unknown in metric tile");
            TextView canRows=(TextView)get(panel,"canRows");check(!canRows.getText().toString().contains("55 66"),"native raw bytes hidden before opt-in");bytes.setChecked(true);check(canRows.getText().toString().contains("55 66"),"opt-in reveals received bytes locally");
            a.packet(new Protocol.Packet(0xc0,new byte[]{7,(byte)0xe8,0x12,0x34}));call(panel,"render");check(!canRows.getText().toString().contains("12 34"),"native dashboard keeps diagnostic identity bytes hidden");
            a.packet(new Protocol.Packet(0xb0,new byte[]{0,2,0}));check(((TextView)get(panel,"gearValue")).getText().toString().equals("—")&&((TextView)get(panel,"socValue")).getText().toString().equals("—"),"invalid B0 clears visible metrics immediately despite render throttle");check(data.status()==null&&!((TextView)get(panel,"vehicle")).getText().toString().contains("75%"),"invalid latest B0 clears older displayed vehicle data");
            check(!((HardwareCapture)get(a,"hardware")).active(),"live packet display never starts recording automatically");call(a,"clearIdentity");check(data.canCount()==0&&data.status()==null,"identity reset clears live source values");
        }finally{tabs.setCurrentTabByTag("tools");call(a,"clearIdentity");}
        return checks;
    }
}
