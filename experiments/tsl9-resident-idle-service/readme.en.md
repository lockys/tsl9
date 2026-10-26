# Idle service and register-helper candidate C/C++

[繁體中文](README.md) · [Main scheduler](../tsl9-resident-scheduler/readme.en.md) · [Clock services](../tsl9-resident-clock-services/readme.en.md)

Three complete bodies total **518 bytes/178 instructions**: conditional RAM0x2000061A..0x2000078A (368 bytes), Flash0x6430E..0x6434A (60) and0x638EA..0x63944 (90). Adjacent0x2000078A/0x200007A0 belong to separate functions and are excluded.

This is a public SDK V1.31 candidate; installed ROM identity remains unproved. The [C/C++ source](resident_idle_service.c) preserves original registers and C/assembly, not an ordinary HOST-callable API.

## Verified flow

- Identical C11/C++17 objects; every original-context byte matches. There are41 positive FUNC regions and28 relocations. One conditional Xwchc byte port is checked against primary definitions and28 official vectors.
- The actual scheduler tail at0x200008BE **releases its own32-byte frame first**. The idle body has its own32-byte frame. These two own frames do not overlap, but callbacks, callees, IRQ and whole-program stack bounds remain open.
- Scheduler raw-clock/idleCB nonnull-check edges dominate the selected tail. Pointer stability is still required. Compiled public bleConfig_t.idleCB offset40 matches0x20003214; the header declares `uint32_t (*)(uint32_t)`. The callee has no additional null guard.
- The service saves0x4002420C, writes zero, executes FENCE.I and restores the saved word before every local idleCB path. This instruction order does not establish physical IRQ semantics.
- Four raw-clock call sites and fresh reads are preserved. The fallback constant is **-30000000**, with at most one original-branch MaxCount subtraction. No general modulo or physical-time conversion is substituted.
- Before idleCB,0x20003520 is set to1 and a zero argument is replaced by live MaxCount. Nonzero callback return skips the local timer call; zero return reaches the real timer service. Both real helpers run, followed by a flag clear, only on the fresh nonzero gate-and-flag branch.
- Gate0x20003538 and pointer0x20003590 are reloaded before/after the callback. Pointer+8 uses AND mask0xFFCCFFFF and OR mask0x00330000. Because state can change, **paired physical restoration is unproved**.

The Flash helpers use block pointers at0x2000353C/0x20003508, requiring at least120/56 valid bytes. Physical register identity, aliases, side effects and ownership remain unknown.

## Actual partial composition and limits

The real idle body resolves the existing0x2000061A import; the real prior timer body resolves this unit's timer import. Actual nonloadable C/C++ ET_REL objects contain **4944 bytes CODE+256 bytes DATA/1716 instructions**,434 positive FUNC regions, one OBJECT and317 relocations. Every input byte, symbol and relocation is retained.

RAM0x20002610 and Flash0x63DD0 remain genuine imports, along with overall callback/RAM contracts. The previous **4-byte startup source gap** and unproved arithmetic-helper semantics remain. APP byte coverage stays **95.54%**, not functional completion. No new BIN is supplied; physical RAM/ROM/ISA, IRQ, stack, Flash and original-hardware OTA compatibility remain unproved.

Evidence: [full audit](audit-result-v1.json), [summary](summary.json), [original instructions](evidence-v1.json), [specification and hashes](spec-v1.json). Idle-phase, callback-return and deadline diagnostics are unimplemented feature candidates.

## Reproduce

Provide the original APP, SDK/header/instruction references and retained native artifacts required by the spec, evidence and audit. Original SDK inputs and native artifacts are not included or automatically downloaded. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-idle-service/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-idle-service/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts, use `--replay experiments/tsl9-resident-idle-service/build/native-v1` for the first command and omit `--link-trial` for the second. No target, HOST model or ISA execution, hardware access or vendor API traffic was performed.
