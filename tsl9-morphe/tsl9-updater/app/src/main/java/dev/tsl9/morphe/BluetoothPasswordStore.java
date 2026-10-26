package dev.tsl9.morphe;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.Arrays;
import javax.crypto.*;
import javax.crypto.spec.GCMParameterSpec;

/** AES-GCM ciphertext in no-backup storage; the key stays in Android Keystore. */
final class BluetoothPasswordStore {
    private static final byte[] AAD="TSL9 BLE password v1".getBytes(StandardCharsets.US_ASCII);
    private final File file;
    private final String alias;
    BluetoothPasswordStore(Context context){this(new File(context.getNoBackupFilesDir(),"bluetooth-password.enc"),"tsl9.bluetooth.password.v1");}
    BluetoothPasswordStore(File file,String alias){this.file=file;this.alias=alias;}
    static boolean valid(String value){return value!=null&&value.matches("[\\x20-\\x7e]{4}");}
    String load(){
        byte[] plain=null;
        try(DataInputStream input=new DataInputStream(new AtomicFile(file).openRead())){
            // v1: one format byte, 12-byte nonce, four encrypted bytes + 16-byte tag.
            byte[] encoded=new byte[33];input.readFully(encoded);
            if(encoded[0]!=1||input.read()!=-1)return "";
            SecretKey key=key(false);if(key==null)return "";
            Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE,key,new GCMParameterSpec(128,Arrays.copyOfRange(encoded,1,13)));cipher.updateAAD(AAD);
            plain=cipher.doFinal(encoded,13,20);
            String value=new String(plain,StandardCharsets.US_ASCII);
            return valid(value)?value:"";
        }catch(IOException|GeneralSecurityException|RuntimeException unavailable){return "";}
        finally{if(plain!=null)Arrays.fill(plain,(byte)0);}
    }
    boolean remember(String value){
        if(!valid(value))return false;
        byte[] plain=value.getBytes(StandardCharsets.US_ASCII);AtomicFile target=new AtomicFile(file);FileOutputStream output=null;
        try{
            Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");cipher.init(Cipher.ENCRYPT_MODE,key(true));cipher.updateAAD(AAD);
            byte[] encrypted=cipher.doFinal(plain),nonce=cipher.getIV();
            if(nonce==null||nonce.length!=12||encrypted.length!=20)return false;
            byte[] encoded=new byte[33];encoded[0]=1;System.arraycopy(nonce,0,encoded,1,12);System.arraycopy(encrypted,0,encoded,13,20);
            output=target.startWrite();output.write(encoded);target.finishWrite(output);output=null;return true;
        }catch(IOException|GeneralSecurityException|RuntimeException unavailable){if(output!=null)target.failWrite(output);return false;}
        finally{Arrays.fill(plain,(byte)0);}
    }
    private SecretKey key(boolean create)throws GeneralSecurityException,IOException{
        KeyStore keys=KeyStore.getInstance("AndroidKeyStore");keys.load(null);
        Key existing=keys.getKey(alias,null);
        if(existing instanceof SecretKey)return (SecretKey)existing;
        if(existing!=null||!create)return null;
        KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(alias,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT).setKeySize(256).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());
        return generator.generateKey();
    }
}
