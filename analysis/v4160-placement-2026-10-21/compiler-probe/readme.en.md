# Bounded size and jump-width probes

The frozen reset-memory C/header compiled at **-Oz** produce a **66-byte leaf** and a **68-byte fragment**, each with **20 instructions**, in both C11 and C++17. The previous -Os results were 78/80 bytes and 24 instructions. The allocation remains T0/A0/A1/A2 only. All three source GP observations now correspond to three physical GP operand reads; the two loop SCCs remain. Both versions still exceed the original 62-byte range. The fragment's `c.j` spelling still emits four-byte JAL x0, with continuation relocation at offset 64; the strict missing-provider link rejects it. A numeric nonoverlap witness supplies an address, not continuation code.

The same one-flag -Oz change on the frozen clock register model gives **query 196 bytes / 64 instructions**, **fields 38 bytes / 10 instructions**, identical to -Os. The query allocator is A3/A4/A5 with the explicit external A2 primitive; fields allocate only A4/A5. The existing exact field normal-output pattern and all actual raw-destination checks pass. Query branch semantics are not proved by these structural checks.

Each reset configuration passes the pinned ELF, LLVM IR, full raw-byte coverage, encoded destination and two-loop CFG gates, plus three actual compiled negative controls and six transcript controls. Each clock configuration passes its pinned ELF/full-byte/RD/acyclic-CFG gates, plus three actual compiled controls and fourteen transcript controls. No target code is executed. The normal reset outputs are structurally constrained and shared-C behavior was tested in the separate hosted review; there is no full native loop, changing-GP/interrupt or original fallthrough ABI proof.

Synthetic assembly establishes actual two-byte C.J at displacements +2046 and -2048, with signed two-byte-aligned range [-2048,2046]. An external target only +378 away still produces four-byte JAL x0 under this assembler and `--no-relax`; spelling `c.j` does not guarantee compression. JAL x0 has encoded two-byte-aligned displacement range [-1048576,1048574]. Raw immediate fields are checked against actual linked symbols. These are geometry witnesses only. The hypothetical addresses in the receipt are not proven owned free storage. Reset/query/fields begin with a four-byte original instruction; a two-byte write alone splits that instruction. IRQ begins with two two-byte instructions. No original entry thunk is installed, no firmware BIN is generated, and no original bytes are changed.

`results.json` selects seven byte-identical receipt copies. Historical local object/ELF/IR/log archives remain under `build/` and are not required for fresh compilation. A checkout must contain the frozen source models and the explicitly pinned prior verifier/parser source dependencies. It does not need prior build archives.

```sh
python apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-probe/probe_oz.py --project-root . --tool-dir /path/to/llvm/bin --language both
python apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-probe/probe_oz.py --project-root . --tool-dir /path/to/llvm/bin --language both --fragment
python apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-probe/probe_clock_oz.py --project-root . --tool-dir /path/to/llvm/bin --language both
python apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-probe/probe_thunks.py --project-root . --tool-dir /path/to/llvm/bin
python apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-probe/check_probes.py --project-root .
```

The thunk command additionally reads the pinned original image only to frame first instructions. The read-only checker validates sealed metadata and current source/dependency hashes; it replays static gates when the selected historical local archives exist. Add `--require-local-builds` to require those archives. Metadata checking is not fresh compilation. LLVM tools are locally supplied; no download, network, device access, RV32 execution or emulation occurs.

One initial synthetic `.S` preprocessing attempt failed to rename a sandbox temporary file. The successful plain `.s` witnesses need no preprocessing; that failed attempt is retained in the local archive and is not counted as evidence.
