package com.lockys.tsl9updater;
import static com.lockys.tsl9updater.UiMessage.m;

import java.security.*;
import java.util.*;

/** Explicit formats only. Padding is an opt-in format, never a silent conversion. */
public final class FirmwareImage {
    public enum Format { PAGED, RAW, RAW_FF_PAD }
    public static final int PAYLOAD=1024, PAGE=1026, MAX_PAGES=256;
    public final String sha256,transferSha256;public final int fileBytes,paddingBytes;public final Format format;
    private final byte[][] pages;
    private FirmwareImage(byte[] source,Format f,byte[][] p){
        pages=p;fileBytes=source.length;format=f;paddingBytes=f==Format.RAW_FF_PAD?p.length*PAYLOAD-source.length:0;
        try{sha256=digest(MessageDigest.getInstance("SHA-256").digest(source));MessageDigest transferred=MessageDigest.getInstance("SHA-256");for(byte[] page:p)transferred.update(page,2,PAYLOAD);transferSha256=digest(transferred.digest());}
        catch(NoSuchAlgorithmException e){throw new IllegalStateException(e);}
    }
    public static FirmwareImage parse(byte[] bytes,Format format){
        if(bytes==null||format==null)throw new UiException(m("bin_missing"));
        int unit=format==Format.PAGED?PAGE:PAYLOAD;
        if(bytes.length==0||(format!=Format.RAW_FF_PAD&&bytes.length%unit!=0))throw new UiException(m("bin_length",unit));
        int count=(bytes.length+unit-1)/unit;if(count>MAX_PAGES)throw new UiException(m("bin_limit"));
        byte[][] pages=new byte[count][];
        for(int j=0;j<count;j++){
            if(format==Format.PAGED){pages[j]=Arrays.copyOfRange(bytes,j*PAGE,(j+1)*PAGE);if(((pages[j][0]&255)<<8|(pages[j][1]&255))!=j)throw new UiException(m("bin_index",j));}
            else{pages[j]=new byte[PAGE];if(format==Format.RAW_FF_PAD)Arrays.fill(pages[j],(byte)0xff);pages[j][0]=(byte)(j>>>8);pages[j][1]=(byte)j;int n=Math.min(PAYLOAD,bytes.length-j*PAYLOAD);System.arraycopy(bytes,j*PAYLOAD,pages[j],2,n);}
        }return new FirmwareImage(bytes,format,pages);
    }
    public int pageCount(){return pages.length;}
    public byte[] page(int n){return pages[n].clone();}
    private static String digest(byte[] bytes){StringBuilder b=new StringBuilder();for(byte v:bytes)b.append(String.format(Locale.ROOT,"%02x",v&255));return b.toString();}
}
