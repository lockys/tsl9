# Flash register prefixes and automatic frame saves: independent review

Formal C11/C++17 components pass independent static review. Five Flash leaves occupy **198 bytes identical to the original machine code**. Program retains all100 bytes/38 instructions, every original boundary and five known loop/copy entry roles. The six-function component has262 bytes/99 instructions. The wrapper still differs by six save-order bytes. [繁體中文](readme.zh-TW.md)

`receipts/c.json` and `receipts/cpp.json` bind actual `native-final` artifacts. Component ELF SHA-256: `575b2e1009437c77d71081fffeaa32988ff10b23c78decb01e9ad976c5e6c9c7`. Each language rejects **18 actual-ELF byte controls**. Four uncompiled MIR transcript controls are separately labelled.

## Exact save frontier

IRQ9A42 first decrements SP by16 in both versions. Original9A44..9A4A saves S2→SP+0, RA→+12, S0→+8, S1→+4. LLVM saves RA,S0,S1,S2 to those same respective slots. Four two-byte instructions differ by eight bytes. All bytes from9A4C onward match, including fresh live-frame RA/S0/S1/S2 reloads.

Quarter9C0A first decrements SP by32. Original9C0C..9C10 saves S0→SP+24,S1→+20,RA→+28; LLVM saves RA,S0,S1. Three instructions differ by six bytes. All bytes from9C12 onward match: S1 receives A0,9C14 stores A1 atSP+12, CSR mask136 is established, and calls/reloads/returns keep original roles.

Completed saves produce the same frame without changing other GPR values. Partially written slots, possible first fault locations and asynchronous observations differ. Receipts enumerate each frontier and do not equate complete-frame equality with pointwise equivalence.

## Actual fixed-backend diagnosis

Eight MIR dumps use unchanged compiler, source and profile, stopping immediately before/after `prologepilog`: C/C++ × IRQ/quarter × before/after. Source, adapter and compiler hashes are checked before/after. No profile search or target execution occurs.

IRQ has no stack object or saves before the pass; afterward it has a16-byte frame and RA/S0/S1/S2 spills. Quarter initially has only its20-byte source-slot object; afterward it has a32-byte frame and RA/S0/S1 saves. All generated saves precede the C body and inline primitives. Actual JAL primitives honestly declare RA clobbers.

The observed difference is introduced by automatic frame lowering. C declaration/lifetime ordering has no direct mechanism to order those generated stores. This bounded evidence is not a universal impossibility proof. Omitting RA/callee-save clobbers or duplicating manual saves is not a sound repair. A transparent source-owned ABI scheduling step needs separate validation. The native components sealed here **have not received** that step; no compiler-emitted-original-order claim is made.

## Native contract and replay

Actual six ET_REL bodies equal their linked components after only five declared JAL fixups. Leaves contain no extra calls/data allocations. RV32 LLVM IR, volatile i32 observation counts and non-naked functions are checked. Original instruction identity binds normal residues and observation order. Wrapper admission requires a valid frame, completed accesses, terminating polls and no unmodelled asynchronous interference.

The prior whole image's20 incoming width/address/RA contracts are retained as evidence and component entries remain unmoved. Those callers are absent from this component, so `new_whole_image_incoming_reverified=false` is explicit. Prior caller evidence is not presented as a newly integrated whole-image proof.

```sh
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/check_seal.py --project-root .
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/review.py --project-root . --component-folder MODE_DIR --report independent-result.json
python3 -B apk-analysis/tsl9-v4160-flash-register-prefix-2026-10-22/ABI-review/review.py --project-root . --replay independent-result.json
```

Windows can use `python -X utf8 -B`; `review.sh` forwards the same arguments. The shell wrapper was statically inspected, without WSL/Git Bash execution. Normal replay reads retained MIR, pinned original firmware/source evidence and actual components, without archived W-path objects or a Windows compiler. `diagnose_frame.py` is the separate retained eight-compile diagnostic producer.

The native seal includes only named members, excluding preliminary receipts and the separately reviewed `frame-pass-review/`. Work remains offline, without target execution/emulation, device I/O or new BIN generation. Hardware, ROM, unknown computed interior references, complete nonreturn/asynchronous behavior and OTA success remain unproved.
