# V4.1.60 queue: two genuine small providers

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

Only two original V4.1.60 leaves are reconstructed in [src/providers.c](src/providers.c). Ordinary C implements volatile byte load, unsigned predicate, pointer sums and byte store. ASM contains empty register ports only. No opcode carrier, stub or ABS provider; no consumer/curated edits.

| Original PC | Raw | Instruction |
|---|---|---|
| `81AA` | `03c5710a` | LBU A0,167(GP) |
| `81AE` | `8280` | RET |
| `820C` | `8947` | LI A5,2 |
| `820E` | `63e7a700` | BLTU A5,A0,821C |
| `8212` | `9387010c` | ADDI A5,GP,192 |
| `8216` | `aa97` | ADD A5,A5,A0 |
| `8218` | `a3800700` | SB ZERO,1(A5) |
| `821C` | `8280` | RET |

## Actual result and contract

The complete official BIN is76,800B, SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, analysis base `0x8000`. Both original spans are freshly read with critical operand gates. No V4.1.00 offsets/references are used; status is **GP+167**.

- The first single-profile C11/C++17 builds succeeded. Whole object and linked functions equal original **6B/2 instructions** and **18B/6 instructions**. There are exactly two genuine FUNC definitions and24B AX allocation, no UND/global ABS/REL/RELA/writable/NOBITS/unwind/stack/callee.
- The assembler already resolves the local BLTU. Actual relocation count is0; no extra profile/flag or fake target was introduced. Raw gates check unsigned BLTU, rs1=A5,rs2=A0 and the real RET at local offset16.
- Status normally returns `zext_u8[GP+167]`, writing A0 only. Clear preserves entryA0: unsigned index>2 performs no memory access and leaves A5=2; otherwise WRITE8(`u32(GP+193+index)`,0), A5=`u32(GP+192+index)`. Clear writes only A5. Neither leaf writes GP/SP/RA or other GPRs.
- Diagnostic link uses **VMA0**, function spans `[0,6)` and `[6,24)`. Original VAs81AA/820C identify original BIN sources, not this component's physical placement.
- MD closes over actual C and compiler stdint.h only. Compile receipts retain source/tool/resource hashes, exact command/exit/logs. LLVM reads back all8 raw instruction rows. IR retains the fresh volatile byte/zext, unsigned predicate, C pointer sums and sole conditional byte store. C++ noundef differences retain distinct full SSA hashes.

Each language rejects12 actual raw ELF mutants (6 each for object/linked: machine,GP167→175,signed branch,store offset,ABS function,writable allocation) plus3 actual IR mutants (GP offset,signed predicate,nonvolatile store). Changes stay in memory; no mutant provider executes or is emitted. Both language review receipts support read-only replay; generated build artifacts need not be tracked.

## Replay

```sh
# Existing local LLVM and exact official file; all output is create-only.
python experiments/tsl9-queue-small-providers/build.py --project-root . --tool-dir /absolute/LLVM/bin --firmware /absolute/ID-2966-V4.1.60-decoded.bin --build-root /absolute/project/experiments/tsl9-queue-small-providers/build/new-run
# Static review / create-only receipt; no target execution.
python experiments/tsl9-queue-small-providers/check.py --project-root . --folder /absolute/project/experiments/tsl9-queue-small-providers/build/new-run/c --receipt /absolute/project/experiments/tsl9-queue-small-providers/build/new-run/c/verification.json
python experiments/tsl9-queue-small-providers/check.py --project-root . --replay /absolute/project/experiments/tsl9-queue-small-providers/build/new-run/c/verification.json
# Source metadata only; repeat review/replay for cpp.
python experiments/tsl9-queue-small-providers/check.py --project-root .
```

[verify.sh](verify.sh) is the POSIX wrapper; `QUEUE_PYTHON` selects Python. Only Windows Python and the existing NDK27.1.12297006/LLVM18 were actually tested. POSIX shell execution is unverified; denied Git Bash was not retried. All build/replay paths are contained in this experiment/build; replay never starts compiler/linker.

## Limits

These are two genuine offline callee components, without real queue-consumer composition or whole-image integration. Original placement, GP provenance, memory validity/aliasing, global IRQ/fault context, installed ROM and physical behavior remain unproved. Equal leaf bytes do not establish physical placement or safe flashing.

**firmware_ready=false, OTA_ready=false, rebuilt_flashable_BIN=false**. No download/network/target/HOST model/ISA/MMIO/BLE/CAN execution or BIN generation.
