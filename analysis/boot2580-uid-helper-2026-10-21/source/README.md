# Selected BOOT ID2580 UID helper source

The selected 12,288-byte BOOT is SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`, catalog ID2580, label V1.0.00. Its retained analysis base is `0x1000`, supported by the file's header value at offset `0x38`; this is not a physical memory measurement. The complete helper range `[0x1C4A,0x1CC4)` is **122B / 48 instructions**: builder56B/22 and matcher66B/26. The initial count49 was an estimate; the report uses the raw-row count48.

`source-map.json` retains every PC, file offset, width, original instruction, direct branch operand and static CFG edge. `contract.json` records the observed numeric-register and live-memory interface. The checker verifies the complete BOOT hash, exact122B span, all48 raw rows, load/store/control operands and 24 in-memory raw mutation rejections. It performs no ISA execution or emulation.

The source establishes these ordering requirements:

- Builder `0x1C4A` subtracts16 from SP and saves S1. It loads the first pointer at `0x1C52`, nominally from `0x4004C`, **before** saving S0, S2 and RA. It then requests the first loaded target with source `0x1FFFF7EC`, count8, and the input output-address register. The slot address is not a proven function target or copy ABI.
- After that target normally returns to `0x1C68`, source2 is computed from **live S0+2024 before S0 restore**. `0x1C6E` freshly loads the second target from **live S1+76 before S1 restore**. RA is freshly loaded at `0x1C72`; destination2 is computed from **live S2+8 before S2 restore**. The code sets count6, adds16 to then-current SP, and tails through the loaded T1 at `0x1C80`, without creating a new link. Its return destination is the then-live restored RA, not an automatically trusted original caller continuation.
- Matcher `0x1C82` rejects any full-width length unequal to14 without creating a frame or issuing a body memory request. Length14 creates32B, saves S0/RA, and calls the builder with the current SP as destination. Continuing at `0x1C94` requires the delegated builder tail to return to the expected link.
- Each compare iteration reads the **input byte first** at `0x1C9C`, then the **fresh expected byte at live SP+index** at `0x1CA4`. The first mismatch restores the frame and returns raw1; all14 equal returns raw0. Stack values are freshly loaded on restore. No buffer snapshot, constant-time behavior or always-successful memory/return is implied.

The source geometry is conditional: with expected register preservation, normal control returns, exact copy semantics, stable readable sources, valid storage and no destination overlap changing the source, the two requests are `[0x1FFFF7EC,0x1FFFF7F4)`8B and `[0x1FFFF7E8,0x1FFFF7EE)`6B. Output offsets12/13 and0/1 refer to the same source addresses `0x1FFFF7EC/ED`. Thus the tail2 equals the first2 **under those conditions**; the requests cover12 distinct source-byte addresses and produce14 output positions. This report reads no factory memory values and does not recover a real UID or generate a packet.

All pointer targets, memory validity, register/stack preservation, return targets, ROM ABI, installed BOOT identity and hardware behavior remain unproved. This package is source evidence for a synthetic live-state C/C++ adapter, not a recovered original C signature or a resident provider. HALT, TRANSFER and unknown memory/control outcomes must remain distinct from a numeric mismatch.

Portable replay needs only this source package and an existing exact BOOT file:

```powershell
python -B "<source-package>\inspect-source.py" --check --firmware "<absolute-ID-2580-V1.0.00-decoded.bin>" --source-root "<source-package>"
```

The48 retained rows are hard-pinned in `retained-source.json`; the old927-row evidence tree is not needed in D. To additionally check the original historical seals while in the original workspace, append:

```powershell
--verify-historical --workspace "$env:TSL9_ANALYSIS_WORKSPACE"
```

`--check` is entirely read-only and compares both generated JSON files byte for byte, then checks seal members. `--write` is limited to this checker's own unsealed directory and refuses nonidentical existing outputs. No network, hardware, real UID, ROOT/D changes or target execution is involved.
