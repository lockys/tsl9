# Registered callbacks and candidate RF_Config

[繁體中文](README.md) · [Prior handlers](../tsl9-resident-dispatch-handlers/readme.en.md) · [Trap contract](../tsl9-trap-profile-contract/readme.en.md)

Five complete candidate bodies add **1546 bytes /540 instructions**:registration0x58EF2..0x58F14(34B,frame0),conditional registration0x60856..0x6089A(68B,frame16),callback0x58C52..0x58E7A(552B,frame64),callback0x60516..0x60754(574B,frame32),RF_Config0x64BAE..0x64CEC(318B,frame16 or no-frame rejection).

## Actual static provenance

Registration0x58EF2 writes0x58C52 toRAM0x200034F0 at0x58F0E. Registration0x60856 writes0x60516 toRAM0x200034F8 at0x60892. Each store dominates its body's local normal return and both registered callbacks now have complete real bodies. Actual initialization reachability/order is unproved. Two additional CODE values0x57CBE/0x5E8BC are written to0x20003450/0x2000343C;their bodies remain unavailable.

After releasing its64-byte frame,callback0x58C52 tail-jumps from0x58D3C to prior0x57DAE. Callback0x60516 releases32 bytes before tail0x605E0 to0x6020A. AUIPC-T1/JALR-zero at0x60738 also tails to real setter0x2000078A. **The link register iszero;do not rewrite this as an ordinary call or overwriteRA.** Nine actual HI/LO pairs comprise eight calls and one tail,with opcode/register bits verified.

The pinned official header assignsRF_Config index100;carrier word0x401C4 points to0x64BAE. It reads caller callback field+16;zero takes a no-frame rejection return. Other paths may reject too. On paths reaching configuration copy,it zeroes32 bytes atglobal0x20003540 then copies32 caller bytes there. Compiling the actual primaryrfConfig_t declaration inRV32 C11/C++17 gives size32,alignment4,rfStatusCB offset16,structurally locating the shared callback at0x20003550.

This is conditional provenance:caller memory must be valid and not overlap the global region cleared first,and callee memory/register contracts must hold. Actual supplied callback value,originalAPP use and installedROM/ABI identity remain unproved. Header/table correspondence is not a physical connection test.

## Verification and limits

Entry CFGs reach every body instruction. Frames balance at all normal returns and typed tails,including the no-frame RF rejection path. C11/C++17 objects are identical;all1546 original-context bytes match. All52 official Xwchc positive vectors and39 actual operations are checked. The145 positive FUNC regions are compiler fragments,not145 logical functions.

The nonloadable composition retains **12272 CODE+256 DATA bytes /4291 instructions**,1010 FUNC regions,oneOBJECT and753 relocations. Complete input bytes/symbols/relocations and independent ELF readers agree. Following the newly identified callbacks exposes **11 genuine unavailable callees**;11 prior real providers are reused,without stubs or ABS functions. Three opaque calls,two additional numeric CODE bodies and other RAM/descriptor dependencies remain open.

APP byte coverage stays95.54%;newAPP CODE=0. The inherited4-byte startup gap,ROM/RAM/ISA,GP/IRQ/frame/aliasing,Flash andOTA remain open. No hardware,HOST model or ISA execution,vendor API traffic,APP integration or newBIN. **Usable replacement firmware has not been successfully reverse engineered.** Configuration/callback provenance diagnostics remain an unimplemented UI candidate.

[Audit](audit-result-v2.json) · [Summary](summary.json) · [Original instructions/provenance](evidence-v1.json) · [C/C++](resident_callback_registration.c) · [Primary ABI assertions](config_abi.c)

## Reproduce

Provide the pinned originalAPP,SDK/instruction references,prior native artifacts and the trap contract's saved official headers. Missing inputs are not downloaded.

```sh
python experiments/tsl9-resident-callback-registration/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v2
python experiments/tsl9-resident-callback-registration/audit-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v2
```

Use fresh trial names. For retained artifacts,use `--replay experiments/tsl9-resident-callback-registration/build/native-v2` in the first command and omit `--link-trial` in the second. Tool hashes pin Windows NDK LLVM;cross-platform compilation is unverified.
