# Readable native interrupt initialization

The new `experiments/tsl9-v4160-interrupt-init/src/interrupt_init.c` was compiled as actual RV32 C11 and C++17. Both native objects are byte-identical. The initializer is 118 bytes / 43 instructions; the original `0x9A42..0x9AD2` capture occupies 144 bytes / 46 instructions. Each of the four new RCC helpers is 22 bytes. These are new reconstruction symbols, not original-address aliases.

Both modes produce a linked `COMPONENT-ONLY-NOT-FIRMWARE.elf`, with no undefined symbols, libcalls, writable data, or runtime stubs. Linking at diagnostic address `0x1000` preserves the initializer machine bytes. The component has **not** replaced any section in the existing 691-allocation image.

The LLVM IR and the actual emitted machine instructions independently establish the same 20 ordered effects: CSR `0x800` clear-mask `0x88`; six fresh 32-bit RCC reads and six 32-bit RMW stores; six ordered PFIC-address stores with their original byte/word widths; CSR `0x800` set-mask `0x88`. The returned `A0` is the final fresh RMW result. The CSR sequence does not restore a saved CSR value. The general helper IR also retains zero versus every nonzero 32-bit flag behavior. Four source mutants per language were actually compiled and rejected: incorrect CSR mask, incorrect PFIC access width, missing fresh reads, and an invented status return.

`results.json` identifies the source, compiler/linker/objdump, real build receipts, object/linked hashes, and verification limits. Local build directories retain objects, IR, disassembly, logs, and compiled mutants. Those generated directories are not required to compile a fresh component from a published checkout.

## Run a fresh static verification

Python 3.10+ and LLVM tools capable of RV32IMAC plus Zicsr are required. Supply the executables installed in your environment:

```sh
python3 analysis/v4160-interrupt-init-2026-10-21/native-plan/verify_native.py \
  --project-root . \
  --clang /path/to/clang \
  --linker /path/to/ld.lld \
  --objdump /path/to/llvm-objdump \
  --language both
```

The investigation workspace uses the `apk-analysis/tsl9-v4160-interrupt-init-2026-10-21/` prefix instead of the published `analysis/v4160-interrupt-init-2026-10-21/` prefix. An optional `--tool-dir` selects a directory containing the three executables. Native flags are recorded in each new receipt; the verified Windows toolchain is Android NDK 27.1.12297006, Clang 18.0.2, with `--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -Os -ffreestanding -mno-relax`. The verifier fails if a different compiler emits an instruction or IR form outside the implemented proof profile; it does not silently weaken its checks.

Only local compilation, linking, ELF parsing, IR analysis, and static disassembly occur. The machine proof annotates straight-line constant definitions and fresh-load expression identities. It does not create guest RAM/CSR state, execute instructions, emulate an ISA, or perform hardware I/O.

`audit.py` is a separate historical baseline audit and the reusable ELF parser. Its `main` command reads the specific retained source-image build; this historical command is not needed by `verify_native.py`. The baseline audit rechecks actual C/C++ merged objects: 691 nonempty allocated sections, 8,280 raw RELA records, and the one real undefined resident symbol `__tsl9v4160_rom_entry`. An additional empty `.text` section supplies no implementation. One direct relocation is observed from `0x9258` to `0x9A42`; no other direct section reference is present in those objects. This does not exclude indirect references or prove the installed resident implementation.

## Integration obligations still open

1. The 118-byte size comparison proves only that this compiler's initializer is smaller than the captured 144-byte source extent. It does not place it at `0x9A42`, account for the remaining 26 bytes, validate interior/indirect references, or prove compatibility with the existing image layout. The full image gate must explicitly authorize and verify a source replacement while protecting every other section, symbol, relocation, and data byte; the old immutable byte-fidelity gate must remain intact.
2. The new leaf removes the original 16-byte stack frame and six helper call/return boundaries. It preserves standard callee-saved registers but changes caller-saved register residues. Static source observation gives the final original `A0` result; it does not establish a complete original C ABI, asynchronous interrupt ABI, interrupt-time register observation, or timing equivalence. The real call chain and IRQ entry/exit behavior still require proof before integrating this leaf as an original-entry replacement.
3. The exact board, MCU revision, memory domains, installed ROM/resident service, PFIC/CSR behavior, and actual peripheral side effects remain unverified. The original source-image build still has one unresolved resident implementation. No physical OTA compatibility follows from this component link.

No original or rebuilt RV32 code was executed. No firmware BIN was produced by this verifier, no device was flashed, and the result is not approved for Bluetooth OTA.
