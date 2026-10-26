# Scheduler polling/state-service candidate C/C++

[繁體中文](README.md) · [Main scheduler](../tsl9-resident-scheduler/readme.en.md) · [Idle service](../tsl9-resident-idle-service/readme.en.md)

Two complete bodies are reconstructed: conditional RAM0x20002610..0x2000263A (42 bytes) and Flash0x63DD0..0x63E58 (136), totaling **178 bytes/66 instructions**. This is a public SDK V1.31 candidate; installed ROM identity is unproved. The [C/C++ source](resident_scheduler_state_services.c) retains original registers and C/assembly, not an ordinary HOST-callable API.

## Verified

- Identical C11/C++17 objects; every original-context byte matches. There are21 positive FUNC regions and15 relocations. Eleven conditional Xwchc byte ports are checked against primary definitions and28 official vectors.
- Scheduler calls0x20000812/0x200008CC enter the polling body; far call0x2000096E enters the state service. Independent adjacent functions are excluded.
- Polling freshly reads bits0 of state bytes0/1 at0x20003514 and register word at `*(0x2000353C)+100`. If flags are not ready and the word remains nonzero, execution branches back to0x20002620. **Termination is unproved**; no timeout or negative target test is added.
- Every normal polling return follows a byte5 clear. The preceding byte5 load, whose result is unused, is preserved. A0 is not assigned a status; a fixed success return is not asserted.
- The state service freshly reads byte8 at0x63DDE/0x63E14/0x63E2C, checking8/6/7. **No single cached switch is substituted** because earlier handlers may affect later state.
- For state8, parameter block0x20003560 supplies A2=byte3 and A3=byte2. When the parameter bit0/buffer-pointer conditions hold, A0=buffer+2 and A1=buffer byte1; otherwise A0=A1=0 while A2/A3 are retained. A nonzero0x64F04 return sets state byte9 to1; status semantics remain unknown.
- States6/7 use descriptor pointers0x20003438/0x2000344C and byte11/byte7 guards. **The descriptor pointers themselves have no local null guard.** The own16-byte frame is released at normal return and before the0x57DAE tail.

Physical byte-state layout, descriptor bounds, register identity, ownership and handler side effects remain open. Retained compile-only BLE/clock assertions do not establish this runtime state layout.

## Genuine dependencies and composition

The real bodies resolve the previous0x20002610/0x63DD0 imports and expose three actual callees: **0x57DAE,0x6020A,0x64F04**. These remain genuine UND without stubs. Import counts are not functional-completion percentages. A608-byte positive0x64F04 reference is also retained, **not counted as reconstructed CODE** or proof of its semantics/dependency closure.

Actual nonloadable C/C++ ET_REL objects contain **5122 bytes CODE+256 bytes DATA/1782 instructions**,455 positive FUNC regions, one OBJECT and332 relocations. Every input byte, symbol and relocation is retained.

The previous **4-byte startup source gap**, unproved arithmetic semantics and overall callback/RAM contracts remain. APP byte coverage stays **95.54%**, not functional completion. No APP integration or new BIN is provided; physical RAM/ROM/ISA, IRQ, stack, Flash and original-hardware OTA compatibility remain unproved.

Evidence: [full audit](audit-result-v1.json), [summary](summary.json), [original instructions/callee reference](evidence-v1.json), [specification and hashes](spec-v1.json). Polling/phase diagnostics are unimplemented feature candidates.

## Reproduce

Provide the original APP, SDK/header/instruction references and retained native artifacts required by the spec, evidence and audit. Original SDK inputs and native artifacts are not included or automatically downloaded. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-scheduler-state-services/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-scheduler-state-services/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts, use `--replay experiments/tsl9-resident-scheduler-state-services/build/native-v1` for the first command and omit `--link-trial` for the second. No target, HOST model or ISA execution, hardware access or vendor API traffic was performed.
