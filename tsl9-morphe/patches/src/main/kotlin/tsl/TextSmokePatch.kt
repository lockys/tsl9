package tsl

import app.morphe.patcher.patch.AppTarget
import app.morphe.patcher.patch.Compatibility
import app.morphe.patcher.patch.rawResourcePatch
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest

private const val WX_PATH = "assets/SaaA_embed/release_2_wx64f19032ca1ea79e.wxapkg"
private const val WX_SHA256 = "6476a038c1861a431c5039b1644774cb60c338ce64ec64802955f069e19c37e3"

val textSmokePatch = rawResourcePatch(
    name = "TSL wxapkg text smoke test",
    description = "Change only the first tab label from 状态 to 狀態·M (TSL 1.2.7).",
    default = true
) {
    compatibleWith(Compatibility(
        packageName = "com.tencent.weauth",
        name = "TSL electronic module",
        targets = listOf(AppTarget(version = "1.2.7"))
    ))
    execute {
        check(packageMetadata.packageName == "com.tencent.weauth" &&
            packageMetadata.versionName == "1.2.7" && packageMetadata.versionCode == "127") {
            "This smoke patch requires exactly com.tencent.weauth 1.2.7 (127)."
        }
        val file = get(WX_PATH)
        val bytes = file.readBytes()
        val digest = MessageDigest.getInstance("SHA-256").digest(bytes)
            .joinToString("") { "%02x".format(it.toInt() and 255) }
        check(digest == WX_SHA256) { "Unexpected original wxapkg; refusing to patch." }
        file.writeBytes(patchTabLabel(bytes))
    }
}

private data class Entry(val name: String, val offsetSlot: Int, val offset: Int, val size: Int)

/** Splice one disjoint config range, keeping all original overlapping JS aliases intact. */
internal fun patchTabLabel(bytes: ByteArray): ByteArray {
    val input = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
    check(bytes.size >= 18 && bytes[0] == 0xBE.toByte() && bytes[13] == 0xED.toByte())
    val indexSize = input.getInt(5)
    val bodySize = input.getInt(9)
    check(indexSize >= 4 && bodySize >= 0 && 14L + indexSize + bodySize == bytes.size.toLong())
    input.position(14)
    val count = input.int
    check(count == 76) { "Unexpected wxapkg entry count." }
    val entries = (0 until count).map {
        check(input.position() + 4 <= 14 + indexSize)
        val length = input.int
        check(length > 0 && input.position().toLong() + length + 8 <= 14L + indexSize)
        val nameBytes = ByteArray(length).also { input.get(it) }
        val slot = input.position()
        val offset = input.int
        val size = input.int
        check(offset >= 14 + indexSize && size >= 0 && offset.toLong() + size <= bytes.size)
        Entry(nameBytes.toString(Charsets.UTF_8), slot, offset, size)
    }
    check(input.position() == 14 + indexSize && entries.map { it.name }.toSet().size == count)
    val target = entries.single { it.name == "/app-config.json" }
    val end = target.offset + target.size
    check(entries.filter { it != target }.none { it.offset < end && it.offset + it.size > target.offset }) {
        "Config overlaps another entry; this splice is not applicable."
    }
    val old = "\"text\":\"状态\""
    val new = "\"text\":\"狀態·M\""
    val text = bytes.copyOfRange(target.offset, end).toString(Charsets.UTF_8)
    check(text.split(old).size == 2) { "Expected exactly one original tab label." }
    val replacement = text.replace(old, new).toByteArray(Charsets.UTF_8)
    val delta = replacement.size - target.size
    check(delta == 3) { "Unexpected UTF-8 size delta." }
    val result = bytes.copyOfRange(0, target.offset) + replacement + bytes.copyOfRange(end, bytes.size)
    val output = ByteBuffer.wrap(result).order(ByteOrder.BIG_ENDIAN)
    output.putInt(9, bodySize + delta)
    entries.forEach { entry ->
        if (entry.offset >= end) output.putInt(entry.offsetSlot, entry.offset + delta)
        if (entry == target) output.putInt(entry.offsetSlot + 4, replacement.size)
    }
    return result
}
