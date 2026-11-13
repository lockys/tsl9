# V4.1.60 record-helper static window map

Offline, Python 3 standard library only. From the repository root:

```sh
python -I -S -B experiments/v4160-record-helper-layout-map/test_verify.py
python -I -S -B -O experiments/v4160-record-helper-layout-map/test_verify.py
python -I -S -B experiments/v4160-record-helper-layout-map/verify.py
```

The default inputs are `experiments/tsl9-record-helpers/spec-v1.json`, `experiments/tsl9-record-helpers/src/record_helpers.v1.c`, and `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`. Use `--spec PATH`, `--source PATH`, or `--bin PATH` to select other copies; their raw bytes must match the same pins. Missing inputs fail; nothing is fetched or reconstructed. Inputs are never written. Tests include synthetic cases; their CLI failure checks read the default spec and source but not the real BIN.

Pins (SHA-256 of raw bytes):
- spec: `f658349a73f7b246cbb037fc32185afbd12773cf2fa1f924eafbf6687a081d44`
- original source: `deebd11bf4d9f852eade96fb581004ae2edbbbc14e3fbd11c5811bcd64e9e2f6`
- BIN: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, 76800 bytes, mapped at `0x8000`.

The verifier pins the exact spec and source bytes before parsing; duplicate JSON object keys fail, including in nested objects. It checks each named, nonoverlapping half-open region against the actual BIN slice and its spec hash, then checks the whole-input BIN identity. The pinned source's `REGION void name(void)` definitions must match the spec name set uniquely. It separately requires `b0b0..b0ba`: bytes `97170020a38da7e28280`, SHA-256 `e3f6cec8c02b5619561c69f571f2b440db3d1b264b672e0f7520483a03dcf7eb`. Synthetic tests call `validate_b0` directly, without whole-spec or whole-image pins, and reject incorrect address, end, size, hash, each changed byte, truncation, duplicate and missing entries. Success JSON is emitted only after all checks; addresses and gaps are half-open. Expected: 68 regions, 910 bytes, 8 adjacent groups, 7 gaps, min `0xa6aa`, max end `0x18232`.

This is **static BIN windows and inventory**, not proof of original-address C reconstruction, control flow, whole-image reconstruction or ABI, symbol ownership, relocations, or any linker script. No sections are invented and no holes are filled. A whole-input hash is an identity check only. No compiler, linker, target, or network is used.
