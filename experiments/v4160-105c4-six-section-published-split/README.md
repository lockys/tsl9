# 0x105c4 six-section selected-link replay

This offline experiment compares six chosen RV32 sections, using the original
owner and a source split with a pure C replacement for `0x105c4`. It does not
build or execute a firmware image. The original formal sources still contain
inline assembly. The C replacement and the source split are experimental;
their presence here does not change the formal build or its guards.

The experiment fixes the reference BIN's length (76,800 bytes) and SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
The mapping `PC = 0x8000 + file offset` is an explicit assumption. It checks
these 94 selected bytes in each of four independent links:

| Section | PC | Bytes |
|---|---:|---:|
| target | `0x105c4` | 12 |
| trampoline_b | `0x107c6` | 18 |
| trampoline_a | `0x1083c` | 12 |
| caller_a | `0x10944` | 22 |
| tail | `0x10bbe` | 4 |
| caller_b | `0x10bde` | 26 |

For both C11 and C++17, the probe compiles the complete owner, its byte-pinned
in-memory split, the callback unit and the candidate leaf with the manifest's
`queue-consumer-a0-a5` profile. The experimental candidate also uses a macro
rename. It links the original pair and the split pair plus leaf separately at
those addresses. The selected input relocation check covers seven ordered
`(owner section, offset, type, symbol name, addend)` tuples, not all relocation
metadata or all relocations in the input objects. The probe checks the selected
output sections against the BIN, and verifies six symbols by name, output
section index and value. Symbol type, binding, size and visibility are **not**
verified. It rejects named undefined symbols, requires a symbol table and
rejects a dynamic symbol table; these checks are not a general ELF validator.

The link is strict with respect to unresolved symbols in this selected link,
but `/DISCARD/` deliberately removes sections matching the listed patterns,
including `.llvm_addrsig`. Unselected non-alloc sections are not inventoried.
The ELF has no `PT_LOAD`; it is not a loadable image. In particular, normal
returns can lead outside the six selected sections; see
`experiments/v4160-105c4-selected-return-boundaries/README.md`. This replay
proves neither all fallthrough/control flow nor reachability, private ABI,
original memory ownership, complete addrsig remapping or full BIN equivalence.

## Requirements and commands

Run from the repository root on Windows with Python 3.9 or newer and the locally installed
Android NDK 27.1.12297006 LLVM toolchain. Set `TSL9_NDK_BIN` to the directory
containing `clang.exe` and `ld.lld.exe`; relative paths are resolved before
switching to a temporary directory. The probe pins both executables and the
NDK's `stdint.h` by SHA-256 as well as the seven repository inputs listed in
`PINS` in `probe.py`; the seven files must exist at those paths with exactly
those bytes. A checkout that transforms line endings may fail the pins; use the
exact repository blob bytes rather than altering the pins. The tool directory
must have the expected adjacent NDK resource-header layout. Tool hashes do not authenticate the files or their
un-pinned DLLs, Python, operating system or inherited environment. Temporary
files and before/after snapshots are not a security sandbox or a complete
concurrent-modification defence. C and C++ use separate, freshly created output
directories; successful positive compile and link commands must produce their
expected output files.

```text
python -B experiments/v4160-105c4-six-section-published-split/probe.py
python -B experiments/v4160-105c4-six-section-published-split/test_replay.py
python -B -O experiments/v4160-105c4-six-section-published-split/test_replay.py
```

Even when selected checks pass, `probe.py` prints JSON with
`status: INCOMPLETE_FAIL_CLOSED`, `passed: false` and exits **1**. Only
`selected_checks_passed: true` reports success for this limited experiment.
On an error it also exits 1 and reports `selected_checks_passed: false`.
No arguments are accepted. Its result records input hashes and the hash of
bytes parsed from each final ELF; it does not save those temporary ELFs or
attest provenance, nor does a hash prove toolchain or runtime correctness.

For each C/C++ original/split link, the probe mutates the actual final ELF to
check rejection of missing/dynamic/null-only symtabs and, independently for
all six selected symbols, missing/duplicate/wrong-address/wrong-section
mutations. The wrong-section example is `SHN_ABS`; wrong address is `+2`.
For each language it also checks a missing leaf, wrong placement and wrong
leaf constant. `test_replay.py` checks the four cases, returned selected bytes
against the BIN, and their reported negative names, invalid arguments, missing
tool-directory environment and seven individual repository-input pin mutations
in a temporary copy. Seven source-level fault injections cover a missing-symbol
acceptance in the null-only symtab negative, a fake successful missing-leaf
linker status, acceptance of wrong-address, wrong-constant and dynamic-symtab
mutations, and successful C++ compile/link commands with their outputs removed.
The tests separately alter the observed relocation tuple's offset, type,
symbol name and addend before comparison, and confirm a disabled-comparison
control yields a changed tuple. These injections change only the first tuple
and rejection is reached only in the C owner path, not separately in split or
C++. The expected tuple list is a fixed oracle, not an independent relocation
decoder. These are source-level fault injections, not mutations of real ET_REL
files. They do not cover every guard. The test checks
the final ELF hash's format, not its binding to retained ELF bytes (the ELFs
are temporary). Its expected input hashes are computed from
the temporary copies; the probe supplies the independent fixed pins. Run the
normal and `-O` commands separately; no CI result is asserted here.
