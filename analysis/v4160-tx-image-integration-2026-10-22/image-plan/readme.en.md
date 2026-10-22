# Layout and candidate-BOOT shape checks for the complete TX image

[繁體中文](README.md)

This check reads original ID2966, a rebuilt candidate BIN and retained candidate BOOT ID2580. It verifies the permitted replacement range and inherited software conditions. It does not generate firmware, transmit packets or connect hardware. This round's implementation, source-review and ABI-review separately establish actual C/C++ provenance, ELF layout, calls and relocations.

## Exact scope

- Original ID2966 is 76,800 bytes, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
- The candidate must have the same complete extent. Only VA `0x8A56..0x8B6E`, file offsets `0xA56..0xB6E`, may differ. Every other byte, including entry and tail data, must remain identical. Missing image content is never replaced with padding.
- Retained ID2580 BOOT has SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`. Fourteen source-instruction byte anchors are reread, including W's 1026-byte length condition, unsigned page bound and the weak APP-first-byte condition `0x6F`.
- The inherited selected-BOOT contract establishes 1024 data bytes, a BE16 index and numeric pages0..95 only. The candidate has75 complete pages0..74, without padding. The software formula `0x08008000 + index*1024` does not prove a physical Flash alias.
- Per-page SHA-256 and sum16 over index bytes plus page data support offline comparison. No complete OTA frame, UID or identity command is generated, and these calculations are not Flash readback.

Five actual byte/length counterexamples must reject: an entry-exterior change, tail change, missing byte, padding byte and changed BOOT first-byte immediate. This check alone does not establish that the permitted TX bytes are legal code; source and ABI evidence remain necessary.

## Reproduce

From a delivered or published project:

```sh
python3 -B analysis/v4160-tx-image-integration-2026-10-22/image-plan/verify-layout.py --original /absolute/ID-2966-V4.1.60-decoded.bin --candidate /absolute/NOT-FLASH-VALIDATED-tx-integrated.bin --boot /absolute/ID-2580-V1.0.00-decoded.bin --receipt /absolute/new-layout-receipt.json
```

The research workspace uses `apk-analysis/tsl9-v4160-tx-image-integration-2026-10-22/image-plan/`. Receipts are create-only; inputs remain untouched.

## Unproved requirements

Selected-BOOT facts come from `v4160-ota-handoff-2026-10-21/boot-acceptance`; their facts/source-map hashes are recorded in the new receipt. This check rereads retained BOOT bytes and selected anchors without rederiving whole-BOOT semantics or identifying the installed version.

Image CRC/signature policy, ROM, hardware SKU, physical Flash/RAM, BLE ordering, full14-byte identity, restart and recovery still need separate proof. Correct first byte, page count and local checks do not establish OTA acceptance. There is no RV32 execution/emulation or vendor API request.
