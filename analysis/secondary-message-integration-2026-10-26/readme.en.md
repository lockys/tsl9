# Secondary message: curated SRC integration

[繁體中文](README.md) · [Verification summary](summary.json) · [Evidence](evidence.json) · [Unprovided contracts](provider-contracts.json)

Nine original-context CODE bodies and two DATA objects are curated into `src/`. Formal address-byte coverage is now **72,610 / 76,800 = 94.54%**: 68,648B CODE plus 3,962B DATA. This is not feature completion or flash readiness.

- 158 C/H files,124 CODE/eight DATA units;264 C11/C++17 comparisons and528 actual objects pass.
- All156 previous source files,246 CODE results and1,477 artifact identities remain unchanged;the frozen verifier is unmodified.
- The curated component and original-coordinate link retain all5,215 relocation roles,71 real CODE aliases and six real DATA labels.
- Static checks cover23,314 instructions,4,576 direct transfers,1,406 call-return positions and13 guarded jump tables,with zero ordinary position gaps.

[Message/dispatch C/C++](../../src/native/receive/secondary_message_dispatch.c) retains original register,stack,ROM and control ports. [DATA C/C++](../../src/native/receive/secondary_message_data.c) supplies only seven event cells and the observed12-byte copy source,without adjacent padding. The cells reach six actual CODE entries;two DATA and five callable HI/LO operands bind positive real providers.

Six compiler UND remain. The existing lookup at `0x1AAE8` is outside that inventory and still lacks a global index bound. The905 register-indirect transfers include RETs;runtime targets and global reachability are not all proved. The original EBREAK/vector boundary at `0x8034`/`0x8038` remains;its handler/resume target is unproved.

## Reproduce

Specs pin tool versions and hashes. Current evidence uses the existing Windows/NDK27.1.12297006/LLVM18 environment. Set `LLVM_BIN` and create fresh outputs in order:

```sh
python scripts/verify-curated-source.py --tool-dir "$LLVM_BIN" --build-root build/curated-source/secondary-message-20261026-v1
python experiments/tsl9-secondary-message-data/build-v2.py --tool-dir "$LLVM_BIN" --include-curated --trial data-v2
python experiments/tsl9-secondary-message-data/verify-source-v2.py --tool-dir "$LLVM_BIN"
python experiments/tsl9-secondary-message-data/integrate-v2.py --tool-dir "$LLVM_BIN" --trial component-v2
python experiments/tsl9-original-layout/build-v64.py --tool-dir "$LLVM_BIN" --trial secondary-message-v2
python experiments/tsl9-original-layout/verify-flow-v64.py --trial secondary-message-flow-v2
```

Retain prerequisite-stage inputs listed by the [source index](../../src/readme.en.md). Trials cannot overwrite retained directories;use each native step's `--replay` for existing outputs. This milestone publishes text sources,verifiers and receipt summaries,with no newly uploaded ELF,`.o` or BIN.

**No flash-validated BIN is available.** The diagnostic ELF has entry=0/PT_LOAD=0. Six unimplemented addresses are hidden NOTYPE reference constants,with no ABS FUNC. No target/HOST-model/ISA execution,hardware access or vendor API request occurred. Complete startup,ROM ABI,RAM/IRQ,Bluetooth and OTA compatibility remain unproved. [Feature candidates](feature-candidates.json) are offline diagnostic-tool proposals only.
