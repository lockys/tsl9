# NV read callback: original register interface

[繁體中文](readme.zh-TW.md)

Readable C with minimal register/call ports improves the ID2966 V4.1.60 NV read callback. The identical source is curated at [src/native/nv/nv_read_registers.c](../../src/native/nv/nv_read_registers.c). This is a separate component, not integrated into an OTA BIN.

## Improvement and actual artifacts

The older C candidate was32B/14 instructions and used A3 for source/slot-base scratch. C11/C++17 now both produce **30B/14 instructions**. The wrapper does not write A3 or use RA as a source scratch register. The actual provider may still write A3; the claim covers wrapper instructions only.

Original `[0x1979A,0x197B8)`:30B/13 instructions, SHA256 `e9e2a0f4b50184fa5c7b37ee004867f393b8c960fe9e66e81dc40af897114f62`. New component SHA256: `55eaeff68d528f2e86c97ce41148fa5ef921bd325a35e86d439df5a1cc6dedda`. These are **not byte-identical**.

C performs the fresh volatile slot read and32-bit shift. Ports handle only fixed registers and the MOV/JALR call boundary, with no copied instruction carrier or provider stub. Before the call:

| Register | Value |
| --- | --- |
| A0 | Entry A2: destination |
| A1 | Entry A0: source |
| A2 | u32(entry A1 << 2): byte count |
| A4 | Entry A2 |
| A5 | Fresh R32(0x4004C) |

Shift wrap is retained: word count0x40000000 produces zero bytes. Neither the original nor this component adds a null-target guard/count clamp.

## Explicit remaining gaps

- Original reads the slot before allocating the frame and saving RA; the candidate allocates16B and saves RA first.
- Candidate transiently shifts A1 then moves A2; intermediate A4 timing also differs.
- Original restores RA before A0=0; candidate sets zero first.
- Installed slot/provider identity and full ABI remain unknown. Static UND=0 does not prove the indirect callee, normal return or successful copy.

The reviewed resident candidate preserves entry A3 on null/zero-count early returns, so removing extra wrapper A3 writes matters at generic boundaries. That candidate is not established as the installed provider. Matching normal projection is not fault/IRQ/stack-alias equivalence.

## Offline verification

From the project root, supply the original BIN, installed LLVM and a new build directory explicitly:

```sh
python3 experiments/tsl9-nv-read-registers/verify.py --project-root . --tool-dir "/absolute/path/to/llvm/bin" --firmware "/absolute/path/to/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/path/experiments/tsl9-nv-read-registers/build/new-run"
```

On Windows use `py -3` or `python` if needed. Actual tools were Windows Android NDK27.1.12297006/LLVM18. Tool/stdint hashes must match this profile; other platforms were not tested.

Latest local receipts: `build/component-v2/{c,cpp}/verification.json`. Each object/linked component has one30B FUNC/AX section, no extra allocation, eh_frame, UND, global ABS or relocations. IR checks actual source/count/destination/fresh-target SSA dependencies and conservative callee clobbers. Fixed candidate bytes plus13 original operand rows support instruction annotations, rather than a separate ISA execution proof.

```sh
python3 experiments/tsl9-nv-read-registers/verify.py --project-root . --replay "/absolute/path/to/build/component-v2/c/verification.json"
```

Early native-v1 RA/SP reservation errors remain retained. v2 removed A3 but added RA scratch. v3's reserved-register/opaque-callee-clobber conflict was rejected without disabling warnings; the repaired call-boundary model uses the standard v4 profile. Component-v1's C++ IR `noundef` parser failure remains; verifier support produced passing v2. Older outputs are historical snapshots, not claimed replayable with the revised verifier.

No RV32/MMIO execution, hardware operation or firmware BIN generation. Hardware, installed ROM/BOOT, complete startup/IRQ and OTA compatibility remain unproved.
