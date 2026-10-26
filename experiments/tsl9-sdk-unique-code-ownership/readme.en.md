# Unique SDK CODE ownership by original PC

[繁體中文](README.md) · [Previous RF bridge](../tsl9-original-RF-bridge/readme.en.md)

Fix one complete SDK body, `0x63C54..0x63D6A`, selected twice under different names. Reuse the earlier real provider `tsl9_candidate_register_config_63c54`; regenerate three dependent C/C++ bodies totaling 840 bytes /289 instructions. No new distinct CODE, stub or ABS function is introduced.

## Verified evidence

- The regression checker fails on the actual old composition: 278 original-PC bytes have two allocations. All 16 paired FUNC regions have equal bytes and address-typed relocations. The old check enforced section/symbol-name uniqueness only.
- The new composition passes unique ownership: **12,658 CODE+256 DATA bytes /4,412 instructions**, 1,037 FUNC regions, 781 relocations and 19 genuine unavailable named dependencies. FUNC region counts are not logical function counts.
- Complete before/after original-PC native byte maps, typed relocation relation sets, DATA bytes/type/flags/alignment and genuine dependencies are identical. The removed 278 bytes /95 instructions /9 relocations were duplicate allocations, not new reconstruction progress.
- C11/C++17 artifacts are identical. Whole CFG own frames, every selected input byte/symbol/relocation and two independent ELF readers pass. The previous full static audit chain is freshly verified.

Old sources and receipts are preserved. The previous 12,936 CODE bytes measured actual allocation, including this duplication. Original-PC tags describe source contracts, not completed physical address placement.

APP remains 159 C/H files and95.54% byte coverage, not functional completion. No new BIN, APP integration, target/model execution or hardware access. The inherited4-byte startup source gap, physical ROM/RAM/ISA/IRQ, whole-program stack/aliasing, Flash and OTA compatibility remain open. **Usable replacement firmware has not been successfully reconstructed.**

[C/C++](unique_dispatch.c) · [Regression checker](verify-ownership-v1.py) · [Audit](audit-result-v1.json) · [Summary](summary.json)

## Reproduce

Provide the pinned local inputs, prior native artifacts, Windows NDK LLVM and official headers required by the trap audit. Missing inputs are not downloaded.

```sh
python experiments/tsl9-sdk-unique-code-ownership/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-sdk-unique-code-ownership/build/native-v1
python experiments/tsl9-sdk-unique-code-ownership/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
python experiments/tsl9-sdk-unique-code-ownership/verify-ownership-v1.py --object experiments/tsl9-sdk-unique-code-ownership/build/composition-v1/c/candidate.o
```

For new artifacts replace `--replay` with `--trial` in the first command and add `--link-trial` to the second; both names must be unused. Tool hashes pin Windows LLVM; cross-platform compilation is unverified.
