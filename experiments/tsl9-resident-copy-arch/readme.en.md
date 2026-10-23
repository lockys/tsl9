# Resident copy: exact architectural reconstruction of an SDK candidate

[繁體中文](README.md) · [English](readme.en.md)

The same [copy.v1.c](src/copy.v1.c) compiles as C11 and C++17. Six private regions linked at conditional RAM address `0x20000332` reproduce all **58 bytes / 18 instructions** of the public WCH V1.31 candidate at `[0x405A2,0x405DC)`. This is not measured installed TSL9 resident identity, an injected Runtime provider, or a flashable BIN.

Only A3–A6 are written. A0–A2, T0, A7, SP, GP and RA are preserved. The earlier 52B normal-I/O projection remains available; this version removes its extra T0/A7 writes. Every path first saves `[0x4002420C]`, writes zero and executes FENCE.I, including null-pointer/zero-count paths. Forward fresh byte reads precede destination calculation, index increment and destination writes. Overlap, uint32 wrapping and instruction-prefix ordering are retained; faults do not guarantee restoration. Normal exits retain the saved word in A4 and `0x40024000` in A5; A3/A6 are unchanged on skipped copies, otherwise contain the last destination address/byte. RET targets `RA & ~1`. Physical register identity and interrupt effects are unknown.

Use `probe-v2.py` with a new output directory, then `verify-v3.py --folder <directory> --write` for a create-only receipt; omit `--write` for read-only replay. Select existing tools through the environment or `--llvm-bin`. Nothing is downloaded or executed. v3 consumes unchanged v2 compiler artifacts; earlier checkers and receipts remain frozen.

The proof checks the actual candidate digest, all code bytes/LLVM addresses, six strong definitions, five object edges, exact C SSA/volatile/register ports, complete inputs/artifacts/MD include closure, per-command argv/consumed bytes/logs and ELF entry/LOAD permissions/alignment. Each language passes 50 bounded negative controls; an independent review rejects 38/38 additional provenance/PHDR mutations. Linked UND/RELA/global ABS are zero. The ELF has 58B of RX code plus a separate 180B read-only header LOAD. This is static evidence, with no HOST behavior model, ISA emulation, MMIO or hardware operation.

See the [analysis and public evidence](../../analysis/resident-copy-arch-2026-10-23/README.md). Actual installed `[0x4004C]`, resident identity, completed startup, IRQ, physical ISA/MMIO and OTA compatibility remain unknown. The prior 740B transmit-chain proof is unchanged and does not become complete firmware.
