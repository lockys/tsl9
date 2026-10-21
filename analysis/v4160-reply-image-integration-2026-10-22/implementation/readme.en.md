# Complete source image with twelve readable functions

[繁體中文](README.md)

This scope actually recompiles34 raw carriers and9 typed TUs into a76800-byte offline image containing12 readable functions/650 bytes. Reply's original NOTYPE0/local-entry0 remain as a zero-byte source boundary; the new FUNC124 is separate. No old role is promoted or replaced by an ABS provider.

`verify_image.py` performs compilation/linking and readonly replay. `reply.o` becomes `reply-ordered.o` through the explicit `reply-order.json` stage. `canonical53.ld` merges that native input section into its original owner. `pre-frame-integrated.o` already contains ordered reply code and is not labeled compiler-only; existing frame scheduling produces `source-integrated.o`. The two stages change28 and14 bytes by permuting newly compiled words only.

Actual C11/C++17 `NOT-FLASH-VALIDATED-reply-integrated.bin` outputs are76800 bytes with SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`: zero differences from original and the preceding eleven-function image. Original BIN, archived objects, padding and opcode templates do not generate code.

## Commands

```sh
python -B experiments/tsl9-v4160-reply-image-integration/verify.py --project-root . --tool-dir "$LLVM" --language both
python -B experiments/tsl9-v4160-reply-image-integration/verify.py --project-root . --replay RECEIPT
python -B analysis/v4160-reply-image-integration-2026-10-22/implementation/check_image.py --project-root .
```

Working cases use `apk-analysis/tsl9-` instead of `analysis/`. Default `check_image.py` checks sealed metadata only. `--require-local-builds` requires both selected actual archives; `--receipt FRESH` replays another fresh root's receipt. Main CLI also accepts `--firmware`, tool overrides and a create-only build root; replay rejects tool/build overrides. Shell wrappers preserve these options.

Each language has61 chronological commands,43 full `-MD` rules,74 observed project inputs,14 generated inputs and1 actual Clang resource header. Fourteen TUs include that header. Source/header/tool/proof/policy hashes are checked before/after use;9 IR files correspond to the typed TUs.

Gates preserve691 allocations,679 carriers,8257 outside RELAs plus12 typed JALs=8269,53 canonical relative bindings,21 incoming entries and11 discharged private branches. Actual9DF4 is a2-byte C.JAL with RA9DF6; relocation naming is not treated as the instruction's link semantics. Excluded `.llvm_addrsig` metadata explicitly retains the56-byte prefix plus the new actual symbol index; final ELF omits it.

All15 LOAD byte/memory/permission extents cover original ownership. Export has no holes, hidden padding, RAM or ROM bytes. Strict linking rejects missing resident ROM; the successful witness only declares numeric0x40000. Retained source carriers supply the actual original TX body.

Each language rejects41 actual controls:30 ELF/RELA/image,4 dependency,6 ordering JSON and1 chronology;5 readonly CLI cases also pass. `receipts/` publishes selected metadata, with real W archive paths/hashes in `results.json`. Objects, logs and controls stay in ignored local `build/` and are not implied published by metadata.

This remains partial readable reconstruction plus raw carriers. Resident ABI, arbitrary callee SP/GPR destruction, async/faults, computed interior entries, board, BLE, Flash and OTA compatibility are unproved. No RV32 execution, ISA emulation, network, packets or device I/O occurs. Actual tools are Windows NDK27.1.12297006; no other host platform is claimed tested.
