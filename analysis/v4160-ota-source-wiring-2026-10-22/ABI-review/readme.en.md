# Independent review of real C source entry wiring

[繁體中文](readme.zh-TW.md)

This review checks source/ELF/experimental-image wiring, not flash readiness. The strong FUNC alias is produced in the same translation unit as the immutable568B shared C kernel. It is neither an ABS address stand-in nor a fabricated function.

Standard objcopy changes only the original canonical GLOBAL NOTYPE to WEAK NOTYPE on a copy. All691 base allocations,8261 relocations and other symbol roles remain intact. The original530B body stays at9C4A. Partial linking adds actualC and explicit nonexecuting FF data:693 allocations,8281 relocations, nine real allocated callee/callback bindings and one remaining trueROM UND.

The final numeric address witness places actualC at1AC00 with two genuine FUNC568 aliases. Encoded JAL14094 links to1AC00 usingrd1 and still returns through14098. All original allocated addresses and bytes remain, except that one caller word. The77824B experimental image contains the old76800B prefix, real linkedC568B and explicit nonexecutingFF456B. Every file-backed section equals its image bytes; the data fill is neither executable padding nor borrowed original code.

Checks cover the entire relocation union, all20 native relocation opcode/rd/target/HI20/LO12 fields, ordinary symbol roles and metadata provenance. Two attribute mapping markers become nonproviderABS metadata; two SECTION roles correspond to real new allocations. Excluded addrsig is58 prior bytes plus4 actual new bytes, then removed. The historical linker removes comment and SECTION metadata while retaining FILE/code mappings and ISA attributes; these deltas are explicit.

Fresh evidence includes all11 actual compiler/IR/objcopy/partial/strict-link/address-witness/extraction recipes, four project MD dependencies plus the actual stdint resource, tool/source hashes, the genuine alias IR,193 instruction operands and full8register opaque bridges. The algorithm and HOST core are unchanged, so HOST is not rerun.

The actual official ID2966 bytes at18730 are6f70120d, a no-linkrd0 transfer to40000. The reset186AA+134 relocation remains a genuine ROM UND in source partials. Strict linking without a real ROM definition must fail without an output. The final ADDRESS-WITNESS-ONLY assigns ABS40000 solely to inspect numerical addresses. It supplies no installed ROM body or physical provider proof.

Nine actual-ELF counterexamples cover fakeABS alias, missing weak binding, missingC allocation, missing caller link, wrong caller target, wrong callbackHI20, changed outside bytes, executable fill and fakeROM provider. Rejections must hit the intended semantic gate. Mutations stay under this review'sbuild/; producer artifacts remain untouched.

```sh
python -B ABI-review/check.py --project-root ROOT
python -B ABI-review/review.py --project-root ROOT --folder MODE --firmware FW --receipt NEW.json --controls
python -B ABI-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

Defaultcheck.py validates source and sealed metadata only; it does not read generated image archives or original firmware. Actual review requires an explicit folder and official firmware. Receipts are create-only outside the generation folder. Replay reads existing artifacts without compiling or rebuilding mutations. Prototype mode is diagnostic, not a selected formal admission. Shell wrappers acceptPYTHON.

Only the recorded caller route is proved; unknown computed entries may still reach the retained530B body. Physical S/SP/register contracts, escaping reply pointers, opaqueROM, IRQ/fault/asynchronous observations, Flash/NV ownership, installedBOOT, CRC/signature/recovery and OTA remain unproved. The matching return address is one checked projection. Numeric1AC00 placement does not establish21 free physical pages.

The seal contains source/result metadata only, excluding generatedbuild objects/ELFs/BINs. See selected.json and reference-pins.json for final evidence bindings.
