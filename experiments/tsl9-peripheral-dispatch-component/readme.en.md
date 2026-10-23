# Peripheral-write and receive-dispatch partial composition

[繁體中文](README.md)

Actually partially link the existing 950B dispatch component and 212B native peripheral-write object: 1162B, 402 instructions and 49 genuine FUNCs. Preserve cold regions, all input bodies and 57 pending RELA entries; five genuine UND remain. The appended provider is at offset 950 and its existing callsite is at 888, checked against the actual input object.

This is a diagnostic VMA0 `ld.lld -r --no-relax` component. Symbol binding does not resolve machine control operands or prove ordinary C ABI, original placement, ROM, silicon or OTA compatibility. No BIN is generated or executed; this is not flashable firmware.

`build.py` fully replays both existing formal chains, then runs exactly one linker and one LLVM readback per language without compilation. Fresh output directories retain actual recipes, logs, objects and receipts. Checks cover the complete source/tool closure, every body, symbol, relocation, original fixed bits, control operand families and all 402 readback rows. Negative controls mutate in-memory ELF or typed inputs without relying on whole-file hashes. Firmware and input objects remain unchanged.

```sh
python3 experiments/tsl9-peripheral-dispatch-component/build.py \
  --project-root "$TSL9_ROOT" --llvm-bin "$LLVM_BIN" \
  --dispatch-root "$TSL9_ROOT/experiments/tsl9-record-dispatch-component/build/component-v1" \
  --peripheral-root "$TSL9_ROOT/experiments/tsl9-peripheral-write/build/verified-v2" \
  --build-root "$TSL9_ROOT/experiments/tsl9-peripheral-dispatch-component/build/component-v1"
python3 experiments/tsl9-peripheral-dispatch-component/check.py \
  --project-root "$TSL9_ROOT" --llvm-bin "$LLVM_BIN" \
  --replay "$TSL9_ROOT/experiments/tsl9-peripheral-dispatch-component/build/component-v1/c/verification.json"
```

Use `cpp` instead of `c` for C++. Adding `--require-firmware-ready` must still reject after the complete static check. The default check validates source metadata only and does not claim a link run. Failed outputs are retained without overwriting or unbounded retries. Public derivative receipts are handled by the project's publication workflow; local originals must not be mislabeled anonymous public originals.
