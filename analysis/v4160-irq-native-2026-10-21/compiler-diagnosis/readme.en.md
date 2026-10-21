# Actual cause of the reserved-stack diagnostic

This is one compiler diagnostic on the **unchanged frozen original IRQ-register C/header sources**. It removes only `-ffixed-x2` from the previous -Oz profile, allowing stack addressing while preserving every other reservation, including A1 and T0. It is **not an accepted native candidate** and does not relax the no-stack, register, no-hidden-call or original-layout requirements.

C11 and C++17 emit byte-identical machine functions: each of the four RCC helpers is **52 bytes / 21 instructions**, the initializer is **168 bytes / 62 instructions**, and an unexpected local `OUTLINED_FUNCTION_0` is **16 bytes / 7 instructions**. All five requested functions allocate a 16-byte frame. Exact ELF-bound disassembly covers all six functions without skipped bytes; independent raw destination fields confirm SP writes and T0 writes. No unresolved symbol or writable ELF allocation is present, but a resolved local outlined function is still a hidden implementation and fails the goal's no-hidden-call requirement.

The observed spills explain why this backend asks for SP in all five original functions. They do not prove that stack use is unavoidable for an equivalent readable C implementation.

| Function | Frame slot | Actual value and use |
|---|---:|---|
| Every RCC helper | SP+4 | OR(before, mask), retained for the enabled A0 commitment |
| Every RCC helper | SP+8 | selected after value, retained independently for the common return |
| Every RCC helper | SP+12 | fresh before value, stored in the outlined function and reloaded into enabled A5 or disabled A4 |
| Initializer | SP+8 | constant `0x02020006`, cached after materialization and reloaded for the third RMW |
| Initializer | SP+12 | constant `0x101D`, cached after materialization and reloaded for the fifth RMW |

The helper IR computes OR, AND_NOT and a select before its shared volatile store, then branches into the register-commitment blocks. The selected SSA value survives independently until the final return. The machine pattern retains the corresponding before/OR/select values in the three slots above. The compiler's assembly comments identify folded spills/reloads. The initializer uses its stack to cache repeated literal masks; there is no source/LLVM IR `alloca`, no explicit `frame-pointer` IR attribute and no actual frame-pointer setup. The complete internal allocator-pass cause has not been reconstructed; the concrete emitted spill values and sites are confirmed.

**A1 is not copied, spilled or restored in this diagnostic.** Each helper directly tests incoming A1 twice and assigns zero only on its disabled path. Thus a speculative incoming-A1 snapshot is not the observed cause. Main explicitly commits A1=1/0. The optimizer also creates a local outlined function: each helper uses AUIPC/JALR with **T0**, despite `-ffixed-x5`, and the outlined function returns through T0. The extra T0 write is confirmed from raw RD bits. Compiler register flags alone therefore cannot substitute for final machine checks on this toolchain/profile.

`analysis.json` gives the actual addresses, SSA names, slots and encoded-register summaries. Six transcript mutations per C/C++ artifact reject missing initializer/helper/outlined rows, altered raw bytes, truncation and an unparsed outlined line. These are static annotations and checker controls: no RV32 code, CSR, memory state or branch path is executed or emulated. Goal gates remain false.

The local pinned Clang hidden help reports:

```text
--enable-machine-outliner=<value> - Enable the machine outliner
  =never                         - Disable all outlining
```

This was obtained with `clang -cc1 -mllvm --help-hidden`, exit 0. The inferred driver spelling to evaluate in a future explicitly selected source profile is `-mllvm -enable-machine-outliner=never`; it was **not compiled here**. `clang-help-hidden.json` contains only relevant matched lines and the exact compiler/raw-help hashes. The raw help log remains local. No outliner-disable profile or further compiler/source alternative was tried.

```sh
# Fresh reproduction of this explicitly rejected-goal SP diagnostic only.
python apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-diagnosis/diagnose_stack.py --project-root . --tool-dir /path/to/llvm/bin --language both

# Read-only metadata/current-source check; replay local archives when present.
python apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-diagnosis/check_diagnosis.py --project-root .
```

The fresh CLI needs the frozen sources, local tiny parser and supplied LLVM tools, not historical build archives. It emits a diagnostic ELF, never a firmware BIN. `results.json` selects two byte-identical receipt copies. The read-only checker validates sealed metadata; add `--require-local-builds` to require the selected historical archives and repeat full raw coverage/spill annotations. Metadata validation is not fresh compilation. Build objects/ELF/IR/assembly/logs remain local. One initial gate rejected the unexpected sixth function; it was changed to record and reject the outlined candidate explicitly, and the initial archive is retained.

The next source-design question is a readable branch-first calculation/store/commit lifetime with explicit register commitments and controlled mask materialization. It has not been tested in this scope. Any future native candidate must actually pass no SP, no extra clobbers, no hidden calls, normal-output and original-layout gates before integration. No original/model/sealed evidence, delivery checkout or published checkout was edited. No network, hardware access, target execution, ISA emulation or OTA operation occurred.
