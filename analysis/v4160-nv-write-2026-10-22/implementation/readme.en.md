# NV-write callback and timer: genuine native C/C++ reconstruction

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

Actual ID2966 firmware was reread across six source groups, **294B / 115 rows**: write callback 0x197BE..0x197F0, timer 0x19764..0x1979A and four real flash leaves. Readable C11/C++17 is reconstructed without original-opcode templates, a HOST interpreter or target execution.

A new C file ordinarily includes sealed flash-entry-order/src/flash_native.c/native_io.h and retains all six genuine helper definitions. Noinline forward declarations preserve meaningful C call boundaries without editing old bodies. New timer logic is ordinary volatile C; only a minimal `mv output,gp` read bridge follows the existing native-clock pattern. It neither sets GP nor substitutes a constant provider.

## Write call sequence

Inputs are A0=destination and A2=source; entry A1 is unused. Normal completion calls actual C definitions in order:

1. unlock(original destination)
2. erase(original destination)
3. program(original destination, source)
4. lock(program's normal A0 result)
5. delay(1), then wrapper result 0

No status(49) or CSR mask is added to this sequence; zero is not hardware status. The real program helper still writes 64 WORDs across a 256-byte window, freshly interleaving each source read and destination write without prebuffering. Unused genuine status/quarter definitions remain inventoried; quarter's existing status49/CSR136 belong only to its old body.

Original program entry also has A2=freshly reloaded frame source. The typed two-argument program projection covers normal effects only because that callee ignores entry A2 before setting its own 256 count; it is not full physical entry-state equivalence.

## Exact timer addresses and effects

Use numeric addresses without inventing units or hardware field names:

1. Fresh R32(E000F004); W32(E000F004,value&~1).
2. Fresh R8(uint32(GP+382)), multiplied by full incoming A0 modulo 2^32.
3. W32(E000F010,product); W32(E000F014,0).
4. Two separately fresh R32(E000F000) operations, followed by OR16 and OR33 writes respectively.
5. Repeated fresh R32(E000F004) until bit0 is **SET**.
6. Fresh R32(E000F000), AND~1 writeback; normal A0 retains input.

Polling has no timeout or guaranteed return. There are at least 12 target accesses, not 13. The two CTRL reads are not combined; initial +4 is not changed to +0. Offsets 16/20 are numeric descriptions, without new counter semantics.

## Actual compiled outputs and limits

| Genuine global FUNC | Bytes / instructions | Note |
| --- | ---: | --- |
| status 18E90 | 8 / 3 | Unused by new sequence |
| unlock 18E98 | 30 / 10 | Additional own-written A1 |
| lock 18EB6 | 14 / 6 | Real C helper |
| erase 18EC4 | 46 / 19 | Additional own-written A1 |
| program 18EF2 | 100 / 38 | Genuine 64-WORD loop |
| quarter 9C0A | 64 / 23 | Unused by new sequence |
| delay 19764 | 60 / 23 | Frameless; writes A1/A2 |
| write 197BE | 72 / 26 | 16-byte frame; five real C calls |

All corresponding C/C++ function bytes match. Whole ET_REL: **394B / 148 instructions / eight globals; UND=0, RELA=10, no ABS provider**. Five R_RISCV_CALL_PLT relocations belong to the new callback; five genuine JAL relocations belong to retained quarter. A real linker must still resolve them. This ET_REL is not declared executable or placed at original addresses.

Original write is 50B / 20 rows with 32-byte frame; new write is 72B / 26 rows with 16-byte frame, saving S0/S1. Original source is stored in a frame slot then freshly reloaded before program; new C retains it in a register. Normal-effect projection requires valid private stack and no adverse frame/source/destination/MMIO alias.

Original timer writes A2/A3/A4/A5, preserving A1 and retaining product in A2. New timer adds A1 writes and exits with A1=E000F000 and A2=last fresh E000F000&~1; A3/A4/A5 also lack the original fixed exit values. New write therefore fails full original register ABI. New unlock/erase A1 writes and retained quarter's old inline-ASM clobber declarations need independent review. Standard C call syntax does not establish original secondary-register outputs.

Full ABI, fault/IRQ/asynchronous behavior, original-frame observations, placement and installed-provider admission remain false. No flag chasing, fake provider, stub, ABS, link, BIN or flashing occurs. Real Flash/MMIO code is present: **do not execute these artifacts on HOST or hardware**. No native/CPU/ISA/ESIL/MMIO execution, HOST matrix or network operation occurs.

## Entries and evidence

```sh
sh experiments/tsl9-nv-write-callback/verify.sh --project-root "$PWD" --tool-dir LLVM --build-root NEW
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
python3 CASE/implementation/provenance.py --project-root ROOT --firmware ORIGINAL_V4160.bin
```

CASE supports workspace apk-analysis/tsl9-v4160-nv-write-2026-10-22 and delivered analysis/v4160-nv-write-2026-10-22. NEW must be create-only beneath model/build; omission uses UUID. W archives are build/native-v1/{c,cpp}, retaining real objects, complete IR/disassembly, six MD inputs, actual tool/resource-header hashes, all logs, relocations and receipts. Default check reads source/metadata only; explicit receipts read actual artifacts without recompilation or execution. Only provenance or check --firmware rereads six original FW ranges.

Python/sh sources are portable; native results admit existing fixed Windows NDK hashes only. sh runtime remains unverified; the previously denied Git Bash is not retried. Authored text uses LF, one EOF newline and pre-seal Git-style whitespace checks. Old sources and raw compiler logs remain unchanged. original-*.bin files are 50B/54B original-evidence slices, not rebuilt images.

Initial original-source capture used an older narrow decoder that explicitly rejected 1977E ORI. The sealed binding-review decoder context then captured complete evidence before the first native compilation. C/flags did not change and no native recipe was added. The source-capture error summary is retained beneath build/source-capture-history.

Independent raw review finds that retained quarter's generic inline-ASM clobber contract omits A1 for unlock/erase although these actual helpers write A1. The bounded current quarter path saves source at SP+12 and reloads after erase, so no live-A1 counterexample was observed on that path. This does not admit its generic ASM contract or full original ABI.
