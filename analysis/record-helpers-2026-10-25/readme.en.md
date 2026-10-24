# Record helpers and periodic callbacks

[繁體中文](README.md) · [English](readme.en.md)

Twelve whole functions add **910B /306 instructions**. Twelve old imports gain real bodies;ten new dependencies are exposed,including three static data addresses. The remaining count is145. No new firmware BIN or live control was produced.

| Static proof | Result |
| --- | --- |
| Standalone C11 /C++17 | Same object;68 code regions,73 RELA,51 direct controls,11 typed address pairs |
| Curated source | 128 C/H;202 function comparisons plus2 independent data comparisons =204 comparisons /408 objects |
| Component | 37,372B code +1,750B data;13,023 instructions;3,119 FUNC,71 retained zero-size aliases,2,468 RELA;145 true imports |
| Original addresses | All39,122 selected bytes equal the official BIN;3,132 owners in112 adjacent-only spans |
| Transfers | 2,198 direct transfers;771 call-return positions;zero ordinary continuation gaps |
| Semantic checks | 140 reviewed opcode witnesses and29 decoded RAM address checks |

Confirmed behavior:

- F47E stores the requested byte,keeps full-width request/notification inputs and preserves the entry opposite flag snapshot across F1C2. That snapshot controls callback/cancellation;it is not a fresh state-byte reload.
- F4D0 uses a zero test to toggle BFA1 and reschedules itself with numeric50. F578 increments BFA6 modulo256 before its unsigned threshold3 test,selecting135 or1500. Both update local record bits and force F1C2 submission.
- EF76 updates the mode byte and selects unprovided addresses1A430/1A454/1A478 with counts17/17/53. F016 preserves its writes around EE9A,including ignoring that call's result.
- F058 selects25/40/32 from settings or cancels and directly invokes EDF2. DE82 forwards the full input as a schedule argument. A6AA,B0B0,B572,B594 and18218 preserve their clear/store/normalize/mask order.

The register-bound C includes explicit private architecture ports;whole original source and ordinary/async ABI restoration are not claimed. Schedule values have unknown time units;seat/do-not-disturb labels remain unconfirmed.

Seven new helper/callback bodies and three table payloads remain unprovided. Current roles are121 direct provider names,24 address-only names and one mixed direct/address name(EDF2,included among direct names). The prior opaque default and17 static pools remain unprovided.

Physical MCU/board,installed ROM,RAM ownership/capacity,IRQ/startup/Flash/OTA remain unproved. The diagnostic ELF has entry0 and no PT_LOAD. No target,host model,ISA emulator or hardware was executed. The full authentication body remains private/unresolved.

[Instruction evidence](evidence.json) · [Contracts](provider-contracts.json) · [Measured summary](summary.json) · [Remaining providers](next-providers.json) · [Feature candidates](feature-candidates.json)

[Selected source](../../src/native/receive/record_helpers.c) · [Native recipe](../../experiments/tsl9-record-helpers/spec-v1.json) · [Source proof](../../experiments/tsl9-record-helpers/verify-source-v1.py) · [Integration recipe](../../experiments/tsl9-record-helpers/integration-v1.json) · [Layout recipe](../../experiments/tsl9-original-layout/spec-v31.json) · [Flow verifier](../../experiments/tsl9-original-layout/verify-flow-v34.py)

From the repo root,with the pinned local tools and retained receipts:

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v34.py --replay experiments/tsl9-original-layout/build/record-helpers-flow-v1
python3 -B experiments/tsl9-record-helpers/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-helpers/build/component-v2
```

`LLVM_BIN` is your local LLVM bin directory. Raw build receipts and superseded trials stay local. No flashing occurs.
