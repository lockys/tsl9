package com.lockys.tsl9updater;

import android.annotation.SuppressLint;
import android.bluetooth.*;
import android.bluetooth.le.*;
import android.content.Context;
import android.os.*;
import java.util.*;

/** All state lives on the main Looper. One GATT operation is in flight at a time. */
@SuppressLint("MissingPermission")
final class BleClient {
    static final UUID SERVICE=UUID.fromString("0000fff0-0000-1000-8000-00805f9b34fb");
    static final UUID DATA=UUID.fromString("0000fff1-0000-1000-8000-00805f9b34fb");
    static final UUID CCCD=UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");
    interface Events {
        void log(String line);void state(String state);void found(BluetoothDevice device,String name,int rssi);
        void ready();void disconnected();void packet(Protocol.Packet packet);void notification(byte[] bytes);
    }
    private final Context context;private final Events events;private final Handler handler=new Handler(Looper.getMainLooper());
    private final Protocol.Decoder decoder=new Protocol.Decoder();private final ArrayDeque<Write> queue=new ArrayDeque<>();
    private BluetoothGatt gatt;private BluetoothGattCharacteristic characteristic;private BluetoothLeScanner scanner;
    private boolean scanning,busy;private String phase="CLOSED";private int chunkSize=20,writeType=BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT;
    private int epoch;private Write current;
    private static final class Write { final int cmd;final byte[] frame;final Runnable done;final VehicleControls.WriteGuard guard;int offset;Write(int c,byte[] f,Runnable r){this(c,f,r,null);}Write(int c,byte[] f,Runnable r,VehicleControls.WriteGuard g){cmd=c;frame=f;done=r;guard=g;} }
    BleClient(Context c,Events e){context=LanguageSettings.wrap(c.getApplicationContext());events=e;}
    private String s(int id,Object... args){return context.getString(id,args);}
    boolean open(){return scanning||!"CLOSED".equals(phase);}
    boolean ready(){return gatt!=null&&"READY".equals(phase);}
    boolean idle(){return ready()&&!busy&&current==null&&queue.isEmpty();}
    BluetoothAdapter adapter(){BluetoothManager m=(BluetoothManager)context.getSystemService(Context.BLUETOOTH_SERVICE);return m==null?null:m.getAdapter();}
    void scan(){
        stopScan();BluetoothAdapter a=adapter();if(a==null||!a.isEnabled()){events.state(s(R.string.ble_enable));return;}
        scanner=a.getBluetoothLeScanner();if(scanner==null){events.state(s(R.string.ble_scanner));return;}
        try{scanning=true;scanner.startScan(null,new ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build(),scanCallback);events.state(s(R.string.ble_scanning));events.log("SCAN start target=TSL/FFF0 duration=10s");
            int token=epoch;handler.postDelayed(()->{if(token==epoch&&scanning){stopScan();events.state(s(R.string.ble_scan_done));}},10000);
        }catch(SecurityException|IllegalStateException e){scanning=false;events.state(s(R.string.ble_scan_denied));}
    }
    private final ScanCallback scanCallback=new ScanCallback(){
        @Override public void onScanResult(int type,ScanResult r){handler.post(()->{
            if(!scanning)return;String name=r.getScanRecord()==null?null:r.getScanRecord().getDeviceName();
            if(name==null)name=r.getDevice().getName();if(name==null)name=s(R.string.ble_unnamed);
            List<ParcelUuid> services=r.getScanRecord()==null?null:r.getScanRecord().getServiceUuids();
            if(name.toUpperCase(Locale.ROOT).contains("TSL")||(services!=null&&services.contains(new ParcelUuid(SERVICE))))events.found(r.getDevice(),name,r.getRssi());
        });}
        @Override public void onScanFailed(int code){handler.post(()->{stopScan();events.log("SCAN failed code="+code);events.state(s(R.string.ble_scan_failed,code));});}
    };
    void stopScan(){if(scanner!=null&&scanning){try{scanner.stopScan(scanCallback);}catch(SecurityException|IllegalStateException ignored){}}scanning=false;}
    void connect(BluetoothDevice device){
        close();phase="CONNECT";int token=epoch;events.state(s(R.string.ble_connecting));events.log("GATT connect transport=LE attempt");
        try{gatt=device.connectGatt(context,false,callback,BluetoothDevice.TRANSPORT_LE);}
        catch(SecurityException|IllegalArgumentException e){problem(s(R.string.ble_connect_denied));return;}
        handler.postDelayed(()->{if(token==epoch&&!ready())problem(s(R.string.ble_connect_timeout));},15000);
    }
    private void discover(BluetoothGatt g){phase="SERVICES";events.log("GATT discoverServices");if(!g.discoverServices())problem(s(R.string.ble_discover_rejected));}
    private final BluetoothGattCallback callback=new BluetoothGattCallback(){
        @Override public void onConnectionStateChange(BluetoothGatt g,int status,int state){handler.post(()->{
            if(g!=gatt)return;events.log("GATT connection status="+status+" state="+state);
            if(status!=0||state==BluetoothProfile.STATE_DISCONNECTED){problem(s(R.string.ble_disconnected,status));return;}
            if(state==BluetoothProfile.STATE_CONNECTED){phase="MTU";if(!g.requestMtu(247))discover(g);else handler.postDelayed(()->{if(g==gatt&&phase.equals("MTU")){events.log("MTU timeout; conservative payload=20");discover(g);}},4000);}
        });}
        @Override public void onMtuChanged(BluetoothGatt g,int mtu,int status){handler.post(()->{
            if(g!=gatt)return;if(status==0)chunkSize=Math.max(20,Math.min(244,mtu-3));events.log("GATT MTU="+mtu+" status="+status+" chunk="+chunkSize);if(phase.equals("MTU"))discover(g);
        });}
        @Override public void onServicesDiscovered(BluetoothGatt g,int status){handler.post(()->{
            if(g!=gatt||!phase.equals("SERVICES"))return;if(status!=0){problem(s(R.string.ble_service_failed,status));return;}
            BluetoothGattService s=g.getService(SERVICE);characteristic=s==null?null:s.getCharacteristic(DATA);
            if(characteristic==null){problem(s(R.string.ble_missing));return;}
            int props=characteristic.getProperties();boolean write=(props&BluetoothGattCharacteristic.PROPERTY_WRITE)!=0;
            boolean noResponse=(props&BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE)!=0;
            if((!write&&!noResponse)||(props&BluetoothGattCharacteristic.PROPERTY_NOTIFY)==0){problem(s(R.string.ble_properties));return;}
            writeType=write?BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT:BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE;
            events.log("GATT FFF0/FFF1 properties="+props+" writeType="+writeType);
            BluetoothGattDescriptor cccd=characteristic.getDescriptor(CCCD);
            if(cccd==null||!g.setCharacteristicNotification(characteristic,true)){problem(s(R.string.ble_notify_failed));return;}
            phase="CCCD";boolean accepted;
            if(Build.VERSION.SDK_INT>=33)accepted=g.writeDescriptor(cccd,BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)==BluetoothStatusCodes.SUCCESS;
            else{cccd.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);accepted=g.writeDescriptor(cccd);}
            if(!accepted)problem(s(R.string.ble_cccd_rejected));
        });}
        @Override public void onDescriptorWrite(BluetoothGatt g,BluetoothGattDescriptor d,int status){handler.post(()->{
            if(g!=gatt||!phase.equals("CCCD")||!d.getUuid().equals(CCCD))return;
            events.log("GATT CCCD status="+status);if(status!=0){problem(s(R.string.ble_subscribe_failed,status));return;}phase="READY";events.state(s(R.string.ble_ready));events.ready();
        });}
        @Override public void onCharacteristicChanged(BluetoothGatt g,BluetoothGattCharacteristic c,byte[] value){byte[] copy=value.clone();handler.post(()->notifyValue(g,c,copy));}
        @Override public void onCharacteristicChanged(BluetoothGatt g,BluetoothGattCharacteristic c){if(Build.VERSION.SDK_INT<33){byte[] value=c.getValue();if(value!=null){byte[] copy=value.clone();handler.post(()->notifyValue(g,c,copy));}}}
        @Override public void onCharacteristicWrite(BluetoothGatt g,BluetoothGattCharacteristic c,int status){handler.post(()->{
            if(g!=gatt||!busy||current==null||!c.getUuid().equals(DATA))return;busy=false;
            events.log("GATT write callback status="+status+" frameOffset="+current.offset);
            if(status!=0){problem(s(R.string.ble_write_failed,status));return;}writeNext();
        });}
    };
    private void notifyValue(BluetoothGatt g,BluetoothGattCharacteristic c,byte[] value){
        if(g!=gatt||!c.getUuid().equals(DATA))return;
        events.notification(value.clone());
        List<Protocol.Packet> packets=decoder.push(value,SystemClock.elapsedRealtime());
        events.log("GATT notify bytes="+value.length+" completeFrames="+packets.size());
        for(Protocol.Packet p:packets){events.log(String.format(Locale.ROOT,"RX cmd=0x%02X len=%d payload=redacted",p.command,p.payload.length));events.packet(p);}
    }
    void send(int command,byte[] data,Runnable done){
        if(!ready()){problem(s(R.string.ble_not_ready));return;}
        queue.add(new Write(command,Protocol.encode(command,data),done));writeNext();
    }
    void sendGuarded(int command,byte[] data,Runnable done,VehicleControls.WriteGuard guard){
        if(!ready()){problem(s(R.string.ble_not_ready));return;}
        queue.add(new Write(command,Protocol.encode(command,data),done,guard));writeNext();
    }
    private void writeNext(){
        for(Iterator<Write> it=queue.iterator();it.hasNext();){Write pending=it.next();if(pending.guard!=null&&!pending.guard.allow()){it.remove();events.log("TX pending actuation canceled cmd="+pending.cmd+" payload=redacted");}}
        if(!ready()||busy)return;
        if(current!=null&&current.offset==current.frame.length){Runnable done=current.done;current=null;if(done!=null)done.run();}
        if(busy||!ready())return;if(current==null)current=queue.poll();if(current==null)return;
        Write w=current;if(w.offset==0&&w.guard!=null&&!w.guard.allow()){current=null;events.log("TX actuation canceled before first chunk cmd="+w.cmd);writeNext();return;}
        int end=Math.min(w.offset+chunkSize,w.frame.length);byte[] chunk=Arrays.copyOfRange(w.frame,w.offset,end);
        boolean accepted;
        try{if(Build.VERSION.SDK_INT>=33)accepted=gatt.writeCharacteristic(characteristic,chunk,writeType)==BluetoothStatusCodes.SUCCESS;
            else{characteristic.setWriteType(writeType);characteristic.setValue(chunk);accepted=gatt.writeCharacteristic(characteristic);}}
        catch(SecurityException|IllegalArgumentException e){problem(s(R.string.ble_write_denied));return;}
        if(!accepted){problem(s(R.string.ble_write_rejected));return;}
        w.offset=end;busy=true;events.log(String.format(Locale.ROOT,"TX chunk cmd=0x%02X bytes=%d offset=%d/%d",w.cmd,chunk.length,end,w.frame.length));
        int token=epoch;handler.postDelayed(()->{if(token==epoch&&busy&&current==w&&current.offset==end)problem(s(R.string.ble_write_timeout));},7000);
    }
    private void problem(String detail){events.log("GATT STOP "+detail);close();events.state(detail);events.disconnected();}
    void close(){
        stopScan();epoch++;phase="CLOSED";busy=false;queue.clear();current=null;characteristic=null;chunkSize=20;decoder.reset();
        BluetoothGatt old=gatt;gatt=null;if(old!=null){try{old.disconnect();old.close();}catch(SecurityException ignored){}}
    }
}
