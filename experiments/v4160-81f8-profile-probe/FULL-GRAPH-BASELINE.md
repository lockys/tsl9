# 0x81f8: baseline and graph replacement constraint

The existing v4.1.60 residual-callbacks integration verifier was run in an isolated source snapshot, against the SHA-256 pinned original firmware, using Android NDK LLVM 27.1.12297006. Command (with `TSL9_LLVM_BIN` set to the LLVM bin directory):

```
python -B experiments/tsl9-v4160-startup/verify-gatt-ingress-extension.py --spec experiments/tsl9-v4160-startup/evidence/residual-callbacks-integration.json --firmware <original-bin>
```

The verifier returned `passed: true`, `code_bytes: 70764`, `native_BIN: false`, `OTA_ready: false`. This is the **unchanged assembly baseline**, not a run with the pure-C candidate. It checks C and C++ modes; the receipt includes absolute local paths and was not committed. The baseline retains the original open ROM and callback contracts, and is not a flashable build.

As an integration feasibility check, `llvm-objcopy --remove-section=.text.tsl9v4160.direct_successors_81f8` against the resulting C `native-extension.o` failed: the section cannot be removed because `.text.tsl9v4160.post_table_code_a054+0x8e` has a relocation against `__tsl9v4160_call_81f8`. This is an actual relocation dependency, not proof that replacement is impossible. Build a candidate-aware graph from the original component objects instead; do not weaken historical fixed-source or relocation checks.

The separate `graph_probe.py` only replaces the owner in a three-source partial graph. The complete candidate-aware graph, original-address witness and unchanged surrounding sections/relocations remain to be checked. No execution, hardware, ROM identity or OTA claim follows from these offline checks.
