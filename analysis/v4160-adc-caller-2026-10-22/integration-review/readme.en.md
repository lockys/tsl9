# Independent ADC caller-injection review

[繁體中文](README.md) | [English](readme.en.md)

This scope reads already-built C/C++ integration artifacts. It does not call the integration producer's inspect/replay as its judgment, relink, or generate a BIN. A separate bounded `struct` ELF32 reader checks headers, sections, symbols, RELA and program headers. JAL immediate/register fields are independently calculated and cross-checked with the previous typed decoder and complete actual LLVM disassembly. The sealed ABI artifact receipt is reread to bind the linked110 B to the genuine reviewed C function.

Actual C/C++ candidates match:78,848 B, SHA256 `ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`. The existing77,824 B experimental baseline has SHA256 `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`. Its entire preimage is preserved except the four caller bytes at `0x19896`, which originally still match ID2966's JAL to `0x1892E`.

Actual assembler `call_site.o` has one `R_RISCV_JAL` type17 relocation referencing the real undefined `tsl9_adc_config_1892e` symbol. The native ET_REL genuinely defines that FUNC; no numerical provider is supplied. The final four-byte JAL targets `0x1B000`, displacement `0x176A`, retaining RA=`0x1989A`. Review separately verifies symbolic JAL/norelax/norvc source, two RX owners in the linker script, exact actual commands, tool hashes, successful logs and source pins.

The linked ELF has only executable allocations `.caller` (`0x19896`,4 B) and `.adc` (`0x1B000`,110 B). Each RX LOAD exactly matches its section's file offset/address/file and memory extent. No runtime hole, headers, page padding or allocated NOBITS exists. UND0/RELA0/ABS0 hold. Non-LOAD container layout bytes are not packed into the runtime page. The only retained FUNC is genuine C110; four other real native globals are actually removed by GC, while their original five-function object remains covered by the previous review.

Baseline `0x8000+77824=0x1B000`; one1024-byte page is appended:110 actual C bytes and914 explicit FF tail bytes. The preimage/caller/C/tail are compared byte-for-byte without modifying the original baseline file. Raw BIN encodes no execute permissions; ELF RX boundaries do not establish hardware protection.

Seven in-memory controls reject per artifact: caller RA, target, section size, hidden LOAD memory hole, inherited preimage, C payload and FF tail. No mutant BIN is written and no CPU/MMIO/ISA/ESIL execution occurs.

The candidate inherits the earlier OTA C568, original carriers and `0x40000` ROM address-witness limitations. The new ELF's clean UND/ABS inventory does not implement the whole raw image's ROM providers. This scope proves only the new ADC caller injection, not whole-image provenance or a complete source rewrite. Conditional normal caller projection still requires a valid private144-byte stack, no alias/async interference, unobserved private-frame residue and normal polling completion. Full callee ABI, fault/IRQ, Flash/NV ownership, physical ROM/BOOT/chip, BLE OTA acceptance and recovery remain unproved. The candidate stays **NOT-FLASH-VALIDATED**.

Metadata only: `check.py --project-root ROOT`. Actual review: `check.py --project-root ROOT --integration-receipt BUILDER/c/verification.json --receipt NEW.json`; read-only artifact replay: `--replay NEW.json`. Receipts are create-only. W `apk-analysis/tsl9-*` and D/P `analysis/*` layouts are supported. `linked=false` and `BIN_generated=false` describe this reviewer's actions; `actual_linked_ELF_read=true` and `candidate_BIN_read=true` identify the existing artifacts read.

No new HOST matrix, hardware, network or Git Bash retry occurs. Shell runtime remains unverified. Authored text uses LF/single EOF; default README equals Traditional Chinese, with separate English.
