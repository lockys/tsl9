# Original TX integrated: all APP bytes reproduced

The regular source build now compiles `src/native/tx_candidate/original_tx.c`
instead of the three-part candidate TX and its instruction-order postpass.
This is a named-instruction, naked inline-assembly reconstruction with labels
and two genuine PC-relative RAM relocations. No original TX byte array or
binary slice supplies the build output. The source is curated from the earlier
symbolic TX experiment; only its section name changes for regular integration.

Fresh C11 and C++17 full diagnostic candidates are each **76,800 bytes** and
match the original V4.1.60 decoded BIN **byte for byte**, with zero differences:

`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`

The previous 93-byte TX difference is gone. All **73,676 selected bytes** also
match the original; the full builder adds the existing 3,124-byte dispatcher
reconstruction. That dispatcher still compiles fragments separately and
reassembles their bytes, rather than directly linking all fragment objects.
The source inventory now records **176 source/header files, 125 CODE
units and 15 DATA units**, plus the separately compiled replacement TX input.
The additional file does not create a second TX allocation.

## Link and ownership evidence

The 280-byte TX section is compiled as C11/C++17 using the existing register
profile and `-Werror`. It has exactly two relocations: HI20 at offset `0x80`
to undefined `__tsl9v4160_data_2000b18c`, and LO12_I at `0x84` to the actual
local HI20 anchor. Strict TX-only linking without RAM fails; linking with the
wrong RAM address fails the original-byte guard. The regular aggregate keeps
this real dependency rather than baking in an unrelocated RAM immediate.

The three public entry/return bindings are retained, with exact section-backed
values and sizes: `__tsl9v4160_call_8a56` (8 bytes),
`tsl9_filter_external_8a56` (size 0), and `tsl9_tx_oversized_return` (2 bytes
at `0x8B6C`). Existing aggregate checks count eight incoming entry references
by target name; they do not compare the full before/after owner, offset, type
and addend projection. The final byte comparison verifies the actual linked
call encodings. The new object replaces only the old 280-byte composite.
The original helper remains available as an archived candidate experiment;
the regular aggregate no longer invokes its object postpass.

The selected aggregate still has seven unresolved dependencies. Its strict
original-coordinate link has six after the inherited stack witness. The
conditional full link still needs the unknown resident at `0x40000`, even
after the three conditional DATA aliases and candidate RAM object. Numerical
diagnostic witnesses and byte equality do not prove these runtime contracts.

## Reproduction and tests

With Python 3.10+ and local RISC-V LLVM, run from repo root using new output
directories outside the repository:

```sh
python -B scripts/verify-curated-source.py
python -B scripts/build-source-spans.py --tool-dir /path/to/llvm/bin --out /new/external/selected
python -B scripts/build-v4160-source-candidate.py --tool-dir /path/to/llvm/bin --out /new/external/candidate
python -B experiments/v4160-original-tx-integrated/check.py --build-root /new/external/selected --candidate-root /new/external/candidate --original /path/to/ID-2966-V4.1.60-decoded.bin
python -B experiments/v4160-original-tx-integrated/test_tx.py --tool-dir /path/to/llvm/bin
```

The selected build also passed with `python -O -B` and `PYTHONOPTIMIZE=1`;
normal and optimized audits agree. The complete candidate was freshly built
in normal mode and audited under both modes, not rebuilt in optimized mode.
The build does not read the original BIN or a previous candidate for TX bytes;
the separate audit checks the original's identity before comparison.

Tests compile four altered instruction sources in both languages: length
guard, branch predicate, payload store offset and return-frame restoration.
All eight compiled mutations are rejected by the linked byte check.
Four relocation/entry metadata mutations and two wrong-named RAM links are
also rejected. The actual TX build separately rejects missing RAM and an
incorrect numerical RAM address. No target code is executed.

`verification.json` contains the actual source/full-image audits, tests and
nested builder receipts. `source-change.json` records the previous local
inputs. The older 95.75% formal source proof remains archived evidence with
its original scope; it has not been relabeled as this complete byte comparison.

## What remains

This is **complete offline APP byte reproduction**, not proof of portable C,
recovered original source, runtime behavior, hardware compatibility or a
flashable build. The diagnostic ELF has entry zero and no `PT_LOAD`.
The RAM range's ownership, private calling conventions, three global DATA
bounds, installed resident ROM, startup/IRQ behavior and device/OTA operation
remain unproved. Opaque observed data and instruction-level code remain in
the source tree. Next work should narrow those execution contracts and improve
the semantic reconstruction, while preserving the now exact image bytes.
