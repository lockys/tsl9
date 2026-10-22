# C/C++ reconstruction of conditional resident memory leaves

[繁體中文](README.md)

This round reconstructs three conditional candidate algorithms in readable C11/C++17: compare each byte to one value, fill, and forward byte copy. A typed IO port preserves the MMIO save, zero and FENCE.I prefix before argument checks, and the restore on normal completion. **These components are not installed-ROM replacements. There is no new BIN; the existing 550-byte OTA experiment and existing experimental image are unchanged.**

[C/C++ source and reproduction](../../experiments/tsl9-resident-memory-leaves/README.md) | [Compilation and tests](implementation/README.md) | [Independent model review](model-review/README.md)

| Candidate RAM address | Complete reference body | Normal semantics |
| --- | --- | --- |
| 0x200004BC | 62 bytes / 19 instructions | Fresh byte loads compare against full32-bit A1. All matching bytes return1; null/count0 return0. |
| 0x2000039C | 46 bytes / 14 instructions | Stores low8 bits and returns the advanced destination. Null/count0 skip the byte loop. |
| 0x20000332 | 58 bytes / 18 instructions | Fresh source load precedes destination store; returns the original destination. Forward overlap can feed prior writes into subsequent reads. |

All three still perform their MMIO prefix on null/count0. They are not interchangeable libc operations. A failed or nonreturning IO observation retains its completed prefix without inventing cleanup or a successful return.

[Pre-copy verification](precopy-review/README.md) binds actual caller arguments config+24,255,6. An all-FF MAC takes the rejection branch. The complete leaf has no nested call, explicit S1/SP/S/GP/RA destination or configuration write. Under the stated mapping, valid-memory, normal-access, no adverse alias and no asynchronous-modification premises, this extends the prior conditional App staCB-zero derivation through the configuration copy, without identifying an installed value.

[Continuation verification](continuation-review/README.md) reads both complete228-byte/92-instruction initializer bodies. Eight post-copy default stores miss config+52..55. The first subsequent indirect call freshly reads config+44; the original App's source for that pointer is **0x197F0**. That callback's ADC/MMIO/nested-call effects and a later direct initialization call remain unresolved. Neither initialization-wide nor runtime callback-zero lifetime is claimed.

Metadata defaults are separate from explicit retained-source reads. Each scope documents inputs, tools and receipts. Authored HOST tests run27 cases/219 checks per language; independent HOST tests run16 narratives/940 assertions per language. Each suite rejects three actually compiled semantic controls per language. These execute only authored C/C++ with synthetic IO.

Native C/C++ compare, fill and copy functions are146/138/160 bytes, plus a genuine86-byte local C begin helper, totaling530 bytes/218 instructions. The original three reference leaves total166 bytes/51 instructions and are frameless. The new components use a context/structure-return ABI and are not in-place replacements. Native compilation produces objects and IR without RV32 execution. This530-byte sum is unrelated to the OTA handler's size.

Native objects retain genuine unresolved IO symbols. There is no numeric fake provider, link/BIN, hardware IO or vendor-service request. Fixed Windows LLVM measurements do not validate other native hosts; Python/POSIX shell entries remain portable, with no new PowerShell script.

Physical board/installed ROM/BOOT identity, complete original register/stack/IRQ ABI, physical MMIO effects, Flash/NV ownership and OTA acceptance/recovery remain unproved. A useful proposed offline configuration diagnostic could show an all-FF MAC, missing paired read/write callbacks when SNV is enabled, and defaults that zero-valued fields would receive. This could extend the pre-update ROM/NV precondition summary, separating conditional deductions from measurements. It remains a proposal, is not an installed feature, and cannot certify a flashable image.
