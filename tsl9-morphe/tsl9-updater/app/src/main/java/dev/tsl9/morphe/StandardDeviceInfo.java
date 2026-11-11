package dev.tsl9.morphe;

import java.nio.charset.StandardCharsets;

/** Standard DIS values only; serial numbers and opaque identifiers are never read. */
final class StandardDeviceInfo {
    private StandardDeviceInfo() {}
    static String safeValue(int status, byte[] value) {
        if (status != 0) return "unavailable";
        if (value == null || value.length == 0) return "empty";
        String text = new String(value, StandardCharsets.UTF_8).trim();
        if (text.length() == 0) return "empty";
        if (text.length() > 48 || !text.matches("[A-Za-z0-9 ._+/-]+")
                || text.matches(".*[A-Za-z0-9]{9,}.*")
                || text.matches(".*[0-9]{6,}.*")) return "redacted";
        return text;
    }
}
