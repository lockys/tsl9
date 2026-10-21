# Complete offline image with eleven readable functions

[繁體中文](README.md)

Actual fresh C11/C++17 builds compile34 raw carrier TUs,2 IRQ TUs and6 Flash TUs.
Both produce the same76,800-byte `NOT-FLASH-VALIDATED-irq-and-flash.bin`, SHA-256
`de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`.
This remains a partial readable reconstruction plus raw carriers, not recovered
original source or a flash-validated firmware.

```sh
python3 -B experiments/tsl9-v4160-flash-image-integration/verify.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B analysis/v4160-flash-image-integration-2026-10-22/implementation/verify_image.py --project-root . --replay /absolute/path/to/c/verification.json
python3 -B analysis/v4160-flash-image-integration-2026-10-22/implementation/check_image.py --project-root . --require-local-builds
```

The analysis workspace uses `apk-analysis/tsl9-v4160-` instead of `analysis/v4160-`.
Python3.9+ and compatible installed LLVM tools are required. The actual tools were
NDK27.1.12297006 Clang18.0.2/ld.lld/llvm-objcopy on Windows. Shell wrappers are
provided without a Linux/macOS/WSL/Git Bash execution claim. Overrides are
`--clang`, `--linker`, `--objcopy`; `--build-root` is create-only inside the project.
Language selects fresh builds; replay uses receipt language. Firmware is forwarded
to build/replay checks and must still match the pinned original ID2966 digest.

Eleven readable functions occupy526 bytes (IRQ264+Flash262). Gates preserve all691
original allocation names/types/flags/sizes/alignment/entry sizes/VMAs, all680
retained partial-storage digests,53 real section-relative bindings and20 incoming
entry references, including C.JAL return-PC+2 and a tail JAL that does not write RA.
Only eleven exact quoted-assembly blocks in four carrier TUs are removed.
All other source bytes remain unchanged.

Each language runs56 actual LLVM commands. Forty-two MMD rules bind their own
target, primary source and forced adapter:72 pinned original files plus12 generated
inputs. Measured RELA is8270=8259 unchanged outside roles/sites/types/signedaddends/
multiplicities+11 typed JALs. Relative to the original8280-record carrier, four IRQ
and six Flash private branch roles are explicitly discharged through original/new
branch bytes, PCs, types, conditions, targets and recorded outside-reference
inventory. No old private label becomes a numeric alias or provider.

FILE/SECTION/mapping metadata is separately inventoried. Eight typed input attribute
markers become eight unreferenced local ABS metadata records; these supply no code.
All eleven object/linked native bodies match the sealed native components.
Each language rejects23 actual ELF/RELA/LOAD/image controls plus3 dependency-rule
association controls.

Raw partial bytes and final image bytes are different stages:20 original allocations
change during relocation. The680 retained hashes compare partial storage to its
source-derived ledger. Final sections, all15 LOAD payloads and every exported byte
are separately checked. LOAD memory/permission coverage exactly matches allocated
memory, including35,160 RAM NOBITS bytes; RAM contributes no file bytes.
No old-object linking, old-BIN fallback, padding, NOP tail or NOBITS export is used.

The new image differs from the original at70 bytes: eight existing IRQ prologue
bytes and62 Flash bytes. It therefore adds62 differences relative to the prior
eight-difference IRQ image. Exact addresses/values are in the source manifest and
actual receipt image checks.

Strict linking fails on the sole missing ROM resident and produces no output.
A separate numeric0x40000 witness resolves addresses only, providing zero ROM bytes.
It is not a ROM implementation or execution/physical-compatibility proof.
Known program interior roles remain, but original instruction boundary8 changes;
initial scratch A2/A5 use and wrapper save ordering differ. Full GPR prefixes,
pointwise/asynchronous/interrupt equivalence and unknown computed/ROM references
remain unproved. Normal contracts require completed accesses/eventually cleared
polls and no unmodeled asynchronous interference.

No RV32 execution/emulation, hardware, BLE/UART/CAN/Flash I/O or network is used.
Chip/board/ROM, timing, power failure, boot, recovery and OTA remain unproved;
`flashable=false`. Reports use UTF-8 LF; the copied historical layout retains its
original sealed CRLF bytes. The one-time manifest extractor records historical
provenance; fresh builds do not need historical objects. Build/log/control binaries
remain local. Read-only checking explicitly reports missing archives rather than
treating selected metadata as fresh artifact verification.
