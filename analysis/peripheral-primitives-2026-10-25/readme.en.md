# Peripheral primitives and calibration

[繁體中文](README.md) · [English](readme.en.md)

Twenty-four complete functions add **2,020B /677 instructions**. They supply22 old imports without exposing a new external provider. The remaining count falls from165 to143. No new data,firmware BIN or live control was added.

| Static proof | Result |
| --- | --- |
| Standalone C11 /C++17 | Same object;120 genuine code regions,64 RELA,direct controls only;external19160 is already supplied by the parent |
| Curated sources | 130 C/H;206 function/code-unit comparisons plus2 independent data comparisons =208 comparisons /416 objects |
| Component | 40,474B code +1,771B data;14,085 instructions;3,313 FUNC,71 retained zero-size aliases,14 readonly objects,2,598 RELA |
| Original coordinates | All42,245 selected bytes equal the official BIN;3,327 owners in106 adjacent-only spans |
| Transfer positions | 2314 direct transfers;827 call-return positions;zero ordinary continuation gaps |
| Semantic witnesses | 256 reviewed instructions;16 original signed DIV sites |

Confirmed instruction behavior:

- 188E2 conditionally pulses reset masks512/1024 through existing19160 for the two encoded pointer values. 1892E retains its three config-word masks and access order.
- 189AE retains full-width channel/rank branches and original variable shifts. The ADC-like helpers keep original word loads,bit gates and the low16 result extraction;no new bounds or clamps were introduced.
- 18F56 reads words at1FFFF7E8/1FFFF7EC and emits six bytes into the caller buffer. This supplies the source of the boot config's candidate MAC field;no actual identifier was read,and physical memory properties remain unproved.
- Clock-control helpers retain word/byte RMW widths,including the two separate zero-byte writes at1909E. 19220/19248 keep config-mode entry/exit and high-before-low halfword stores.
- 191C6 keeps consecutive high/low halfword sampling,rechecks the high word and conditionally samples low again. This is not proof of an atomic or monotonic physical counter.
- The complete1929A..196C4 calibration body keeps all signed DIV/register shifts,status polling,sign-dependent rounding,trim writes,full register restoration and post-return alternatives. S10 starts at4 and is decremented/truncated before its exit check;other hardware polls retain their original waits.
- 19764 keeps the GP+382 scaled multiply,low/high compare writes,two distinct control RMW cycles,status polling and final clear. Time units and interference remain unproved.

The register-bound C includes explicit architecture ports;no target,host model,ISA emulator or hardware was executed. Physical silicon,ROM/private ABI,clock inputs,calibration convergence,buffer/RAM/Flash capacity,IRQ and OTA compatibility remain unproved. Prior version data and14 readonly objects are retained. The opaque default and20 static payload references remain unprovided;the full authentication body stays private/unresolved. The diagnostic ELF has entry0 and no PT_LOAD.

[Raw evidence](evidence.json) · [Contracts](provider-contracts.json) · [Measured summary](summary.json) · [Remaining providers](next-providers.json) · [Feature candidates](feature-candidates.json)

[Selected source](../../src/native/startup/peripheral_primitives.c) · [Native recipe](../../experiments/tsl9-peripheral-primitives/spec-v1.json) · [Source proof](../../experiments/tsl9-peripheral-primitives/verify-source-v1.py) · [Integration recipe](../../experiments/tsl9-peripheral-primitives/integration-v1.json) · [Layout recipe](../../experiments/tsl9-original-layout/spec-v33.json) · [Flow verifier](../../experiments/tsl9-original-layout/verify-flow-v36.py)

With the existing pinned local tools and retained receipts,from the repo root:

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v36.py --replay experiments/tsl9-original-layout/build/peripheral-primitives-flow-v1
python3 -B experiments/tsl9-peripheral-primitives/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-peripheral-primitives/build/component-v1
```

`LLVM_BIN` is your local LLVM bin directory. Raw receipts remain local. No flashing occurs.
