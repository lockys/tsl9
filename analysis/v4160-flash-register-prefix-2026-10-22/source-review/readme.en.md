# Independent Flash register and instruction-frontier review

[繁體中文](readme.zh-TW.md)

The final C11/C++17 objects, IR and linked components were independently read. All five Flash leaves, **198 bytes / 76 instructions**, are byte-identical to original ID2966. The 64-byte / 23-instruction quarter wrapper retains its existing three-store permutation: six changed bytes and three instruction-frontier differences. Total ownership remains 262 bytes / 99 instructions. No full firmware BIN, RV32 execution, emulator, hardware or network operation was produced/performed.

Both final components have SHA-256 `575b2e1009437c77d71081fffeaa32988ff10b23c78decb01e9ad976c5e6c9c7`. This component evidence does not update the previous `de159…` full-image proof automatically.

## Source-backed frontier requirements

`baseline.json` was extracted from actual original `0ee64183…` and prior integrated `de159bb3…` images. Portable review freshly decodes all 99 original instructions and rechecks twenty existing raw source controls, while explicitly declining to claim rereading an absent prior full build archive.

| Entry / extent | Original requirement and previous discrepancy | Final result |
| --- | --- | --- |
| `18E90` / 8 | A5 base, SW32 A0 to base+12, RET via RA. | Already and still exact. |
| `18E98` / 30 | Materialize A3 high, A5 base, A3 low, A4 high; first key1 store at18EA8 precedes key2 low ADDI at18EAA. Prior materialization/store order differed. | All ten instructions and boundaries exact. |
| `18EB6` / 14 | A4 base; fresh CTRL into A5; A3=8000; OR/write A5. | Already and still exact. |
| `18EC4` / 46 | Fresh CTRL into A4 at18EC8, A3 mask at18ECA, A0 alignment at18ECE; RMW/poll use A4. Prior alignment was earlier and several scratch uses were A3. | All nineteen instructions exact. |
| `18EF2` / 100 | First CTRL read into A5; A3 mask before A0 ANDI at18EFA. Prior read used A2 and18EFA was inside a different 32-bit instruction; later commit/poll scratch registers also differed. | All thirty-eight instructions exact, including both ADD source encodings. |
| `9C0A` / 64 | Original saves S0,S1,RA; existing compiler prologue saves RA,S0,S1. | Unchanged wrapper retains six different bytes / three frontier differences. |

These differences go beyond normal-return values. For example, key2 may contain only its high part versus its completed value before a potentially faulting store; A2 may have been overwritten before the first program poll; a nonterminating poll may expose different A3/A4 contents. Those are static deductions from encoded operands, not observed faults or interrupts. Exact leaf bytes provide stronger encoding evidence but do not establish hardware exception precision, timing or asynchronous behavior.

Restoring the18EFA instruction boundary does not establish safe arbitrary interior entry: required live registers, control flow and caller state remain separate obligations. No fabricated alias or absence of computed/encoded/ROM references is inferred.

## Actual checks and reuse

`frontier.py` decodes instruction fields without CPU state or instruction evaluation. It compares each PC, width, opcode, destination/source registers, immediate and target. A separate narrow comparator permits same-destination commutative ADD/AND/OR source exchanges to explain earlier candidates. The final gate is stronger: all198 leaf bytes must match.

All six actual partial objects have one original-size executable function allocation, the original destination-register set, no hidden leaf dependencies, and exactly five wrapper JAL relocations at original offsets. Partial/linked bytes differ only in those JAL immediate fields. IR checks independently bind volatile32 sites, the post-firststore key2 dependency, and the initial read/mask/A0-alignment SSA order.

Readable C retains memory operations, polls and loops. Native constraints use empty fixed-register identity barriers plus two bounded address ADD primitives: A1/A0 plus A5 into A3 in original operand order. This is not pure standard C. The leaf IR checker admits precisely those two ADD strings, not arbitrary opcode bodies. IR text checks are not claimed to be a complete formal semantics proof.

Each final producer language archive passed read-only replay of57 actual files,99 raw instruction controls and three actually compiled native controls. This review additionally rejected twelve real ELF mutations and seven real IR mutations. Eleven ELF cases regress a register/order frontier; one commutative ADD encoding case fails only the stricter original-byte gate and is explicitly not mislabeled a semantic frontier difference. IR controls cover volatility, width, the initial A5 bridge, mode masks, key2 dependency, and address operand/opcode changes. Their component and IR identities match the final build exactly. Actual mutant files remain local under `build/controls`; the retained receipt is archival, not a claim of default regeneration.

The source audit pins five final core files, unchanged host backend/public header and preexisting HOST macros, and63 ordered provider expressions after reducing address aliases to existing `fn_add`. Added host primitives are identities, fully-known constants and existing unsigned32 addition; split key constants are checked modulo2^32.

The unchanged independent `expected-effects.c` was freshly compiled and executed against the final core in C11 and C++17: **12 synthetic scenarios /8964 checks each**. Every host executable was format/architecture guarded before launch; no RV32 execution occurred. There are **zero newly compiled independent semantic mutants** this round; the old mutant matrix was not repeated. Original evidence/oracle/backend are reused by exact identity; new machine-code and positive-host evidence were actually checked this round.

## Portable entry

Metadata, current source, original99 instructions and20 controls:

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin
```

Actual new objects/IR/component plus archived receipt and strict leaf-byte admission:

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin --receipt /path/to/native-build/c/verification.json --require-exact-leaves
```

`--candidate-folder` checks the six objects, IR and component without claiming full receipt replay; `--candidate-elf` checks only linked instruction frontiers. The shell wrapper uses `PYTHON` or `python3`; Windows may invoke Python directly. Controls/positive host checks require fresh output directories rather than modifying this sealed record.

ROM, full-image integration, wrapper pointwise/asynchronous equivalence, physical fault prefixes, chip compatibility, installed BOOT identity and OTA acceptance remain unproved. No newly proposed user feature is claimed implemented.
