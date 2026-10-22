# Compact OTA dispatcher: independent review

[繁體中文](README.md)

The selected shared C/C++ component measures **568 bytes / 193 instructions / a 48-byte frame**, 208 bytes below the previous776 and still **38 bytes above the original530**. Nine genuine UND obligations remain. There is no link, numeric provider, stub, padding or BIN. The previous immutable original530/169 source proof is reused as raw evidence, not as proof that the new native code executes correctly.

## Actual evidence

- The genuinely independent fixture is reused byte-for-byte. Each fresh C11/C++17 run passes **16 narratives, 18 dispatches and898 behavioral assertions**, rejecting four actually compiled semantic controls. The old776 is not rebuilt; no HOST suite was run for the ineffective no-unroll hypothesis.
- A bounded mechanical rewrite reconstructs the selected C from the immutable baseline: six reply exits jump to three same-site/callee labels, retaining setter and memory-effect order. W small/page masks remain63, U/R7 and packet15. HOST header/provider/frame primitives are identical. There is no selected no-unroll pragma.
- Native response storage is separated from the port into a wrapper-owned `volatile uint8_t[2]`; the port holds its pointer. The full eight-register readwrite bridge and caller/memory clobbers are unchanged. Actual IR has that sole two-byte alloca rather than an escaping argument struct, with volatile stores and pointer materialization retained.
- All193 raw instruction operands agree with independent LLVM text. Four actual recipes, MD's three project files and observed `stdint.h`, source/tools and artifacts are checked. Twenty RELA records comprise twelve direct JALs and four callback HI/LO pairs; one indirect copy call reads slot4C. The nine UND are never replaced with fabricated providers.
- There is one static quarter JAL. Actual local CFG shows counter1024 stepping−256 and both argument cursors stepping+256 after normal return, with one backedge. Preserving those three callee-saved registers yields four calls at offsets0/256/512/768. This is conditional static arithmetic/def-use, not target execution or arbitrary-callee proof. Two loop-operand controls and three SP/link/GP controls are rejected.

## Frame and alias limits

Same frame size is not equal contents. Original code saves seven registers. Native code saves ten: RA@44,S0@40,S1@36,S2@32,S3@28,S4@24,S5@20,S6@16,S7@12,S8@8. The actual private reply occupies **SP+6/+7**, versus original liveSP+12/+13. Blindly rebinding toSP+12 would collide with the native S7 save.

Separate C objects help the compiler; they do not prove that the unknown resident ignores numeric pointer identity, SP, adjacent storage or original aliases. A real packet-provider contract must establish how it consumes content/length. Hosted live-SP cases are not physical native-stack proof. Full original ABI/prefix/footprint/placement/ROM/IRQ/BOOT/OTA/recovery remain unproved.

## Previous-document correction

`baseline-correction.json` supersedes only the old case README.md/readme.zh-TW.md/readme.en.md line12 claim of four unrolled static quarter calls. The actual776 object has one quarter relocation at658(0x292), and a backedge at676(0x2A4) to652(0x28C). Its independent reports already recorded one. Four describes conditional dynamic invocations; the no-unroll probe gave no reduction. No old sealed bytes were edited.

## Run

Relative script paths start at this case directory. `ROOT` is the actual project root. Original and published evidence layouts are supported; Python/sh portability does not claim other LLVM host platforms were tested.

```sh
python3 -B ABI-review/check.py --project-root ROOT
python3 -B ABI-review/run-host.py --project-root ROOT --language both
python3 -B ABI-review/run-host.py --project-root ROOT --replay HOST_RECEIPT.json
python3 -B ABI-review/review.py --project-root ROOT --folder NATIVE_MODE --receipt NEW_REVIEW.json --firmware OFFICIAL.bin
python3 -B ABI-review/review.py --project-root ROOT --replay NEW_REVIEW.json --firmware OFFICIAL.bin
```

Default source/metadata checks emit false actual-artifact flags. Explicit native review or HOST replay emits the applicable true flag. Hosted builds are create-only under this scope's `build/`, with the immutable executable-machine guard before/after every launch. Native review receipts must be outside producer folders. Omit `--firmware` to avoid reading the original BIN; replay preserves that mode and never recompiles/relaunches. The seal includes source/metadata only, no compiled archives.
