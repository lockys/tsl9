# OTA update evidence

[繁體中文](OTA-EVIDENCE.md)

At update start the app saves a separate local record of the selected file and transmitted payload SHA-256, format, page counts, commands, page numbers, retries, readback policy, final E reply and readback result. Entries use the phone's clock. Later A0 version bytes may be recorded; they do not by themselves establish device identity or whether the observation occurred after reboot.

After completion or interruption use the existing **Export debug log** button. The `LATEST OTA EVIDENCE` section is independent of the rolling debug log. It accepts only specified fields and excludes UID, VIN, MAC, passwords and firmware payloads. Review the entire debug export before sharing. A new update replaces the prior OTA record, so export anything needed first. The record is limited to 512 KiB; during the same app session an export flags a write failure as potentially incomplete.

`readbackVerified=true` means the app's per-page comparison passed; `eReplyReceived=true` means an E response arrived; `restartVerified=false` means execution after reboot is unverified. Do not reflash solely to produce a log. This debug APK has not been tested on physical hardware.
