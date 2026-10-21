# Source-owned ABI frame scheduling: independent object audit

The frozen scheduler passes **six actual object transformations, two complete linked witnesses,21 actual-object guard controls and three pre-write path-alias rejections**. C/C++ merged objects, standalone IRQ main.o and Flash quarter.o are covered. [繁體中文](readme.zh-TW.md) · [简体中文](readme.zh-CN.md)

Scheduler SHA-256: `dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d`; policy: `2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d`. The parent native ABI diagnostic seal remains unchanged.

The step permutes only **existing C.SWSP instructions from newly compiled objects**: eight IRQ bytes and six wrapper bytes. Every other object byte, section metadata, symbol and RELA remains unchanged. There is no original-BIN generation input, opcode template, padding or whole-function assembly. The pipeline is explicitly C/C++ compiler plus source-owned ABI scheduling; the compiler alone did not emit the final order.

Both actual links yield144-byte IRQ/64-byte wrapper bodies identical to original machine code. All691 allocations,15 LOADs,53 bindings,8,259 outside RELA and20 known incoming width/target/RA contracts remain. These witnesses isolate scheduling over the previously verified full-image compiler objects. They do not establish a newly integrated image with this round's five new leaves. The original firmware is read only for comparison; no BIN is produced.

All21 controls reject wrong GPR/slot/high64 offset/overlap/width/frame, LOCAL or hidden FUNC, size, interior symbols, relocation sites/targets, unwind, storage aliases, duplicate owner names, ELF kind/program-header/float flags, empty/duplicate selection and reapplication. Input=output,input=receipt,output=receipt reject before writes, preserving the source. Previously found public-role, path and owner-name guards were repaired and retested.

```sh
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/frame-pass-review/check_seal.py --project-root .
```

Alternatively use `sh .../review.sh --project-root . --replay .../report.json`. Read-only replay parses retained pre/post objects, actual linked witnesses and receipts, repeating the pure plan, metadata/call checks and21 artifact controls without linking or writing files. The three actual API path rejections are retained evidence; replay does not call the writing API again. `audit.py --report PATH` is the separate historical-profile producer requiring original compiler artifacts/linker and producing six object pairs/two static ELFs. The shell wrapper was statically inspected without WSL/Git Bash execution.

Prefix shape alone cannot authenticate C/C++ provenance or decode every resolved branch in arbitrary objects. Integration must bind source,42TU commands, tool/policy, pre-objects and layout. Retained pre-object copies and compiler-receipt hashes preserve the checked lineage. Actual IRQ/wrapper bodies contain only the known JALs/RET and no direct branch back into save intervals. Unknown computed interior entries remain unexcluded. Complete nonreturn/asynchronous behavior, ROM, hardware and OTA success remain unproved.

The seal includes only selected report artifacts and named members, excluding preliminary/final-candidate reports and other build runs. No target execution/emulation, device I/O, network or new firmware BIN occurs.
