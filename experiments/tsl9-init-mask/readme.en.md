# Register-mask operation at the end of initialization

[繁體中文](README.md) · [English](readme.en.md)

`src/init_mask.c` reconstructs the V4.1.60 leaf at `[0x19106,0x19124)` as readable C. C++17 uses the same source with C linkage. It reuses the sealed `tsl9-v4160-irq-native/src/native_io.h` adapter for the minimum register bridge; the volatile read, bit operation and write are ordinary C. There is no opcode carrier, stub or fabricated ABS provider.

For a nonzero enable argument, the function freshly reads the 32-bit word at `0x40021014` and writes `before | mask`. For zero, it writes `before & ~mask`. A0 returns the written value; A1 retains every input bit. On the enabled path A4=0x40021000 and A5=before; the disabled path reverses those A4/A5 outputs. The full 32-bit mask is retained.

## Actual evidence

Both C11 and C++17 were compiled with the recorded LLVM 18 tools and the existing four-register allocation policy, linked, and inspected statically. Each complete 30-byte, 12-instruction function equals the actual original firmware bytes. Code SHA256:

`69724f8e22551d238b67e52e25b3c1cbcaa62db28756da9b59a5c96ff7f16d87`

The firmware SHA256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`; file offset 0x11106 corresponds to VA 0x19106 under the analysis base 0x8000. Current local receipts are `build/canonical-20261022-v3/{c,cpp}/verification.json`. Only A0/A4/A5 are written; the leaf has no calls, stack/GP accesses, CSR operations or loops. Generated RV32 code was neither executed nor emulated.

The C object and ELF allocate 30 code bytes; the linked function VMA is zero. The C++ object additionally allocates 40 bytes of `.eh_frame` with three relocations, for 70 allocated bytes total. Its linked `.eh_frame` occupies 44 bytes, the function VMA is 0x2C, and total allocation is 74 bytes with zero remaining relocations. The whole C++ component therefore cannot be described as a 30-byte allocation or given the C version's placement.

The initial verifier rejected the ordinary `.text.<function>` object section name before producing a success receipt. That failed directory, `build/canonical-20261022-v1`, is preserved. The section-name check was corrected; the source, flags, tools and complete 30-byte equality requirement were retained.

Independent review confirmed actual object and linked equality in v2, while identifying weaker receipt provenance checks. The v3 schema additionally enforces both complete bodies, exact tool/resource hashes, the complete input set, each successful command and retained log, and reports section addresses and total allocation. v1/v2 data remain preserved, but are not claimed replayable with the modified verifier; the current replay entry point applies to v3. These static checks do not attest compilation inside a trusted execution environment or demonstrate hardware execution.

## Portable entry point

```sh
python3 experiments/tsl9-init-mask/verify.py --project-root ROOT --tool-dir LLVM_BIN --firmware ORIGINAL_BIN --build-root NEW_MODEL_BUILD
python3 experiments/tsl9-init-mask/verify.py --project-root ROOT --replay EXISTING_MODE/verification.json
```

Use absolute paths. NEW_MODEL_BUILD must be a new directory below this model's build directory; omission selects a UUID. The current evidence profile accepts only the recorded tool and LLVM stdint resource hashes. The Python entry point does not require PowerShell; the sh wrapper only forwards arguments and was not run in this session. Replay reads existing source, firmware, objects, ELF and receipts without recompiling.

## App connection and limits

[source-map.json](source-map.json) records the exact leaf and App-tail bytes. Additional static reading of `[0x19AEE,0x19B16)` shows that an initializer result of zero takes the normal path; a nonzero result reaches the self-loop at 0x19AF0. App sets A1=1 and A0=64 before calling 0x19106. It then freshly restores RA from active SP+92 and S0 from SP+88, writes 0xE000E104=0x80000000 and 0xE000E108=1 in that order, adds 96 to SP, and returns at 0x19B14. This 40-byte App reading is not a reconstructed C App and is outside the leaf verifier's pass scope.

The normal App exit A0 is the freshly read word OR 0x40, not a success code. A1=1, A4=1 and A5=0xE000E000. The external caller selected by the saved RA remains unknown. Numeric addresses do not identify the physical chip or peripheral semantics.

VMA zero is an offline comparison layout. Physical Flash ownership, installed ROM, complete startup, fault/IRQ/asynchronous equivalence and OTA compatibility remain unproved. **Rebuilt firmware has not been successfully flashed. No firmware BIN is produced, and no BLE/CAN/UART/Flash or third-party API operation is performed.**
