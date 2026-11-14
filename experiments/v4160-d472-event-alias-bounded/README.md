# D472 event alias: bounded source audit

This isolated, standard-library-only audit reads five files from the repository root. It checks fixed SHA-256 pins, the two selected manifest entries and their complete ordered C11/C++17 profile flags, the selected event JAL/relocation text, leaf declaration text, compact alias mapping, and selected aggregate-script text for alias construction, `--defsym`, remaining undefined symbols, and symbol section-index and value comparisons. It does not run the aggregate script.

The pins correspond to the five Git blobs in commit `5b62cd05ac3ddbbb75114ae88d8ca7434fbb8b4e` (the stated verified remote main); local `git hash-object` values were compared with `git ls-tree` for that commit. This comparison uses the locally available Git objects, not a new remote verification.

| Input | SHA-256 |
|---|---|
| `src/source-build-manifest.json` | `466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739` |
| `src/compact-layout.json` | `af2aec2d6b88b40c72c4f7ddc1c696630ac65f25462d3173c18d53d140896b4b` |
| `src/native/receive/state_events.c` | `c33e586aa7fd0eea2aef5367f3408675aa4615fc5e2d50d2243cc7a3350d55cf` |
| `src/native/receive/state_leaf_reads.c` | `28678f21b07c71613fe5f7b0f3e4f8a69d2b732a98e98d9d9be125653c2f7487` |
| `scripts/verify-source-aggregate.py` | `e6fd9bb60f2414fe7a60f25d3e751c0d459978a25487c234b926ce4248674a37` |

Selected mapping: `tsl9_events_external_d472` → `tsl9_state_leaf_entry_d472`; event profile `ring-bank`, leaf profile `queue-consumer-a0-a5`.

From repository root:

```
python -B experiments/v4160-d472-event-alias-bounded/audit.py
python -B experiments/v4160-d472-event-alias-bounded/test_audit.py
python -B -O experiments/v4160-d472-event-alias-bounded/test_audit.py
```

Tests create and remove copies inside this experiment. They reject changed or missing inputs and exercise repinned changes to selected profiles, relocation, symbol, mapping and aggregate checks. A copied CLI is also tested with an altered input under normal and optimized Python. A separate repinned, syntactically valid but disabled condition demonstrates that a text fingerprint can pass without the corresponding guard being effective. Re-pinning is test-only via the Python function; the CLI always uses fixed pins. Both normal and optimized runs use explicit exceptions, not assertions in the audit.

**Limits:** Hashes establish identity to the pinned bytes, not provenance or trust. Text fingerprints can occur in comments or dead code and are not parsing, semantic or control-flow proofs. This does not compile, inspect generated relocations or symbols, perform a link, establish ABI compatibility or runtime behavior, or establish correctness of the alias at execution. It makes no full-image claim and does not execute, emulate or flash target code.
