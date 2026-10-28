package dev.tsl9.morphe;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.view.View;
import android.view.ViewTreeObserver;
import android.widget.TabHost;
import android.widget.TabWidget;
import android.widget.TextView;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** Measures the real drawn navigation after transitions; never uses Bluetooth. */
final class NavigationLifecycleChecks {
    private final Instrumentation instrumentation;
    private Activity activity;
    private int checks;
    private final StringBuilder samples=new StringBuilder();
    NavigationLifecycleChecks(Instrumentation instrumentation,Activity activity){this.instrumentation=instrumentation;this.activity=activity;}
    private void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    private void focus(boolean expected) throws Exception {
        long deadline=android.os.SystemClock.uptimeMillis()+8000;boolean[] focused={false};
        do{instrumentation.runOnMainSync(()->focused[0]=activity.getWindow().getDecorView().hasWindowFocus());if(focused[0]==expected)break;Thread.sleep(50);}while(android.os.SystemClock.uptimeMillis()<deadline);
        check(focused[0]==expected,"Activity window focus becomes "+expected);
    }
    private void rotate(int requested,int expected) throws Exception {
        instrumentation.runOnMainSync(()->activity.setRequestedOrientation(requested));
        long deadline=android.os.SystemClock.uptimeMillis()+8000;int[] orientation={0};
        do{instrumentation.runOnMainSync(()->orientation[0]=activity.getResources().getConfiguration().orientation);if(orientation[0]==expected)break;Thread.sleep(50);}while(android.os.SystemClock.uptimeMillis()<deadline);
        check(orientation[0]==expected,"real display orientation changes to "+expected);
    }
    private void frame() throws Exception {
        CountDownLatch drawn=new CountDownLatch(1);
        instrumentation.runOnMainSync(()->{
            View decor=activity.getWindow().getDecorView();
            decor.getViewTreeObserver().addOnPreDrawListener(new ViewTreeObserver.OnPreDrawListener(){
                public boolean onPreDraw(){decor.getViewTreeObserver().removeOnPreDrawListener(this);drawn.countDown();return true;}
            });
            decor.requestLayout();decor.invalidate();
        });
        check(drawn.await(8,TimeUnit.SECONDS),"navigation transition drew a real frame");
        instrumentation.waitForIdleSync();
    }
    private void measure(String state) throws Exception {
        frame();
        instrumentation.runOnMainSync(()->{
            TabHost host=activity.findViewById(android.R.id.tabhost);TabWidget bar=host.getTabWidget();
            View parent=(View)bar.getParent();int viewport=parent.getWidth()-parent.getPaddingLeft()-parent.getPaddingRight();
            float density=activity.getResources().getDisplayMetrics().density;
            int nominal=Math.min(Math.round(360*density),Math.round(viewport*0.52f));
            int slot=Math.round(48*density);
            for(int index=0;index<bar.getTabCount();index++){
                TextView label=(TextView)bar.getChildTabViewAt(index);
                slot=Math.max(slot,(int)Math.ceil(label.getPaint().measureText(label.getText().toString()))+label.getPaddingLeft()+label.getPaddingRight()+Math.round(2*density));
                check(label.getWidth()>=48*density-1&&label.getHeight()>=48*density-1,state+": 48dp touch target");
                check(label.getPaint().measureText(label.getText().toString())<=label.getWidth()-label.getPaddingLeft()-label.getPaddingRight()+1,state+": localized label fits");
            }
            int expected=Math.min(viewport-Math.round(32*density),Math.max(nominal,slot*bar.getTabCount()+bar.getPaddingLeft()+bar.getPaddingRight()));
            check(Math.abs(bar.getWidth()-expected)<=2,state+": pill width remains nominal or expands only for measured labels, actual="+bar.getWidth()+" expected="+expected);
            check(Math.abs(bar.getLeft()+bar.getWidth()/2f-(parent.getPaddingLeft()+viewport/2f))<=2*density,state+": centered capsule");
            if(samples.length()>0)samples.append("; ");samples.append(state).append('=').append(bar.getWidth()).append('x').append(bar.getHeight()).append('/').append(viewport);
        });
    }
    String run() throws Exception {
        measure("initial");
        for(int round=0;round<3;round++)for(int destination=0;destination<4;destination++){
            final int tab=destination;
            instrumentation.runOnMainSync(()->((TabHost)activity.findViewById(android.R.id.tabhost)).setCurrentTab(tab));
            measure("tab"+round+"-"+destination);
        }
        for(int round=0;round<3;round++){
            instrumentation.getUiAutomation().performGlobalAction(android.accessibilityservice.AccessibilityService.GLOBAL_ACTION_HOME);
            focus(false);
            Intent intent=new Intent().setClassName(activity,"dev.tsl9.morphe.MainActivity").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
            instrumentation.getTargetContext().startActivity(intent);focus(true);measure("resume"+round);
        }
        instrumentation.runOnMainSync(()->{
            ((TabHost)activity.findViewById(android.R.id.tabhost)).setCurrentTabByTag("tools");
            try{java.lang.reflect.Field picker=activity.getClass().getDeclaredField("fileButton");picker.setAccessible(true);((View)picker.get(activity)).performClick();}catch(Exception error){throw new RuntimeException(error);}
        });
        focus(false);
        instrumentation.getUiAutomation().performGlobalAction(android.accessibilityservice.AccessibilityService.GLOBAL_ACTION_BACK);
        focus(true);measure("picker-cancel-return");
        for(int round=0;round<3;round++){
            Instrumentation.ActivityMonitor monitor=instrumentation.addMonitor("dev.tsl9.morphe.MainActivity",null,false);
            instrumentation.runOnMainSync(()->activity.recreate());
            Activity next=monitor.waitForActivityWithTimeout(12000);instrumentation.removeMonitor(monitor);
            check(next!=null&&next!=activity,"Activity recreation completes");activity=next;measure("recreate"+round);
        }
        rotate(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE,android.content.res.Configuration.ORIENTATION_LANDSCAPE);
        measure("landscape");
        rotate(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT,android.content.res.Configuration.ORIENTATION_PORTRAIT);
        measure("portrait-return");
        return "PASS "+checks+" navigation lifecycle assertions: "+samples;
    }
    Activity activity(){return activity;}
}
