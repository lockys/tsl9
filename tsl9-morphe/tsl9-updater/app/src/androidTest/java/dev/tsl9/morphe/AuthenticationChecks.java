package dev.tsl9.morphe;

import java.lang.reflect.Field;

/** Synthetic packets only. No device, password, or Bluetooth operations. */
final class AuthenticationChecks {
    private final MainActivity activity;
    private int checks;
    AuthenticationChecks(MainActivity activity){this.activity=activity;}
    private void set(String key, boolean value)throws Exception{Field f=MainActivity.class.getDeclaredField(key);f.setAccessible(true);f.setBoolean(activity,value);}
    private boolean get(String key)throws Exception{Field f=MainActivity.class.getDeclaredField(key);f.setAccessible(true);return f.getBoolean(activity);}
    private void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    int run()throws Exception{
        byte[] info=new byte[76];info[3]=1;
        set("passwordRequired",true);set("passwordAccepted",false);set("authPending",true);set("authSent",false);
        activity.packet(new Protocol.Packet(0xa0,info));check(!get("passwordAccepted"),"A0 before password transmission cannot authenticate");
        set("authSent",true);activity.packet(new Protocol.Packet(0xa0,new byte[1]));check(!get("passwordAccepted"),"short A0 cannot authenticate");
        activity.packet(new Protocol.Packet(0xa8,new byte[]{0}));check(!get("passwordAccepted")&&!get("authPending"),"explicit rejection cancels pending authentication");
        activity.packet(new Protocol.Packet(0xa0,info));check(!get("passwordAccepted"),"A0 after rejection cannot authenticate");
        set("authPending",true);set("authSent",true);activity.packet(new Protocol.Packet(0xa0,info));check(get("passwordAccepted")&&!get("authPending"),"valid A0 following a password attempt enables the existing session");
        set("passwordAccepted",false);set("passwordRequired",false);return checks;
    }
}
