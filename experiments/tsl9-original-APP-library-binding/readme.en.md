# Original APP callbacks and local IRQ ordering

[繁體中文](README.md) · [RF task/sampling](../tsl9-original-RF-task-path/readme.en.md) · [CPU-store contract](../tsl9-tscb-store-contract/readme.en.md) · [Trap contract](../tsl9-trap-profile-contract/readme.en.md)

This study adds cross-APP/SDK configuration and ordering evidence. **No target code is added or recompiled.** Six complete APP reference functions,totaling **2,136 bytes /697 instructions**,match the original BIN and retained C/C++ original-address diagnostic ELFs byte-for-byte. Two independent ELF readers agree.

## Concrete callback literals

Initializer0x199E2 allocates96 bytes and builds64 configuration bytes atSP+16,disjoint from savedS0/RA atSP+88/+92:

| Field | Original literal | Store PC /caller stack |
| --- | --- | --- |
| tsCB,config+44 | 0x197F0 | 0x19A9E /SP+60 |
| rcCB,config+48 | 0x197B8 | 0x19AB2 /SP+64 |

Both stores dominate the library call0x19AEC in its complete normal-return CFG. The original APP explicitly prepares nonnull callbacks. The six-byte MAC helper/copy avoids both fields;no physical MAC/UID values were read.

Candidate slot0x400A4 points to BLE_LibInit0x43C7E. After zero/copy64 into0x200031EC,call0x43D38 reads tsCB at+44 and stores its result halfword at baseline0x200031A4. The monitor0x43EDC reads the same tsCB/rcCB words. **Matching installed ROM,completed copy64,valid nonoverlapping memory and callee/IRQ/alias contracts** conditionally connect these calls to existing APP C/C++. Live pointers remain unobserved;opaque-call effects are not fully closed.

rcCB0x197B8 tails withA0=3 and no own frame to existing calibration worker0x1929A..0x196C4. Its own frame is80 bytes. Signed DIV,polling and RMW remain original;calibration convergence and whole-program stack budget are unproved.

## tsCB result width

Callback0x197F0..0x1995C calls ADC candidate helper0x18A66 at0x198DC. Actual **C.SLLI16/C.SRLI16** instructions select low16 bits,stored at ownSP+28 at0x198E0,loaded at0x1991E and moved intoA0 at0x19948.

The call/save/load/move dominate normal return;that own-frame word has one explicit store. The complete14-function CPU-store contract is freshly verified. Under its valid-memory,normal-return,nonalias and no-asynchronous-overwrite conditions,the original callback returns0..65535. This narrows the prior uint16_t ABI provenance condition;**it does not prove Celsius units,physical ADC identity or calibration success**.

## Version and IRQ boundaries

The APP compares only the21-byte prefix `CH32V20x_BLE_LIB_V1.3`. The candidate version pointer is0x6E6A0 and comparator RAM0x20000442 has a retained real body. Prefixes match,but this does not distinguish complete library versions or chip variants,or identify the installed ROM. Valid pointers/comparator contracts remain required.

At0x199EC,the APP copies word0x20000008 into incomingGP+384. With resetGP0x20004000 preserved,this is the LLE-wrapper word0x20004180. The assignment dominates every external call in this function and both direct enable-store sites:

- 0x19B08 writes0x80000000 to0xE000E104,numerically corresponding to candidateIRQ63.
- 0x19B0E writes1 to0xE000E108,numerically corresponding to candidateIRQ64.

The original main CFG calls this initializer before RF_RoleInit/the RF constructor. **A correct nonzero slot2 value,stableGP/unmodified callback word,and ordering before every possible global dispatch remain unproved.** Earlier IRQ state,callee/DMA/alias effects and physical vector mode remain unknown. This establishes local encoded order,not physical startup success.

## Use and status

[Existing startup C/C++](../../src/native/startup/resident_startup.c) · [Peripheral C/C++](../../src/native/startup/peripheral_primitives.c) · [Evidence](evidence-v1.json) · [Verification](verification-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-original-APP-library-binding/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned local originalBIN,native artifacts,Windows NDK LLVM and official headers. Missing inputs are not downloaded. Cross-platform verification is unconfirmed.

APP remains159 C/H files and95.54% byte coverage. The SDK composition stays20,112 CODE+256 DATA with11 genuine unavailable named dependencies. No newBIN,APP integration,target/HOST-model/ISA execution or hardware access. The4-byte startup source gap,ROM/RAM/ISA/IRQ,stack/aliasing,callbacks,Flash/OTA remain open. **Usable replacement firmware has not been successfully reconstructed.** Startup configuration provenance/compatibility evidence display remains an unimplemented read-only UI candidate.
