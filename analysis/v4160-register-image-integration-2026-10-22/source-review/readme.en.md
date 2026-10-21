# Independent review of the explicitly ABI-scheduled source image

[繁體中文](readme.zh-TW.md)

Actual final C11 and C++17 objects, IR, pre/post scheduling objects, linked ELFs, LOADs and BINs were read independently. Both **76,800-byte BINs are byte-identical to original ID2966**, SHA-256:

`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`

The pipeline is **C/C++ compiler output plus an explicit ABI save-order scheduling pass**. The compiler did not independently emit the scheduled order. This is a hybrid reconstruction: eleven readable functions /526 bytes, with680 allocations retained as original instruction/data carriers. It is not a complete readable C/C++ rewrite. No RV32 execution, emulator, hardware, network operation or new user feature implementation was performed.

## Actual generation chain

Each language freshly compiles42 TUs:34 retained-carrier TUs and eight typed TUs providing eleven functions. The57 recorded commands comprise56 LLVM commands and one Python `-B` scheduling command:

```text
42 source TUs → raw-carriers.o + typed-providers.o
              → compiler-integrated.o
              → schedule.py → source-integrated.o
              → strict rejection / numeric ROM witness link
              → objcopy → actual BIN
```

Original BIN bytes are validation references, not compiler/scheduler/link/export inputs in this round. The retained source carriers already contain original instructions/data; they are not claimed to be newly recovered high-level algorithms. Eight adapters add types, sections and real FUNC aliases without emitting ledger opcodes or copying the original BIN into the output.

Both actual compiler objects have SHA `63720dca234286d4b2bd012855606c0ca6c01a9effefb3066d1d8889f2657826`; both scheduled objects have SHA `4e86cebc1119d30a726386cc520d73c5384920bb74bd97dbbc5dfa505c6bfbf2`.

## Explicit14-byte ABI scheduling and its limits

The reviewed scheduler/policy are `dc680558…876535d` / `2af7789f…0a694d`. The pass permutes existing C.SWSP halfwords; it synthesizes no opcode, adds no padding and reads no original BIN for generation.

| Function | Compiler saves | Scheduled saves |
| --- | --- | --- |
| IRQ9A42 | RA→SP+12,S0→SP+8,S1→SP+4,S2→SP+0 | S2→SP+0,RA→SP+12,S0→SP+8,S1→SP+4 |
| Quarter9C0A | RA→SP+28,S0→SP+24,S1→SP+20 | S0→SP+24,S1→SP+20,RA→SP+28 |

The independent checker reconstructs the permutation from actual pre-object halfwords and compares every output byte. Exactly14 file bytes change; size, all section metadata, symbols and relocations remain identical. This is not admission based only on receipt booleans.

ELF shape alone cannot authenticate newly compiled C/C++ origin. The full review therefore also binds source identities,42 actual TU objects, all50 Clang object/IR language/standard/target recipes, the pre-object component bytes and merge inputs, current tool/policy, scheduler recipe, post-object and final link inputs. A correct prologue or historical scheduling receipt alone is insufficient.

The scheduler rejects recorded symbol/relocation anchors inside scheduled intervals. This does not exclude resolved direct branches or computed interiors in arbitrary input ELFs. A distinct sealed ABI review covers the admitted functions/call frontiers; general computed/encoded/ROM-reference absence remains unproved. Earlier standalone tests used historical compiled objects and are not counted as these42 fresh compilations. The actual new pre/post chain is independently retained and checked.

## Independent scope

- All691 allocations,680 retained partial-object contents, eleven actual readable pre/post bodies and real section-owned FUNC aliases.
- All8259 outside relocation roles/types/signed addends/multiplicity; eleven typed JALs,8270 total; twenty known entry references and53 relative bindings.
- Four exact source filters remove only the eleven owners; no selected raw fallback remains in any of34 actual carrier objects.
- All42 actual `.d` targets/primary sources/adapters,72 existing project inputs and twelve generated inputs, plus ten scheduling source/policy/documentation inputs. `-MMD` excludes compiler system/resource headers; a complete system-header closure is not claimed.
- Fifteen actual PT_LOAD file/memory/permission maps equal the linked sections and BIN. RAM remains NOBITS at20004000,35160 bytes.
- Six actual Flash IR volatile32/register/address relationships and supplemental producer IRQ IR/full static replay.

Each language's201 actual artifacts/logs/dependency files passed readback, with producer read-only replay of23 ELF/RELA/image, three dependency and four scheduling-receipt controls. Two newly authored independent controls modify actual recipe-record JSON: a C receipt mislabeled C++, and a typed IR standard contradicting its language. Both fail the specific source-language gate. No compiler or target is launched for these controls; they are not compiled native/host semantic mutants.

Prior sealed original-instruction, native-component and HOST proofs/mutant matrices are reused by exact identity. The old host mutant matrix was not blindly repeated. Fresh evidence is the two-language whole source/scheduling/artifact chain and focused new source-record controls.

## Portable commands

Default checks current source, sealed metadata and expected bytes, without claiming actual build archives exist or were replayed:

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin
```

For the complete actual new chain:

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin --receipt /path/to/new-build/c/verification.json
```

The shell wrapper uses `PYTHON` or `python3`; Windows may invoke Python directly. Publication retains source, receipt metadata and reports, not full local build archives. Historical receipt paths do not imply availability on another machine; pass an actual fresh receipt there. Portable mode needs no W-only baseline objects or frame ABI test archives and explicitly reports `original_baseline_archives_replayed: false`.

## Unproved boundaries

Strict linking still rejects the missing `__tsl9v4160_rom_entry`. The witness script assigns40000 without ROM bytes/implementation. Identical BINs do not verify ROM contracts, physical boot, chip/Flash compatibility, fault/asynchronous behavior, installed BOOT or OTA acceptance. Those remain false/unknown. Retained carrier bytes are not presented as a complete readable source recovery.
