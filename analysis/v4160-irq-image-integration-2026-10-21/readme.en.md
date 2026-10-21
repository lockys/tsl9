# Readable IRQ integration into the complete source image

[繁體中文](readme.zh-TW.md)

This milestone places the verified IRQ initializer and four RCC helpers back into the complete original layout. **The output remains NOT-FLASH-VALIDATED, not verified flashable firmware.** Readable C/C++ replaces only five functions. The remaining code and data are retained original instruction/data carriers; this is not complete source recovery.

## Rebuild

Use Python 3.10+ and local LLVM tools capable of compiling RV32, from the project root:

```sh
sh experiments/tsl9-v4160-irq-image-integration/verify.sh --tool-dir /path/to/llvm/bin --language both
```

Python can invoke the same entry directly. Windows Python/LLVM evidence does not establish POSIX shell, Linux, macOS or CI success. Every build uses a new directory. RV32 is never executed or emulated, and no BLE, UART, CAN or physical Flash operation is performed.

## Admission boundary

- Compile the pinned 34 original translation units plus two readable C/C++ units anew. Remove only the five replaced original instruction sections.
- Preserve 691 allocation extents, 686 retained storage sections, 53 section-relative bindings and eight external entry calls. Check actual symbol roles rather than inventing absolute-address function providers.
- Preserve all 8,270 outside-owned RELA records. The new core contributes six JALs; four old helper branch RELA records are explicitly discharged by identical helper bytes. The new total is 8,276.
- Strict full linking must reject the sole missing resident ROM provider. A separate address witness assigns only the original ROM address `0x40000`; it supplies no ROM bytes or presence proof.
- Require exactly 76,800 exported bytes, fully backed by real sections and ELF LOAD contents, without hole filling, original-BIN fallback or RAM NOBITS export. Admit only the eight specified byte changes at `0x9A44..0x9A4B`.
- Build C and C++ separately and compare their images. Actual ELF, relocation and image negative controls must reject invalid inputs. Receipts bind sources, tools, command logs and actual artifacts.

Read actual results and hashes under [integration](integration/), with independent [contract](contract-review/) and [source](source-review/) reviews. These evidence scopes are separate.

## Unproved requirements

Four register-save instructions occur in a different order. Matching final frame contents does not prove equivalence at arbitrary interruption points. Installed ROM, exact board/chip identity, all runtime data and callbacks, startup/interrupt compatibility, updater acceptance, physical Flash and BLE OTA remain incompletely established. The original APK and 22 vendor BINs remain unchanged.

The [feature candidates](../v4160-irq-callframe-2026-10-21/feature-candidates/readme.en.md) remain proposals. This image does not implement the proposed DND explanation, status panel, snapshots, preflight or diagnostic export.

