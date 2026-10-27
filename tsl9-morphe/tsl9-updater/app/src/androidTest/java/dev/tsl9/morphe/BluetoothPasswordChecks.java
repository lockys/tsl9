package dev.tsl9.morphe;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Instrumentation;
import android.widget.EditText;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.Arrays;

/** Synthetic passwords and a recording callback; each UI step waits for idle. */
final class BluetoothPasswordChecks {
    private final Activity activity;private final Instrumentation instrumentation;
    private int checks;private AlertDialog dialog;
    BluetoothPasswordChecks(Instrumentation instrumentation,Activity activity){this.instrumentation=instrumentation;this.activity=activity;}
    private void check(boolean ok,String why){checks++;if(!ok)throw new AssertionError(why);}
    private interface Step {void run()throws Exception;}
    private void ui(Step step)throws Exception{
        final Throwable[] failure={null};
        instrumentation.runOnMainSync(()->{try{step.run();}catch(Throwable error){failure[0]=error;}});
        instrumentation.waitForIdleSync();
        if(failure[0]!=null)throw new RuntimeException(failure[0]);
    }
    private static final class Wire implements BluetoothPasswordDialog.Events {
        int sends,failures;byte[] last;
        public void submit(byte[] password){sends++;last=password.clone();Arrays.fill(password,(byte)0);}
        public void rememberFailed(){failures++;}
    }
    private File file(String name){return new File(activity.getNoBackupFilesDir(),name+".enc");}
    private String alias(String name){return "tsl9.password.synthetic."+name;}
    private BluetoothPasswordStore store(String name){return new BluetoothPasswordStore(file(name),alias(name));}
    private void cleanup(String name)throws Exception{new android.util.AtomicFile(file(name)).delete();KeyStore keys=KeyStore.getInstance("AndroidKeyStore");keys.load(null);if(keys.containsAlias(alias(name)))keys.deleteEntry(alias(name));}
    private byte[] read(File file)throws IOException{try(FileInputStream input=new FileInputStream(file);ByteArrayOutputStream output=new ByteArrayOutputStream()){byte[] chunk=new byte[128];int n;while((n=input.read(chunk))!=-1)output.write(chunk,0,n);return output.toByteArray();}}
    private void write(File file,byte[] bytes)throws IOException{try(FileOutputStream output=new FileOutputStream(file)){output.write(bytes);}}
    private EditText input(){return dialog.findViewById(android.R.id.edit);}
    private void open(BluetoothPasswordStore store,Wire wire)throws Exception{ui(()->{dialog=BluetoothPasswordDialog.create(activity,store,wire);dialog.show();});}
    private void type(String value)throws Exception{ui(()->input().setText(value));}
    private void verify()throws Exception{ui(()->dialog.getButton(AlertDialog.BUTTON_POSITIVE).performClick());}
    private void dismiss()throws Exception{ui(()->{if(dialog!=null)dialog.dismiss();});}
    int run(String mode)throws Exception{
        final String sample="Q7!z",replacement="T2@x",name="dialog-checks",restart="restart-checks";
        if("preview".equals(mode)){
            cleanup(restart);
            try{
                check(store(restart).remember(sample),"preview fixture saved through real encrypted store");Wire wire=new Wire();open(store(restart),wire);
                ui(()->{check(sample.contentEquals(input().getText()),"preview shows the remembered value");check(input().getTransformationMethod() instanceof android.text.method.PasswordTransformationMethod,"preview password remains masked");check(wire.sends==0,"preview never transmits Bluetooth");});
                instrumentation.getUiAutomation().waitForIdle(500,5000);
                android.graphics.Bitmap screenshot=instrumentation.getUiAutomation().takeScreenshot();check(screenshot!=null,"actual native screenshot captured");
                try(FileOutputStream output=new FileOutputStream(new File(activity.getExternalFilesDir(null),"password-prefill.png"))){check(screenshot.compress(android.graphics.Bitmap.CompressFormat.PNG,100,output),"native PNG saved");}finally{screenshot.recycle();}
            }finally{dismiss();cleanup(restart);}return checks;
        }
        if("seed".equals(mode)){cleanup(restart);check(store(restart).remember(sample),"restart fixture saved through real Android Keystore");return checks;}
        if("restore".equals(mode)){
            try{Wire wire=new Wire();open(store(restart),wire);ui(()->{check(sample.contentEquals(input().getText()),"password prefills after a separate App process starts");check(wire.sends==0,"process restart never automatically sends a password");});}finally{dismiss();cleanup(restart);}return checks;
        }
        cleanup(name);Wire wire=new Wire();
        try{
            BluetoothPasswordStore store=store(name);check(store.load().isEmpty(),"first launch has no remembered password");
            open(store,wire);ui(()->{check(input().getText().length()==0,"first password field is empty");check(!input().isSaveEnabled(),"password excluded from view saved state");check(input().getTransformationMethod() instanceof android.text.method.PasswordTransformationMethod,"remembered input remains masked");});
            for(String invalid:new String[]{"123","12345","全形密碼"}){type(invalid);verify();ui(()->check(dialog.isShowing()&&input().getError()!=null,"invalid password keeps dialog open"));check(wire.sends==0&&store.load().isEmpty(),"invalid input neither sends nor overwrites stored value");}
            type(sample);verify();check(wire.sends==1&&Arrays.equals(wire.last,sample.getBytes(StandardCharsets.US_ASCII)),"only Verify explicitly submits four original bytes");ui(()->check(!dialog.isShowing(),"manual submission closes password dialog"));
            open(store(name),wire);ui(()->check(sample.contentEquals(input().getText()),"next password dialog prefills the last submitted password"));check(wire.sends==1,"prefill does not submit authentication");
            type(replacement);ui(()->dialog.getButton(AlertDialog.BUTTON_NEGATIVE).performClick());check(sample.equals(store(name).load()),"cancel does not overwrite the remembered password");ui(()->check(input().length()==0,"dismissed input is cleared"));
            byte[] first=read(file(name));check(!new String(first,StandardCharsets.ISO_8859_1).contains(sample),"persistent file does not contain plaintext password");
            check(store.remember(sample),"same valid password can be saved again");check(!Arrays.equals(first,read(file(name))),"each encrypted write uses a fresh nonce");
            check(!store.remember("bad")&&sample.equals(store.load()),"invalid saves preserve the previous password");
            check(store.remember(" a! ")&&" a! ".equals(store(name).load()),"ASCII spaces are preserved rather than trimmed");
            check(store.remember(replacement)&&replacement.equals(store(name).load()),"manual replacement persists across new store instances");
            byte[] damaged=read(file(name));damaged[damaged.length-1]^=1;write(file(name),damaged);check(store.load().isEmpty(),"tampered ciphertext falls back to empty manual entry");check(store.remember(sample)&&sample.equals(store.load()),"manual submission replaces damaged ciphertext");
            cleanup(name);check(store.load().isEmpty(),"missing key or data never blocks manual entry");check(store.remember(sample),"store recovers after key and file reset");
            File backup=new File(file(name).getPath()+".bak");write(backup,read(file(name)));check(store.clear()&&store.load().isEmpty()&&!backup.exists(),"forget removes ciphertext and atomic backup");check(store.remember(sample),"password can be remembered again after forget");
            File blocked=file("blocked-checks");write(blocked,new byte[]{1});
            try{BluetoothPasswordStore unavailable=new BluetoothPasswordStore(new File(blocked,"child.enc"),alias("blocked-checks"));open(unavailable,wire);type(replacement);int before=wire.sends;verify();check(wire.sends==before+1&&wire.failures==1,"storage failure still permits explicit manual authentication");}finally{cleanup("blocked-checks");}
        }finally{dismiss();cleanup(name);if(wire.last!=null)Arrays.fill(wire.last,(byte)0);}
        return checks;
    }
}
