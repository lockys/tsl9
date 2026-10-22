# Conditional resident memory leaves

[繁體中文](readme.zh-TW.md)

Readable C11/C++17 algorithms reconstruct three retained SDK candidate RAM leaves. Numeric addresses identify conditional source evidence, not installed providers. No original RV32 instruction execution or emulation occurs.

| Candidate leaf | Original extent | Normal result |
| --- | --- | --- |
| compare-byte | 200004BC, 62B / 19 instructions | 1 only for nonnull, nonzero-length input whose bytes all equal the full 32-bit expected value; otherwise 0 |
| fill | 2000039C, 46B / 14 instructions | u32(destination+count), or original destination for null/zero length |
| forward copy | 20000332, 58B / 18 instructions | Original destination; no copy for null source/destination or zero count |

All first READ32-save / WRITE32-zero at 4002420C, then FENCE.I, before null/count tests. Normal and early exits restore the captured original word. These are not libc substitutes: expected is not byte-truncated; fill truncates only its stored byte; copy freshly reads before each forward store, so overlap feeds back. Address arithmetic wraps modulo32. The raw instructions do not promise generic invalid-memory/fault cleanup.

Shared C uses five explicit numeric-address ports: read8, write8, read32, write32 and fence_i. HOST callbacks operate synthetic memory. CONTINUE denotes a completed known effect; HALT/TRANSFER/UNKNOWN stop the algorithm with its effect prefix and no invented restore/normal return. A diagnostic budget exists only in HOST ports. Typed context flow/counter bookkeeping is not physical register evidence.

## Measured scope

Authored HOST C/C++ each pass 27 cases / 219 checks and reject three actually compiled semantic mutants: expected-byte truncation, reverse source reads, and zero instead of saved-MMIO restoration. Cases cover fresh/short-circuit reads, MMIO/data alias, overlap, address wrap, null/zero and stop prefixes.

Native compilation produces ET_REL/IR/MD and complete static disassembly only. C/C++ contain compare146B, fill138B, copy160B plus a genuine local begin86B: 530 allocated code bytes / 218 instructions, 13 relocations and five real I/O UND symbols. The typed context/flow-result ABI uses sret and frames; it is not the original frameless leaf ABI. host_io.c is compiled only for authored HOST tests, not offered as a physical MMIO/FENCE.I provider. No link/BIN, numeric provider, fake extent, opcode generation or hardware access is involved.

## Commands

```sh
sh experiments/tsl9-resident-memory-leaves/verify.sh --project-root "$PWD" --language both
python3 CASE/implementation/probe.py --project-root ROOT --tool-dir LLVM --language both
python3 experiments/tsl9-resident-memory-leaves/verify_host.py --project-root ROOT --replay HOST_MODE/verification.json
python3 CASE/implementation/probe.py --project-root ROOT --replay NATIVE_MODE/verification.json
```

Both fresh CLIs accept create-only `--build-root NEW` inside model/build; omission creates a UUID directory. Outputs are `{c,cpp}/verification.json`. CASE is published analysis/v4160-resident-memory-2026-10-22 or workspace apk-analysis/tsl9-v4160-resident-memory-2026-10-22. check.py defaults to source/metadata only; repeatable explicit `--host-receipt` / `--native-receipt` read actual archives and fail if missing. Replay never recompiles.

Portable Python/POSIX-sh entries use the existing immutable local-machine guard before every HOST executable, including mutants. Native measurements use pinned Windows NDK LLVM; unverified Linux/macOS native binaries are not admitted. No complete vendor ROM is copied. Independent scopes supply candidate source proof/explicit reference readback. Installed identity, full original ABI, provider readiness and physical/OTA compatibility remain unproved.
