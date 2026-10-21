# Finite data stage

`finite_data_native.c` reconstructs ten actual read-only source views without
filler or aliases. The independent role proofs support seven canonical **data
storage/identity** definitions: the 13B AD payload at `0x19DEC`, five NUL-ended
comparison literals (40B) and the 5B literal at `0x1A69C`. Sizes describe the
new C/C++ objects, not unknown original C object extents or opaque callees'
maximum read widths. No resident function ABI is provided.

The three U16 scheduling sequences at `0x1A430`, `0x1A454` and `0x1A478` use
own storage names. Their 17/17/53 words total 174B. The original canonical
pointer names remain genuine UND: state aliases, asynchronous updates and
object lifetime are still unproved. All three 2B gaps remain unallocated.

The native stage adds 232B to the prior 641 allocations. It retains the complete
unchanged prior validation, then checks both C11 and C++17 artifacts: 651 actual
allocations, 8107 semantic RELA occurrences, every inherited section and symbol
occurrence unchanged, exactly seven canonical data names resolved and precisely
23 dependencies left unresolved. The compiler's local mapping metadata is
matched against the actual standalone data unit with one explicit linker
normalization for `.riscv.attributes`; it is not treated as a global provider.

Code remains 70764B; RO becomes 3962B. The numeric-address witness covers
74726 original bytes, with 2074 bytes still absent from this integration. Every
captured byte and original address is checked. The witness's remaining numeric
assumptions are not implementations. Strict final linking must still fail;
there is no flashable BIN or OTA package.

From the reconstruction project root:

```powershell
python -X utf8 -B experiments/tsl9-v4160-startup/verify-finite-data-extension.py `
  --current-receipt <absolute-path-to-prior-version-literal-verification.json>
```

The verifier finds the local original firmware and sealed role proofs in
`analysis/v4160-data-frontier-2026-10-21`; explicit `--firmware` and
`--proof-root` select those local inputs. No target code is executed, no device
is accessed and no vendor endpoint is called.
