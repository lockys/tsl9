# Independent Flash native C/C++ artifact review

All six **normal return register contracts and component size limits pass** for the retained C11/C++17 objects, LLVM IR and component ELFs. This does not admit a complete firmware image. No RV32 execution, CPU emulation, device operation, network request or BIN creation occurs. [繁體中文](readme.zh-TW.md)

`review-c.json` and `review-cpp.json` bind actual build paths, source/tool hashes, commands/logs, every instruction and the checks. Original contracts come from the immutable sibling `source/seal.json`. The reviewer independently parses actual ELF contents rather than trusting producer PASS fields; no product source or prior sealed evidence was changed.

| Original entry | Original bytes | Actual C/C++ bytes | Encoded GPR destinations | Entire original bytes identical |
|---|---:|---:|---|---|
| `9C0A` | 64 | 64 | RA/SP/S0/S1/A0/A1, plus callees | No |
| `18E90` | 8 | 8 | A5 | Yes |
| `18E98` | 30 | 30 | A3/A4/A5 | No; constant materialization reordered |
| `18EB6` | 14 | 14 | A3/A4/A5 | Yes |
| `18EC4` | 46 | 46 | A0/A3/A4/A5 | No |
| `18EF2` | 100 | 94 | A0/A2/A3/A4/A5/A6 | No |

Actual profiles use RV32IMAC_Zicsr/ILP32, `-Oz`, disabled machine outliner and relaxation, and per-function register reservations. Actual encoded destinations are checked independently: reservation flags alone are not preservation proof. Helpers have no stack, hidden call, RA write or extra allocated data. Program never writes A1; A6's last definition is the final source word load.

The actual wrapper has a32-byte frame with source store/fresh reload at `SP+12`, and fresh RA/S0/S1 restores at offsets28/24/20. An earlier64-byte probe used `SP+16`; that concrete finding was reported and corrected before admission. Five actual linked JALs resolve to the original helper entries. CSR800 is cleared by136 before the chain and set by136 afterward; prior CSR state is not restored.

Normal wrapper A0 is destination aligned down256; A1 is the freshly selected frame source; A2=256, A3=`0x8000`, A4=`0x40022000`, A5 is the final lock's fresh control word OR `0x8000`, and A6 is the final source word. Normal program A3=`0xFFFEFFFF`, A4 is the final fresh control word AND that mask, A5 is the base, and A1 is unchanged. Complete native patterns and fixed-register IR outputs are checked, with only32-bit volatile accesses.

The native program loop starts0, advances4 and stops256, retaining64 ordered LW32/SW32 transfers at offsets0..252 and a bit1 poll after every word. Initial bit0/bit1 and final bit0 polls and fresh control RMW ordering remain. Each language has **15 actual machine-byte counterexamples** and **3 uncompiled IR transcript counterexamples** covering frame, CSR, width, stride, branch, registers and volatile observations. The latter are explicitly not compiled C-source mutations.

The actual component ELF has six dedicated executable allocations at original entries, no undefined symbols, residual relocations or additional allocations. Object bytes plus five independently encoded JAL fixups equal the linked bytes exactly. This admits the normal six-function component only. **A94-byte body does not prove ownership or padding of the remaining6 bytes of the original100-byte extent.** Full carrier storage, interior entries, aliases and relocation integration remain open.

Known differences remain: original save order S0/S1/RA/A1 becomes RA/S0/S1/A1. Native program aligns A0 after the two initial polls; the original aligns it before the first control write. Pointwise interrupt behavior, exact frame prefixes, fault/nonreturn physical GPR prefixes are therefore not equivalent claims. Normal contracts require a valid frame, completed accesses, terminating polls and no unmodelled asynchronous interference. HOST evidence cannot remove these limits. Hardware success, MCU/Flash capacity, recoverability and OTA readiness remain unknown.

Offline replay: `python replay.py --check`. This invokes no compiler or disassembler. Present local Windows tools are rehashed; absent tools use sealed actual tool-byte observations. Preserve the referenced build artifacts with the review reports.

For renamed package paths use `python replay.py --check --context-json <local-map>`. Fields may specify `project_root`, `parser_path`, `source_dir`, `firmware_path`, and mode-indexed `build_roots`/`linked_elfs`. Only input locations and in-memory historical location labels change; sealed reports remain untouched. Fresh tools may supply API `observed_tools`: actual tool path to equal `before_sha256`/`after_sha256`, rehashed if present. Original firmware/parser/core digests and every native semantic gate remain strict. `context-check.json` proves default/explicit equality for both languages and rejects six wrong-parser/firmware/tool-drift controls.
