# Reset-memory C component: independent review

The reviewed component is `experiments/tsl9-v4160-reset-memory/src/reset_memory.c` and its header. Source requirements come from the sealed original memory slice `0x186BA..0x186F8` (62 bytes / 17 instructions), reviewed separately under `source-review/`. The original image and initializer are used as **data only**; no original or rebuilt RV32 code is executed.

The readable C core keeps the source's independent first/second/third GP observations, forward interleaved READ32/WRITE32 copy, unsigned comparisons, uint32 increments, fresh zero-start formation and word-width zero stores. It reports the A0/A1/A2 continuation values through a host-only test boundary. No source-level mismatch was found within that ordered numeric-memory interface. This conclusion does not prove native register allocation, SP/RA behavior, T0 residue, the optional fragment transfer or original entry/continuation ABI.

## Independent evidence

`independent-tests.c` implements a separately authored event oracle and two independent byte arrays. Expected forward-copy reads use a byte-level shadow updated after each expected write; actual callbacks update a different byte array. This catches live overlap, including numeric unaligned aliases, rather than treating the original initializer as an immutable snapshot. Every callback checks the next exact event and is bounded before any host memory access. Unexpected extra loops, GP observations or source reads fail immediately; no physical numeric address becomes a host pointer.

Each C11 and C++17 host build passes **5 groups / 538 cases / 193964 assertions**:

- Every copy count 0..32 paired with every zero count 0..12.
- Normal 32-word copy plus all 8758 zero writes, three independent GP values, unsigned sign-boundary comparisons and wrapped-bound skip cases.
- Forward overlap in both directions with gaps of one through eight words, using live byte-level contents.
- Numeric unaligned destination/zero-start requests, including partial-byte overlap effects. These are fake-backend cases and do not establish hardware alignment support.
- Exact-boundary skips, unaligned terminal cursor residues and reported A0/A1/A2 values.

Eleven source mutants are **actually compiled and rejected by assertions in each language**, 22 compiled negatives overall: cached copy bound, cached clear GP, signed copy comparison, wrong copy increment, wrong zero increment, inclusive copy bound, inclusive zero bound, wrong A0, wrong A1, wrong A2 and read-ahead address. A compile failure is not counted as a behavioral rejection. Each retained receipt pins the actual compiler, original input, component, independent test, runner, helper, executable and mutation results.

`receipts/` preserves byte-identical copies of both independent receipts and the parent's C/C++ host receipts (each 5 groups / 338 cases / 133601 assertions). Historical compiler logs, host executables, object files and generated mutation sources remain in the working archive's excluded `build/`; they are not required published payloads. Retained hashes record those actual local artifacts without implying they are available in a published checkout.

The event oracle also checks read-before-write order and exact widths on positive cases; the retained read-ahead mutant changes the read address, not the read/write order. The documented mutant count does not imply a separately compiled write-before-read mutant.

## Remaining native requirements

The host macro replaces only GP reads, numeric memory operations and three output observations. It cannot validate the production inline assembly or physical I/O. The C body is a new helper and may use a compiler-defined prologue/epilogue; the original memory slice falls through without RET or link formation. T0's original last-copy-word residue is not part of the three-output test interface. The next original instruction assigns T0=31 on ordinary straight-line continuation, but that alone does not prove absence of intervening physical trap/interrupt observation.

The native fragment's continuation symbol, stack state, untouched registers, actual A0/A1/A2 residues and GP observation sites require bounded native object/link review and a source-bound continuation adapter. Ordinary C semantics do not by themselves prove architectural binary transparency. Constant source address 0x1AB60 also needs the intended initializer at that mapped location in the final image. None of these host results proves hardware identity, RAM access, complete startup, ROM/IRQ compatibility or OTA readiness.

```sh
python3 run-review.py --project-root /absolute/path/project --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin --language c
python3 run-review.py --project-root /absolute/path/project --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin --language cpp
```

The runner requires Python 3 and an installed C/C++ compiler, using the project's portable compiler locator. It stores new receipts only beneath this review's `build/`. Tested locally on Windows/MSVC; these receipts do not establish Linux/macOS execution. There are no vendor requests, physical memory operations, target execution or ISA emulation.

`check-review.py --project-root /absolute/path/project` is a separate read-only identity/receipt check. It checks the sealed original source evidence, the current component input hashes and retained receipt hashes without rerunning compilers or host executables. Its success is receipt binding, not an additional behavior test or native proof.
