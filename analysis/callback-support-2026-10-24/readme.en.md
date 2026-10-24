# Callback pointer and payload support reconstruction

[繁體中文](README.md)

Two complete functions now bind in [C/C++](../../src/native/receive/callback_support.c): **D1A8 pointer return10B plus16DAC payload wrapper40B,50B/18 instructions**. Five original regions retain real control references,32B frame and calls,without replacement results.

C11/C++17 components are identical: **14668B code+674B data,5096 instructions,963 RELA,78 genuine UND**. All previous14618B code and674B data remain unchanged. The new16CC4 call binds the existing actual implementation. Native placement makes all selected **15342B** match the official BIN at original addresses. This remains an entry-zero diagnostic ELF without PT_LOAD, **not flashable firmware**.

| Original entry | Confirmed static behavior |
| --- | --- |
| D1A8–D1B2 | Returns `0x2000BF48` without dereferencing it. After133A8,the caller sets A1 to that pointer,A2=19,A0=SP+60,and indirectly calls S0 |
| 16DAC–16DD4 | Returns immediately when `((A0-1)&255)>1`; otherwise retains full A0 and calls16CC4 with A1=SP+12,A2=2,A3=0 |
| 16DBA–16DCC | Creates32B frame,saves RA atSP+28,stores two zero bytes with SH zero atSP+12,and performs real JAL16CC4 |
| 16DCC–16DD4 | Restores RA/SP and returns,or directly returns through the conditional target; both exits retained |

The low-byte predicate does not validate full A0 as exactly1 or2; full A0 is forwarded. The19B field meaning,actual S0 target and physical send effect remain unknown. Length alone does not establish VIN identity,and no hardware commands were executed.

[Original instructions](evidence.json) · [Results and hashes](summary.json) · [78 pending providers](next-providers.json) · [Integrator](../../experiments/tsl9-callback-support/integrate-v1.py)

The collection has103 C/H files,76 code units and one independent data unit:154 comparisons/308 objects. Prior150 results and901 artifact records are unchanged. Of838 direct transfers,760 target measured instructions and78 remain unimplemented references. All4678 ordinary sequential and293 potential call-return positions are owned. Runtime context/targets for240 register-indirect transfers,10 MRET and the8034 EBREAK remain unproved; this is not complete CFG or hardware equivalence.

Next: the complete171BA pending entry and writers/consumers of2000BF48. Possible added feature: **offline field-layout export with identifier masking**,currently a proposal only; no module control strategy was changed.

Physical MCU,RAM/installed ROM,private ABI,asynchronous IRQ and OTA compatibility remain unproved. No target/HOST/ISA execution,hardware,network,BIN,commit or push. Historical personal information remains unresolved.

```sh
python3 experiments/tsl9-callback-support/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-support/build/component-v1
python3 experiments/tsl9-original-layout/build-v9.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/callback-support-v1
python3 experiments/tsl9-original-layout/verify-flow-v8.py --replay experiments/tsl9-original-layout/build/callback-support-flow-v1
```
