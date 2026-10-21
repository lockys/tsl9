# Actual readable Flash native C/C++ milestone

ID2966's original six functions occupy262 bytes/99 instructions. The actual C11
and C++17 component is256 bytes/98 instructions and both linked ELFs have SHA-256
`1097156d90ee982a6c03c903785b563acae0357d1bbc7b7c2e29315adbf5d613`.
Quarter/status/unlock/lock/erase/program sizes are64/8/30/14/46/94 against original
64/8/30/14/46/100. All six fit their individual bounds; this is not image admission.

Three runnable entry points, using Python3.9+ and installed local compilers:

```sh
python3 -B experiments/tsl9-v4160-flash-native/verify.py --project-root . --language both
python3 -B analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --replay /path/to/native/c/verification.json
```

The working analysis checkout uses `apk-analysis/tsl9-v4160-` instead of
`analysis/v4160-`. Both CLIs support create-only `--build-root`; the host CLI also
has `--replay`. Shell launchers forward the same arguments. Native overrides are
`--clang`, `--linker`, `--objdump`, `--firmware`. Python/MSVC/LLVM were actually run
on Windows; POSIX launchers are supplied as source, without a claim of WSL/Git
Bash or other-OS execution. `probe_native.py` is the retained early Windows
diagnostic and formal CLI's profile module, not the portable primary entry; it
must be delivered as a sealed dependency.

The same readable core uses native volatile32 accesses and unbounded polls. Host
providers handle only numeric addresses/in-memory fixtures. Unknown data masks
propagate through RMW and stores; unknown addresses/conditions, HALT/TRANSFER and
synthetic poll-budget exhaustion stop at observed external effects without
rollback, lock, CSR cleanup or an invented native timeout. Normal GPR results are
separate from unproved intermediate/nonreturn physical GPR states. Fresh SP+12
and RA/S0/S1 loads are modeled; changed or unknown fresh return targets remain
transfer/unknown boundaries. A0 is the aligned destination, not a success code;
A2 is not an input length. No helper address-range guard is invented.

Each canonical host language passes5 groups/481 cases/247191 checks and6 actually
compiled/run semantic mutations. Tests include an independent expected full
key/status/CTRL/data/CSR trace, every HALT/TRANSFER provider-effect prefix, fresh
CTRL observations, live source mutation, overlapping forward copies, wrapping
addresses, known-bit propagation and fresh frames. The separate review has a
different oracle. These are synthetic provider results, not controller emulation.

Every positive/negative host launch checks executable format/machine/width before
subprocess creation and unchanged bytes afterward. Host architecture comes only
from the current Python executable header plus runtime pointer width. Read-only
replay reparses all seven outputs. The actual RV32 component and nine malformed or
wrong-machine controls were rejected with zero subprocess calls. Four Linux/macOS
header fixtures test parsing only, without foreign OS execution. macOS currently
requires thin Mach-O Python; universal/fat interpreters are rejected.

Native compilation derives reserved-register sets from original writes/arguments.
Six objects/IR files strictly link without UND at original entry addresses. Gates
cover every raw disassembly byte, bounded CFG, RV32IMAC_Zicsr/ILP32 headers, exact
normal-operation/register patterns, no helper stack, hidden function or extra
allocated state. The pinned independent checker rejects15 machine and3 IR
negatives. Actual before/after source/tool pins and6 project dependency files are
recorded; `-MMD` excludes compiler system/resource headers. Sealed original262B/99
instruction evidence is reused without pretending to rerun the historical
691-owner audit after publication.

Quarter's32-byte frame, fresh SP+12, five original call PCs/targets and fresh
RA/S0/S1 restores are retained. Save order changes from S0/S1/RA to RA/S0/S1.
Program aligns A0 after the initial polls instead of before them. Thus pointwise,
asynchronous and nonreturn GPR-prefix equivalence remain false. Normal contracts
require completed accesses, eventually cleared poll bits and no unmodeled
asynchronous interference. Only status and lock are byte-identical originals.

Program's remaining6-byte source tail has no storage/interior-entry ownership
solution. No padding, BIN, old-image patch or full-image integration is performed.
Future integration must separately prove the six original FUNC aliases/sections,
all references/callers and interior/tail obligations. High-address callers do not
prove physical Flash capacity. Chip/board/ROM, timing, boot, recoverability,
physical compatibility and OTA remain unproved. `check.py` replays available local
archives and reports missing ones explicitly; build archives are not published.
