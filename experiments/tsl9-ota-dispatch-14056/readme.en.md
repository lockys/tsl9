# Bounded command dispatcher model at 0x14056

[繁體中文](README.md)

The candidate instructions at `0x14062..0x140B6` classify a byte command. `0x45`, `0x52`, `0x53`, `0x55` and `0x57` reach `0x1408E`, which calls `0x9C4A` at `0x14094`. The caller at `0x8A48` targets `0x14056`. Command values alone do not establish complete OTA semantics.

The [C/C++ model in src](../../src/native/receive/ota_dispatch_14056.inc) classifies only those five forwarding cases; it implements no other branches or hardware calls. The verifier checks actual disassembled instructions and compiles the model to WebAssembly for all 256 synthetic byte inputs. This tests the model without executing the firmware.

`python scripts/verify-ota-dispatch-14056.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`

The model is not integrated into the candidate image and does not replace the original carrier. The complete ABI, other commands, abnormal entry, hardware and OTA compatibility remain unverified. Potential authentication material is not disclosed.
