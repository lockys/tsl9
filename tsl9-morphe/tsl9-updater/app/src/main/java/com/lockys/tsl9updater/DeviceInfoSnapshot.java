package com.lockys.tsl9updater;
import java.util.Locale;
/** A0 local fields only. The OEM's complete revision is server metadata, not an A0 byte. */
public final class DeviceInfoSnapshot {
    public final int hardwareByte,bluetoothByte,applicationByte,replyBytes;
    public final boolean normalMode;public final long receivedAt;
    private DeviceInfoSnapshot(byte[] data,long now){hardwareByte=data[0]&255;bluetoothByte=data[1]&255;applicationByte=data[2]&255;normalMode=(data[3]&1)!=0;replyBytes=data.length;receivedAt=now;}
    public static DeviceInfoSnapshot parse(byte[] data,long now){if(data==null||data.length<18)throw new IllegalArgumentException("A0 information too short");return new DeviceInfoSnapshot(data,now);}
    private static String prefix(int value){return String.format(Locale.ROOT,"%X.%X",value>>>4,value&15);}
    public String bluetoothPrefix(){return prefix(bluetoothByte);}
    public String applicationPrefix(){return prefix(applicationByte);}
    public boolean revisionKnown(){return false;}
}
