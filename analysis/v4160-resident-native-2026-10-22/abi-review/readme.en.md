# Independent ABI review: three-argument native resident adapters

[繁體中文](readme.zh-TW.md)

The actual C11/C++17 objects expose three uint32 arguments and a uint32 result. Final public entries use direct volatile I/O and real `FENCE.I`, with no context/sret, stack or nested call. This establishes a bounded normal-effect projection, not complete original ABI, placement or hardware admission.

| Entry | Original bytes/instructions | Final bytes/instructions | Additional original-preserved registers written |
| --- | --- | --- | --- |
| compare `200004BC` | 62/19 | 52/19 | A6 |
| fill `2000039C` | 46/14 | 48/16 | A3, A6, A7 |
| copy `20000332` | 58/18 | 52/17 | T0, A7 |

Original copy already writes A6. Original fill does not write A3; A3 therefore belongs in its additional-write set. Other original scratch return values also differ.

The public entries total152B/52 instructions. Three genuine context algorithms and five genuine I/O globals remain separately allocated: another230B/86 instructions. The complete object contains11 real FUNCs,382B/138 instructions, no RELA and no UND. Unused globals are reported rather than hidden. No linking, BIN export, target execution or unchanged HOST rerun occurred.

The first ordinary profile used30B wrappers with64B frames and three CALL_PLT calls into the shared context/sret algorithms; the full object was320B/125 instructions. One motivated repair added include-boundary always_inline declarations and an empty full-width A0/A1/A2 exit bridge. Shared algorithm bodies remain immutable; only `zifencei` was added to the established target feature profile. Ordinary-profile source snapshots/receipts are historical; they cannot be replayed as current-source successes after the source change.

## Independent checks and limits

The reader decodes every instruction in all eleven allocated functions and compares operands with actual LLVM disassembly. It checks ownership, local CFG targets, register writes, widths, IR, real sources/tools, six actual `-MD` inputs and all four command records. Producer read-only provenance replay is an additional layer, not a substitute for the independent ELF/operand checks.

Complete measured operand/CFG inventories bind the three final entries without executing or interpreting CPU state. They establish guard read32/save, zero write32 and FENCE.I before initial argument tests, with saved-word restoration on every normal exit. Compare uses full32 A1 and returns0/1; fill writes low bytes and returns the advanced address; forward copy reads before each write and returns the initial destination. Actual RV32 additions/loops retain modular addressing. Final entries never write A1/A2/SP/RA/GP/S registers and have no runtime calls or spills. Actual IR confirms three numeric arguments, erased local context and full-width exit bindings.

Three raw single-operand counterexamples per language decode successfully and are rejected: wrong compare-expected register, wrong saved-word restoration, and halfword replacing copy's byte load.

Normal memory/result claims require mapped accesses that return normally. Extra A3/A6/A7/T0 writes remain observer/caller obligations, not automatically harmless because a conventional ABI calls them scratch, nor proof that every conventional caller fails. Compare/fill update A0 at different points relative to byte accesses, and final scratch values differ. Fault/interrupt prefixes, installed resident identity and physical hardware behavior remain unproved.

Fill48B exceeds original46B. Shorter compare/copy entries do not prove ownership of the remaining10B/6B. No tail padding, fixed placement, rerouted call, borrowed original body or relaxed storage gate is included.

## CLI

Default sealed metadata/source-only verification requires no generated archive:

```sh
python3 -B <case>/abi-review/check.py --project-root <ROOT>
sh <case>/abi-review/verify.sh --project-root <ROOT>
```

Explicit actual-object review and read-only replay:

```sh
python3 -B <case>/abi-review/review.py --project-root <ROOT> --folder <MODE> --receipt <NEW-review.json>
python3 -B <case>/abi-review/review.py --project-root <ROOT> --replay <review.json>
```

MODE requires final-source `verification.json`, `native.o`, `native.ll`, `native.d` and four actual command logs. Write independent receipts outside MODE so the producer artifact inventory is unchanged. Only explicit artifact modes report `actual_native_artifacts_read=true`; the default reports `metadata_only=true`. Retained `selected.json` observations do not replace fresh artifact review.
