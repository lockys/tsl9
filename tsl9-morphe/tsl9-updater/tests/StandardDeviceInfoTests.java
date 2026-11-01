package dev.tsl9.morphe;
import java.nio.charset.StandardCharsets;

public final class StandardDeviceInfoTests {
    private static void eq(String expected, String actual) {
        if (!expected.equals(actual)) throw new AssertionError(expected + " != " + actual);
    }
    private static byte[] bytes(String text) { return text.getBytes(StandardCharsets.UTF_8); }
    public static void main(String[] args) {
        eq("V4.1.60", StandardDeviceInfo.safeValue(0, bytes(" V4.1.60 ")));
        eq("unavailable", StandardDeviceInfo.safeValue(5, bytes("V4.1.60")));
        eq("empty", StandardDeviceInfo.safeValue(0, null));
        eq("empty", StandardDeviceInfo.safeValue(0, bytes(" ")));
        eq("redacted", StandardDeviceInfo.safeValue(0, bytes("ABC123456789")));
        eq("redacted", StandardDeviceInfo.safeValue(0, bytes("123456")));
        eq("redacted", StandardDeviceInfo.safeValue(0, bytes("value@hidden")));
        System.out.println("StandardDeviceInfoTests: 7 synthetic privacy and status checks passed.");
    }
}
