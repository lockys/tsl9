package com.lockys.tsl9updater;

import android.app.AlertDialog;
import android.content.Context;
import android.os.SystemClock;
import android.view.Gravity;
import android.widget.*;
import java.util.*;

/** Native receive-only dashboard. The host owns the existing BLE/capture session. */
final class LivePanel {
    interface Host {void query();void startCan(String filter);void stopCan();void export();}
    final ScrollView view;private final Context c;private final TextView summary,vehicle,canSummary,canRows;
    private final Button query,start,stop,export;private final EditText filter;private final CheckBox showBytes;
    private LiveVehicleData data;private boolean connected,receiving;private long lastDraw;
    LivePanel(Context context,Host host){
        c=context;view=new ScrollView(c);LinearLayout body=new LinearLayout(c);body.setOrientation(LinearLayout.VERTICAL);body.setPadding(dp(20),dp(20),dp(20),dp(28));body.setBackgroundColor(0xfff2f5f1);view.addView(body);
        body.addView(label(s(R.string.live_title),26));body.addView(label(s(R.string.live_hint),13));
        query=button(s(R.string.car_read_status),host::query);body.addView(query);summary=label("",14);body.addView(summary);
        body.addView(label(s(R.string.live_vehicle_title),20));vehicle=label(s(R.string.live_no_status),15);vehicle.setTextIsSelectable(true);body.addView(vehicle);
        body.addView(button(s(R.string.live_meanings_button),()->new AlertDialog.Builder(c).setTitle(s(R.string.live_meanings_button)).setMessage(s(R.string.live_meanings)).setPositiveButton(android.R.string.ok,null).show()));
        body.addView(label(s(R.string.live_can_title),20));body.addView(label(s(R.string.live_can_hint),13));
        filter=new EditText(c);filter.setHint(s(R.string.live_filter));filter.setSingleLine(true);filter.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);body.addView(filter);
        start=button(s(R.string.live_start_can),()->host.startCan(filter.getText().toString()));stop=button(s(R.string.capture_stop),host::stopCan);body.addView(start);body.addView(stop);
        showBytes=new CheckBox(c);showBytes.setText(s(R.string.live_show_bytes));body.addView(showBytes);
        canSummary=label("",14);body.addView(canSummary);canRows=label(s(R.string.live_no_can),13);canRows.setTypeface(android.graphics.Typeface.MONOSPACE);canRows.setTextIsSelectable(true);body.addView(canRows);
        export=button(s(R.string.hardware_export),host::export);body.addView(export);
        showBytes.setOnCheckedChangeListener((b,on)->{lastDraw=0;if(data!=null)render();});
        view.setOnApplyWindowInsetsListener((v,insets)->{body.setPadding(dp(20),dp(20)+insets.getSystemWindowInsetTop(),dp(20),dp(28));return insets;});
    }
    private int dp(int value){return Math.round(value*c.getResources().getDisplayMetrics().density);}
    private String s(int id,Object... args){return c.getString(id,args);}
    private TextView label(String text,int size){TextView v=new TextView(c);v.setText(text);v.setTextSize(size);v.setTextColor(0xff202724);v.setPadding(0,dp(5),0,dp(5));return v;}
    private Button button(String label,Runnable action){Button b=new Button(c);b.setText(label);b.setAllCaps(false);b.setOnClickListener(v->{try{action.run();}catch(IllegalArgumentException e){Toast.makeText(c,UiStrings.error(c,e),Toast.LENGTH_LONG).show();}catch(SecurityException e){Toast.makeText(c,s(R.string.nearby_permission),Toast.LENGTH_LONG).show();}});return b;}
    private void put(TextView v,String text){if(!text.contentEquals(v.getText()))v.setText(text);}
    void update(LiveVehicleData data,boolean connected,boolean readAllowed,boolean startAllowed,boolean stopAllowed,boolean exportAllowed,boolean recording){
        if(this.connected!=connected||receiving!=stopAllowed)lastDraw=0;this.data=data;this.connected=connected;receiving=stopAllowed;
        query.setEnabled(readAllowed);start.setEnabled(startAllowed);stop.setEnabled(stopAllowed);export.setEnabled(exportAllowed);filter.setEnabled(!recording);
        if(SystemClock.elapsedRealtime()-lastDraw>=500)render();
    }
    private String number(Double value,String unit,int decimals){return value==null?s(R.string.live_unknown):String.format(Locale.ROOT,"%."+decimals+"f",value)+unit;}
    private String bool(Boolean value){return value==null?s(R.string.live_unknown):s(value?R.string.live_open:R.string.live_closed);}
    private void row(StringBuilder out,int label,String value){out.append(s(label)).append(": ").append(value).append('\n');}
    private void render(){
        lastDraw=SystemClock.elapsedRealtime();LiveVehicleData.Snapshot t=data.status();
        String freshness=t==null?s(R.string.live_no_status):s(R.string.live_received,String.format(Locale.ROOT,"%.1f",data.ageMs(t.at)/1000.0),t.bytes,s(data.statusFresh()?R.string.live_fresh:R.string.live_stale));
        if(t!=null&&(t.gear<1||t.gear>4))freshness+="\n"+s(R.string.car_wait_park,t.gear);
        put(summary,s(connected?R.string.ble_ready:R.string.disconnected)+"\n"+freshness);
        if(t==null){put(vehicle,s(R.string.live_no_status)+(data.statusBytes()>=0?"\n"+s(R.string.car_short_status,data.statusBytes()):""));}
        else{
            StringBuilder rows=new StringBuilder();row(rows,R.string.live_gear,t.gearLabel());row(rows,R.string.live_speed,t.speed+"");row(rows,R.string.live_soc,t.batteryPercent==null?s(R.string.live_unknown):t.batteryPercent+"%");
            row(rows,R.string.live_odometer,number(t.odometerKm," km",1));row(rows,R.string.live_frunk,bool(t.frunkOpen));row(rows,R.string.live_trunk,bool(t.trunkOpen));
            row(rows,R.string.live_cabin,number(t.cabinC," °C",1));row(rows,R.string.live_ambient,number(t.ambientC," °C",1));row(rows,R.string.live_voltage,number(t.voltage," V",2));
            row(rows,R.string.live_door_bits,String.format(Locale.ROOT,"0x%X",t.doorBits));row(rows,R.string.live_light_bits,String.format(Locale.ROOT,"0x%X",t.lightBits));put(vehicle,rows.toString());
        }
        List<LiveVehicleData.CanFrame> frames=data.recent(50);put(canSummary,s(receiving?R.string.recording:R.string.capture_stopped)+"\n"+s(R.string.live_can_summary,data.canCount(),data.idCount(),frames.size()));
        if(frames.isEmpty()){put(canRows,s(R.string.live_no_can));return;}
        StringBuilder rows=new StringBuilder();for(LiveVehicleData.CanFrame f:frames){
            String hz=f.averageHz()==null?"?":String.format(Locale.ROOT,"%.1f",f.averageHz());String seconds=String.format(Locale.ROOT,"%.1f",data.ageMs(f.lastAt)/1000.0);
            rows.append(s(R.string.live_can_row,String.format(Locale.ROOT,"%04X",f.id),f.length,f.count,hz,seconds)).append('\n');
            String raw=f.visibleHex(showBytes.isChecked());rows.append(raw!=null?raw:s(f.diagnosticIdentity()?R.string.live_diagnostic_redacted:R.string.live_bytes_hidden)).append("\n\n");
        }put(canRows,rows.toString());
    }
}
