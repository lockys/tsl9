# TX full image: independent source and entry-role review

[繁體中文](readme.zh-TW.md)

This offline review covers ID2966 V4.1.60 TX at `0x8A56..0x8B6E`, 280 bytes, with firmware file base `0x8000`. `reference.json` was measured from the actual prior twelve-region object. Portable checks use that sealed reference and do not silently require historical build objects.

The implementation honestly defines canonical `__tsl9v4160_call_8a56` as GLOBAL FUNC8, a LOCAL typed body270, and a GLOBAL typed return leaf2. These occupy the original allocation in order. Coverage means **13 original regions, 15 actual provider FUNCs, 930 bytes**, with the rest still supplied by the original carrier. No numeric/ABS entry provider, whole-function original assembly, or original BIN code-generation input is admitted.

The original eight private roles comprise seven control targets and one PC-relative anchor. Eleven owned relocations comprise nine control references plus HI/LO. Three new relocations remain: branch at+4, genuine allocated RAM HI at+128, and LO at+132 naming the actual new local anchor. All addends are zero. The other eight control references require actual compiled-CFG evidence; disappearance of private labels alone does not establish equivalence.

Nine known incoming sites retain their instruction widths and link behavior: C.JAL at8368→RA836A and841C→RA841E; JAL at9BE0→9BE4,135A8→135AC,13B30→13B34,13B80→13B84,13C2E→13C32,14738→1473C; sole rd0 JAL at13EAC leaves RA unchanged. All linked targets remain8A56. The9BE0 ET_REL JAL is a genuine unresolved placeholder; its relocation and linked bytes are checked rather than assuming a resolved partial-object immediate. All8258 non-TX relocations must remain semantically identical, allowing only the explicit canonical target-size projection280→8.

The independent recipe oracle reconstructs67 chronological commands,46 fresh TUs (34 raw,11 typed C/C++,1 direct assembler),11 IR units and three explicit Python ordering stages. Forty-five `-MD` rules bind each own target, primary and forced adapter. Observed closure is78 existing project dependencies,14 generated inputs and one compiler resource header, plus one directly pinned non-preprocessed assembly source. Of85 source pins, canonical `src/tx_native.c` is a source-identity reference rather than a compiled TU.

Each of the three TX providers contributes one attributes mapping marker, including the assembler input. Their three merged ABS `$d` metadata roles are distinct from forbidden numeric runtime providers. Only the typed body adds the one-byte excluded `.llvm_addrsig` payload02; the final ELF/BIN excludes it.

Default checks validate source/reference metadata and explicitly report `actual_source_compile_provenance_replayed:false`. An explicit new receipt replays actual command/source/dependency/object/ELF/BIN evidence and sets that flag true:

```sh
python3 -B check-review.py --project-root /path/to/project --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python3 -B check-review.py --project-root /path/to/project --firmware /absolute/ID-2966-V4.1.60-decoded.bin --receipt /absolute/new-build/c/verification.json
```

Per-language controls include nine actual ELF byte mutations and fourteen independent recipe/dependency/receipt countercases: fabricated FUNC280/ABS provider, wrong linkage, PCREL addend, incoming interior target, rd/link/RET, wrong sources, bypassed scheduling, language/preprocessing, dependency associations, omitted IR pins, outer logs, preflight argv and direct assembly stability. Unchanged HOST behavior matrices were not repeated.

This is partial readable C/C++ plus a narrow assembly entry and explicit scheduling of existing compiled words. It is not pure Clang or a general ordinary-C ABI replacement. Whole original ABI, unknown ROM behavior, computed/interior-reference absence, asynchronous behavior, code-as-data, hardware, installed BOOT identity, flashing and OTA compatibility remain unproved. No target execution, ISA emulation, network or device operation occurs.
