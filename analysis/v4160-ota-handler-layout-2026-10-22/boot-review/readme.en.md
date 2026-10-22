# BOOT ID2580 W numeric bound

[繁體中文](readme.zh-TW.md)

This is an offline static reread of actual BOOT ID2580 bytes, not a guard claim copied from the command-adapter README. Original SHA256 is `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`,12,288 bytes, analysis base1000/file end4000. Command body21BE..235C is414 bytes/144 instructions, SHA256 `44702abb50c4489f378bb1036d8cf949817301e2e07d8af8434f7d6e119438d5`.

Explicit-file checking redecodes all144 instructions against sealed original bytes/order, checks18 page-guard operand records and W/E flow, and rejects five new single-field raw controls. The old18 controls and HOST/Flash matrices are not rerun. The only extra code view is scheduled target20E2's four bytes: LUI T1,8000; JR T1. No wider BOOT/ROM investigation occurred.

## What the operands establish

W reads active at liveGP+139 and requires full length1026. It reads low byte at payload+1 FIRST(2210), then high byte at payload SECOND(2214). Shifts/OR/low16 truncation at221C..2232 form BE16 page p.

| PCs | Actual field/value |
|---|---|
|2218|LUI A4=F7FF8000|
|222A/222E|A5=20000+32=20020|
|2234/2236|S0=(p+20020)<<10; initial destination08008000+p*400|
|2238/223C|A5=18000-100=17F00|
|223A|A4=(destination+F7FF8000) mod2^32; equals p*400 for the original u16 page domain|
|2240|**BLTU A5,A4→21E2** rejects offsets above17F00|

Thus **unsigned pages0..95** pass; page96 has offset18000 and fails. This is integer algebra derived from verified operands, not CPU execution or instruction simulation. Destination does not overflow in the original BE16 domain, so the bound reduces to p<=floor(17F00/400)=95.

| Extent | Numeric result |
|---|---|
|Accepted initial pages|96 pages/98,304 bytes, low8000..20000; Flash alias08008000..08020000|
|Last page95|Destination0801FC00, final256-byte quarter starts0801FF00, full page ends08020000|
|Original Runtime ID2966|SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`;76,800 bytes=75 pages, base8000/file EOF1AC00|
|Guard-numeric interval beyond current Runtime EOF|Pages75..95,21 pages/21,504 bytes(5400), low1AC00..20000/Flash alias0801AC00..08020000|

**These21 pages are not proven free Flash.** File extents are not a full physical ownership map. Constants do not measure Flash capacity, reserved NV/metadata or root policy. They do not establish that extending the image or overwriting this region is safe.

## Write/readback/finish limits

- 2256 loads the target from4004C and225E conditionally calls it for alignment copy. Overlap/resident semantics remain unproved.
- 2272 calls20E6. S2 offset increments by256 before the call and live S2/S4 control continuation afterward. Four calls and later addresses require appropriate callee return/preservation conditions; the initial guard is not a global limit after arbitrary opaque/asynchronous changes.
- 2282 reads Flash32 before live RAM32 at2288. First mismatch branches to the epilogue at228A; there is no Runtime FF/full-page echo. Match setsA2/A3=0 and tails to2AA0 for empty W reply, without proving a BLE ACK was delivered.
- The selected E block checks active only, clears it, schedules192C/200 then20E2/400 and tails with empty E. It does not read incoming payload/length/UID or whole-image completion state.20E2's four bytes prove a numeric jump8000, not actual scheduling, physical alias mapping, startup state or compatibility.

This bounded flow **does not establish whole-image CRC/signature/page-completeness validation**. It does not establish that the entire BOOT lacks upstream framing, metadata or root checks; those were not reconstructed here. Installed ID2580 identity, physical Flash/NV ownership, MCU/resident, interruption recovery and complete OTA remain unproved.

## Replay

```sh
# Sealed metadata/numeric deduction only; neither BIN read nor raw controls
python3 -B check.py --project-root ROOT

# Supply BOTH flags for actual BOOT/Runtime reads and five raw controls
python3 -B check.py --project-root ROOT --boot ID2580.bin --firmware ID2966.bin
```

Default reports `metadata_only=true`, `actual_BOOT_read=false`, `actual_Runtime_read=false`; explicit files report false/true/true. Both working `apk-analysis/tsl9-` and delivered `analysis/` evidence layouts are resolved, without historical W builds. No compiler/HOST, target execution, ISA/ESIL stepping, hardware, network, UID/VIN transmission or new BIN occurs.
