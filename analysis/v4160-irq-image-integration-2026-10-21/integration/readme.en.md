# Actual source-integrated offline IRQ image

The fresh C11 and C++17 builds each compile all 34 original carrier translation
units plus the two readable frozen callframe translation units. Only five exact
assembly section blocks are removed from two copied carriers; all other source
text remains unchanged. Owning-TU forced includes attach the five original section
names and real global FUNC aliases. The full source-derived image is 76800 bytes,
SHA-256 `47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`.

The runner admits exactly eight changed bytes at `0x9A44..0x9A4C` (exclusive end),
including their exact values. These permute the four complete two-byte stack
stores. The first SP adjustment, main body from offset10, four helper bodies and
every other image byte remain original. Normal-boundary component evidence does
not prove pointwise or asynchronous equivalence during that changed save order.

Fresh portable command (Python 3.9+ and local LLVM with the required RV32 flags):

```sh
python3 -B analysis/v4160-irq-image-integration-2026-10-21/integration/verify_image.py \
  --project-root . --tool-dir /path/to/llvm/bin --language both
```

In the working analysis checkout replace `analysis/v4160-` with
`apk-analysis/tsl9-v4160-`. `verify_image.sh` forwards the same arguments and uses
`$PYTHON`, `python3`, then `python`. The Python CLI was actually exercised on
Windows; the POSIX launcher is supplied as source and has not been run using WSL
or Git Bash. Tool overrides are `--clang`, `--linker`, `--objcopy`; an explicit
`--firmware` selects the hash-checked offline reference. `--build-root NEW` must
name a nonexistent directory. No package download or network activity occurs.

Each actual build checks 691 original allocations, 686 retained section storage
hashes, 53 section-relative canonical bindings, all original nonmetadata symbol
roles plus exactly five public C FUNC names, all 8270 outside-owned RELA records
with full symbol roles and signed addends, six original-site native JAL records
and zero helper relocations (8276 total). Four obsolete private branch symbols and
their four original type44 relocations are discharged explicitly. No allocated
exception metadata, hidden function, writable storage, alias-as-ABS provider,
extra section or linker padding is admitted.

Metadata is separately bounded: original SECTION roles remain exact, FILE records
are the original34 plus the two readable TUs, retained mapping markers preserve
their roles with only assembler ordinal renumbering, and five selected `$d`
markers become native `$x` markers. Each new typed input's `.riscv.attributes`
marker becomes an unreferenced local ABS0 marker during the actual partial link;
exactly those two nonstorage additions and two `.comment` markers are inventoried.
They are not providers. The final image is checked against every file-backed
section and every actual LOAD VMA/LMA; RAM remains 35160-byte NOBITS and contributes
no flat bytes. There is no fallback to old data for missing output.

The strict final link actually fails for the sole missing
`__tsl9v4160_rom_entry`. A separate script assigns only its numeric address
`0x40000` to create `ADDRESS-WITNESS-ONLY.elf`; it supplies no ROM bytes or behavior.
Only that witness is exported to a new `NOT-FLASH-VALIDATED-irq-callframe.bin`.

Each language has 44 recorded actual LLVM invocations, 36 `.d` dependency rules
covering exactly71 original native inputs plus four generated copies/adapters,
before/after source/tool/proof identity checks, structural LLVM IR checks and
15 retained actual ELF/RELA/image negative artifacts, all rejected. These are
static checks, not RV32 execution or emulation. The compiler profile is the
previously proved `-Oz`, outliner disabled, reserved-register profile; C++ adds
`-fno-exceptions`. No other optimization profile was explored here.

The `.d` files use `-MMD`: this is the non-system project source/header closure.
Compiler system/resource headers are excluded from that inventory. Exact local
LLVM executable hashes and actual compiled bytes are recorded separately.

Replay an actual local build without compiling:

```sh
python3 -B analysis/v4160-irq-image-integration-2026-10-21/integration/verify_image.py \
  --project-root . --replay /path/to/build/c/verification.json
```

`replay(root, receipt)` checks actual artifact/log pins, commands, dependency
closure, current tool/source/proof identities, ELF, relocation, image, IR and all
15 negative artifacts. `check_image.py --project-root ROOT` checks this sealed
report and selected byte-identical metadata receipts; `--require-local-builds`
also requires and replays both historical local archives. Published metadata does
not pretend excluded build archives were replayed. Independent reviews bind their
own actual builds separately.

This is an offline source-storage integration milestone. Most of the firmware
remains raw captured sections. Missing resident ROM, source-exterior reads,
callback/data contracts, arbitrary computed interior entries, board/chip identity,
interrupt timing and observations between reordered saves remain unresolved.
Physical compatibility, bootability, OTA and safe flashing remain unproved. No
target code was run, no emulator or hardware was used, and no network request was
made. Build/log archives remain local and are not published with these documents.
