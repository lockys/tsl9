package dev.tsl9.morphe;

import android.app.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.lang.reflect.*;
import java.security.KeyStore;
import java.util.concurrent.*;

/** Native fourth destination with synthetic local data; never sends Bluetooth. */
final class SettingsUiChecks {
    private final Instrumentation test;private Activity activity;private int checks;
    SettingsUiChecks(Instrumentation test,Activity activity){this.test=test;this.activity=activity;}
    private void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    private Object get(String name)throws Exception{Field f=activity.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(activity);}
    private Object optional(String name)throws Exception{try{return get(name);}catch(NoSuchFieldException missing){return null;}}
    private void set(String name,Object value)throws Exception{Field f=activity.getClass().getDeclaredField(name);f.setAccessible(true);f.set(activity,value);}
    private Object call(String name)throws Exception{Method m=activity.getClass().getDeclaredMethod(name);m.setAccessible(true);return m.invoke(activity);}
    private interface Step {void run()throws Exception;}
    private void ui(Step step)throws Exception{Throwable[] failure={null};test.runOnMainSync(()->{try{step.run();}catch(Throwable error){failure[0]=error;}});test.waitForIdleSync();if(failure[0]!=null)throw new RuntimeException(failure[0]);}
    private boolean inside(View parent,View child){for(View v=child;v!=null;v=v.getParent() instanceof View?(View)v.getParent():null)if(v==parent)return true;return false;}
    private void open()throws Exception{ui(()->{TabHost tabs=(TabHost)get("tabs");check(tabs.getTabWidget().getTabCount()==4,"four pill destinations include Settings");tabs.getTabWidget().getChildTabViewAt(3).performClick();});}
    private void frame()throws Exception{CountDownLatch draw=new CountDownLatch(1);ui(()->{View decor=activity.getWindow().getDecorView();decor.getViewTreeObserver().addOnPreDrawListener(new android.view.ViewTreeObserver.OnPreDrawListener(){public boolean onPreDraw(){decor.getViewTreeObserver().removeOnPreDrawListener(this);draw.countDown();return true;}});decor.requestLayout();decor.invalidate();});check(draw.await(8,TimeUnit.SECONDS),"settings draws a real native frame");test.waitForIdleSync();}
    private void landscape()throws Exception{
        ui(()->activity.setRequestedOrientation(android.content.pm.ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE));
        long deadline=SystemClock.uptimeMillis()+8000;int[] orientation={0};
        do{ui(()->orientation[0]=activity.getResources().getConfiguration().orientation);if(orientation[0]==android.content.res.Configuration.ORIENTATION_LANDSCAPE)break;Thread.sleep(50);}while(SystemClock.uptimeMillis()<deadline);
        check(orientation[0]==android.content.res.Configuration.ORIENTATION_LANDSCAPE,"settings screenshot uses actual landscape configuration");frame();
        test.getUiAutomation().waitForIdle(300,5000);SystemClock.sleep(1000);frame();
    }
    int run(String mode)throws Exception{
        File file=new File(activity.getNoBackupFilesDir(),"settings-ui-checks.enc");String alias="tsl9.password.synthetic.settings-ui";BluetoothPasswordStore fixture=new BluetoothPasswordStore(file,alias);Object originalStore=optional("passwords");
        try{
            if(originalStore!=null)ui(()->set("passwords",fixture));
            final String[] origin={null};final int[] width={0};ui(()->{TabHost tabs=(TabHost)get("tabs");origin[0]=tabs.getCurrentTabTag();width[0]=tabs.getTabWidget().getWidth();});
            open();frame();
            ui(()->{
                TabHost tabs=(TabHost)get("tabs");View root=(View)get("settingsPage");
                check("settings".equals(tabs.getCurrentTabTag())&&root.isShown(),"Settings is a real visible fourth destination");
                check(tabs.getTabWidget().getWidth()==width[0],"changing to Settings preserves the capsule width");
                check(!(Boolean)get("leaving"),"settings keeps the BLE-owning Activity in foreground");
                check(root.getWidth()>=tabs.getWidth()-2,"settings uses the normal full-width content area");
                for(String name:new String[]{"language","deviceInfo","readButton","passwordButton","hw20","captureDetails","exportButton","logView"})check(inside(root,(View)get(name)),name+" belongs to Settings");
                for(String name:new String[]{"fileButton","match","flashButton","cancelButton","versionButton"})check(!inside(root,(View)get(name)),name+" remains in the update workflow");
                check(!(Boolean)call("carTabVisible"),"vehicle controls are not active in Settings");
            });
            if(mode.startsWith("preview")){
                if("preview-landscape".equals(mode))landscape();
                if("preview-tools".equals(mode)){ui(()->((TabHost)get("tabs")).setCurrentTabByTag("tools"));frame();}
                if("preview-diagnostics".equals(mode)){ui(()->((View)get("captureDetails")).setVisibility(View.VISIBLE));frame();ui(()->((ScrollView)get("settingsPage")).fullScroll(View.FOCUS_DOWN));frame();}
                android.graphics.Bitmap image=test.getUiAutomation().takeScreenshot();check(image!=null,"native settings screenshot captured");
                try(FileOutputStream out=new FileOutputStream(new File(activity.getExternalFilesDir(null),"settings-page.png"))){check(image.compress(android.graphics.Bitmap.CompressFormat.PNG,100,out),"native settings PNG saved");}finally{image.recycle();}return checks;
            }
            check(fixture.remember("Q7!z"),"synthetic remembered password prepared");
            ui(()->{call("refreshSavedPassword");check(((View)get("forgetPasswordButton")).isEnabled(),"stored password can be cleared without BLE");((View)get("forgetPasswordButton")).performClick();});
            check(fixture.load().isEmpty(),"forget clears the local encrypted password");ui(()->check(!((View)get("forgetPasswordButton")).isEnabled(),"forget state refreshes"));
            HardwareCapture capture=(HardwareCapture)get("hardware");
            ui(()->{capture.start(HardwareCapture.Mode.TEXT,false);call("refresh");((TabHost)get("tabs")).setCurrentTabByTag("tools");});open();
            ui(()->{check(capture.active(),"entering Settings preserves active capture");check(!((View)get("language")).isEnabled(),"language recreation remains disabled during capture");check(!((View)get("hw20")).isEnabled(),"OTA readback policy remains locked during capture");((TabHost)get("tabs")).setCurrentTabByTag("tools");check(capture.active(),"leaving Settings preserves capture");capture.stop("synthetic_settings");call("refresh");});
            open();Instrumentation.ActivityMonitor monitor=test.addMonitor("dev.tsl9.morphe.MainActivity",null,false);ui(()->activity.recreate());Activity next=monitor.waitForActivityWithTimeout(12000);test.removeMonitor(monitor);check(next!=null&&next!=activity,"Settings Activity recreates");activity=next;test.waitForIdleSync();frame();
            ui(()->{TabHost tabs=(TabHost)get("tabs");check("settings".equals(tabs.getCurrentTabTag())&&((View)get("language")).isShown(),"Settings is restored after recreation");tabs.setCurrentTabByTag(origin[0]);});frame();
            ui(()->{TabHost tabs=(TabHost)get("tabs");check(origin[0].equals(tabs.getCurrentTabTag()),"primary destinations remain reachable");check(tabs.getTabWidget().getWidth()==width[0],"capsule width survives settings recreation");});
        }finally{
            new android.util.AtomicFile(file).delete();KeyStore keys=KeyStore.getInstance("AndroidKeyStore");keys.load(null);if(keys.containsAlias(alias))keys.deleteEntry(alias);
        }
        return checks;
    }
    Activity activity(){return activity;}
}
