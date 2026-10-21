# Five actual native C/C++ components

The frozen branch-owned C implementation compiles and links with local Clang 18.0.2 for RV32IMAC_Zicsr/ILP32 using **-Oz**, `-mllvm -enable-machine-outliner=never`, and only A0/A1/A4/A5 available to the allocator. Every other integer register, including SP/T0/A2/A3, remains reserved. The verifier independently checks emitted bytes and encoded destinations; compiler flags alone are not treated as preservation evidence.

| Result | C11 | C++17 |
|---|---:|---:|
| Each of four RCC helpers | 30 bytes / 12 instructions | 30 bytes / 12 instructions |
| Initializer | 180 bytes / 65 instructions | 180 bytes / 65 instructions |
| Executable allocation ownership | 300 bytes, passed | 300 bytes, passed |
| Extra read-only allocated metadata | 0 | `.eh_frame`: object 120 bytes; linked 124 bytes |
| All allocated bytes owned by the five functions | true | **false** |
| Initializer fits original 144 bytes | **false** | **false** |

All **120 helper bytes** equal the pinned ID2966 original image at their actual original addresses **0x19124 / 0x19142 / 0x19160 / 0x1917E**. The diagnostic linker places the initializer at **0x30000**, outside the original image range. This is a virtual component address, not proved available flash or an installed entry thunk. The initializer remains 36 bytes too large for `[0x9A42,0x9AD2)`.

The exact profile preserves C++ `.eh_frame` instead of discarding it or adding exception flags. Its linked metadata is orphan-placed at VA0, includes a four-byte terminator, and has no proved storage/integration plan. Executable ownership and all-allocation ownership are separate gates; recognizing metadata does not turn the latter true. Both full-image integration and OTA readiness remain false.

The native checks establish five actual function symbols, no undefined symbols/aliases/hidden implementation, no writable data, no SP/T0/A2/A3 access or writes, and **zero encoded A1 writes in each standalone helper**. Full ELF-bound disassembly covers every raw byte, including instructions after each helper's first RET. Encoded destination fields are compared independently with displayed mnemonics. The raw compressed branch target is checked, both helper return regions are reachable, and the direct CFG has no escape or cycle. Every executable allocation byte belongs to these five functions; extra C++ non-executable allocation is recorded separately.

The initializer's finite straight-line static def-use proof confirms **20 ordered CSR/MMIO effects**, six distinct fresh RCC reads, exact RMW masks, all PFIC widths/values, and final normal outputs **A0=last fresh RMW, A1=0, A4=128, A5=0xE000E000**. The LLVM IR checker accounts for every initializer instruction, verifies transparent fixed-register primitives and **seven ordered returning commitments**. Helpers receive a separate branch-owned IR structural check; their strongest native identity evidence is the actual original-byte comparison. No guest RAM, CSR state, PC stepping, target inputs, instruction execution or ISA emulator is created. Interrupt/pointwise semantics and complete original ABI are not proved. Main temporarily uses A1 as PFIC address scratch; its final value is checked separately.

Each language has **five actual compiled and linked negative controls**: A2 write, SP write, wrong final A1, wrong PFIC width and wrong helper register offset. All are rejected. Thirty transcript controls per language reject missing/altered/truncated/unparsed rows across all five functions. None of the generated components or controls is executed.

```sh
# From either the analysis workspace or the published/delivered project root:
python apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both

# Equivalent POSIX launcher (Python is selected via PYTHON, python3, then python):
sh apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/verify_native.sh --project-root . --tool-dir /path/to/llvm/bin --language both

# Read-only closure; add --require-local-builds to require historical archives:
python apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/check_native.py --project-root .
```

`--clang`, `--linker` and `--objdump` override individual local executables; otherwise `--tool-dir`, the known Windows NDK directory or PATH is used. The original image is selected from explicit `--firmware`, then the workspace `exports/.../ID-2966-V4.1.60-decoded.bin`, then `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`. The exact 76800-byte SHA-256 is always required. `path-resolution.json` records successful read-only lookup/hash checks against the existing W/P/D images; it does not claim native builds there. The direct Python CLI was tested on Windows; the POSIX launcher is shipped as source and was not executed through WSL/Git Bash.

Fresh builds need only the three pinned native/public source files, this verifier/parser, the offline original image and local LLVM tools. They do not require old build archives, original full-image gates, network or a device. Outputs are component-only ELF/IR/logs, never a firmware BIN. `results.json` selects two byte-identical receipt copies outside `build/`; compiled artifacts and negative-control sources remain local. Receipts preserve original compile-run script pins and the final static replay under the completed checker after C++ IR attribute/default-path handling was finalized. Successful static proof does not imply original placement or firmware readiness.

`check_native.py` validates sealed source/metadata pins and replays actual ELF/IR/native/control gates when the selected local archives exist. Missing historical archives are reported explicitly. Metadata validation is not fresh compilation. No original image/model/old sealed evidence or delivery/published checkout was changed by this review.
