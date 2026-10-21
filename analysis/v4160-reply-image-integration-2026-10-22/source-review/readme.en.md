# Independent source provenance: twelve-function image

[繁體中文](readme.zh-TW.md)

This review concerns the complete offline ID2966 V4.1.60 payload built from twelve readable native functions (650 bytes) and the remaining raw carriers. It does not describe a fully recovered firmware source tree or a general-purpose C ABI. Native source still relies on its documented register, opaque-call and resident-provider conditions. Existing raw-source and HOST seals remain unchanged; this milestone adds compilation/integration evidence rather than rerunning unchanged HOST suites.

## Source and pipeline boundaries

`source-inputs.py` independently checks the79 native project files: precisely the prior76 plus `page_reply.c`, `page_reply.h` and `reply_io.h`. HOST adapter files are absent from native dependency closure. It independently reconstructs all five filtered carrier inputs from exact quoted-assembly owner spans. Eleven old typed owners are removed; reply storage is replaced by its original zero-byte AX boundary, preserving the GLOBAL NOTYPE size0 and local size0 entry roles. This prevents a hidden original124-byte fallback alongside the new C FUNC124.

The source/compiler pipeline has two distinct ordering stages:

1. Compile34 raw TUs and nine typed TUs, plus nine matching LLVM IR units. The reply remains a standalone one-allocation object. Apply the narrow reply ABI pass to `reply.o`, producing `reply-ordered.o` by rearranging existing compiler-owned instructions.
2. Merge the eight other typed objects with that ordered reply, merge with raw carriers through `canonical53.ld`, then apply the older IRQ/quarter save-word pass to the full `pre-frame-integrated.o`, producing `source-integrated.o`.

The boundary script places the original zero-byte reply owner before the real native reply input section. The original public symbol remains NOTYPE0; the C function supplies a distinct GLOBAL FUNC124 at the same entry. The old private null-branch role is discharged by actual local compiled control flow. Original incoming `9DF4` bytes `693b` are **RV32 C.JAL**, rd=x1, target9B8E, link9DF6. This follows the narrow correction seal `89992f1f7d8f98595b5e151d34479ef0876162d697087c8e562d72036472a34c`; the relocation name RVC_JUMP alone does not imply a no-link jump. Release at9BF8 remains the separate no-link T1 tail.

The compiler body, typed-provider body and final scheduled body are distinct identities. Manifest fields containing `native_object_sha256` describe **function-body bytes**, not the complete ELF object. Actual complete object digests are retained in artifact pins. The final whole payload can equal original bytes while intermediate ELF metadata differs legitimately; metadata equality must follow its specific role rules rather than an all-object byte-identity claim.

## Independent actual provenance checks

`provenance.py` reconstructs exact profiles from the immutable eight-provider and standalone reply sources, then checks the chronological61 recorded commands:59 compiler/query/link/export invocations and two explicit Python `-B` stages. It checks exact source, language, ISA/ABI, flags, forced adapter, output roles, logs and exits. Neither a BIN, old object nor a whole-object reply ordering input is admitted in those generation recipes. Original firmware is a comparison/reference input only.

Each of43 actual object TUs emits `-MD` dependencies, including compiler resource headers. The measured project closure is74 unchanged existing inputs plus14 generated inputs (five filters and nine adapters), with one actual Clang resource header. Every rule is bound to its own object target, first primary source and forced adapter. Nonproject paths must be discovered under the actual compiler resource directory and have the pinned resource-relative header digest. The discovery command/log/tool and before/after header fingerprints are checked. This is the observed header closure of these43 recipes, not an inventory of all toolchain files.

Each actual raw carrier object is inspected for selected machine-code fallback. The actual empty reply section must have only its precise original NOTYPE/local roles. These source checks are separate from the companion ABI/LOAD/image review and the producer's replay; no producer `passed` boolean substitutes for an independent source check.

Thirteen focused controls mutate actual recorded data in memory: ten recipe/source/profile/order cases and three Make-rule target/primary/adapter cases. They include using raw reply.o in the typed merge, ordering a full merged object, reversing the required stage chronology, compiling the HOST source instead, injecting a hidden response file and changing `-MD` to `-MMD`. Every control must be rejected. They are **record/rule controls, not newly compiled semantic mutants**. This scope does not rerun the unchanged87-case producer or90-case independent HOST suites.

## Evidence and execution limits

Selected final receipt identities and measured results are recorded in `selected-receipts.json`. The final C and C++ receipts (`23f9ac76…27d71` and `1904e97f…b0c18`) each pin223 artifacts and41 producer controls (30 ELF/RELA/image, four dependency, six ordering-receipt and one chronology control). Both passed this independent61/43 provenance gate and13 focused controls, the separate ABI/LOAD/image gate, and producer read-only replay. The one resource header is observed in14 of the43 actual dependency rules. `results-c.json` and `results-cpp.json` retain these actual readback reports. Generated build artifacts are excluded from the publication seal. Default checking validates current source, sealed references and selected metadata; it explicitly reports that actual archived build artifacts were not replayed. Optional actual-receipt checking reads the real compilation artifacts/dependencies/objects/IR/logs and invokes read-only producer replay; it launches no target or compiler command.

The expected76800-byte offline payload SHA256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. The strict link must still fail for the sole missing ROM provider. The second link uses only the explicit numeric ROM address witness0x40000; it supplies no ROM bytes or resident implementation. Full device memory, installed BOOT/ROM identity, arbitrary asynchronous/fault equivalence, hardware behavior and OTA acceptance remain unproved. This adds no end-user feature and produces no flash-validation claim. No RV32 execution, ISA emulation, BLE traffic or vendor request occurs in this review.

## Portable interface

From the workspace root (published cases use `analysis/v4160-reply-image-integration-2026-10-22`):

```sh
python3 -B apk-analysis/tsl9-v4160-reply-image-integration-2026-10-22/source-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

The shell wrapper accepts the same options; set `PYTHON` if needed. Add `--receipt PATH/verification.json` to inspect a real current C or C++ build. Default metadata checking does not require the archived Windows compiler/resource directory. Actual archive replay requires the recorded tools, headers and real artifacts to remain accessible; source-only default checking is not a substitute for them.
