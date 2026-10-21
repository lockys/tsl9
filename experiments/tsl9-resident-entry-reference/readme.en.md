# Resident entry reference

This candidate-specific C/C++ model covers entry, initialization and RAM seed dataflow:230 bytes/66 instructions plus a4-byte header. The source proof rejects35 raw operand mutations; each language's host suite has5 groups/121,496 checks.

```sh
sh ./verify.sh --language both
```

The portable entry verifies the exact carrier, tail, Runtime, source seal and dependencies before compiling our host program. Strict main-only data stops at source6EAA4; main+captured tail stops at6EB2C. Neither path may skip the missing read to zeroing or MRET. Synthetic unknown-memory fixtures are conditional experiments, not artifact repair or physical fault proof. Live registers, helper identity conditions and explicit return/MRET boundaries remain part of the model.

The selected reference does not identify installed ROM or establish a native ABI. No original execution/emulation, physical I/O or BLE OTA validation occurs. The [historical sealed note](README.md) remains unchanged for old receipts.
