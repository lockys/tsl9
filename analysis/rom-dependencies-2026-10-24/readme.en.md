# ROM dependencies and state callback reconstruction

[繁體中文](README.md)

Seven complete functions now bind in [C/C++](../../src/native/receive/rom_dependencies.c): **422B/153 instructions,55 original regions,42 direct controls and one callable-address pair**. This closes9792,9FC2,A2EE,ABF2 and includes the required81DE,A204 and9F74 paths.

| Complete original extent | Size |
| --- | --- |
| `81DE–81EE` | 16B / 6i |
| `9792–979E` | 12B / 5i |
| `9F74–9F7A` | 6B / 2i |
| `9FC2–9FC8` | 6B / 2i |
| `A204–A2EA` | 230B / 81i |
| `A2EE–A37C` | 142B / 54i |
| `ABF2–ABFC` | 10B / 3i |

C11/C++17 components match: **15654B code+674B data,5457 instructions,1048 RELA,79 genuine UND**. Previous15232B code and674B data are retained. Closing four old references exposes10816,B6EA,D05C,so80→79. Native placement makes all selected **16328B** match the official BIN at original VMAs. This remains an entry-zero diagnostic ELF without PT_LOAD, **not flashable**.

9792 selects2 for full A0=0 or250 otherwise,then tails9454. 9FC2 freshly reads byte[GP+172];ABF2 reads byte2000BEE0 at its original PC. 81DE reads the configuration byte at offset5,masks low2 bits and adds1,retaining its original1–4 range.

A2EE retains its16B frame and every tail/RET path. Under original conditions,it updates GP+176 as(old+1)&3,setsGP+175=1,and forwards9F74 with low32(original input*1000) to9124. 9F74 clearsGP+175. Complete230B A204 preserves GP+178/179/180 state accesses,the40038-table indirect call and all branches. No default behavior replaces unknown tails. Units,action-code meanings and physical functions remain unknown;passing an address does not prove callback registration or execution.

[Original instructions](evidence.json) · [Results,fields and hashes](summary.json) · [79 pending providers](next-providers.json) · [Integrator](../../experiments/tsl9-rom-dependencies/integrate-v1.py)

The collection has105 C/H files,78 code units and one independent data unit:158 comparisons/316 objects. Prior154 results and925 artifact records are unchanged. Of917 direct transfers,838 target measured instructions and79 remain unimplemented references. All5009 ordinary sequential and317 potential call-return positions are owned. Runtime context/targets for261 register-indirect transfers,10 MRET and the8034 EBREAK remain unproved;this is not a complete CFG.

Next:10816,B6EA,D05C. Possible added feature: an **offline state-counter and callback-parameter inspector**,currently only a proposal,displaying raw values,addresses and unknown units without changing hardware controls.

Physical MCU,RAM/ROM,private ABI,concurrent state/IRQ and OTA remain unproved. No target/HOST/ISA execution,network,hardware,BIN,commit or push. Historical privacy issues remain unresolved.

```sh
python3 experiments/tsl9-rom-dependencies/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rom-dependencies/build/component-v1
python3 experiments/tsl9-original-layout/build-v11.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/rom-dependencies-v1
python3 experiments/tsl9-original-layout/verify-flow-v10.py --replay experiments/tsl9-original-layout/build/rom-dependencies-flow-v1
```
