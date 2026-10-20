# Independent final candidate artifact review

Result: **PASS for the admitted experimental static artifact contract. No blocking artifact finding.** This review parsed the actual C and C++ ELF files using a newly written Python standard-library ELF32 parser, decoded RISC-V numerical references directly, reconstructed Flash payloads from sections, and compared bytes and hashes. It did not import or run the candidate/core audit code, build anything, execute/emulate a target, access hardware/network, or modify re-tsl9. New review files are confined to this directory.

Actual reviewed builds:

- C: `experiments/tsl9-ch32v208-candidate/build/c/9d67b31c0a504ab7835d26e94b1d6802`
- C++: `experiments/tsl9-ch32v208-candidate/build/cpp/4a468349eb29421caee467369d4d45fe`

Both BINs have 76800 bytes and SHA256 `32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc`. Every Flash section's actual linked bytes match its original source offset. Independently concatenating their sorted payloads yields exactly the objcopy BIN and retained original Runtime. The entire modeled span `[0x8000,0x1AC00)` is explicitly covered with no padding gaps.

| Check | Independently observed result in both builds |
|---|---|
| ELF identity | ELF32 little endian, ET_EXEC, RISC-V machine243, flags1, entry0x8000 |
| Resolution | Zero named UND; zero REL/RELA sections |
| Flash sections | 692 contiguous PROGBITS sections: 667 core sections76447B plus25 carrier sections353B |
| Runtime segment | PT_LOAD R+X, VMA=LMA0x8000, file/memory size76800B |
| RAM segment | PT_LOAD R+W, VMA=LMA0x20004000, file size0B, memory size35152B |
| RAM section | One NOBITS section35152B, excluded from BIN file payload |
| Attributes | One separate PT_RISCV_ATTRIBUTES header; `.riscv.attributes` is nonallocated and not PT_LOAD |
| Initializer | One physical136B initializer at0x1A7E0, within the2204B union at0x1A2D0; RAM destination0x20004000 |
| ABS assumptions | Exactly two added global ABS/NOTYPE/size0 symbols: ROM0x40000 and opaque lookup0x19D10; the separate existing SP ABS remains0x20010000 |
| Defined core symbols | All allocated defined core symbols preserve numerical section-relative value, type and size; hidden aliases may be localized by final linking |

The final C ELF SHA256 is `3f6d6247efb817929cffb026f7edf7a125579fe99b3ca8ef018fe637657fb947`; C++ ELF SHA256 is `43466ef03bd09c9613ff4840684c502b11adc6d5cc9acbe8c8cd7e2d89567fc7`. Their ELF metadata differ while their complete Flash/BIN payloads agree.

Direct numeric instruction decoding confirmed these original contracts: image entry0x8000 JAL x0→0x183FE; GP0x20004000; SP0x20010000; initializer source0x1A7E0; two explicit GP+136 initialization boundaries; BSS end0x2000C950; vector base0x8038; clock call0x18474 JAL ra→0x1849E; mepc0x8FE6; ROM tail0x18484 JAL x0→0x40000. The lookup reference at0xCDAC decodes to0x19D10. Five reset CSR writes and operand registers were also checked. The entire final reset section matches the retained original bytes, including copy/zero loop instructions. The ROM tail does not write a return address to0x18488.

The core object is reused, SHA256 `e60e2df377b398c564e18203de2669da62cb8745309eeb29061aa1c17ff04eab`. Each language path retains98 source hash guards (19 active experiment plus79 baseline entries), all independently rehashed. This candidate build records fresh C/C++ compilation of the353B carrier; carrier ELF sections also match the final/original bytes. The reviewer did not recompile. The preserved product manifest describes292 model inputs and480 files, which is a different accounting boundary; all480 listed file sizes/hashes were independently verified unchanged. Do not describe292 inputs as freshly compiled this round.

Both existing core objects still have exactly the two original unresolved symbols, and both old strict failure logs still contain exactly those two diagnostics with their retained hashes. Neither old strict checks nor prior seals were changed by this review.

The final delivery at `candidate-bin/ch32v208-2026-10-20` was also checked: BIN, ELF, map, README and SCOPE are exact copies of the declared sources. Its BIN/ELF/map come from the reviewed C++ build. Manifest hashes for both build receipts and both old original manifests agree with disk. Its source counts correctly report98 per language, and its limits remain explicit.

No new high-level semantics or features are established by a byte-identical reconstruction. Opaque/native-assembly core representations and original carrier bytes remain distinguishable in the records; these artifacts do not demonstrate full high-level C/C++ recovery. The two ABS bindings are external-address assumptions, not ROM or table providers. The missing272B lookup tail, BLE/ROM ABI, actual MCU/PCB/crystal identity, physical RAM/stack/IRQ behavior, BOOT/ROOT/ROM supply, and hardware/OTA acceptance remain unproved. `target_ready=false`, `ota_verified=false`, `goal_complete=false` remain required.

Reproducibility/evidence files:

- `independent-review.py`: self-contained ELF/parser/hash/numeric checks; writes a new `review.json` only and refuses to overwrite it.
- `review.json`: detailed per-language observed values and pass receipt.
- `verify-delivery.py`: independent delivery identity and claim-boundary check; writes a new `delivery-review.json` only.
- `delivery-review.json`: five exact-copy identities and receipt/manifest checks.

The first parser draft assumed all global hidden aliases stay global in a final ELF. Actual inspection showed the linker localizes such aliases; the checker was corrected to verify unique name/value/type/size across all symbols. This was a reviewer-checker adjustment, with no target artifact change. The completed independent checks then passed.
