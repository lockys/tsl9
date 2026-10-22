# Callback call boundaries and conditional ROM contracts

[繁體中文](README.md)

This milestone reads original ID2966, the existing 624-byte C/C++ components and two retained official ROM candidates. **It changes no C/C++ model, does not recompile unchanged components, executes no firmware and generates no BIN.** The existing complete experimental TX image is unchanged and is not verified as flashable.

## Confirmed scope

| Question | Static evidence | Limit |
| --- | --- | --- |
| Is the GP+42 halfword missing from a call argument? | Original LHU A5 at `0x8800` only feeds SH at `0x8808`; the target LW at `0x880C` kills A5. Native LH A0 at `0x120A` only feeds SH at `0x120E`; MV at `0x121A` kills A0 before JALR at `0x1220`. Both datum values are dead at the call. | Equivalent low16 stores do not prove intermediate fault/asynchronous-interrupt prefixes equal. |
| Should A4 be added? | The original datum is in A5, not A4. The matching native window leaves A3/A4/A6/A7 untouched. No missing C argument is found here; adding `a[4]` would be unjustified. | Other sites retain their own assigned-argument and opaque-residue contracts. |
| May fifteen calls be paired by sorted address? | No. Matching uses target slots, arguments, event branches and adjacent memory/call signatures. | Equal call counts do not establish semantic correspondence. |
| Are physical S roles equal? | No. At original `0x86E0`, S4 is context and S7 is `0x40000`; the matching native site uses different C local values in those physical registers. | A difference alone does not prove ABI failure. Callee preservation alone does not prove that incoming S values are unobserved. |
| Must return-address numbers be identical? | They differ. In the closed small function pair behind candidate ROM slot `+0x13C`, RA is only saved/restored/returned through, and incoming S4/S7 are not read. | This is conditional on the checked candidates and instruction profile, not installed-ROM evidence or a statement about every callee. |
| Is slot `+0xD4` fully closed? | Its local function and bounded direct small helpers are inspected. | Three deeper flash callees remain opaque; transitive ABI is not proved. |

See [original local proof](source-review/readme.en.md), [actual native call correspondence](native-review/readme.en.md) and [candidate ROM](resident-review/readme.en.md). The previous sealed fifteen-site original argument contract remains authoritative instead of duplicating it.

Nominal native slot correspondence is conditional on conventional callee-saved preservation. Separate reaching-definition frontiers retain the possibility that an opaque call changes every register. Fifteen nominal matches do not prove full physical prefix equivalence, and unknown outputs/registers are never replaced with zeros.

## Candidate evidence boundary

Retained official V1.40 has `[0x4013C] = 0x4B4EE` and `[0x400D4] = 0x4C25C`; V1.31 has `0x4B456` and `0x4C1C4`. The slot `+0x13C` pair contains a 22-byte wrapper and a 36-byte lookup helper. Nonstandard instruction interpretation is explicitly conditional on the checked LLVM Xwchc profile; unknown opcodes are never treated as NOPs.

Candidate headers name the slots `GATTServApp_ReadCharCfg` and `GATT_Notification`. The actual small pair returns zero for no entry, otherwise the zero-extended byte at `entry+2` (0..255). **It is not proved to return only Boolean 0/1.** The callback's first `==1` test and later `&1` test must therefore remain distinct. This supports a candidate interpretation of a notification CCC gate followed by notification submission, making the wait-reason proposal more concrete without claiming installed identity or an implemented diagnostic feature.

These files are not ROM dumps from the physical TSL9. Version strings, equal fragments and the app's expected-version prefix do not establish installed identity. This milestone does not copy complete vendor ROMs to GitHub. Actual candidate checks require an explicit local reference root; metadata checks do not read candidate artifacts.

## Reproduce

```sh
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/source-review/check-review.py --project-root /absolute/re-tsl9 --firmware /absolute/re-tsl9/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin --component /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/EXISTING/ordered/c/COMPONENT-ONLY-NOT-FIRMWARE.elf
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/native-review/review.py --project-root /absolute/re-tsl9 --folder /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/EXISTING/ordered/c --receipt /absolute/re-tsl9/analysis/v4160-callback-call-frontiers-2026-10-22/build/new-c.json
```

Delivery builds usually have an additional `native/` directory. Select the actual absolute `ordered/c` or `ordered/cpp` path from your formal receipt. These commands read existing artifacts without invoking the compiler. New receipts must not overwrite old files or live inside old artifact sets. Candidate commands and metadata/actual distinctions are documented in resident-review.

Next work must narrow the remaining callee roles, installed ROM identity and required RAM/interrupt contracts. Full original632 storage ownership, placement, BOOT/hardware/BLE OTA remain unproved. Do not pad the remaining eight bytes or substitute candidate normal-return evidence for physical validation. Offline OTA preflight and wait-reason display remain proposals, not implemented hardware features.
