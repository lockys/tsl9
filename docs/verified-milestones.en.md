# Verified milestones

## Shared OTA command C/C++ and actual native gaps

The U/S/W/R/E handler at `0x9C4A..0x9E5C` now has readable shared HOST/native C11/C++17. Each language passes 10 own HOST cases / 8,292 checks and three compiled semantic mutants; independent HOST passes 16 cases / 18 dispatches / 898 behavioral assertions and four compiled semantic mutants. These are guarded synthetic tests, without RV32 or hardware execution.

Each actual ET_REL contains 776 bytes / 285 instructions / a 112-byte frame, versus the original 530 bytes / 48-byte frame. Independent review covers nine true undefined references, 23 relocations, all instruction fields and native negative controls. The 246-byte excess, callee preservation, live S/SP/RA, placement and OTA acceptance remain unproved. **No link or new BIN; the complete TX image is unchanged.** W proves writes to a numeric BOOT alias, not Runtime self-update. [Code and evidence](../analysis/v4160-ota-handler-2026-10-22/readme.en.md)

## Callback native component reduced to 624 bytes

New C11/C++17 components each contain 624 bytes / 223 instructions. They explicitly reserve S10/S11, read the current physical GP at six uses and swap two existing saves through an explicit stage. Independent reviews confirm a 48-byte frame, eleven save/restore pairs and fifteen indirect calls; HOST suites are not rerun. The remaining eight original bytes contain executable instructions. Full prefix, call-return ABI, tail ownership and original placement remain unproved. **This component is not integrated and adds no BIN; the existing complete TX image is unchanged.** [Evidence and limits](../analysis/v4160-callback-registers-2026-10-22/readme.en.md)

Further static call-boundary review confirms that the GP+42 datum is killed before both calls, with no missing A4 argument here. The small function pair behind `+0x13C` in two official ROM candidates only saves/returns through RA and does not observe incoming S4/S7. This narrows specific constraints, without identifying installed ROM or proving other callees. Candidate slots correspond to CCC configuration reads and notification submission; the read returns 0..255, so the original `==1` and `&1` gates remain distinct. [Call boundaries and candidate conditions](../analysis/v4160-callback-call-frontiers-2026-10-22/readme.en.md)

## Previous readable event callback and native gaps

The 632-byte callback at `0x8614..0x888C` now has readable C/C++ covering event priority, two context/connection records, chunk length, retries and follow-up events. A single explicit-inline diagnostic reduces native allocation from 1,034 to one 658-byte function with a 48-byte frame and fifteen indirect calls. It remains 26 bytes too large, with extra S10 saves, save order, return-address and unknown-ROM contracts unresolved. **This callback is not integrated into the complete BIN and adds no flashable image.** [Analysis and limits](../analysis/v4160-event-callback-2026-10-22/readme.en.md)

## TX source in a complete experimental BIN

Fresh C11/C++17 pipelines each compile 46 units and produce the same 76,800-byte experimental BIN. Thirteen original function regions / 930 bytes use fifteen real FUNC roles; 678 other sections retain original carriers. All 93 differences from official ID2966 are inside TX; other bytes are unchanged. SHA-256: `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`. **The new BIN is not verified as flashable.** [Complete integration](../analysis/v4160-tx-image-integration-2026-10-22/readme.en.md) | [Experimental image](../artifacts/offline-images/ID2966-V4.1.60-tx-integrated/readme.en.md)

Earlier no-integration/no-new-BIN statements below describe their historical scope. Full ABI, physical ROM/BOOT/Flash, CRC/signature policy and hardware OTA remain unproved.

## Actual native repair of the TX entry and split restores

Fresh C11/C++17 components link to 280 bytes each: an eight-byte narrow assembly entry, a 270-byte readable body and a real two-byte return leaf. A standard ELF branch relocation makes oversized input return without stack access. Both resident-call return addresses match original 0x8A90/0x8AB6. The public entry honestly remains FUNC8, without fabricated single-FUNC280 metadata.

A new scheduling stage moves only five newly compiled saves and five restores. It restores source save order and the fresh-read boundaries around descriptor stores. Actual C/C++ pre/post objects and linked components pass independent checks; every other ELF byte and metadata remains identical. No new opcode or original-firmware bytes generate code. Actual missing-RAM-provider and out-of-range-branch links are also rejected by the linker.

This is a reproducible native component milestone, not complete-image integration or proof of full ABI, physical hardware/ROM/BOOT or BLE OTA. No new BIN is produced. The complete image remains the twelve readable functions / 650 bytes below. See the [current analysis](../analysis/v4160-tx-register-abi-2026-10-22/readme.en.md).

## Original OTA packet construction and measured native differences

Actual C11/C++17 host suites each pass 107 cases / 15,605 checks and eight compiled semantic negatives. Independent suites each pass 31 cases / 78,283 checks and fourteen compiled semantic negatives. These use synthetic providers, numeric memory and explicit ROM boundaries; they do not execute or emulate RV32. Every host executable is checked by the existing immutable machine guard.

Readable C/C++ now follows `0x8A56..0x8B6E`: the original 280 bytes / 96 instructions, forty operand mutations, nine external direct entries and eleven owner RELA records have been checked. The entry payload limit is 1039 bytes and buffer stride is 1062 bytes. Original descriptor writes are 16 bits and the final task read is one byte; wider memory operations are not interchangeable.

The compile probe fits the original 280-byte section, but independent review rejects original ABI admission. Its frame precedes the original guard, restores occur later, and some operands/control flow differ. An existing-word permutation alone cannot close these gaps. This is readable logic reconstruction and bounded native-gap evidence, **not a new complete image or flashable BIN**. The complete image remains the twelve-function / 650-byte version below.

Offline packet preflight and update wait-reason display are recorded proposals, not implemented hardware features. ROM slots retain raw numeric/live-register contracts; candidate SDK names do not identify the installed version or prove its ABI. See the [analysis](../analysis/v4160-ota-tx-2026-10-22/readme.en.md) and [follow-up path](../analysis/v4160-ota-tx-2026-10-22/continuation-plan/readme.en.md).

## Twelve readable functions in the complete image with full header dependencies

The OTA page reply is now integrated, bringing readable code to twelve functions / 650 bytes. Fresh C11/C++17 pipelines each compile 34 original carriers and nine readable units. Their 61 commands comprise 59 LLVM operations and two explicit ABI ordering stages. Each language records 223 actual artifact pins and 41 integration controls. Both 76,800-byte outputs exactly match official ID2966 V4.1.60 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.

All 43 compilations use full `-MD`: 74 project inputs, fourteen generated inputs and one actual Clang `stdint.h` resource header, used by fourteen units. Old `-MMD` omission did not prove that system headers were unused. Independent source review checks full recipe chronology, compiler-versus-ordered inputs and thirteen record mutations; these are not target executions.

Complete artifact checks cover 691 allocations, 679 retained carriers, 8,257 outside plus twelve JAL relocations, 53 relative bindings, 21 incoming entries and fifteen LOADs' full file/memory extents and permissions. The original public NOTYPE / size 0 and local reply entries remain. Incoming `9DF4` is `C.JAL` linking to `9DF6`. Additional compiler address-signature metadata is bound to its actual source/payload instead of being arbitrarily ignored.

This is partial source recovery; other contents remain original carriers. **Not verified as flashable.** ROM is only a numeric-address witness; hardware, installed ROM/BOOT, BLE OTA and recovery remain unproved. No RV32 execution/emulation or hardware operation; unchanged existing host suites were not rerun. See the [integration](../analysis/v4160-reply-image-integration-2026-10-22/readme.en.md) and [offline image](../artifacts/offline-images/ID2966-V4.1.60-reply-integrated/readme.en.md).

## Native C/C++ OTA page reply and original entry boundary

Readable C/C++ now covers `0x9B8E..0x9C0A`: 124 bytes / 50 instructions. Fresh builds for each language explicitly order two regions of existing compiler words, link at the original address and read back an exact original function. Only 28 bytes inside those regions change; all other ELF bytes remain identical. LLVM alone did not emit the final order. Strict linking without TX fails; successful linking supplies only a numeric `0x8A56` address witness.

Each language passes 87 host cases / 3,634 checks and six actual compiled semantic negatives. The independent source-effect suite adds 90 cases / 6,699 checks and ten actual compiled negatives. Native evidence adds eleven raw/IR controls, three compiled negatives and three linked ELF controls. Independent ordering checks reject eighteen actual malformed ELF inputs, five path hazards and three receipt tamper cases per language. Synthetic host evidence does not prove unknown resident register preservation.

An actual two-object partial link preserves the original public NOTYPE / size 0 and local LOCAL / size 0 entries, with no numeric ABS entry alias or padding; the readable function remains a real FUNC / size 124. Original incoming roles, retained carrier allocations and outside relocations are checked. **The complete image remains the prior eleven-function / 526-byte version; the twelfth function is not yet integrated.** Physical hardware, installed ROM/BOOT and BLE OTA remain unverified. See the [component](../experiments/tsl9-v4160-ota-page-reply/readme.en.md), [ordering pass](../experiments/tsl9-v4160-reply-abi-order/readme.en.md) and [integration boundary / feature candidate](../analysis/v4160-ota-page-reply-2026-10-22/integration-plan/readme.en.md).

## Eleven readable functions restore the original complete-image bytes

Five Flash leaves, totaling 198 bytes / 76 instructions, now restore the original registers, entry prefixes, boundaries and machine code. IRQ and quarter automatic saves are restored through an explicit ABI scheduling step. It only permutes existing C.SWSP instructions in newly compiled objects, creates no opcodes or padding, and never fills bytes from an original BIN. Compiler-only and scheduled objects/receipts are retained separately; Clang alone did not produce the final order.

Fresh C11/C++17 pipelines each compile 42 translation units: 34 original carriers, two IRQ/RCC units and six Flash units. Their 57 actual commands include one explicit Python ABI transformation. Both export 76,800-byte images exactly matching official ID2966 V4.1.60 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. Eleven readable functions occupy 526 bytes; remaining image content is still original carriers. **This is partial source recovery.**

Checks cover 691 allocations, 680 retained storage sections, 8,259 outside and eleven owned JAL RELA records, 53 real relative bindings, twenty incoming entries and ten explicitly discharged internal branches. Actual sections and fifteen LOADs back every exported byte, without holes, NOBITS or ROM export. Strict linking still rejects the missing resident-ROM provider; successful linking supplies only a numeric-address witness.

Independent source and ABI reviews read actual compilation provenance, pre/post objects, ELF and BIN. Separate scheduling checks reject 21 malformed objects and three path aliases; parent replay rejects seven actual receipt/output tamper controls per language. Archived metadata checks, actual archive replay, fresh compilation and hardware evidence remain distinct. GitHub excludes generated build objects; the local re-tsl9 delivery retains the complete independent scheduling archive.

**Not verified as flashable; the full goal remains incomplete.** Exact chip/board, installed ROM/BOOT, physical interrupts/Flash, BLE OTA acceptance and recovery remain unproved. Next priority is BLE page reception/replies and version identity, keeping Runtime-to-BOOT and BOOT-to-Runtime directions separate. New features remain [local preflight/status proposals](../analysis/v4160-irq-callframe-2026-10-21/feature-candidates/readme.en.md), without a hardware implementation claim. See the [new integration](../analysis/v4160-register-image-integration-2026-10-22/readme.en.md) and [save-scheduling tool](../experiments/tsl9-v4160-frame-schedule/readme.en.md). Windows Python/LLVM evidence does not establish shell, Linux, macOS or CI execution.

## Eleven readable IRQ/Flash functions in the complete offline image

Actual C11/C++17 builds compile 34 original carriers, two IRQ/RCC units and six Flash units, then export identical 76,800-byte images with SHA-256 `de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`. Seventy bytes differ from the official image: eight previous IRQ bytes and 62 new Flash bytes. Eleven readable functions occupy 526 bytes; the other contents remain original carriers, so this is partial source reconstruction.

All 691 allocations and 680 retained storage sections are checked, together with 53 true section-relative bindings and twenty incoming entries. Actual RELA count is 8,270: 8,259 outside records preserve complete roles and multiplicity, plus eleven typed JALs. Ten original internal branch records are explicitly discharged by their bytes, conditions, PCs and targets. Compressed incoming calls and the tail jump retain their respective return-address behavior. Partial storage and relocated image data are checked at separate layers.

Every exported byte is backed by actual sections/LOADs, without holes, original-BIN fallback, RAM NOBITS or ROM bytes. Strict linking still rejects the missing ROM provider; successful linking uses a numeric address witness only. Independent source/layout and ABI reviews inspect actual linked artifacts. Supplemental literal scanning finds no selected interior-address U32LE values in three complete images, but cannot exclude computed or ROM references. Full fault prefixes, original program `+8` boundary, pointwise/asynchronous IRQ state, board/chip, installed BOOT and BLE OTA remain unproved. **This BIN is not verified as flashable.** See the [English guide](../analysis/v4160-flash-image-integration-2026-10-22/readme.en.md). Windows LLVM evidence does not establish shell, Linux, macOS or CI execution.

## Original-size Flash program and entry event order

The new C11/C++17 program function naturally occupies 100 bytes / 38 instructions. Two fresh base-register loads and explicit A0/A5 primitive constraints recover its complete extent without NOPs, padding or borrowed original bytes. The six Flash functions now total 262 bytes / 99 instructions. Both languages produce identical component ELFs. The initial control read at offset +4 precedes A0 alignment at +6 and the first control store at +14; five program loop destinations retain their original addresses. The last six bytes are actual cleanup and return instructions.

Canonical host suites pass 481 cases / 247,191 assertions and reject six compiled mutations per language. Fresh independent expected-effect suites pass 12 scenarios / 8,964 assertions and reject twelve compiled mutations per language; every host executable is architecture-checked before and after its launch. Independent static review checks the actual component bytes, IR and known branch roles. An alternate firmware-reference path is compiled and replayed explicitly, and replay with the wrong reference context is rejected.

This replaces the previous six-byte ownership gap, but does not preserve every instruction boundary: original program offset +8 lies inside the new four-byte alignment instruction. Scratch-register and fault/nonreturn prefixes, asynchronous behavior, ROM, board and OTA compatibility remain unproved. This component milestone produces no new complete image or BIN. The sealed next-integration plan covers 691 allocations, eleven readable functions, 680 retained storage sections, 8,259 outside RELA records and twenty incoming entry references; its 42 planned compilation units are not yet a completed whole-image build. See the [English guide](../analysis/v4160-flash-entry-order-2026-10-22/readme.en.md). Run `python experiments/tsl9-v4160-flash-entry-order/verify.py --language both` for host checks, or `python analysis/v4160-flash-entry-order-2026-10-22/implementation/verify_native.py --project-root . --tool-dir <LLVM-bin> --language both` for static native checks. Windows evidence does not establish shell, Linux, macOS or CI execution.

## Six readable V4.1.60 Flash functions

Shared C11/C++17 source reconstructs the quarter wrapper, status, unlock, lock, erase and 64-word program functions. Original evidence covers 262 bytes / 99 instructions; native components at the six original entry addresses occupy 64/8/30/14/46/94 bytes. Status and lock have 22 original-identical bytes. The normal contract preserves the 32-byte frame, fresh `SP+12` source reload, five ordered calls, CSR mask 136 and normal register residues. Program's six-byte remainder has no new storage owner; no new complete image or BIN is produced.

Canonical host suites pass 481 cases / 247,191 assertions and reject six compiled mutations per language. Independent expected-effect tests add 12 scenarios / 8,964 assertions and twelve compiled mutation rejections per language. Native checks separately inspect actual machine code/IR, rejecting fifteen machine-byte and three IR controls per language. Original source, six high-address caller slices and the full object's recorded relocation frontier are separate evidence scopes.

The frontier identifies twelve external entry references and eleven owned call/branch records among the prior object's 8,276 RELA; the other 8,265 must retain their roles in future integration. No external interior target in those recorded RELA does not establish absence in ROM, numeric indirect references or unknown runtime state. Frame-save order, fault/nonreturn GPR prefixes, pointwise/asynchronous state, board/ROM/Flash and BLE OTA remain unproved. See the [English guide](../analysis/v4160-flash-native-2026-10-22/readme.en.md). Default host command: `python experiments/tsl9-v4160-flash-native/verify.py --language both`; native command: `python analysis/v4160-flash-native-2026-10-22/implementation/verify_native.py --project-root . --tool-dir <LLVM-bin> --language both`. Windows evidence does not establish POSIX/Linux/macOS/CI execution.

## Readable IRQ source in the complete offline image

Actual C11/C++17 builds recompile 34 original instruction/data carriers plus two readable units, then link and export identical 76,800-byte images. SHA-256 is `47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`. Only eight specified bytes at `0x9A44..0x9A4B` differ, permuting four prologue register-save instructions. Original APK/vendor BINs and the prior source-identical fixture remain unchanged.

Checks cover all 691 original allocations, 686 retained storage sections, 53 real section-relative bindings and eight external entry calls. All 8,270 outside-owned RELA records retain exact roles and multiplicity. The new total is 8,276: six new core JALs replace ten old owned records, explicitly discharging four helper branch RELA records through identical bytes. Every exported byte is backed by actual sections and LOAD contents, without hole filling, original-BIN fallback, RAM NOBITS or ROM-byte export.

Each language has actual dependency closure for 36 compiled units, 44 checked commands and 15 actual ELF/relocation/image negative controls. Strict full linking rejects the sole missing ROM provider; the successful artifact uses only a numeric `0x40000` address witness. Readable C/C++ replaces five IRQ/RCC functions; all other original instruction/data carriers remain, so this is not complete source recovery.

The image is [NOT-FLASH-VALIDATED-irq-callframe.bin](../artifacts/offline-images/ID2966-V4.1.60-readable-IRQ-integration/NOT-FLASH-VALIDATED-irq-callframe.bin). Entry points and separate independent reviews are in the [English guide](../analysis/v4160-irq-image-integration-2026-10-21/readme.en.md). Installed ROM, asynchronous interrupt state, hardware, physical Flash and BLE OTA remain unproved; this BIN is **not verified flashable**. Windows Python/LLVM builds do not establish shell, Linux/macOS or CI results.

## 144-byte IRQ callframe and C++ allocations

Readable C/C++ main now uses six explicit4-byte JALs to shared RCC helpers and a compiler-generated16-byte frame. Actual C11/C++17 main functions are144 bytes, with four30-byte helpers: all264 bytes /94 instructions fit their original extents, without extra allocations. C++ `-fno-exceptions` removes prior unwind metadata; a separate predecessor experiment confirms that this sole flag does not change its five function bodies.

Main's first SP adjustment and134 bytes after offset10 match the original; all120 helper bytes are identical. Four2-byte prologue stores are permuted. Slot sets, all six JAL PCs/targets/RA links, instruction boundaries and fresh frame reloads are checked separately. **Pointwise stack state and asynchronous IRQ equivalence remain unproved.**

Canonical host suites pass9184 cases /246384 assertions per language. Independent suites pass3820 cases /138312 assertions per language and reject60 compiled mutations in total. Each native language rejects six compiled/linked controls and30 coverage controls. The next source-carrier integration plan identifies34 C TUs,691 allocations and53 section-relative aliases. Four original helper branch RELA records are discharged by exact byte identity; new objects must not be falsely reported as retaining8280 RELA.

No new BIN or full-image integration is produced this round. The previous76,800-byte offline image and gate remain unchanged; ROM, board, hardware interrupt and OTA compatibility remain unproved. Use `sh experiments/tsl9-v4160-irq-callframe/verify.sh --language both`, or sibling `verify-native.sh --tool-dir <LLVM-bin> --language both`. Windows Python/MSVC/LLVM evidence does not establish Linux/macOS or shell execution; existing CI account restrictions were neither retried nor changed.

## Branch-first IRQ core and original-address RCC bytes

The new C/C++ core gives each RMW branch its own read, operation, store and returned value. Per-use base/immediate primitives and an explicit returned-A0 bridge avoid the previous spill ranges; machine outlining is disabled. Each RCC helper is 30 bytes and links at its original 0x19124/0x19142/0x19160/0x1917E address with all 120 bytes identical to the original BIN. Complete machine checks show only A0/A4/A5 writes and exact A1 preservation. The IRQ initializer writes only A0/A1/A4/A5 and matches normal output registers; machine code and LLVM IR separately check the 20 ordered effects and six fresh RCC reads.

Each C11/C++17 canonical host suite passes 4 groups / 9184 cases / 246384 assertions, reusing the complete 264-byte/94-instruction source proof. Independent host tests pass 3820 cases / 138312 assertions per language and reject 44 actually compiled mutations in total. Each native language separately rejects five compiled mutations and 30 disassembly-coverage controls.

The 180-byte initializer exceeds its original 144-byte extent, with no accepted alternative placement. C++ adds allocated `.eh_frame`: 120 bytes in the object and 124 linked bytes. Its all-allocated-bytes-function-owned gate explicitly remains false; read-only metadata still requires integration. Normal return evidence does not prove intermediate or asynchronous IRQ equivalence. Full image, ROM, hardware and OTA compatibility remain unproved. No RV32 execution, original-image change or new BIN occurs.

Use `sh experiments/tsl9-v4160-irq-native/verify.sh --language both`; the sibling `verify-native.sh --tool-dir <LLVM-bin> --language both` runs native static checks. New evidence is under `analysis/v4160-irq-native-2026-10-21/`. Windows Python/MSVC/LLVM results remain separate from unverified POSIX shell, Linux/macOS and CI results.

## Placement audit and interrupt register model

The exact owned pool is eight separated original ranges totaling 540 bytes: reset memory 62, clock query 174, fields 40, IRQ initializer **144**, and four RCC helpers **30 each**. A byte-bound audit verifies all 691 section bindings and 8,280 RELA records against the full fixed linker layout. The helpers have other callers. No external direct interior entry was found within admitted code, but 939 indirect instructions leave computed targets unresolved. Summing bytes does not establish a safe contiguous placement.

Actual old native IRQ bodies disprove a useful-looking space assumption: the 118-byte initializer and 22-byte helpers write A2/A3, while the original preserves them. Their A1/A4/A5 residues also differ. A3 survives along the existing caller path to an unresolved callback, so these old bodies cannot supply replacement space under the original contract.

The new `interrupt-registers` C/C++ model retains the 20 MMIO/CSR effects, exact helper A1 bits, branch-specific A4/A5 and final initializer A1=0/A4=128/A5=`0xE000E000`. Each full-source host language passes four groups / 9,184 cases / 246,384 checks. These are host normal-boundary results. Its intended native profile currently fails with `Stack pointer required, but has been reserved.` in all five functions; it emits no object/ELF and has **no accepted native register or placement proof**. Three bounded diagnostic combinations also fail. IR checks and expected-failure reproduction are recorded separately from successful compilation. Restructuring branch-local value lifetimes remains implementation work.

One actual native size improvement is verified independently: unchanged reset C/C++ under `-Oz` produces a 66-byte leaf and 68-byte fragment, down from 78/80; the original is 62. Physical GP operands reduce from four to three. Clock query/fields remain 196/38. Synthetic jump witnesses check two-byte resolved C.J and four-byte external JAL x0 geometry, without supplying an original entry adapter or allocating space. No original image is changed and no BIN is generated.

Use `sh experiments/tsl9-v4160-interrupt-registers/verify.sh --language both`. Source, ABI counterevidence, independent tests, successful bounded probes and failed new native profiles are under `analysis/v4160-placement-2026-10-21/`, with English and Traditional Chinese guides separated. Destination/checkout verification produces fresh local results; historical build archives are not shipped. Linux/macOS, original intermediate IRQ state, ROM, board, Flash and rebuilt-image OTA remain unverified.

## Reset memory initialization

The reset slice at `0x186BA..0x186F8` now has a readable C/C++ implementation: separate GP observations, interleaved forward word copy, unsigned bounds, BSS word clear and the normal boundary A0/A1/A2 values. The exact ID2966 source proof covers 62 bytes / 17 instructions and rejects 17 raw mutations. Its 128-byte initializer is read as data. Each host language passes five groups / 338 cases / 133,601 checks; the independent review adds five groups / 538 cases / 193,964 checks per language and rejects 22 actually compiled mutants in total.

The original slice falls through into CSR setup. Its normal A0/A1 values survive the original clock initializer to the unresolved ROM entry, so a conventional C helper cannot silently discard them. A separate 372-byte / 130-instruction reset/clock caller proof documents that boundary. Installed ROM identity and interrupt compatibility remain unproved.

The native leaf compiles to 78 bytes / 24 instructions versus the original 62-byte slice. It has a C-generated return, while the optional continuation fragment produces 80 bytes and a four-byte JAL even though its source requests `c.j`. Neither fits the original extent. Numeric continuation linking at a nonoverlapping diagnostic address is only a relocation witness; it does not supply the original entry adapter. Full instruction-byte, register, memory-width and loop-CFG checks are separate from native all-path or asynchronous-state equivalence. No original image is replaced and no BIN is generated.

Use `sh experiments/tsl9-v4160-reset-memory/verify.sh --language both`. The source, caller, independent C/C++ and compiler review records are under `analysis/v4160-reset-memory-2026-10-21/`. Selected review source/text and receipt metadata are delivered; historical build archives remain in the workspace, while destination verification creates fresh local outputs. Windows results do not establish Linux/macOS or POSIX-shell launch success.

## Clock normal-return register contracts

The user reported successful official-BIN selection and firmware update through `tsl9-morphe` on 2026-10-21. This is an official-image OTA baseline reported by the user, with exact APK/BIN identities and versions still unspecified. It is separate from the rebuilt-image boot, acceptance and recovery requirements below.

The clock reconstruction now includes the original path-specific A3 value, conditional A2 assignment, query A4/A5 and the full field-function A5 product. A new 298-byte / 98-instruction caller witness and 130 inspected passthrough rows show A3 surviving to the unresolved callback at `0x131E0` through a fresh pointer at `0x4004C`. The concrete continuation after `1973C` is `9F4C`, then `131C2`. This makes discarding A3 unsafe without further evidence; it does not prove the callback consumes it.

The new C11/C++17 host suite passes six groups / 293,845 checks per language; independent tests pass four groups / 5,345 cases / 250,316 checks and reject sixteen actually compiled residue/A2 countercases in total. The unchanged 214-byte / 69-instruction source proof and fifty raw controls are reused, and original integer destination fields are checked separately.

Native builds use compiler register reservations and explicit physical-register constraints. The query uses only A2–A5, with A2 reserved from general allocation; its body is 196 bytes versus the original 174, leaving a 22-byte placement gap. The field body is 38 bytes versus the original 40. Its complete ten-instruction machine pattern confirms unsigned division, byte/halfword stores and normal-return A4=1000/A5=full product. These component proofs do not establish asynchronous intermediate-state, IRQ, full-image, ROM or physical compatibility. No original body is replaced and no BIN is produced.

Use `sh experiments/tsl9-v4160-clock-registers/verify.sh --language both`; native CLI and evidence limits are under `analysis/v4160-clock-abi-2026-10-21/compiler-review/`. Linux/macOS and POSIX-shell execution remain unverified while the previously observed CI account restriction is unresolved. New documentation remains split by language.

## Readable native clock and derived fields

The two clock functions now have a separate readable C/C++ implementation with actual volatile MMIO/RAM accesses and live GP primitives, without the older register-interpreter adapter. It reuses the unchanged 214-byte / 69-instruction source proof and 50 raw negative controls. Each host language passes six groups / 269,618 checks. Independent tests pass four groups / 5,345 cases / 214,811 assertions per language and reject ten actually compiled countercases in total.

Freestanding C11 and C++17 RV32 builds each produce a 170-byte query and a 44-byte derived-field function. The latter exceeds its original 40-byte extent, so these bytes cannot be substituted at the original placement. Linked components have no undefined symbols, runtime helpers or writable data. Full ELF-bound disassembly coverage verifies four/three GP read sites, load/store widths and direct branch boundaries; LLVM IR checks the dynamic GP offsets and unsigned arithmetic. Ten compiled native source controls and 24 disassembly-transcript controls are rejected in total. This is structural evidence, not a native all-path semantic or original register/stack/interrupt ABI proof.

Use `sh experiments/tsl9-v4160-native-clock/verify.sh --language both` for source/host checks. The standalone LLVM CLI is documented in `analysis/v4160-native-clock-2026-10-21/native-review/readme.en.md`. No RV32 code is executed or emulated, no original image is changed and no new BIN is generated. New guides and review documents have separate English and Traditional Chinese files; each `README.md` only links the language versions.

## Readable native interrupt initialization

The new component reconstructs `0x9A42` and four RCC helpers as readable C/C++, with direct volatile MMIO and CSR instructions in native builds. The original five functions occupy 264 bytes / 94 instructions; 94 raw instruction mutations are rejected. Each hosted language passes 4 groups / 6,680 checks; independent tests pass 4 groups / 34,267 assertions per language and reject six actually compiled countercases.

C11 and C++17 also compile and link as freestanding RV32 components: four 22-byte helpers and a 118-byte initializer. Both LLVM IR and actual machine-code checks identify the 20 ordered effects, including six fresh RCC reads, exact word/byte widths, CSR clear/set masks and the final RMW return value. Eight compiled native mutations are rejected. These are standalone component checks. There is no full-firmware replacement, original stack/register ABI proof, RV32 execution or physical I/O. The existing 691-section / 8,280-relocation image and its one unresolved resident entry remain unchanged.

Use `sh experiments/tsl9-v4160-interrupt-init/verify.sh --language both` for its separate source/host check. Native checks require LLVM and the explicit CLI documented under `analysis/v4160-interrupt-init-2026-10-21/native-plan/`. The previous cross-platform CI attempt was blocked before any steps by GitHub account billing/spending-limit restrictions; no rerun or billing changes were made.

## Portable entry and clock calculation

The portable Python backend verifies four models: runtime-loop, system-clock-query, resident-entry and resident-copy. Each checks its sealed source proof and then builds and runs our own C11 and C++17 host tests. Windows native compiler results pass; Linux, macOS and shell launch results require separate CI evidence. PowerShell and CMake are not dependencies of this entry.

The new clock-query model covers ID2966 V4.1.60 addresses `0x18834..0x188E2` and `0x1973C..0x19764`: 214 bytes and 69 instructions. Its source proof rejects 50 raw operand mutations. Each language passes 7 groups and 1,414 checks. It retains separate RCC reads, live register/address changes, a live prescaler table, unsigned arithmetic and width-limited stores. The initializer integration binds only the two proven call sites; the intervening call remains opaque.

## Earlier reconstructed models

| Model | Source evidence | Host tests per language |
| --- | --- | --- |
| Runtime main, initializer, loop and dispatcher | 220 bytes / 80 instructions; 45 raw mutations rejected | 6 groups / 1,431 checks |
| Reference resident entry, initializer and RAM seed | 230 bytes / 66 instructions plus 4-byte header; 35 raw mutations rejected | 5 groups / 121,496 checks |
| Reference byte copy | 58 bytes / 18 instructions; 23 raw mutations rejected | 5 groups / 772 checks |

These counts describe selected source and synthetic host behavior. Original firmware is data; it is never executed or emulated. The captured resident candidate lacks original bytes at `0x6EB2C`; a synthetic continuation cannot establish the missing implementation.

## Migration and evidence limits

The migration inventory records 116 historical PowerShell scripts and 93 root suites. The four portable models do not replace historical RV32/ELF, integration or download gates. The new downloader prototype supports dry-run and an offline HTTP boundary double only; its 23 cases are not a live vendor-download result.

Source proofs are under `analysis/*/source/`. Full local independent and composition receipts may bind host executables and logs excluded from publication. `publication-manifest.json` verifies the files actually shipped. Historical sealed documents retain their bytes; new user guides have separate English and Traditional Chinese files.

WCH CH32V20x is a hardware hypothesis, not a confirmed TSL9 part. Installed ROM, board, startup/interrupt ABI, physical Flash behavior and BLE OTA acceptance remain unproved. The existing 76,800-byte source-identical offline image remains **NOT-FLASH-VALIDATED**.
