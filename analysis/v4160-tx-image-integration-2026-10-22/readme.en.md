# Readable TX source in a complete experimental image

[繁體中文](README.md)

This milestone integrates the reviewed TX entry, readable C/C++ body and return leaf into the complete ID2966 V4.1.60 layout. Fresh C11 and C++17 pipelines produce the same 76,800-byte experimental BIN, SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. Exactly 93 bytes differ from the official image, all inside `0x8A56..0x8B6E`; every other byte is unchanged. **The new file is not verified as flashable and is not official firmware.**

## Source and static evidence

- Thirteen original function regions total 930 bytes, represented by fifteen genuinely allocated FUNC roles. TX honestly exposes an eight-byte public entry, a local 270-byte body and a two-byte return leaf; no fabricated FUNC280 or numeric provider substitutes for real code.
- Each language freshly compiles 46 units: 34 original carriers, eleven readable C/C++ units and one direct assembler entry. All 45 C/C++ units use full `-MD`; the non-preprocessed assembly input is directly pinned. The 67 internal recipes comprise 64 LLVM operations and three explicit ordering stages. Outer resource lookup and source generation are recorded separately.
- Checks cover all 691 allocations, 678 retained original carriers, 8,261 relocations and fifteen LOAD ranges/permissions. The 8,258 non-TX relocations allow only nine target FUNC-size projections from 280 to the real eight-byte entry; other original roles and bytes remain unchanged.
- Thirty recorded boundary references comprise 29 owners outside selected regions plus one selected page-reply call. They do not enumerate every image call. The nine direct TX incoming references include a no-link jump at `0x13EAC`; unknown computed/interior references remain unproved.

[Implementation](implementation/readme.en.md) and [independent source review](source-review/readme.en.md) check actual recipes, dependencies, IR, objects, ELF and the complete artifact set. [Independent ABI review](ABI-review/readme.en.md) reads actual objects, calls, relocations, three scheduling stages and the whole image. Default metadata validation does not replay actual build artifacts; supply a new build receipt explicitly.

## Local layout and remaining work

The [layout checker](image-plan/readme.en.md) reads candidate BOOT ID2580 and the new image: 75 pages of 1,024 bytes, indices 0..74, fourteen BOOT byte anchors and five actual byte/length negatives. It creates no complete OTA packet, uses no device identity and does not prove installed BOOT identity, physical Flash aliasing or CRC/signature policy.

This remains partial source reconstruction with 678 original carrier sections. Resident ROM addresses are numeric witnesses. Full original ABI, asynchronous behavior, code-as-data, physical chip, installed ROM/BOOT, BLE OTA and recovery remain unproved. No RV32 execution/emulation, hardware operation or vendor API request occurs. Unchanged host behavior suites were not rerun for documentation/integration work.

Local layout checking is now a research utility. Complete packet preflight and update wait-reason display remain [proposals](../v4160-ota-tx-2026-10-22/continuation-plan/readme.en.md), not hardware features. Further work should follow actual calls/data boundaries through the remaining updater while narrowing hardware and ROM/BOOT evidence gaps.

## Reproduce

```sh
python3 -B experiments/tsl9-v4160-tx-image-integration/verify.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both
python3 -B analysis/v4160-tx-image-integration-2026-10-22/source-review/check-review.py --project-root /absolute/re-tsl9 --firmware /absolute/ID-2966-V4.1.60-decoded.bin --receipt /absolute/new-build/c/verification.json
```

Actual compiler evidence currently comes from Windows NDK LLVM. Portable Python/shell entry points do not prove Linux, macOS or CI execution.
