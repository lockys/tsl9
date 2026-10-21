# Explicit TSL9 ABI stack-save scheduling

[繁體中文](README.md)

This tool only schedules automatic stack saves in two functions of newly compiled C/C++ ET_REL objects. The algorithms remain compiled C/C++; the final object is **compiler output plus an explicit ABI save-scheduling step**. Clang alone did not emit the final save order. Matching machine code does not establish hardware or OTA compatibility.

## Why a separate step exists

The current compiler inserts a different save order during its prologepilog stage. Normal-return register values can agree while partially completed stack saves differ. Host tests and normal-return equivalence cannot discharge that difference.

| Function | Compiler save order | Required save order |
| --- | --- | --- |
| IRQ, original `0x9A42` | RA@12, S0@8, S1@4, S2@0 | S2@0, RA@12, S0@8, S1@4 |
| quarter, original `0x9C0A` | RA@28, S0@24, S1@20 | S0@24, S1@20, RA@28 |

Offsets are bytes from the function's new SP. `frame-policy.json` declares registers, slots and order, without original opcode templates. The tool permutes existing two-byte C.SWSP words read from the actual compiler object. It generates no new opcode, adds no bytes, reads no original BIN for generation and uses no padding or original-image fallback.

## Generate and replay

```sh
python3 -B experiments/tsl9-v4160-frame-schedule/schedule.py \
  --project-root /absolute/project \
  --input /absolute/project/build/compiler-integrated.o \
  --output /absolute/project/build/source-integrated.o \
  --receipt /absolute/project/build/frame-scheduling.json

python3 -B experiments/tsl9-v4160-frame-schedule/replay.py \
  --project-root /absolute/project \
  --receipt /absolute/project/build/frame-scheduling.json
```

Matching `.sh` entries support `PYTHON`. All paths must remain inside the explicit project root. Input, output and receipt must be three distinct paths; outputs are create-only. Both functions are selected by default; individual translation units can explicitly select `--functions irq` or `--functions quarter`. Python 3.10+ and the existing SHA256-pinned project ELF parser are required.

## Evidence and limits

- Admission requires RV32 RVC soft-float ET_REL, one public function and one unambiguous executable owner section, exact sizes and compiler save order, and disjoint frame slots.
- Named/mapping symbols, relocation sites or targets in the scheduled interval are rejected, as are aliased storage and relevant unwind/frame/build-id metadata. Reapplication is rejected.
- Length, section metadata, symbols and all RELA records remain identical. Receipts bind actual input/output hashes, tools, policy, existing words and changed offsets. Read-only replay rereads both actual objects and recomputes the complete receipt.
- This pass alone proves a bounded object transformation. Actual C/C++ compile recipes, dependency files and source identities must establish input provenance in the integration pipeline; filenames do not prove provenance.
- Unrecorded computed/encoded interior entries, resident ROM, unknown interrupt observations, physical faults and BLE OTA compatibility remain unproved. No target execution, ISA emulation, BLE, UART, CAN or physical Flash is involved.

Actual Windows Python/LLVM evidence does not establish Linux, macOS, POSIX shell or CI success. Each receipt and integration result remains scoped to its actual environment.

`verify.py --input-c C.o --input-cpp CPP.o --build-root NEW_DIR` transforms and replays both actual objects and rejects seven actual receipt/output tamper controls per language. It uses the explicitly supplied archived compiler objects without fresh C/C++ compilation; the full-image pipeline separately builds a fresh compilation chain.
