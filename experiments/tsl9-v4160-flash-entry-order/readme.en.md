# V4.1.60 Flash entry order and natural 100-byte generation

Actual C11/C++17 compilation with the unchanged LLVM profile produced six functions
at their original entries: quarter/status/unlock/lock/erase/program sizes
64/8/30/14/46/100 bytes, totaling262 bytes/99 instructions.
Both component ELFs have SHA-256
`aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d`.
No padding, manufactured instructions, object patches or flag search was used.

A dependent fixed-A0 bridge places alignment after the initial CTRL read and before
the first CTRL store. Two source-backed A4 base reloads and A5 initial-poll results
express original register sites. HOST macros preserve identical AND semantics.
The bounded experiments measured94,102,100 bytes respectively; the final A5 bindings
naturally eliminate the extra LI A5,0. Exact source changes are checked by
`check.py` and `source-diff.json`; host provider/tests/API and compiler flags stay unchanged.

```sh
python3 -B experiments/tsl9-v4160-flash-entry-order/verify.py --project-root . --language both
python3 -B analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --replay /path/to/native/c/verification.json
```

The analysis workspace uses `apk-analysis/tsl9-v4160-` instead of `analysis/v4160-`.
Both CLIs accept create-only `--build-root` and read-only `--replay`; shell wrappers
forward the arguments. Native overrides include `--clang`, `--linker`, `--objdump`
and `--firmware`. Python3.9+ and installed local compilers are required.
The firmware override applies to both compilation and native archive replay.
An alternative-location reference requires the same explicit firmware path for
replay. Language selects fresh builds; replay uses the receipt language.
`probe_native.py` preserves Windows diagnostics; `verify_native.py` is the portable
primary native entry. Only Windows execution was tested.

Host C/C++ each passed5 groups/481 cases/247191 checks and six actually compiled
semantic controls. Every host launch checks format/machine/width using the running
Python executable header and runtime pointer width; RISC-V ELF243 is rejected.
Replay reparses all seven executables. macOS requires thin Mach-O Python;
universal/fat interpreters are rejected. No Linux/macOS execution claim is made.

The native CLI pins previous immutable compiler/parser/disassembly helpers and flag
profile. A new independent100-byte program checker replaces no old94-byte admission
gate; five unchanged functions retain their original patterns. Gates check all raw
bytes/CFG/GPR/word-width volatile IR, exact allocations, no hidden helper/UND,
original entries and five JAL fixups. The program checker rejects12 machine and3 IR
controls; the CLI additionally rejects one raw control for each of six functions.
MMD covers non-system project sources, excluding compiler resource headers.

Exact function-extent occupancy closes the earlier6-byte gap. It does not admit a
full image. Five known program interior roles retain offsets10/1A/28/38/52, but the
original instruction boundary8 changes. Initial CTRL scratch is A2 instead of A5,
and ANDI/mask-LUI ordering differs. Full scratch/nonreturn GPR prefixes, pointwise
and asynchronous equivalence remain false, as does the wrapper save-order gap.
Normal contracts require completed accesses, eventually cleared polls and no
unmodeled asynchronous interference.

Unknown/HALT/TRANSFER host results preserve external-effect prefixes without
invented cleanup or native timeouts. A0 remains the aligned destination, not a
success code; A2 is not a length input. No helper address-range guard is added.

Whole-section/symbol/RELA/interior-role/LOAD integration is a separate next step.
This milestone creates no BIN, changes no prior image and touches no hardware.
Physical chip/ROM/Flash capacity, timing, power failure, boot, recovery and OTA
remain unproved. Build archives remain local; selected metadata/source are shipped.
Read-only checking explicitly reports missing local archives.
