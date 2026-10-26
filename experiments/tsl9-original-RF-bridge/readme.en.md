# Original APP / candidate RF execution bridge

[繁體中文](README.md) · [RF_Config / callbacks](../tsl9-resident-callback-registration/readme.en.md) · [Trap contract](../tsl9-trap-profile-contract/readme.en.md)

This study prioritizes actual APP use and adds **664 bytes /216 instructions in four complete candidate SDK bodies**:RF_RoleInit0x66056..0x66098(66B,frame16),common reset0x641B0..0x64298(232B,frame32),register initialization0x64298..0x6430E(118B,frame16),registered RF task0x65920..0x65A18(248B,frame16).

## Actual APP evidence

In complete original initialization0x8E88..0x9008,theS0+448 load0x8EBE and indirect call0x8EC2 dominate the constructor call0x8FDC in its normal-return CFG. The originalS0 base0x40000 gives slot0x401C0. Candidate SDK data points to0x66056;the pinned header labels thisRF_RoleInit/index99.

Constructor0x175E8..0x17666 allocates48 bytes and prepares32 configuration bytes atSP+0..31. SavedS1/S0/RA atSP+36/+40/+44 do not overlap. AUIPC/ADDI0x17644 forms callback **0x174EE**,stored atSP+16 at0x1764C. TheS0+452 load0x17654 andA0=SP call0x1765A use slot0x401C4,candidateRF_Config/index100.

All586 APP reference bytes from initialization,constructor and status callback match both the originalBIN and existing compiled original-address diagnosticELF. NoAPP CODE is added or modified. The previous unknown caller value is narrowed to **the original APP explicitly preparing0x174EE**. Actual propagation into global0x20003550 still requires matching installedROM,callee contracts and valid nonoverlapping stack/global memory. Static slot correspondence is not physical API identity.

## Initialization and callback

RF_RoleInit calls0x64298,zeroes36 bytes atcandidate context0x20003560,passes real task callback0x65920 to existingevent-register0x43C4E and stores its returned ID byte at0x20003570. Initialization0x64298 releases its16-byte frame before tailing to0x641B0;do not treat this as an ordinary call retaining that frame.

Actual pointer stores mapRAM0x20003504/0x2000353C/0x20003590/0x20003508 to0x40024300/0x40024200/0x40025000/0x40024100. These are original stores,not proof that values survive unknown callees or asynchronous effects,or that physical register identity/ownership matches. Complete ordering of other internal callback registrations remains open.

Original frameless callback0x174EE checksA1 onstatus2 then readsA2+1/+2/+3 against storage0x2000C7AA/0x2000C7AB. That path requires at least4 readable buffer bytes;there is no null/length guard. Preserve the full other-status predicate:after excludingA0==2,A0>=2 andlow8(A0-17)<=1 tail to0x17442. Matching packet bytes tail to0x173EE withA0=0. Full protocol/byte meaning and buffer validity remain unproved. Independent PC-relative decoding givesAPP context0x2000C7A0;this is not an execution observation.

## Verification and limits

Actual C11/C++17 objects are identical;all664 original-context bytes match. All52 primary Xwchc positive vectors and12 actual operations are checked. Frames balance at every local normal return and tail. The43 positive FUNC regions are compiler fragments,not43 logical functions.

The nonloadable composition contains **12936 CODE+256 DATA bytes /4507 instructions**,1053 FUNC regions,oneOBJECT and790 relocations. Complete input byte/symbol/relocation and independent ELF comparisons pass. The prior11 plus8 new unavailable callees leave **19 genuine named dependencies**. APP andSDK are not integrated into a newBIN.

FormalAPP coverage stays95.54% with159C/H files. The inherited4-byte startup source gap,ROM/RAM/ISA,GP/IRQ/frame/aliasing,Flash andOTA remain open. No target,HOST model or ISA execution,hardware access or vendor API traffic. **Usable replacement firmware has not been successfully reverse engineered.** RF initialization/status/callback provenance diagnostics remain an unimplemented UI candidate.

[Audit](audit-result-v2.json) · [Summary](summary.json) · [Original APP / SDK instructions](evidence-v1.json) · [C/C++](original_RF_bridge.c)

## Reproduce

Provide pinned originalAPP,SDK/instruction references,prior native artifacts,the existing original-address diagnosticELF and the trap contract's local official headers. Missing inputs are not downloaded.

```sh
python experiments/tsl9-original-RF-bridge/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v2
python experiments/tsl9-original-RF-bridge/audit-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1
```

Use fresh trial names. For retained artifacts,use `--replay experiments/tsl9-original-RF-bridge/build/native-v2` in the first command and omit `--link-trial` in the second. Historical native-v1 is retained;current positive evidence uses corrected metadata/native-v2. Tool hashes pin Windows NDK LLVM;cross-platform compilation is unverified.
