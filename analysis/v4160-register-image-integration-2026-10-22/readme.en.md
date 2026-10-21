# IRQ/Flash full offline integration matching original bytes

[繁體中文](README.md)

Actual C11/C++17 pipelines each freshly compile 42 units and export identical 76,800-byte BINs. SHA-256 equals official ID2966 V4.1.60: `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Eleven readable functions account for 526 bytes; remaining contents are original carriers. This is partial source recovery and **is not verified as flashable**.

## Actual generation and evidence

Thirty-four original carrier units, two IRQ/RCC units and six Flash units are compiled and partially linked into `compiler-integrated.o`. Explicit ABI processing only permutes existing automatic saves in two functions, producing `source-integrated.o`. The objects differ in fourteen bytes, while metadata, symbols and all RELA remain identical. Final linking/export uses no original-BIN fill or function replacement. The original BIN is a comparison reference; retained carriers have their own source and relocation identities.

Each language binds 57 actual commands, 42 exact dependency rules and 201 actual artifacts. Checks cover 691 allocations, 680 retained storage sections, 8,270 RELA records, 53 relative bindings, twenty incoming entries and ten explicitly discharged original branches. Actual sections and fifteen LOADs back every exported byte without padding, RAM NOBITS or ROM export. Strict linking still rejects the missing resident-ROM implementation; successful linking provides only a numeric-address witness.

Each generation rejects 23 actual ELF/relocation/image controls, three dependency controls and four scheduling-receipt controls. The [independent source review](source-review/readme.en.md) checks actual 42-unit compilation/dependency provenance. The [independent ABI review](ABI-review/readme.en.md) checks actual save order, function bytes, entry/return boundaries and full image. Default archived-metadata checks are explicitly distinct from actual artifact replay.

## Build and read-only replay

```sh
python3 -B analysis/v4160-register-image-integration-2026-10-22/implementation/verify_image.py \
  --project-root /absolute/project --tool-dir /absolute/LLVM/bin --language both \
  --firmware /absolute/project/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin

python3 -B analysis/v4160-register-image-integration-2026-10-22/implementation/verify_image.py \
  --project-root /absolute/project --replay /absolute/project/path/to/verification.json \
  --firmware /absolute/project/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

Python 3.10+ and LLVM satisfying the existing tool-identity requirements are needed. Generation creates fresh project-local build storage and never executes/emulates RV32. See the [model guide](../../experiments/tsl9-v4160-register-image-integration/readme.en.md) and [separate ABI scheduling model](../../experiments/tsl9-v4160-frame-schedule/readme.en.md).

## Unresolved

Resident ROM, exact chip/board, installed BOOT, physical interrupts/Flash, BLE update acceptance and recovery remain unproved. Identical bytes do not establish complete high-level source recovery or physical testing. No BLE, UART, CAN, physical Flash or vendor API access occurred, and no new hardware feature is claimed. Windows Python/LLVM evidence does not establish Linux, macOS, shell or CI execution. The full objective remains incomplete.
