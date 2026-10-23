package com.lockys.tsl9updater;
import java.util.Arrays;
/** Locale-independent message data; protocol code has no Android dependency. */
public final class UiMessage {
    public final String key; public final Object[] args;
    private UiMessage(String key,Object[] args){this.key=key;this.args=args.clone();}
    public static UiMessage m(String key,Object... args){return new UiMessage(key,args);}
    public static UiMessage raw(String text){return m("raw",text);}
    @Override public String toString(){return key+Arrays.toString(args);}
}
