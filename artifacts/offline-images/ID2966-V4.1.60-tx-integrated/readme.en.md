# Experimental TX image: not verified as flashable

[繁體中文](README.md)

`NOT-FLASH-VALIDATED-tx-integrated.bin` is the identical complete experimental image produced by fresh C11 and C++17 pipelines. On2026-10-22, the user reported updating this candidate through tsl9-morphe APK and receiving the same final status as the official control: E received, all pages read back equal, version/restart not verified. This establishes a user-reported hardware OTA-session/readback result; complete compatibility and execution after restart remain unproved.

## User-reported hardware observation

[field-observations.json](field-observations.json) separates local binary facts, the official-control screenshot and the candidate report. The supplied screenshot selects the official `ID-2966-V4.1.60-decoded.bin`; the user subsequently identified this candidate and confirmed the same final message. No candidate-selection hash screenshot or raw transfer capture was supplied, so the official screenshot is not treated as byte-level transfer evidence for this candidate.

The user separately reported official updates still displaying V4.1.00 despite changed seat behavior. That observation is not attributed to the candidate. Neither the displayed version nor an E acknowledgment identifies the newly running image. See the [protocol/version evidence](../../../docs/ota-e-response.en.md).

The filename and original `provenance.json` preserve the producer-time validation state. New observations are appended here and in field-observations rather than rewriting original producer evidence.

## Binary and static evidence

- Size: 76,800 bytes.
- SHA-256: `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`.
- Official reference: ID2966 V4.1.60, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
- Exactly 93 differing bytes, all within TX `0x8A56..0x8B6E`; all other bytes are identical.
- Thirteen original function regions / 930 bytes use fifteen allocated FUNC roles; 678 other sections retain original carriers. This is partial source reconstruction.

The file is copied from the matching formal producer outputs without overwriting the 22 official BINs. [Source and independent review](../../../analysis/v4160-tx-image-integration-2026-10-22/readme.en.md) cover actual source, allocation, relocation, calls and page shape. ROM/BOOT identity, physical Flash aliasing, full ABI, CRC/signature policy, complete OTA compatibility and failure recovery remain unproved; the user's session/page-readback report is recorded above. This does not establish general flashing readiness or complete compatibility.
