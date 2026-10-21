# Interrupt-register C core: independent behavior review

The reviewed frozen component is `experiments/tsl9-v4160-interrupt-registers/src/interrupt_registers.c`, `interrupt_registers.h` and `irq_io.h`. It reconstructs the normal-boundary output requirements of original IRQ initialization at 0x9A42 and helpers 0x19124/0x19142/0x19160/0x1917E. The unchanged original source proof covers 264 bytes / 94 instructions and rejects 94 raw controls. This review executes only owned C/C++ host code with the explicit `TSL9_IRQ_REGISTERS_HOST_TEST=1` I/O boundary; it never executes original or rebuilt RV32 firmware.

## Independently tested outputs

Each helper performs a fresh READ32 and then WRITE32 at its exact RCC address. Any nonzero enabled word selects OR; zero selects AND with the 32-bit complement of the mask. The normal output tuple is:

| Path | A0 | A1 | A4 | A5 |
|---|---|---|---|---|
| enabled nonzero | before OR mask | exact incoming enabled bits | 0x40021000 | before |
| enabled zero | before AND NOT mask | exact incoming enabled bits | before | 0x40021000 |

The base is **0x40021000**, not the addressed register's full address. Enabled values 2, 3, 0x100, 0x7FFFFFFF, 0x80000000 and 0xFFFFFFFF are tested as noncanonical nonzero values; preserving truthiness alone is insufficient for A1.

The main initializer's oracle enumerates its twenty ordered external effects: CSR clear, six separate READ32/WRITE32 pairs, six PFIC writes with their original widths, then CSR set. It also checks six helper output observations and the final initializer observation. Every repeated RCC read receives a deliberately different sample. Final A0 is derived from the **last** clear read at 0x4002100C; final A1=0, A4=128 and A5=0xE000E000. A fake environment changes other CSR bits between effects, so the final set is checked against then-current state rather than a restored entry snapshot.

The independent C11 and C++17 host builds each pass **4 groups / 3820 cases / 138312 assertions**: 3168 helper payload/mask/enabled combinations, 256 main fresh-sample scenarios, 384 single-bit helper cases and 12 additional CSR/boundary scenarios. The callbacks compare exact event type, order, numeric address, values and four normal-output fields. They are bounded before any host access; numeric peripheral addresses are never cast to host pointers.

Eighteen mutations are actually compiled and assertion-rejected in each language, **36 compiled negatives** overall. They cover enabled normalization, treating only enabled=1 as true, A4/A5 full-address mistakes, using the modified word instead of the sampled word in outputs, wrong helper address, cached reads, writing before reading, wrong write width, wrong main A0/A1/A4/A5 or return value, wrong CSR mask/order and omitting the final PFIC write. Compiler failure is not counted as behavioral rejection.

No source-level mismatch was found within this host GP-free numeric-I/O/normal-output interface. The retained `receipts/` files pin the actual compiler, all three frozen files, test boundary, independent oracle, runner, helper and actual host executables/mutation outcomes. Historical host EXEs, object files, logs and mutation sources remain in this working archive's excluded `build/`; published receipt hashes do not imply those binaries are shipped.

## Native and placement limits

The four fields named A0/A1/A4/A5 are **host output observations**, not physical register captures. Tests do not prove that production inline assembly or a compiler allocation profile preserves A2/A3, emits final A1 correctly, avoids stack changes, preserves other registers, or meets an interrupt/entry ABI. Those requirements belong to separate native object/CFG/encoding checks. They cannot be inferred from these host results, a `void` callback or a successful C return value.

The earlier placement source audit records eight original ranges totaling 540 bytes, all helper callers and unknown indirect-target limits. The previous ordinary-C 118-byte initializer and 22-byte helper sizes are not accepted free space: the separate ABI audit identified incompatible register effects. This new core likewise needs its actual native register contract, size, entry/continuation/reference bindings and final placement proved before integration. No BIN, hardware identity, IRQ/ROM behavior or OTA compatibility is established here.

```sh
python3 run-review.py --project-root /absolute/path/project --language c
python3 run-review.py --project-root /absolute/path/project --language cpp
```

The Python runner uses the project's portable compiler locator and writes a unique build plus byte-identical selected receipt outside `build/`. These results were obtained with Windows/MSVC. They do not establish Linux/macOS execution. No network request, hardware I/O, ISA emulation or firmware execution occurs.

`receipts/parent-c.json` and `parent-cpp.json` retain the parent's full source-plus-ABI-counterevidence host runs, each 4 groups / 9184 cases / 246384 assertions. They are distinct from this independent suite. The native compiler review reported all four bounded candidate configurations required stack state and did not pass the intended native constraints; native verification remains false. A read-only `check-review.py --project-root <project>` binds current frozen input hashes, all three immutable peer seals and the four selected receipt files without rerunning tests. Successful binding does not promote those host receipts to native proof.
