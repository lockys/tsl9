# TX C/C++ HOST effect review

[繁體中文](readme.zh-TW.md)

This independently reviews the shared readable algorithm in `experiments/tsl9-v4160-ota-tx/src`. The reference is the sealed original `0x8A56..0x8B6E` 280-byte/96-instruction raw contract, reached through sibling `source-review-v2`. It is not a proof that a normal C interface reproduces every original machine register or instruction boundary.

The independent oracle compiles actual C11 and C++17 HOST builds. Each selected language passed **4 groups, 31 cases, 78,283 checks and 14 separately compiled semantic negatives**. A sparse synthetic byte map represents numeric addresses; no device address is dereferenced. Expected ordered effects are built from explicit source contracts and fixture data, independently of the implementation's callback trace. Reads use fresh synthetic memory, including writes that alias subsequent source or saved-frame bytes. This is a named algorithm oracle, without CPU state, opcode stepping or an ISA interpreter.

| Group | Cases | Evidence |
| --- | ---: | --- |
| Ordinary lane0/lane1 |14|Lengths0,1,2,7,255,256,1039; exact header, payload, additive checksum, metadata, tail args and widths|
| Guards and failed selection |7|Oversize1040/65536/UINT32_MAX before effects, no matching handle, sentinel, gate2 failure A2=1, first-result residue|
| Live state and aliases |6|Gate1 changes GP/S0/S1/S2/S3; gate2 receives gate1 A2/A3, fresh slot; length1041 after initial guard, length65536 bounded prefix; forward payload overlap; shifted SP and metadata/frame alias; fresh frame edits|
| Unknown and opaque control |4|Unknown payload read, rejected returned memory-callback GPR mutation, opaque gate HALT, delegated tail TRANSFER|

Memory callbacks may edit synthetic memory but cannot edit the model's registers/known mask. Named opaque gates can alter GP/SP/S registers and arguments. This is an explicit HOST abstraction; it does not establish actual ROM callee behavior or machine fault/interruption prefixes. The length guard precedes opaque calls: no new postgate clamp is invented. A low16 counter tested against full32 mutated S0=65536 cannot reach the ordinary exit, so the fixture stops as an explicitly budget-limited UNKNOWN prefix. That budget is HOST-only. Zero-sized and postgate enlarged inputs do not establish safe physical buffer capacity.

The oracle checks the interleaved 32/16/8-bit saves, reads and stores, fresh restored RA/SP/S0, path-dependent A0/A2, all four opaque call arguments, raw and bit0-masked targets/link, and unnormalized delegated results. It does not claim a complete all-register machine-prefix proof. Tail transfer is an opaque provider event; no actual target is called and no wire/BLE frame is sent.

Fourteen actual compiled one-change controls cover guard boundaries/narrowing, cached GP, lost gate2 argument residues, wrong lane, stride/magic, metadata SW instead of SH, wrong tail-byte table, cached restore SP, repeated payload source byte, checksum mask, normalized tail result and unmasked target. Every negative compiled successfully and failed an oracle assertion. An initial draft cached-SP mutation instead triggered an unused-local `/WX` compiler failure; that attempt is preserved only in local build history and is not counted as a semantic negative.

The final read-only replay binds exact compiler/run argument lists and exits, actual log/artifact hashes, all five copied sources to current originals plus exactly the intended mutation, exact positive counters and all fifteen executable guards. Ten in-memory receipt/source-view controls reject changed recipes, counters, exits, missing guards and mutant identities, including a second copied-source change with a forged matching artifact pin. These controls never modify archived files. The producer HOST runner's previously optional guard readback was reported separately; its final reviewed identity is recorded in `selected-verification.json`.

All HOST launches use the immutable native-machine guard `experiments/tsl9-v4160-flash-register-prefix/verify_host.py` (`f1982360…713eb`). Actual selected executables were Windows x64 PE; other platforms are supported by the portable runner but were not tested here. RISC-V target artifacts are never launched. Actual C/C++ source execution, synthetic provider correctness, native compiler output, physical ROM ABI, fixed placement, hardware and OTA acceptance remain separate evidence levels. Current native TX output is not admitted as a binary-compatible replacement; reaching 280 bytes does not resolve its entry guard/frame/restore/call-prefix differences.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/code-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/code-review/run-effects.py --project-root . --language both
```

The `.sh` wrappers accept `PYTHON`. Default `check-review.py` verifies current source and sealed raw proof, but explicitly reports `actual_archived_artifacts_replayed:false`: selected receipt metadata is not a current artifact replay. Add a repeated `--receipt ACTUAL_INDEPENDENT_VERIFICATION_JSON` to inspect an actual local independent archive. `run-effects.py --replay RECEIPT` is read-only; a fresh run creates a new directory under this review's `build/`. Only review source, docs and concise selected metadata are sealed for publication; generated executables, logs, old diagnostic attempts and full archives stay local.
