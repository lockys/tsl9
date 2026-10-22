# Independent source-integrated IRQ image review

Fresh C11 and C++17 builds and subsequent read-only artifact replay passed using the final reviewed runner. Both produce the same 76,800-byte **NOT-FLASH-VALIDATED** candidate, SHA256 `47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`. It differs from the fixed ID2966 original only at eight bytes, `9A44..9A4B`, corresponding to the admitted prologue save-order permutation.

This is a partial readable C replacement of five functions totaling264B: main9A42/144B and helpers19124,19142,19160,1917E/30B each. The other686 original storage sections remain captured original code/data carriers. It does not recover complete readable source, implement a proposed new feature, establish pointwise/asynchronous equivalence or supply a physical ROM provider. Hardware compatibility, startup behavior and OTA readiness remain false.

## Actual evidence and source audit

[review.json](review.json) pins the final runner, portable model wrappers, manifest/layout and selected actual receipt copies. The final runner SHA is `b26410ae9a0d9dece3e5404fb311407dd7c3022a08a7d2fb8c8df7834496c854`. Historical extraction in `prepare_manifest.py` is a one-time provenance operation; the fresh verifier consumes its pinned manifest and copied layout rather than needing old build directories.

The source filter removes exactly the five allowlisted quoted-assembly blocks, once each, through their exact `.size` records. The remaining two filtered source files are byte-recomputed during replay. Forced adapter declarations assign typed functions to original section names and create actual global FUNC aliases in each owning translation unit, including C linkage under C++. The main and helpers use their separately sealed native compile profiles; the main permits the real callframe while helpers retain their narrower register constraints. LLVM IR and selected code hashes bind those compile outputs. No original/rebuilt RV32 code is executed.

Each language has34 retained carrier translation units plus2 typed units,36 actual dependency files,71 pinned original non-system source/header dependencies plus4 generated inputs,44 exact clang/lld/objcopy command records and144 pinned artifacts. `-MMD` excludes compiler system headers; this is an application dependency closure, not a whole-sysroot hash inventory. Before/after snapshots also bind sources, proof members, runner and declared tool files. The shell entries are reviewed but were not executed here; Python model entry was actually used.

All691 original allocated section roles and VAs are checked. The partial object retains8270 outside RELA records with full symbol owner/value/type/visibility, signed addend, site and multiplicity; it has six typed-helper JAL relocations and discharges only four specifically identified old helper branch relocations, totaling8276 RELA. All53 canonical labels stay section-relative, five original global FUNC aliases and eight static incoming entry references remain. The reviewed gate preserves complete metadata inventories, including old ABS mappings plus exactly two measured additions; the private-label exception is four exact roles rather than a prefix wildcard. Unknown computed/interior entries remain unknown.

The strict final link actually fails for the sole unresolved `__tsl9v4160_rom_entry` and creates no strict ELF. A separate script assigns only the numeric address40000 to produce **ADDRESS-WITNESS-ONLY.elf**. This supplies no ROM bytes or provider. All76,800 exported bytes have PROGBITS section storage and matching file-backed LOAD bytes; NOBITS RAM35160B is excluded. This is storage representation evidence, not complete PT_LOAD zero-fill execution or physical memory semantics.

Fifteen actual mutated ELF/RELA/image files per language were rejected and replayed: retained/selected bytes, alias section/type, relative label value, relocation addend/count, RAM kind, extra allocated storage, linked VA, LOAD LMA, out-of-scope/reverted image bytes and truncated/appended images. Rejection reasons and hashes are retained in the selected receipts. No raw APK/minified JS, credential or device identity was copied to this review.

## Static additive-checksum observation

[checksum-note.json](checksum-note.json) records a narrow arithmetic result. All eight byte changes lie in raw plaintext1024B block6 (`9800..9BFF`) and preserve its byte multiset. Its data sum16 is28349 before and after; adding unchanged index bytes`00 06` gives28355. The APK `ready` source sums the complete page including its two index bytes. Therefore the sum would be unchanged **if** those plaintext bytes occur together in the same transfer page with unchanged index bytes. No API/page encoding or actual transfer mapping is inferred.

The saved ID2966 runtime-side W instructions check1026B, use1024 data bytes and derive numeric destination `(0x20000+4+page)<<10`, namely`08001000+page*1024`. That is not the runtime image base8000. These facts do not prove BOOT/runtime mode compatibility, signature/authenticity, whole-image acceptance, Flash success or safe OTA. No JS or target instructions were run to obtain them.

## Read-only replay and fresh reproduction

```sh
python3 check-review.py --project-root /absolute/project --firmware /absolute/ID2966.bin
python3 check-review.py --project-root /absolute/project --artifact-root /original/archived/final-build
python3 /absolute/project/experiments/tsl9-v4160-irq-image-integration/verify.py \
  --project-root /absolute/project --tool-dir /local/llvm/bin \
  --firmware /absolute/ID2966.bin --language both --build-root /new/output/directory
```

Default review replay checks sealed selected JSON, current source/proofs and original-derived image arithmetic without compiling or creating an image. It hashes the optional checksum-reference APK/CFG files when present and explicitly reports their availability; their source fingerprints remain provenance when those private sources are absent, without copying them to make links work. `--artifact-root` additionally replays the actual archived c/cpp artifacts and30 controls; historical receipts contain real absolute command/tool paths and require that layout. A fresh build accepts explicit project, LLVM, firmware and create-only output paths. It is not a claim that old receipt paths can be relocated unchanged.

Selected receipt copies are outside excluded `build/`; original EXEs/objects/ELFs/BINs/logs/dependency files/mutants remain only in that working archive. A read-only preflight found all73 manifest source/header files already present with matching hashes in the publication tree; it performed no publication write. This review changed only its own new scope, not implementation, prior seals or delivered projects.

[繁體中文](readme.zh-TW.md)
