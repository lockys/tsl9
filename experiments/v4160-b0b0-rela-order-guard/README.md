# B0B0 RELA order and owner-boundary guard

`guard.py` SHA-256: `b21ed6d1909b2cd5b51642fdf3449f5b9ae59a20891ac1f8c28f08eb080045d8`. The local, uncommitted unit-split verifier reads, hashes and directly executes those same bytes through `load_pinned`; missing or changed bytes fail closed. Its `facts` calls both helpers on the real check path. The local partial-relink verifier pins that unit-split verifier in turn. Those experiments and their dependencies are not assumed present on clean main; this guard and its synthetic tests stand alone. Pins identify bytes, not trustworthiness.

## API and scope

- `check_owners(elf)` rejects SHT_REL, invalid/zero owner indices and more than one RELA section per owner, including empty and removed-target sections. A valid empty section need not exist on both sides.
- `relocation_facts(elf, target_section, target_index, target_name, mapping_kind)` returns `(retained, removed)`. Retained is an ordered list of `(record, symbol_owner, value, size, info, other)`, where `record` is `(owner, offset, type, addend, symbol_name)` and the owner is tagged as section name or special index. Removed target records remain in parser order. The caller compares the complete retained lists without sorting; duplicates and metadata pairing are significant. It also rejects mapping-symbol references, invalid owners/section symbols and retained references to the removed target.

Call `check_owners` before the projection. The caller must also enforce unique nonempty non-null section names and the other `facts` invariants; these helpers are not a complete ELF verifier. They neither parse ELF nor establish parser correctness, relocation composition semantics, ABI, linkability or runtime equivalence.

## Synthetic checks

From the repository root:

```text
python -I -S -B experiments/v4160-b0b0-rela-order-guard/test_guard.py
python -I -S -B -O experiments/v4160-b0b0-rela-order-guard/test_guard.py
```

The standalone guard suite passed **7 tests** in each mode. It covers same-site reversal, cross-site order, nonadjacent composition, duplicate count/order, metadata pairing, invalid owners, REL rejection, multiple sections including empty sections, input nonmutation, retained references to the target, mapping-symbol relocations and invalid STT_SECTION indices. It does not test a real parser, compiler, linker, target or ABI. The local uncommitted unit-split synthetic suite exercises the pinned integration path; this standalone suite does not test the verifier's loader.

After guard extraction, the local C and C++ unit-split and partial-relink offline replays passed. At that time the guard, unit-split and partial-relink synthetic suites passed 5, 25 and 30 tests respectively in normal and `-O` modes; the guard suite has since changed to 7 tests as above. Temporary ELF files were deleted. This is a local report, not a claim that clean main can replay or that ABI or runtime equivalence was established.
