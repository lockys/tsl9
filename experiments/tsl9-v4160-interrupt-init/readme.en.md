# Readable interrupt initialization reconstruction

This C11/C++17 implementation reconstructs the ordered peripheral effects and A0 result of ID2966 V4.1.60 entry `0x9A42` and its four RCC helpers. Its native build uses volatile word/byte MMIO and two CSR instructions. It does not contain a captured copy of the original instructions or a generic firmware interpreter.

The source proof covers five exact functions, 264 bytes and 94 instructions. The original entry clears CSR `0x800` bits `0x88`, performs six fresh RCC read/modify/write operations, writes three priority-style bytes and three enable-style words, and then sets CSR bits `0x88`. Setting those bits is unconditional; it does not restore their incoming value. The return value is the final fresh read at `0x4002100C` masked with `~0x101D`, not a status invented by the reconstruction.

```sh
sh experiments/tsl9-v4160-interrupt-init/verify.sh --language both
```

Requirements: Python 3.10+ and a C11/C++17 compiler. The Python backend can also be run directly. It verifies the exact original BIN, sealed source members and 94 raw negative controls before building our hosted tests. Tests use access primitives replaced by a synthetic in-process MMIO/CSR trace; they do not access physical devices. Both languages pass 4 groups / 6,680 checks, including changing values between reads, all nonzero helper flags and CSR bits that were initially clear.

Native compilation and static artifact checks are a separate step under `analysis/v4160-interrupt-init-2026-10-21/native-plan/`. A compiled RV32 component is not a firmware image or an original-address replacement. Standard C does not preserve the original caller-saved register residue, exact stack slots, instruction timing, fault behavior or interrupt ABI. Only the ordinary-call/effect interface is reconstructed here. The existing full-image gate and its unresolved resident entry are unchanged. No rebuilt BIN has been verified for BLE OTA.

The root portable registry continues to cover its previous four models; use the separate command above for this component. Local shell launch and cross-platform CI results remain distinct from Python backend results. The previous GitHub CI attempt could not start because GitHub reported account billing/spending-limit restrictions.
