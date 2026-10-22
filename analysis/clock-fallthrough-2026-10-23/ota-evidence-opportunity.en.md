# OTA evidence history: source review and opportunity

[繁體中文](ota-evidence-opportunity.zh-TW.md) · [File digests and evidence type](ota-evidence-opportunity.json)

This review reads the existing Android source only. It does not run the app, storage durability tests, Bluetooth or hardware.

- `MainActivity.onCreate / flushLog` (51–54, 331–347) already writes, reloads and exports a text log containing selected-image/planned-transfer hashes. Truncation and ignored write errors leave completeness and crash durability unproved.
- `FirmwareImage` (13–15) hashes the planned payload. That hash does not measure hardware receipt or startup.
- `OtaSession.onPacket` (60–75) already compares optional page readback. E completes END handling; its payload semantics and postboot behavior remain unknown. Existing Traditional Chinese UI distinguishes matched/skipped/unavailable readback and labels postboot verification incomplete.
- `MainActivity` creates a fresh OTA object (43–55) and restores text history only. `DeviceInfoSnapshot` (3–12) keeps full revision unknown. Separate hardware capture excludes simultaneous OTA, so it does not provide a full OTA receipt.

The useful gap is a local, session-keyed append/atomic evidence receipt linking image/transfer identity, readback policy and measured results, END acknowledgment, and separately sourced runtime/function observations. Reopening should show history without resuming transmission. Default storage should exclude UID/VIN/MAC and unreviewed payloads.

This feature is not implemented. Source roots use `MORPHE_JAVA_ROOT` / `MORPHE_MAIN_ROOT`; see JSON for complete file digests. This pass does not migrate or unlock Morphe directories.
