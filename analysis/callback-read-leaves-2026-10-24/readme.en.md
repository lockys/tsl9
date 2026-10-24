# Callback byte getter reconstruction

[繁體中文](README.md)

Eleven complete getters, **94B/29 instructions**, now bind actual providers in the [C/C++ source](../../src/native/receive/callback_read_leaves.c). Each performs LBU and returns A0, retaining original AUIPC or live GP addressing. No constant-result replacement or new external dependency is used.

C11/C++17 components are identical: **14618B code +674B data,5078 instructions,961 RELA,80 genuine UND**. All previous14524B code and674B data are retained. Native linker placement makes all selected **15292B** match the official BIN at original addresses. This is an entry-zero diagnostic ELF without PT_LOAD, **not flashable firmware**.

| Original entry | Static read address | Complete extent |
| --- | --- | --- |
| `181C4` | `0x2000C925` | 10B / 3i |
| `8440` | live `GP + 364` | 6B / 2i |
| `B1B0` | live `GP + 196` | 6B / 2i |
| `C35A` | `0x2000BF12` | 10B / 3i |
| `CD44` | `0x2000BF26` | 10B / 3i |
| `F6B0` | `0x2000BF9D` | 10B / 3i |
| `F6E2` | `0x2000BF9F` | 10B / 3i |
| `F714` | `0x2000BFA2` | 10B / 3i |
| `F746` | `0x2000BFA4` | 10B / 3i |
| `FA2A` | live `GP + 278` | 6B / 2i |
| `FA36` | live `GP + 279` | 6B / 2i |

PC-relative addresses depend on placing each entry at its original PC. GP entries retain live GP rather than assuming its runtime value or physical memory validity. Calls at13450 and13462 separately read181C4; subsequent shifts/masks assemble different bits from fresh values. This proves neither a coherent snapshot nor field meaning.

[Original instructions](evidence.json) · [Results and hashes](summary.json) · [80 pending providers](next-providers.json) · [Integrator](../../experiments/tsl9-callback-read-leaves/integrate-v1.py)

The collection has102 C/H files,75 code units and one independent pointer-data unit:152 source comparisons/304 objects. Prior148 results and889 artifact records are unchanged; frozen checkers were not edited. Of836 direct transfers,756 target measured instructions and80 remain unimplemented references. All4663 ordinary sequential and292 potential call-return positions are owned. Runtime targets/context for237 register-indirect transfers,10 MRET and the8034 EBREAK remain unproved; this is not a complete CFG proof.

The other nine callback entries retain bounded48B windows and are not presented as complete functions. D1A8 shows an AUIPC/ADDI/RET pointer-return window, outside the byte-getter scope. Next: confirm that complete entry, then16DAC and state writers.

Possible added feature: an **offline state-field inspector** displaying addresses and known bit-assembly evidence. This is only a proposal. Field semantics,GP/RAM ownership,concurrent state,physical MCU/ROM/startup/IRQ and OTA remain unproved. No hardware,network,target/HOST/ISA execution,BIN,commit or push; historical personal information remains unresolved.

```sh
python3 experiments/tsl9-callback-read-leaves/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-read-leaves/build/component-v1
python3 experiments/tsl9-original-layout/build-v8.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/callback-read-leaves-v1
python3 experiments/tsl9-original-layout/verify-flow-v7.py --replay experiments/tsl9-original-layout/build/callback-read-leaves-flow-v1
```
