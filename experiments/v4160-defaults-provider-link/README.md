# Defaults: one genuine provider resolved

The actual APP PC-relative reference to `tsl9_settings_default_data_1a69c` now
resolves to a compiled, section-backed four-byte OBJECT in this isolated link
profile. This uses the **fresh source-only UUID aggregate**, not the older
six-UND frozen component. Its unresolved symbols decrease **8 → 7** after
partial linking. The original-coordinate strict link decreases **7 → 6**;
the inherited linker script supplies the numerical stack witness, explaining
the different counts. No other unresolved provider is removed or replaced.

The source contains precisely `31 32 33 34`, with no string terminator.
These are observed opaque literal bytes, not independently derived semantics,
an authenticated default value, or a recovered product feature. The provider's
name supplies the existing relocation role. Its four-byte extent does not
prove every possible use is bounded to that window.

## What was linked and checked

- Both C11/C++17 compile to one four-byte readonly OBJECT, alignment 1,
  with no imports or relocations. The original parent has one real
  `R_RISCV_PCREL_HI20` reference to this provider.
- Actual partial linking retains every parent allocated section's bytes,
  type, flags, size and alignment, including NOBITS size without inventing
  file bytes. It retains all global/weak definition metadata and named
  relocation roles. Local symbol metadata is not compared.
- Original-coordinate diagnostic links preserve all **73,672** parent
  bytes and add exactly four at `[0x1A69C,0x1A6A0)`, giving **73,676**.
  The C/C++ coordinate bytes are equal. Their ELF file hashes differ due
  to inherited object metadata; whole ELF equality is not claimed.
- The new symbol is a genuine four-byte DATA definition at `0x1A69C`,
  not ABS or a numerical alias. Omitting its object leaves the actual
  parent consumer unresolved even when all other numerical witnesses exist.
- Six other providers still prevent a strict original-coordinate link.
  Diagnostic references supplied for those six remain numerical witnesses,
  including three conditional DATA roles and candidate TX RAM. They are not
  installed ROM/RAM or complete-provider evidence.
- Entry is zero and there is no `PT_LOAD`. All original-byte differences
  remain the inherited **93 TX candidate bytes** in `[0x8A56,0x8B6E)`.
  No full BIN is generated or target code executed.

The selected diagnostic byte hash is recorded in `verification.json`.
The earlier formal 95.75% proof is unchanged. This profile does **not** update
either unified manifest or the regular build pipeline. That next integration
must merge the selected spans and remove the defaults numerical witness,
while avoiding a duplicate defaults definition in the conditional full link.

## Original caller evidence

The checker pins the original 22-byte window `[0x131A0,0x131B6)`, decodes
AUIPC/ADDI register fields and signed immediate, and checks the original
`C.LI A2,4`. The instructions form `A1=0x1A69C` at `0x131AA/0x131AE`;
the indirect call is at `0x131B4`. This establishes a source-pointer and
requested-length contract. It does not establish that the provider copies
four bytes, returns normally, or is the installed candidate routine. Caller
reachability, `S1=0x40000`, valid pointers, aliasing and asynchronous effects
remain separate conditions. Existing local analysis identified the slot
as `0x4004C` under that S1 condition.

## Reproduce offline

Use Python 3.10+, the pinned LLVM executables, the original decoded BIN,
and the exact fresh-source UUID parent outputs identified in `inputs.json`:

```sh
python -B experiments/v4160-defaults-provider-link/verify.py --tool-dir /path/to/llvm/bin --parent-build /path/to/uuid-output/build --output-dir /existing/parent/new-output
python -B experiments/v4160-defaults-provider-link/test_unit.py --tool-dir /path/to/llvm/bin
```

Repeat with `python -O -B` and a new output directory. The parent directory
contains `source/`, `diagnostic-c.ld` and the compact diagnostic ELF files.
Its artifacts were freshly compiled in the UUID integration stage; this
profile hashes and reuses them without claiming another complete recompilation.
It recompiles only the new defaults source. Missing/changed inputs fail,
rather than skipping checks. Parent inputs are rehashed after linking.

The packaged reader retains the earlier v7 ELF32 parser with its section
ceiling raised from 8,192 to 16,384 for the actual 10,945-section fresh
aggregate. Its origin and derived hashes are recorded in `inputs.json`.
This capacity adjustment does not disable extent, symbol or relocation checks.
Unit tests compile both languages and reject altered bytes, extra NUL,
wrong owner, writable data and changed alignment. The build also performs
the missing-provider negative link against the actual consumer.

Analysis uses local files only. GitHub publication is separate. Installed ROM,
private ABI, RAM ownership, complete startup, interrupts, copy effects and
hardware/OTA behavior remain unproved.
