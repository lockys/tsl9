# Native expected-version literal stage

`verify-version-literal-extension.py` extends the frozen residual-callbacks
native stage with **one real C11/C++17 constant object**:

- Symbol: `__tsl9v4160_address_1ab1c`.
- Section: `.rodata.tsl9v4160.version_literal_1ab1c`, flags ALLOC, alignment 1.
- Original interval: `[0x1AB1C,0x1AB32)`, 22 bytes including the terminating NUL.
- Reconstructed value: `CH32V20x_BLE_LIB_V1.3`.

The original caller materializes this address in `a1` at `0x199FC`/`0x19A00`,
sets `a2=21`, and calls its resident comparison provider at `0x19A04`. The
22-byte interval had no allocation in the prior 640-section object. This stage
adds original data; it does not make an ABS symbol, alias existing storage,
insert filler or substitute a reference SDK resident.

The verifier first reruns the unchanged complete prior native gate. It then
checks both C and C++ actual ELF artifacts: 641 nonempty allocations, all prior
640 section bodies/attributes and allocated global provider roles unchanged,
all 8107 semantic RELA occurrences unchanged, and precisely the old undefined
set minus this one data name. The resulting 30 dependencies still cause the
strict final link to fail. Actual ELF countercases exercise the same new
literal gate, including ABS/type/size/offset/visibility/storage corruption.

An explicitly named numeric-address witness checks original placement and
every captured code/RO byte. Its 30 unresolved values are address assumptions,
not implementations. It must not be flashed or described as rebuilt firmware.

From the reconstruction project root, use the existing Python runtime:

```powershell
python -X utf8 -B experiments/tsl9-v4160-startup/verify-version-literal-extension.py `
  --current-receipt <absolute-path-to-the-prior-gatt-ingress-verification.json>
```

The verifier finds the local original ID2966 firmware and the independently
sealed literal proof in the project's analysis folder. Optional `--firmware`
and `--proof` arguments select explicit local copies. Only the declared prior
640-section frontier with the exact original object identity is accepted.

`STT_OBJECT22` describes this reconstructed storage. It does not prove the
extent of the unknown original C object, the maximum read extent of an opaque
resident function, the installed resident identity, IRQ behavior, hardware
compatibility or Bluetooth OTA readiness. No target instructions are executed.
