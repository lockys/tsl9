# Independent Flash component review

[繁體中文](readme.zh-TW.md)

This review independently checked the six readable C/C++ Flash routines against the original ID2966 V4.1.60 source proof. It produced component objects and a component ELF, and performed synthetic host tests. It did not execute firmware, access hardware or a vendor service, or produce a new firmware BIN. The component is not ready for OTA installation.

## Original versions and reuse

`cross-version.json`, produced by `compare-versions.py`, binds the exact current image, old V4.1.00 Runtime and old BOOT hashes. The five original Runtime helpers at 18E90, 18E98, 18EB6, 18EC4 and 18EF2 are byte-identical to the old helpers at 18BE4, 18BEC, 18C0A, 18C18 and 18C46: 198 bytes in total. The 64-byte wrapper moved from 9B6C to 9C0A. Its ten differing bytes belong exclusively to the five direct JAL operands. A small static operand decoder checks their targets; it does not execute instructions. Helper and wrapper address deltas differ, so no global relocation rule follows.

The older `experiments/tsl9-contract-model/src/flash_page.c` supplies useful independently retained expectations for controller addresses, unlock keys, masks, live source-word reads, polls and operation order. It does not establish the new routines' stack or register ABI. Its host `FP_RETURNED` value is not a native controller success result; its poll budget is not a hardware timeout. The separate V4.1.60 `flash_contract.c` models 197BE rather than 9C0A, so its zero-return convention cannot be imported here. `reuse-contract.json` records these distinctions.

## Actual verification

The selected receipts in `receipts/` are copies of actual fresh outputs, not reconstructed summaries. Each C11 and C++17 canonical host run passed 5 groups, 481 cases and 247191 checks, with six actually compiled behavioral mutants. Each independently authored expected-effect fixture passed 12 scenarios and 8964 assertions, rejecting twelve additional compiled mutants. It checks sites, order, widths, values, known masks, fresh control reads, source replacement at stack SP+12 and normal output slots.

Each native build statically checked six functions, 256 bytes and 98 instructions, with sizes 64/8/30/14/46/94. Both languages produced the same component ELF SHA-256 `1097156d90ee982a6c03c903785b563acae0357d1bbc7b7c2e29315adbf5d613`. Each receipt binds 41 artifacts and six compiler dependency rules covering three project native inputs; system/resource headers are excluded from this dependency inventory. Normal ABI patterns, full emitted instruction coverage, CFG, ELF, ISA and IR constraints are checked. Across the two languages there are 30 rejected machine-byte controls and six rejected IR transcript controls. The IR controls alter retained IR text and are not recompiled programs. The host total of 36 compiled controls is a different evidence class. The original source checker separately replays 20 raw-source controls against 262 bytes and 99 original instructions.

Review exposed three underchecks that were corrected before these final runs: normal effect order/value assertions were added before baseline-prefix comparisons; host coverage became exact and runner/helper hashes were checked before and after; the native reviewer now receives the actual model source directory. Exact inputs, receipts and remaining gaps are bound in `review.json`.

## Limits that remain

The native program routine aligns A0 after its initial polls, whereas original 18EFA aligns it earlier. The wrapper uses the original 32-byte frame and fresh SP+12 source reload, but changes prologue save order. Consequently physical GPR prefixes on nonreturn/fault paths and pointwise/asynchronous equivalence are not established. Host flow-prefix results cover provider effects; host register slots are valid normal-return observations, not hardware register captures. A0 returning the aligned destination is not an error/status code. CSR 0x800 clears and later sets mask 136; this is not restoration of its previous value. Original polls have no timeout or error cleanup.

The program body is 94 bytes versus the original 100. The remaining six bytes have not been established free, assigned or integrated. This review does not establish all incoming/interior/computed references, whole-image integration, installed BOOT identity, Flash persistence, controller timing/fault behavior, ROM constraints, physical compatibility or OTA acceptance. No new product feature is implemented by this review.

## Reproduce

From the project root, use Python 3 and a fresh output directory:

```sh
python experiments/tsl9-v4160-flash-native/verify.py --project-root . --language both --build-root apk-analysis/tsl9-v4160-flash-native-2026-10-22/review/build/host-new
python apk-analysis/tsl9-v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /absolute/llvm/bin --language both --build-root apk-analysis/tsl9-v4160-flash-native-2026-10-22/review/build/native-new
python apk-analysis/tsl9-v4160-flash-native-2026-10-22/review/check-review.py --project-root .
```

The host compiler must be supported by `scripts/portable_verify.py`; native tools are Clang, LLD and llvm-objdump. The native runner accepts explicit compiler/linker/objdump and firmware paths. These commands compile and inspect native output; they do not execute RV32 code.

For original-source validation, add `--firmware /absolute/ID-2966-V4.1.60-decoded.bin` to `check-review.py`. To repeat the cross-version comparison, also provide all three options `--old-runtime`, `--boot` and `--old-evidence`. The historical evidence file is `apk-analysis/tsl9-function-hardware/fifteenth-round/flash-review/native-evidence.json`; it is not guaranteed present in a published layout, so supply an authorized local copy explicitly. Missing evidence is a missing input, not a successful check. No old APK/source archive was copied to repair that limitation.

With the retained local archive, `--archive-root /absolute/review/build` additionally replays the four selected formal host/native receipts. Retained receipt paths and compiler/tool fingerprints describe the actual Windows runs. Replay requires those artifacts and matching tools/layout; this is distinct from fresh verification's explicit-path portability. Build archives, executables and mutant copies are excluded from this sealed review. `seal.json` binds the published review files; it does not replace the artifacts required for a full replay.
