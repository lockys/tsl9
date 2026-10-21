# IRQ callframe and pre-integration evidence

[繁體中文](README.md)

The readable C/C++ core is `experiments/tsl9-v4160-irq-callframe/`. Native components contain a 144-byte main and four 30-byte helpers: 264 bytes /94 instructions at the five original entries, without extra C++ unwind allocations. This establishes component extents and normally completed callframe facts; an original-hardware-compatible full BIN remains unfinished.

| Scope | Confirmed | Limit |
| --- | --- | --- |
| source-plan | Original16-byte frame, six4-byte JALs, normal outputs;11 raw controls | Static original source contract |
| cpp-profile | Only `-fno-exceptions` removes metadata from the old300-byte core, with function bytes unchanged | Separate predecessor experiment still has180-byte main |
| source-review | 3820 cases /138312 assertions per language;60 compiled mutations rejected | No native bridge/stack proof |
| compiler-review | 264 bytes /94 instructions per language, original JALs, frame reloads, IR and controls | Four prologue stores reordered |
| image-plan | 34 carrier C TUs,691 allocations and53 canonical alias bindings | Integration plan and retained-object audit, no new image |
| feature-candidates | Proposed additions with existing-source extension points | Proposals only, without implementation or device verification |

The five proposals cover DND state/interval preview, connection/update-stage status, settings snapshot differences, offline firmware inspection and redacted diagnostics. See the [proposals](feature-candidates/readme.en.md) and [evidence location map](evidence-locations.json). Links inside the sealed proposal preserve original workstation provenance. Unpublished raw JS is not copied merely to repair those links; missing source artifacts are not reported as a fresh replay.

Main's SP adjustment and134 bytes after offset10 equal the original. All120 helper bytes are identical. Only the four2-byte stack-store instructions at0x9A44/0x9A46/0x9A48/0x9A4A are permuted. Slots and stored-value sets match, but intermediate stack bytes differ; pointwise and asynchronous IRQ equivalence remain unproved.

```sh
sh experiments/tsl9-v4160-irq-callframe/verify.sh --language both
sh experiments/tsl9-v4160-irq-callframe/verify-native.sh --tool-dir /path/to/llvm/bin --language both
```

Python directly launches each backend. The sealed cpp-profile CLI only recognizes its original workstation dependency layout. In published copies use sibling `run-cpp-profile.sh --tool-dir /path/to/llvm/bin`. This adapter verifies sealed bytes, then changes only the dependency path constant in memory, preserving sealed files, compiler profile and verification gates.

Historical build archives are excluded. Metadata-bound old full-image objects and earlier ABI replays are not described as fresh published-location compilation. Hosted and new native components are actually rebuilt at delivery locations. The existing76,800-byte source-identical image remains unchanged. No RV32 execution/ISA emulation, hardware/vendor access or new BIN occurs.
