package dev.tsl9.morphe;

import android.app.*;
import android.content.*;
import android.graphics.Rect;
import android.net.Uri;
import android.os.*;
import android.provider.MediaStore;
import android.view.*;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Optional API29+ emulator test through the real system DocumentsUI. No BLE calls. */
final class DocumentJourney {
    private final Instrumentation test;private final Activity activity;private final UiAutomation ui;
    private int checks;private final String suffix=Long.toString(SystemClock.elapsedRealtime());
    DocumentJourney(Instrumentation t,Activity a){test=t;activity=a;ui=t.getUiAutomation();}
    private void status(String detail){Bundle b=new Bundle();b.putString("documentJourney",detail);test.sendStatus(1,b);}
    private void check(boolean value,String detail){checks++;if(!value)throw new AssertionError(detail);}
    private Object field(String name)throws Exception{Field f=activity.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(activity);}
    private Button button(View v,String name){if(v instanceof Button&&name.equals(((Button)v).getText().toString()))return(Button)v;if(v instanceof ViewGroup){ViewGroup group=(ViewGroup)v;for(int i=0;i<group.getChildCount();i++){Button b=button(group.getChildAt(i),name);if(b!=null)return b;}}return null;}
    private void pressApp(String name){test.runOnMainSync(()->{Button b=button(activity.getWindow().getDecorView(),name);if(b==null||!b.isEnabled())throw new AssertionError("App button unavailable: "+name);b.performClick();});}
    private interface Match{boolean matches(AccessibilityNodeInfo n);}
    private AccessibilityNodeInfo find(AccessibilityNodeInfo n,Match match){if(n==null)return null;if(match.matches(n))return n;for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo found=find(n.getChild(i),match);if(found!=null)return found;}return null;}
    private AccessibilityNodeInfo waitNode(Match match,String label){long end=SystemClock.elapsedRealtime()+30000;do{AccessibilityNodeInfo found=find(ui.getRootInActiveWindow(),match);if(found!=null)return found;SystemClock.sleep(200);}while(SystemClock.elapsedRealtime()<end);throw new AssertionError("DocumentsUI missing "+label+"; "+tree(ui.getRootInActiveWindow()));}
    private String tree(AccessibilityNodeInfo n){if(n==null)return "null";StringBuilder s=new StringBuilder();walk(n,s);return s.toString();}
    private void walk(AccessibilityNodeInfo n,StringBuilder out){if(n==null||out.length()>6000)return;if(n.getText()!=null||n.getContentDescription()!=null)out.append('[').append(n.getViewIdResourceName()).append(':').append(n.getText()).append('/').append(n.getContentDescription()).append(']');for(int i=0;i<n.getChildCount();i++)walk(n.getChild(i),out);}
    private boolean text(AccessibilityNodeInfo n,String value){return value.contentEquals(n.getText()==null?"":n.getText())||value.contentEquals(n.getContentDescription()==null?"":n.getContentDescription());}
    private void click(Match match,String label){
        long end=SystemClock.elapsedRealtime()+10000;
        do{
            AccessibilityNodeInfo node=waitNode(n->n.isVisibleToUser()&&n.isEnabled()&&match.matches(n),label);
            AccessibilityNodeInfo clickable=node;while(clickable!=null&&!clickable.isClickable())clickable=clickable.getParent();
            if(clickable!=null&&clickable.performAction(AccessibilityNodeInfo.ACTION_CLICK))return;
            // ListView labels may expose no actionable row. Reacquire a current,
            // visible node before injecting a normal touch inside its own bounds.
            AccessibilityNodeInfo fresh=find(ui.getRootInActiveWindow(),n->n.isVisibleToUser()&&n.isEnabled()&&match.matches(n));
            if(fresh!=null){Rect rect=new Rect();fresh.getBoundsInScreen(rect);if(!rect.isEmpty()){
                long time=SystemClock.uptimeMillis();MotionEvent down=MotionEvent.obtain(time,time,MotionEvent.ACTION_DOWN,rect.centerX(),rect.centerY(),0),up=MotionEvent.obtain(time,time+40,MotionEvent.ACTION_UP,rect.centerX(),rect.centerY(),0);
                down.setSource(InputDevice.SOURCE_TOUCHSCREEN);up.setSource(InputDevice.SOURCE_TOUCHSCREEN);
                try{boolean accepted=ui.injectInputEvent(down,true);accepted=ui.injectInputEvent(up,true)&&accepted;if(accepted)return;}finally{down.recycle();up.recycle();}
            }}
            SystemClock.sleep(200);
        }while(SystemClock.elapsedRealtime()<end);
        throw new AssertionError("DocumentsUI click failed: "+label);
    }
    private boolean inRoots(AccessibilityNodeInfo n){for(AccessibilityNodeInfo p=n;p!=null;p=p.getParent()){String id=p.getViewIdResourceName();if(id!=null&&id.endsWith(":id/roots_list"))return true;}return false;}
    private void downloads(){
        click(n->text(n,"Show roots"),"Show roots");
        try{ui.waitForIdle(300,3000);}catch(java.util.concurrent.TimeoutException e){throw new AssertionError("Roots drawer did not become idle",e);}
        // DocumentsUI can acknowledge ACTION_CLICK on an ancestor without
        // selecting the root. Touch the actual visible Downloads label instead.
        AccessibilityNodeInfo downloads=waitNode(n->n.isVisibleToUser()&&n.isEnabled()&&text(n,"Downloads")&&inRoots(n),"Downloads entry in roots_list");
        Rect bounds=new Rect();downloads.getBoundsInScreen(bounds);if(bounds.isEmpty())throw new AssertionError("Downloads root has no visible bounds");
        long time=SystemClock.uptimeMillis();MotionEvent down=MotionEvent.obtain(time,time,MotionEvent.ACTION_DOWN,bounds.centerX(),bounds.centerY(),0),up=MotionEvent.obtain(time,time+40,MotionEvent.ACTION_UP,bounds.centerX(),bounds.centerY(),0);
        down.setSource(InputDevice.SOURCE_TOUCHSCREEN);up.setSource(InputDevice.SOURCE_TOUCHSCREEN);
        try{boolean accepted=ui.injectInputEvent(down,true);accepted=ui.injectInputEvent(up,true)&&accepted;if(!accepted)throw new AssertionError("Downloads root touch rejected");}finally{down.recycle();up.recycle();}
        try{ui.waitForIdle(300,3000);}catch(java.util.concurrent.TimeoutException e){throw new AssertionError("Downloads root did not become idle",e);}
        // Re-selecting the current root may leave the drawer open on this
        // system provider. Close it with Back only after verifying Downloads.
        AccessibilityNodeInfo directory=find(ui.getRootInActiveWindow(),n->{String id=n.getViewIdResourceName();return id!=null&&id.endsWith(":id/breadcrumb_text")&&text(n,"Downloads");});
        AccessibilityNodeInfo drawer=find(ui.getRootInActiveWindow(),n->{String id=n.getViewIdResourceName();return id!=null&&id.endsWith(":id/roots_list")&&n.isVisibleToUser();});
        if(directory!=null&&drawer!=null)test.sendKeyDownUpSync(KeyEvent.KEYCODE_BACK);
        long end=SystemClock.elapsedRealtime()+10000;do{AccessibilityNodeInfo root=find(ui.getRootInActiveWindow(),n->{String id=n.getViewIdResourceName();return id!=null&&id.endsWith(":id/roots_list")&&n.isVisibleToUser();});if(root==null)return;SystemClock.sleep(200);}while(SystemClock.elapsedRealtime()<end);
        throw new AssertionError("DocumentsUI roots drawer did not close");
    }
    private String export(String button,String name)throws Exception{
        pressApp(button);downloads();
        AccessibilityNodeInfo input=waitNode(n->"android.widget.EditText".contentEquals(n.getClassName()==null?"":n.getClassName()),"save filename");
        Bundle args=new Bundle();args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,name);check(input.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,args),"set export filename");
        click(n->text(n,"Save")||text(n,"SAVE"),"Save");
        waitNode(n->"dev.tsl9.morphe.test".contentEquals(n.getPackageName()==null?"":n.getPackageName()),"return from save provider");
        // The host runner reads the real files through ADB after this test finishes.
        Bundle receipt=new Bundle();receipt.putString("documentFile",name);test.sendStatus(1,receipt);return name;
    }
    int run()throws Exception{
        status("create synthetic local fixture");
        check(Build.VERSION.SDK_INT>=29,"real DocumentsUI journey needs API29+");
        String name="tsl9-smoke-input-"+suffix+".bin";byte[] bytes=new byte[1031];Arrays.fill(bytes,(byte)0x5a);byte[] marker="SYNTHETIC_ONLY_NOT_FIRMWARE".getBytes(StandardCharsets.US_ASCII);System.arraycopy(marker,0,bytes,0,marker.length);
        ContentResolver resolver=test.getTargetContext().getContentResolver();ContentValues values=new ContentValues();values.put(MediaStore.Downloads.DISPLAY_NAME,name);values.put(MediaStore.Downloads.MIME_TYPE,"application/octet-stream");values.put(MediaStore.Downloads.RELATIVE_PATH,"Download/");
        Uri fixture=resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,values);check(fixture!=null,"create local synthetic picker fixture");
        try{
            try(OutputStream out=resolver.openOutputStream(fixture)){if(out==null)throw new IOException("fixture stream");out.write(bytes);}
            status("open system bin picker");pressApp(activity.getString(R.string.pick_bin));downloads();click(n->text(n,name),"synthetic bin file");
            // Accessibility actions return before the provider's Activity result arrives.
            status("await selected file result");long resultDeadline=SystemClock.elapsedRealtime()+10000;final boolean[] selected={false};
            do{test.runOnMainSync(()->{try{selected[0]=name.equals(field("imageName"));}catch(Exception e){throw new RuntimeException(e);}});if(selected[0])break;SystemClock.sleep(200);}while(SystemClock.elapsedRealtime()<resultDeadline);
            test.waitForIdleSync();
            final Throwable[] fail={null};test.runOnMainSync(()->{try{FirmwareImage image=(FirmwareImage)field("image");FirmwareImage expected=FirmwareImage.parse(bytes,FirmwareImage.Format.RAW_FF_PAD);check(name.equals(field("imageName")),"real picker delivers selected display name");check(image!=null&&image.fileBytes==1031&&image.paddingBytes==1017,"real ContentResolver reads custom bin");check(expected.sha256.equals(image.sha256)&&expected.transferSha256.equals(image.transferSha256),"real picker preserves original and transfer hashes");check(!button(activity.getWindow().getDecorView(),activity.getString(R.string.flash)).isEnabled(),"synthetic fixture cannot flash without BLE");}catch(Throwable t){fail[0]=t;}});if(fail[0]!=null)throw new AssertionError(fail[0]);
            status("export hardware log through system provider");export(activity.getString(R.string.hardware_export),"tsl9-smoke-hardware-"+suffix+".jsonl");
            status("export phone debug log through system provider");export(activity.getString(R.string.debug_export),"tsl9-smoke-debug-"+suffix+".txt");
            return checks;
        }finally{resolver.delete(fixture,null,null);}
    }
}
