# Callback slot 3 and record objects

[繁體中文](README.md)

Seven complete SDK candidate bodies add **1,180 bytes / 407 instructions** of C/C++. This conditional ROM study does not identify the ROM installed in the original hardware.

| Original PC | Bytes | Scope / limitation |
|---|---:|---|
| `43174` | 40 | Complete linked-record traversal; live memory validity unproved |
| `43932` | 118 | Record/scheduling helper, retaining original calls and branches |
| `5E76C` | 336 | Record callback; literal `60838` still has no supplied body |
| `5E8BC` | 148 | Allocate 232 bytes, install three callbacks, conditionally register slot 3 |
| `5ECA2` | 84 | Record/state helper with three genuine existing callees |
| `60350` | 342 | Record callback, retaining all reachable arms after returns |
| `604A6` | 112 | Record callback, retaining its delayed stack frame |

`60856` stores `5E8BC` and `60516` at RAM `2000343C` and `200034F8`. Given completed initialization, successful allocation, `20003240 == 0`, unchanged pointers and the original private ABI, `5E942` calls `43B28(A0=60516, A1=3)`, storing into `200031D4`. The scheduler loads that slot at `20000816` and calls it at `20000818`. Live ordering, pointer values and all callee effects remain unproved.

Actual C11/C++17 objects are identical. Original-address re-encoding compares every byte; complete CFG/own-frame checks, independent ELF readers and a nonloadable partial link pass. The union contains **36,504 CODE + 392 DATA bytes / 12,602 instructions**, with zero named UND symbols. This does not close runtime dependencies. **40 of 51** register-transfer sites now have at least one evidenced conditional domain: 30 target/target-set domains and 10 skips/caller gates. Eleven sites remain unjoined.

Original APP static coverage remains **95.54%**. Reused compile-only ABI assertions check numeric widths, not the physical ABI. Four startup source bytes remain missing; chip, ROM, RAM, IRQ, Flash, OTA and complete hardware behavior remain unverified. No target, model or emulator execution; no BIN generated.

[C/C++ source](resident_slot3_record_path.c) · [Evidence](evidence-v1.json) · [Checker](audit-v1.py) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

Read-only revalidation from the project root, with `LLVM_BIN` pointing to the checked tools:

```sh
python3 experiments/tsl9-resident-slot3-record-path/audit-v1.py --tool-dir "$LLVM_BIN"
```

Retained local reference files and build artifacts are required; public text receipts do not replace them. On Windows, use `py -3` if needed.
