package com.lockys.tsl9updater;
/** Typed validation failure rendered only at the Android UI boundary. */
public final class UiException extends IllegalArgumentException {
    public final UiMessage detail;
    public UiException(UiMessage detail){super(detail.toString());this.detail=detail;}
}
