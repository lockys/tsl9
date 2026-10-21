# OTA page reply: independent static ABI review

[繁體中文](readme.zh-TW.md) · [简体中文](readme.zh-CN.md)

This scope checks ID2966 V4.1.60 `0x9B8E..0x9C0A` (124 bytes, 50 instructions) and actual C/C++ compiler objects against the sealed `../source-review/` evidence. Final actual references are `experiments/tsl9-v4160-ota-page-reply/build/formal-native-final/{c,cpp}`. Both ordered linked functions equal all124 original bytes. Whole-image integration has not been performed.

The compiler preserves call, branch and terminal offsets. Header writes, full 32-bit index arithmetic and TX argument order match the source. Differences remain only in the save/ROM-load order at `[+0x02,+0x16)` and successful restore order at `[+0x58,+0x60)`: 28 bytes in total. Each window has the same occurrence-aware instruction inventory. The compiler alone has not emitted the original order.

`native.py` checks actual ELF objects, all 50 raw instruction fields and LLVM IR independently for C and C++. Seven actual machine-byte mutations and four IR mutations must reject per language. With an explicit scheduled object, it additionally requires unchanged ELF bytes outside those two windows, identical sections/symbols/relocations, and the complete original instruction order. The sole TX relocation resolves its four-byte JAL.

```sh
python -B native.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --report NEW_REPORT.json
python -B native.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --scheduled SCHEDULED_OBJECT --report NEW_REPORT.json
```

This explicit artifact check does not compile or execute target firmware. Report paths must be new.

The complete actual artifact check and readonly replay below also check the ordering receipt, C11/C++17 recipes, fixed linked entry9B8E and actual TX target8A56/RA9BE4, with three mutated actual linked ELF-byte controls. The ABS TX symbol is a numeric witness; no resident TX implementation is linked. `review.sh` exposes the same interface.

```sh
python -B review.py --project-root ROOT --folder ACTUAL_COMPONENT_FOLDER --receipt NEW_REPORT.json
python -B review.py --project-root ROOT --replay NEW_REPORT.json
python -B verify.py
```

The final command and `verify.sh` are metadata-only by default. They do not replay unpublished build artifacts. No `.o`, `.elf` or `build/` files are seal members. `metadata/` retains final independent C/C++ results and prototype ordering audits:18 malformed actual ELF inputs,5 path controls and3 receipt controls per language. Prototype and final compiler object hashes are identical. `order_audit.py` can rerun these26 ordering controls with an explicit actual folder and new `--work` path.

Allocator/copy targets are freshly loaded through live S2. Success selects A0 before restoring S0, then jumps through freshly loaded T1 without creating RA. Null allocation uses its separate restore/return path; A1..A7 remain allocator-defined. The three-argument IR `musttail` prototype is a raw register adapter: its A1/A2 must forward post-TX values. It does not prove the resident release function's C signature.

Resident SP/callee-saved behavior, unrecorded computed entries, installed ROM identity and physical hardware/OTA compatibility remain unverified. Reordering stack saves and ROM loads changes fault/interruption prefixes; any scheduling layer must be labelled source ABI-order restoration rather than universal semantic commutation. No target CPU execution, emulation, network or physical I/O occurs here.
