package dev.tsl9.morphe;
import android.os.SystemClock;
import android.view.*;
import android.widget.*;
import java.lang.reflect.*;
import java.util.*;
/** Main-thread UI bridge tests with a recording transport. Never sends BLE. */
final class VehicleUiChecks {
    private final MainActivity a;private int checks;
    VehicleUiChecks(MainActivity activity){a=activity;}
    private void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
    private Object get(Object o,String name)throws Exception{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
    private void set(Object o,String name,Object value)throws Exception{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);f.set(o,value);}
    private void call(String name,Class<?>[] types,Object... args)throws Exception{Method m=MainActivity.class.getDeclaredMethod(name,types);m.setAccessible(true);m.invoke(a,args);}
    private boolean containsProfile(View v){if(v instanceof CheckBox&&((CheckBox)v).getText().toString().equals(a.getString(R.string.car_profile)))return true;if(v instanceof ViewGroup)for(int i=0;i<((ViewGroup)v).getChildCount();i++)if(containsProfile(((ViewGroup)v).getChildAt(i)))return true;return false;}
    @SuppressWarnings({"unchecked","rawtypes"}) private void phase(VehicleControls v,String name)throws Exception{Field f=VehicleControls.class.getDeclaredField("phase");f.setAccessible(true);f.set(v,Enum.valueOf((Class)f.getType(),name));set(v,"deadline",SystemClock.elapsedRealtime()+8000);}
    private final class Wire implements VehicleControls.Listener {
        final ArrayList<Integer> codes=new ArrayList<>();final ArrayList<String> logs=new ArrayList<>();Runnable written;
        public void send(int command,byte[] payload,Runnable done){codes.add(command==0xa7?payload[0]&255:command);written=done;}
        public void sendGuarded(int command,byte[] payload,Runnable done,VehicleControls.WriteGuard guard){send(command,payload,done);}
        public void changed(UiMessage value){try{call("carChanged",new Class<?>[]{UiMessage.class},value);}catch(Exception e){throw new RuntimeException(e);}}
        public void log(String value){logs.add(value);}
        void drain(){Runnable r=written;written=null;if(r!=null)r.run();}
    }
    @SuppressWarnings("unchecked") int run()throws Exception{
        TabHost tabs=(TabHost)get(a,"tabs");VehicleControls original=(VehicleControls)get(a,"car");Object selected=get(a,"selectedBytes"),image=get(a,"image");
        try{
            tabs.setCurrentTabByTag("car");check("car".equals(tabs.getCurrentTabTag()),"car tab opens");check(!containsProfile(a.getWindow().getDecorView()),"vehicle profile checkbox removed from UI");tabs.setCurrentTabByTag("tools");check(get(a,"selectedBytes")==selected&&get(a,"image")==image,"tabs preserve selected firmware");tabs.setCurrentTabByTag("car");
            ArrayList<Button> buttons=(ArrayList<Button>)get(a,"carButtons");check(buttons.size()==10,"lock/unlock and eight seat directions");for(Button b:buttons)check(!b.isEnabled(),"disconnected actions disabled");
            check(!((Button)get(a,"carVersionButton")).isEnabled()&&!((Button)get(a,"carRefreshButton")).isEnabled(),"disconnected queries disabled");
            byte[] info=new byte[76];info[1]=0x32;info[2]=0x41;info[3]=1;info[4]=7;a.packet(new Protocol.Packet(0xa0,info));String versions=((TextView)get(a,"carVersionView")).getText().toString();check(versions.contains("4.1")&&versions.contains("3.2")&&!versions.contains("4.1.00"),"versions show only reported prefixes");
            a.packet(new Protocol.Packet(0xb0,new byte[]{0,2,0,0}));check(original.telemetryFresh()&&original.gear()==1,"four-byte monitoring accepted");a.packet(new Protocol.Packet(0xb0,new byte[3]));check(!original.telemetryFresh(),"incomplete monitoring invalidated");
            CheckBox layout=(CheckBox)get(a,"lightLayout");layout.setChecked(true);byte[] changed=info.clone();changed[4]++;a.packet(new Protocol.Packet(0xa0,changed));check(!layout.isChecked(),"new identity resets lighting-layout confirmation");a.packet(new Protocol.Packet(0xa0,new byte[2]));check(get(a,"info")==null&&get(a,"versionInfo")==null,"short A0 clears mode/version info");
            HardwareCapture capture=(HardwareCapture)get(a,"hardware");capture.start(HardwareCapture.Mode.BLE,false);set(a,"hardwareSession",true);a.packet(new Protocol.Packet(0xb0,new byte[4]));a.packet(new Protocol.Packet(0xa3,info));check(capture.records()==2&&capture.snapshot().contains("redacted"),"monitoring and A3 still pass capture bridge");call("stopHardware",new Class<?>[]{String.class,boolean.class},"synthetic_vehicle",false);
            Wire wire=new Wire();VehicleControls fake=new VehicleControls(wire,SystemClock::elapsedRealtime);set(a,"car",fake);set(a,"info",info.clone());fake.onInfo(info);fake.setAvailable(true);call("refreshCarUi",new Class<?>[0]);
            check(buttons.get(0).isEnabled()&&buttons.get(2).isEnabled(),"synthetic connected capability enables lock and seats without checkbox or telemetry");buttons.get(0).performClick();check(wire.codes.equals(Arrays.asList(22)),"native lock click immediately sends A7 22 without confirmation dialog");wire.drain();fake.setAvailable(true);call("refreshCarUi",new Class<?>[0]);buttons.get(1).performClick();check(wire.codes.equals(Arrays.asList(22,23)),"native unlock click directly sends 23");wire.drain();
            check(((TextView)get(a,"carStatus")).getText().toString().equals(a.getString(R.string.car_unlock_sent)),"unlock result explains that unlocking does not open a door");
            layout.setChecked(true);fake.setAvailable(true);check(!fake.telemetryFresh()&&fake.lightingAvailable(),"native car model accepts OEM feature setting without B0");call("refreshCarUi",new Class<?>[0]);check(!((TextView)get(a,"lightStatus")).getText().toString().isEmpty(),"lighting area explains its actual state");
            int beforeReply=wire.codes.size();a.packet(new Protocol.Packet(0xa7,new byte[]{23,0}));check(wire.codes.size()==beforeReply&&wire.logs.toString().contains("CAR OEM A7 reply"),"A7 reply is recorded without retry or fake success");
            fake.setAvailable(true);call("refreshCarUi",new Class<?>[0]);Button seat=buttons.get(2);wire.codes.clear();MotionEvent down=MotionEvent.obtain(0,0,MotionEvent.ACTION_DOWN,1,1,0),up=MotionEvent.obtain(0,10,MotionEvent.ACTION_UP,1,1,0);try{seat.dispatchTouchEvent(down);seat.dispatchTouchEvent(up);}finally{down.recycle();up.recycle();}check(wire.codes.equals(Arrays.asList(26,16)),"native direct seat press/release sends start then one stop");wire.drain();
            phase(fake,"MOVING");wire.codes.clear();((Button)get(a,"passengerSelector")).performClick();check(wire.codes.equals(Arrays.asList(16)),"changing seat selection immediately requests stop");
            check(((View)get(a,"driverPad")).getVisibility()==View.GONE&&((View)get(a,"passengerPad")).getVisibility()==View.VISIBLE,"only the selected seat directional pad is displayed");wire.drain();((Button)get(a,"driverSelector")).performClick();
            byte[] expected=info.clone();expected[30]=0x40;set(fake,"expectedConfig",expected);phase(fake,"CONFIG_CONFIRM");a.packet(new Protocol.Packet(0xa3,expected));check(fake.active()&&!fake.lightReadbackConfirmed(),"A3 echo cannot confirm config");a.packet(new Protocol.Packet(0xa0,expected));check(!fake.active()&&fake.lightReadbackConfirmed(),"A0 confirms config");
            phase(fake,"MOVING");wire.codes.clear();set(a,"pressedSeat",seat);seat.setEnabled(true);MotionEvent cancel=MotionEvent.obtain(0,0,MotionEvent.ACTION_CANCEL,1,1,0);try{seat.dispatchTouchEvent(cancel);}finally{cancel.recycle();}check(wire.codes.equals(Arrays.asList(16))&&fake.active(),"native cancel queues one stop");Object client=get(a,"ble");int epoch=(Integer)get(client,"epoch");call("disconnectRequested",new Class<?>[0]);check((Integer)get(client,"epoch")==epoch&&fake.active(),"disconnect waits for seat stop drain");wire.drain();check((Integer)get(client,"epoch")==epoch+1&&!fake.active(),"stop completion releases transport");
            fake.onInfo(info);phase(fake,"MOVING");wire.codes.clear();a.packet(new Protocol.Packet(0xa0,new byte[1]));check(wire.codes.equals(Arrays.asList(16)),"short A0 while moving still requests stop");wire.drain();
        }finally{set(a,"car",original);set(a,"pressedSeat",null);call("clearIdentity",new Class<?>[0]);tabs.setCurrentTabByTag("tools");call("refresh",new Class<?>[0]);}
        return checks;
    }
}
