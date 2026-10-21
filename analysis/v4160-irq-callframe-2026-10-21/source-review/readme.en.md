# Independent callframe host review

This scope reviews the actual frozen `interrupt_callframe.c` and `rcc_helpers.c` as two linked host translation units. It reuses the sealed independent fixture in `tsl9-v4160-placement-2026-10-21/code-review`; it does not duplicate its oracle or change its old seal. Exact inputs and selected receipt hashes are in [review.json](review.json).

Each C11 and C++17 run checks four groups, 3,820 cases and 138,312 assertions. The standalone helper matrix covers all four offsets, full 32-bit masks and values, and eight enabled words including noncanonical nonzero values. It checks both branch-dependent output tuples: enabled A4 is the base and A5 is the freshly read word; disabled A4 is the read word and A5 is the base. This distinguishes the base from the full accessed address.

The initializer oracle checks 20 ordered external effects: CSR clear, six independent read/write pairs, six PFIC stores, CSR set. All six read samples differ. Store widths, addresses, values, helper sequence, normal output observations and the actual C return are checked. Synthetic CSR state changes between effects prevent a cached snapshot from satisfying the final update. All addresses are numeric fixture keys; no peripheral address becomes a host pointer.

Thirty separately compiled mutants per language must run and fail an oracle assertion. They corrupt call target/order/enabled arguments, final result and return bridge, CSR masks/operations, PFIC widths/addresses/masks, dynamic masks, enabled semantics, branch output residues, read freshness and read/write order. A compiler failure does not count as a rejected behavior mutant.

These tests validate host function linkage and synthetic observable behavior. Host `CF_CALL` is an ordinary C call; native `CF_CALL` instead uses inline assembly JAL and a declared clobber set. Host `CF_RETURN` reports an explicitly supplied output tuple; it does not capture actual target A1/A4/A5 registers. The host branch also replaces CSR, memory access and fixed-register primitives. This review proves no target stack frame, save order, register preservation, JAL reachability, instruction identity, placement or hardware behavior. Native validation must bind the separately linked machine artifacts. No target execution, ISA emulator, device access or network request occurred, and this is not an OTA-ready image.

Reproduce only the host test from any checkout using an available C/C++ compiler:

```sh
sh verify.sh --project-root /absolute/project --language c
sh verify.sh --project-root /absolute/project --language cpp
python3 check-review.py --project-root /absolute/project
```

`--project-root` must identify the checkout containing `experiments` and `scripts/portable_verify.py`. The evidence sibling accepts the documented `tsl9-` and shortened publication folder names. The Python entry was run directly on Windows; this shell wrapper was not executed here. New runs create unique excluded `build/` directories and selected JSON copies in `receipts/`. The sealed selected JSON records executable/input/compiler hashes; historical EXEs, object files, compiler logs and mutant sources remain only in the working archive under excluded `build/`, not in the published evidence. Reproduction executes only newly compiled owned host code.
