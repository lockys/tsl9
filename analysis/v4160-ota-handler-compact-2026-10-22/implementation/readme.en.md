# Compact OTA handler producer and evidence

[繁體中文](readme.zh-TW.md)

The formal verify_native.py compiles new readable C/C++ directly, retaining nine true UND symbols without linking or BIN export. Final output is 568 bytes /193 instructions /frame48 /20 RELA (12 JAL +4 HI20 +4 LO12). It still exceeds the original 530 bytes by38; complete ABI, placement and hardware OTA remain false.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/check.py --project-root .
```

Published paths use analysis/v4160-ota-handler-compact-2026-10-22. Fresh output is a new UUID scope; explicit --build-root must be new and under model/build. Four exact recipes bind source/tool/header identities before/after use, complete generated log/artifact hashes, full raw ELF/LLVM coverage and MD three project files plus actual stdint.h. No flag/fixed-register sweep or original-BIN codegen template was used.

Default check.py validates source/seal/selected metadata with actual flags false. Explicit repeatable --host-receipt / --native-receipt replay real archives. receipts/ contains four selected metadata copies; historical W paths in results.json are not publication dependencies.

No-unroll was ineffective: actual payload equals baseline776. Separating response allocation and sharing terminal replies produced592 then568. hypotheses.json retains measured identities; historical build/source snapshots stay local and are not default archive replays. Formal HOST passes10/8292 and three compiled negatives per language.

ABI-review owns new source/effect/native/independent-HOST comparison. callee-review is bounded callee evidence, not a new raw-source consumer review. Original530B/169raw proof remains in the prior sealed source-review. Candidate resident/App bodies do not establish installed ROM or license dropping bridge registers.

Private C response semantics and conventional callee preservation remain conditional; full physical SP/pointer-alias/GPR/RA/async equivalence is unproved. Matching frame size alone does not grant admission. No RV32 execution, emulation, network, hardware, UID/VIN access or existing-image change occurred.
