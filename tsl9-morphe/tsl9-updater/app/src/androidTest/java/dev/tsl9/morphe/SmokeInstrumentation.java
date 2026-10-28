package dev.tsl9.morphe;

import android.app.*;
import android.content.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Runs only against the local test APK. Never scans, connects, or sends BLE. */
public final class SmokeInstrumentation extends Instrumentation {
    private int checks;
    private boolean documents,switches,navigation;private String locale,passwordChecks,settingsChecks;
    @Override public void onCreate(Bundle b){super.onCreate(b);documents=b!=null&&"true".equals(b.getString("documents"));switches=b!=null&&"true".equals(b.getString("switches"));navigation=b!=null&&"true".equals(b.getString("navigation"));locale=b==null?null:b.getString("locale");passwordChecks=b==null?null:b.getString("passwords");settingsChecks=b==null?null:b.getString("settings");start();}
    private void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    private Object field(Object o,String name)throws Exception{Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
    private Object call(Object o,String name,Class<?>[] types,Object... args)throws Exception{Method m=o.getClass().getDeclaredMethod(name,types);m.setAccessible(true);return m.invoke(o,args);}
    private Button button(Activity a,String label){return find(a.getWindow().getDecorView(),label);}
    private Button find(View v,String label){if(v instanceof Button&&((Button)v).getText().toString().equals(label))return(Button)v;if(v instanceof ViewGroup){ViewGroup g=(ViewGroup)v;for(int i=0;i<g.getChildCount();i++){Button b=find(g.getChildAt(i),label);if(b!=null)return b;}}return null;}
    private Activity exerciseSwitches(Activity current)throws Exception{
        for(int choice:new int[]{1,2,3,0}){
            ActivityMonitor monitor=addMonitor("dev.tsl9.morphe.MainActivity",null,false);
            final Activity old=current;final int selected=choice;
            runOnMainSync(()->{try{((TabHost)field(old,"tabs")).setCurrentTabByTag("settings");}catch(Exception e){throw new RuntimeException(e);}});
            waitForIdleSync();
            runOnMainSync(()->{try{Spinner picker=(Spinner)field(old,"language");check(picker.isShown(),"language selector is visible before choosing "+selected);picker.setSelection(selected);}catch(Exception e){throw new RuntimeException(e);}});
            Locale actual=LanguageSettings.normalized(Build.VERSION.SDK_INT>=24?old.getResources().getConfiguration().getLocales().get(0):old.getResources().getConfiguration().locale);
            android.content.res.Configuration systemConfig=android.content.res.Resources.getSystem().getConfiguration();Locale system=LanguageSettings.normalized(Build.VERSION.SDK_INT>=24?systemConfig.getLocales().get(0):systemConfig.locale);
            boolean sameEffectiveSystem=selected==0&&actual.getLanguage().equals(system.getLanguage())&&actual.getScript().equals(system.getScript());
            Activity next=monitor.waitForActivityWithTimeout(sameEffectiveSystem?2000:12000);removeMonitor(monitor);
            if(next==null&&sameEffectiveSystem){check(LanguageSettings.index(old)==0,"return to already displayed system language clears app override");next=old;}
            else check(next!=null&&next!=old,"language selector recreates Activity for "+choice);
            current=next;waitForIdleSync();final Activity active=current;
            runOnMainSync(()->check(LanguageSettings.index(active)==selected,"language choice persists "+selected));
        }
        return current;
    }
    @Override public void onStart(){
        Bundle result=new Bundle();Activity activity=null;
        try{
            if(locale!=null){
                final String tag=locale.equals("system")?"":locale;
                runOnMainSync(()->{
                    getTargetContext().getSharedPreferences("settings",Context.MODE_PRIVATE).edit().putString("language",tag).commit();
                    if(Build.VERSION.SDK_INT>=33)getTargetContext().getSystemService(LocaleManager.class).setApplicationLocales(tag.isEmpty()?LocaleList.getEmptyLocaleList():LocaleList.forLanguageTags(tag));
                });waitForIdleSync();
            }
            Intent intent=new Intent().setClassName(getTargetContext().getPackageName(),"dev.tsl9.morphe.MainActivity").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK);
            activity=startActivitySync(intent);waitForIdleSync();
            if(settingsChecks!=null){SettingsUiChecks settings=new SettingsUiChecks(this,activity);checks+=settings.run(settingsChecks);activity=settings.activity();result.putString("result","PASS "+checks+" settings checks; no BLE");finish(Activity.RESULT_OK,result);return;}
            if(switches)activity=exerciseSwitches(activity);
            if(passwordChecks!=null){checks+=new BluetoothPasswordChecks(this,activity).run(passwordChecks);result.putString("result","PASS "+checks+" Bluetooth password checks; no BLE");finish(Activity.RESULT_OK,result);return;}
            if(navigation){NavigationLifecycleChecks navigationChecks=new NavigationLifecycleChecks(this,activity);result.putString("result",navigationChecks.run());activity=navigationChecks.activity();finish(Activity.RESULT_OK,result);return;}
            final Activity a=activity;
            final Throwable[] failure={null};runOnMainSync(()->{try{
                android.content.res.Configuration config=a.getResources().getConfiguration();String tag=(Build.VERSION.SDK_INT>=24?config.getLocales().get(0):config.locale).toLanguageTag();
                check(a.getString(R.string.app_name).equals(tag.contains("Hant")?"TSL9 硬體工具":tag.startsWith("zh")?"TSL9 硬件工具":"TSL9 Hardware Tools"),"actual locale title "+tag);
                check(!UiStrings.render(a,UiMessage.m("ota_retry",UiMessage.m("ota_write_page",2,75),2,9)).contains("%"),"nested OTA retry is formatted");
                check(UiStrings.render(a,UiMessage.m("ota_write_page",2,75)).contains("75"),"OTA status uses localized parameters");
                try{FirmwareImage.parse(new byte[1025],FirmwareImage.Format.RAW);throw new AssertionError("expected invalid RAW");}
                catch(UiException e){check(UiStrings.error(a,e).equals(a.getString(R.string.bin_length,1024)),"localized bin validation");}
                check(a.getString(R.string.flash_confirm,75,0,a.getString(R.string.policy_reply),"synthetic-file-hash","synthetic-transfer-hash").contains("synthetic-transfer-hash"),"localized flash confirmation arguments");
                check(LanguageSettings.normalized(Locale.forLanguageTag("zh-Hans-TW")).getScript().equals("Hans"),"explicit Chinese script wins over region");
                check(LanguageSettings.normalized(Locale.forLanguageTag("zh-HK")).getScript().equals("Hant"),"Chinese HK fallback is Traditional");
                if(Build.VERSION.SDK_INT>=24){
                    LocaleList fallback=LanguageSettings.normalized(new LocaleList(Locale.JAPAN,Locale.forLanguageTag("zh-TW")));
                    check(fallback.size()==2&&fallback.get(1).getScript().equals("Hant"),"system fallback language list preserved");
                    android.content.res.Configuration fallbackConfig=new android.content.res.Configuration(config);fallbackConfig.setLocales(fallback);
                    check(a.createConfigurationContext(fallbackConfig).getString(R.string.app_name).equals("TSL9 硬體工具"),"unsupported first locale falls back to supported Traditional Chinese");
                }
                Spinner language=(Spinner)field(a,"language");check(language.isEnabled(),"idle language selection enabled");
                check(button(a,a.getString(R.string.scan))!=null,"scan UI");check(!button(a,a.getString(R.string.flash)).isEnabled(),"disconnected cannot flash");
                check(button(a,a.getString(R.string.pick_bin)).isEnabled(),"picker enabled");check(!button(a,a.getString(R.string.stop)).isEnabled(),"cancel idle disabled");
                Field bytes=a.getClass().getDeclaredField("selectedBytes");bytes.setAccessible(true);bytes.set(a,new byte[1026]);
                call(a,"parseSelected",new Class<?>[0]);check(field(a,"image")!=null,"valid paged file loads");
                bytes.set(a,new byte[1027]);call(a,"parseSelected",new Class<?>[0]);check(field(a,"image")==null,"invalid file clears image");
                check(!button(a,a.getString(R.string.flash)).isEnabled(),"invalid image gate");
                Spinner format=(Spinner)field(a,"format");format.setSelection(1);bytes.set(a,new byte[1024]);call(a,"parseSelected",new Class<?>[0]);
                check(field(a,"image")!=null,"raw file loads");check(!button(a,a.getString(R.string.flash)).isEnabled(),"valid raw cannot bypass connection gate");
                CheckBox match=(CheckBox)field(a,"match");match.setChecked(true);call(a,"clearIdentity",new Class<?>[0]);check(!match.isChecked(),"new connection resets compatibility check");
                CheckBox hw20=(CheckBox)field(a,"hw20");check(!hw20.isChecked(),"OEM hw20 profile is opt-in and not inferred from raw hardware byte");match.setChecked(true);hw20.setChecked(true);check(!match.isChecked(),"changing OEM readback policy requires compatibility reconfirmation");call(a,"clearIdentity",new Class<?>[0]);check(!hw20.isChecked(),"new idle connection resets hardware profile");
                ((TabHost)field(a,"tabs")).setCurrentTabByTag("settings");
                check(button(a,a.getString(R.string.capture_start))!=null&&!button(a,a.getString(R.string.capture_start)).isEnabled(),"capture needs physical BLE connection");
                checks+=new MockupUiChecks(a).run();
                checks+=new BleQueueChecks((MainActivity)a).run();
                checks+=new VehicleUiChecks((MainActivity)a).run();
                checks+=new LiveUiChecks((MainActivity)a).run();
                HardwareCapture capture=(HardwareCapture)field(a,"hardware");
                capture.start(HardwareCapture.Mode.TEXT,false);Field session=a.getClass().getDeclaredField("hardwareSession");session.setAccessible(true);session.set(a,true);
                call(a,"notification",new Class<?>[]{byte[].class},(Object)"SYNTH_TEMP=31\npassword=synthetic-android-secret\n".getBytes(StandardCharsets.UTF_8));
                check(capture.records()==2&&capture.snapshot().contains("SYNTH_TEMP=31"),"Android notification bridge captures firmware text");
                check(!capture.snapshot().contains("synthetic-android-secret"),"hardware text secret redaction");
                check(!button(a,a.getString(R.string.pick_bin)).isEnabled()&&!button(a,a.getString(R.string.flash)).isEnabled(),"capture and flashing are mutually exclusive");
                check(!hw20.isEnabled(),"capture cannot change OTA readback policy");check(!language.isEnabled(),"capture cannot recreate Activity for language");
                call(a,"stopHardware",new Class<?>[]{String.class,boolean.class},"synthetic_smoke",false);
                check(!capture.active()&&button(a,a.getString(R.string.hardware_export)).isEnabled(),"hardware capture stops and exports independently");
                Field stopping=a.getClass().getDeclaredField("captureStopping");stopping.setAccessible(true);stopping.set(a,true);
                Object client=field(a,"ble");call(a,"refresh",new Class<?>[0]);check(!language.isEnabled(),"pending capture stop blocks language change");int oldEpoch=(Integer)field(client,"epoch");
                call(a,"stopHardware",new Class<?>[]{String.class,boolean.class},"synthetic_disconnect_while_stopping",true);
                check((Boolean)stopping.get(a)&&(Integer)field(client,"epoch")==oldEpoch,"pending CAN stop must drain before disconnect");
                call(a,"finishHardwareStop",new Class<?>[0]);check(!(Boolean)stopping.get(a)&&(Integer)field(client,"epoch")>oldEpoch,"disconnect follows CAN stop write completion");
                OtaSession ota=(OtaSession)field(a,"ota");Field otaState=OtaSession.class.getDeclaredField("state");otaState.setAccessible(true);otaState.set(ota,OtaSession.State.PREPARE);
                call(a,"refresh",new Class<?>[0]);check(!language.isEnabled(),"OTA blocks language change");
                int configurationEpoch=(Integer)field(client,"epoch");
                a.onConfigurationChanged(new android.content.res.Configuration(config));check(!(Boolean)field(a,"pendingLanguageRefresh"),"rotation and unchanged locale do not schedule recreation");
                android.content.res.Configuration changedLocale=new android.content.res.Configuration(config);changedLocale.setLocale(Locale.forLanguageTag(tag.startsWith("zh")?"en":"zh-Hant"));a.onConfigurationChanged(changedLocale);
                check(ota.active()&&(Integer)field(client,"epoch")==configurationEpoch&&(Boolean)field(a,"pendingLanguageRefresh"),"external locale refresh defers without stopping OTA or closing BLE");
                Field pending=a.getClass().getDeclaredField("pendingLanguageRefresh");pending.setAccessible(true);pending.set(a,false);
                int beforeFail=(Integer)field(client,"epoch");ota.fail("synthetic_failure_no_ble");
                check((Integer)field(client,"epoch")==beforeFail+1,"OTA failure closes transport at transition");
                Field phase=client.getClass().getDeclaredField("phase");phase.setAccessible(true);phase.set(client,"CONNECT");call(a,"refresh",new Class<?>[0]);check(!language.isEnabled(),"connecting blocks language change");phase.set(client,"CLOSED");call(a,"refresh",new Class<?>[0]);check(language.isEnabled(),"closed connection allows language change");
                int afterFail=(Integer)field(client,"epoch");((Runnable)field(a,"ticker")).run();
                check((Integer)field(client,"epoch")==afterFail,"failed OTA ticker leaves future reconnection alone");
                File hardwareLog=new File(getTargetContext().getFilesDir(),"latest-hardware.jsonl");check(hardwareLog.isFile()&&hardwareLog.length()>0,"hardware journal persisted");
                format.setSelection(2);bytes.set(a,new byte[1025]);call(a,"parseSelected",new Class<?>[0]);FirmwareImage custom=(FirmwareImage)field(a,"image");
                check(custom!=null&&custom.paddingBytes==1023,"custom unaligned bin explicit FF format");
                call(a,"log",new Class<?>[]{String.class},"SMOKE local-ui-check no BLE");call(a,"flushLog",new Class<?>[0]);
                // Observe the completed write on its owning thread: a delayed flush
                // can briefly truncate the file while an off-main length check runs.
                File log=new File(getTargetContext().getFilesDir(),"latest-debug.log");check(log.isFile()&&log.length()>0,"debug log persisted");
            }catch(Throwable t){failure[0]=t;}});
            if(failure[0]!=null)throw new RuntimeException(failure[0]);waitForIdleSync();
            check(getTargetContext().checkCallingOrSelfPermission("android.permission.INTERNET")!=android.content.pm.PackageManager.PERMISSION_GRANTED,"no INTERNET permission");
            if(documents)checks+=new DocumentJourney(this,a).run();
            result.putString("result","PASS "+checks+" Android UI/lifecycle assertions; no physical BLE tested");finish(Activity.RESULT_OK,result);
        }catch(Throwable e){result.putString("result","FAIL "+e.toString());finish(Activity.RESULT_CANCELED,result);}
        finally{if(activity!=null){final Activity a=activity;runOnMainSync(a::finish);}}
    }
}
