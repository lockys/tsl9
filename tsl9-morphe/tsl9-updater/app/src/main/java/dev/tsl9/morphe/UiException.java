package dev.tsl9.morphe;
/** Typed validation failure rendered only at the Android UI boundary. */
public final class UiException extends IllegalArgumentException {
    public final UiMessage detail;
    public UiException(UiMessage detail){super(detail.toString());this.detail=detail;}
}
