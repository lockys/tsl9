# OTA E response: protocol classification

[繁體中文](ota-e-response.zh-TW.md)

The user reported E while attempting an update with a reconstructed BIN, and the same final E when using an official BIN. The App is tsl9-morphe APK; afterward, the device can reconnect and return firmware version information. These are user-reported hardware observations; the agent did not operate the hardware.

The user explicitly identified the [TX integrated candidate](../artifacts/offline-images/ID2966-V4.1.60-tx-integrated/readme.en.md) and confirmed the same final message. Its local SHA256 is `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. The screenshot selects official SHA `0ee64183...fb667`; the candidate result is a textual hardware report, not an independent candidate transfer capture.

The comparison is consistent with END. E is not a confirmed failure symptom. This candidate now has user-reported hardware evidence of OTA-session completion and matching page readback. Execution after restart and complete original-hardware compatibility remain unproved. See the [observation record](../artifacts/offline-images/ID2966-V4.1.60-tx-integrated/field-observations.json).

## Confirmed offline evidence

1. The existing APK extraction's `app-service.js` sends `TxSend(69, ...)` from `UpgradeEnd()` and dispatches received command69 to `UpdateVerNumber0x45()`. Decimal69 is0x45/ASCII E. This belongs to the update-end flow, rather than a generic error classification based on its letter. Script SHA256: `c5eb7ae87e5edf310379f19743d720114c9717c3484b8abd30ad8b158affc017`. No script network operation was executed.
2. Current Morphe updater source `OtaSession.java` sends command0x45 from `end()`. `onPacket()` requires the expected command, then transitions END to DONE. Its comment explicitly says E payload semantics are undocumented. This is a session result, not proof that the new runtime executed. Source SHA256: `da7a612e0314cab3ef46a3c5c2650f8a342e94b5d59607174bbc194dd393e7f0`.
3. Official ID2966 V4.1.60 Runtime, SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, intentionally requests an empty E reply:

| Original VA | Observed operation |
| --- | --- |
| 0x9C6A/0x9C6E | Compare command0x45 and branch to0x9DF8 |
| 0x9DF8..0x9E18 | Require active, full length15, payload mode0 and zero return from0x92F2 |
| 0x9E2C | Clear active |
| 0x9E30/0x9E44 | Request callbacks0x8E18/0x99E8 with parameters200/400; no elapsed-time claim |
| 0x9E48..0x9E50 | Set A3=A2=0 and A1=0x45; jump to common reply |
| 0x9DB4 -> 0x13E98 -> 0x8A56 | Request an empty-payload TX queue handoff; delivery is not established |

This Runtime branch does not establish whole-image CRC, callback completion or new-firmware startup. It accepts mode0, whereas the current APP-only updater sends mode1. Today's E cannot therefore be attributed to this Runtime path without identifying the frame and active updater/BOOT image.

## Why V4.1.00 is not an image fingerprint

The user supplied a further same-device functional comparison: the seat function does not operate after flashing official V4.1.00, then works normally after updating official V4.1.60 through our tsl9-morphe APK. This user-reported hardware behavior supports successful official-image updating through the APK and a change in the device's running behavior, beyond E or page readback alone. It does not validate every hardware/image combination or establish execution of the reconstructed TX candidate.

The user reported official updates still displaying V4.1.00 while seat behavior changed. The following actual code paths allow those observations to coexist:

1. Original APK `getinfo(s)` initializes `fw_ver=s[2]<<8`. Only a positive server `e.fw_ver` replaces it; cached deviceinfo can also be restored. Readable extraction `7FE9D4A3BD32C12F198FBCA429EFC052.js` lines27,29,37 and original app-service.js line3019 contain these steps.
2. Original `getver()` at app-service.js line4012 formats hexadecimal nibbles and the last two digits. Therefore `0x41<<8` displays `V4.1.00`. This conditional derivation does not establish why a particular server/cache path supplied that value.
3. Local standalone updater `DeviceInfoSnapshot.java` likewise treats A0 `data[2]` only as a two-nibble prefix; `revisionKnown()` always returns false.
4. Actual ID2966 code at `0x9E84..0x9EA6` uses the fresh `0x4004C` provider to request copying8 bytes from numeric source `0x08077B00` to active SP, then returns two words. A0 producer `0x13346..0x133A2` places metadata byte1 in final payload index2. `0x1359A..0x135AC` calls the reply entry with command160 and length76. These three ranges total144 bytes/51 instructions and were checked row-for-row against the official BIN.

The firmware chain requires a normally returning copy provider, valid SP/GP, no adverse aliases/IRQ/external mutation and no later helper changes to the header. It is not a measurement of physical metadata or proof of chip identity. Original ledgers are `experiments/tsl9-v4160-startup/evidence/direct-expansion-cfg.json` at0x9E84 and `code-continuation-cfg.json` at0x13346/0x1359A.

## Current boundary

END semantics apply to decoded command0x45, rather than arbitrary payload0x45,error0x0E or App text. The supplied App screenshot and official/candidate comparison remove E itself as a demonstrated failure symptom.

No candidate-selection hash screenshot, raw frame or exact App build was supplied. Existing observations are retained separately; no reflash is requested. Version text alone does not identify an image, and ACK/App DONE/readback have different evidence scopes. No firmware modification, hardware operation or network call was performed for this classification.
