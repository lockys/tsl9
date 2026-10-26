# Two previously missing handlers and real register providers

[繁體中文](README.md) · [Existing LLE / ECALL](../tsl9-resident-lle-callback-gateway/readme.en.md) · [Trap contract](../tsl9-trap-profile-contract/readme.en.md)

Four complete candidate bodies add **1118 bytes /384 instructions**. Functions0x57DAE/0x6020A provide the exact previously undefined names with real CODE,no stubs or ABS function providers.

| Body | Original range,end exclusive | Bytes /own frame |
| --- | --- | ---: |
| Previous missing handler | Flash0x57DAE..0x57EEA | 316 /32 |
| Previous missing handler | Flash0x6020A..0x60350 | 326 /32 |
| Register provider | Flash0x63C54..0x63D6A | 278 /0 |
| Register provider | Flash0x63EDA..0x63FA0 | 198 /16 |

Each entry CFG reaches every body instruction;own frames balance at all local normal returns. The first RET is not an endpoint:handler branches jump back from0x57EE8/0x6034E to earlier shared cleanup. Following independent16-byte-frame entries are excluded. Provider arms following an earlier RET are retained too.

## Evidence and remaining unknowns

Both handlers inspect shared state+7/+9 and conditionally store halfwords0x0107/0x0106 atstate+8. Deferred-state handling is an inference;packet and product-feature semantics remain unproved.

Two actual AUIPC/JALR pairs call the real prior setter0x2000078A. A zero flag at0x20003240 leaves the0x57DAE setter call active withA0=0;the0x6020A path skips that call. Nonzero paths loadA0 fromRAM words0x200034F0/0x200034F8. Those raw callback targets remain unavailable regardless of linker UND counts.

Provider0x63C54 checks descriptor word0x2000350C before two pointed-word updates through internal pointers. Capacity,pointer validity and register identity are unproved. Provider0x63EDA reads,clears and writes back candidate hardware word0x4002420C before every local normal return,with an interveningFENCE.I. Correct savedS2 requires callee preservation and no aliasing;IRQ atomicity or mask semantics are not proved.

An actual state-conditioned opaque call at0x63F26 usesRAM pointer0x20003550 withA0=17,A1=A2=0. It has no pointer null guard and its effects remain open.

## Actual verification

C11/C++17 objects are identical;all1118 original-context bytes match. All52 official Xwchc positive vectors and29 actual conditional operations are checked. The65 positive FUNC regions are compiler fragments,not65 logical functions.

The nonloadable composition retains **10726 CODE+256 DATA bytes /3751 instructions**,865 FUNC regions,oneOBJECT and629 relocations. Two independent ELF readers and complete input byte/symbol/relocation comparisons pass. **This partial composition has zero namedUND**;that does not close all ROM,callback,private-ABI or execution dependencies. Prior real bodies and trap contracts are retained.

APP byte coverage stays95.54%;newAPP CODE=0. PhysicalROM/RAM/ISA,GP/frame/IRQ/aliasing,the inherited4-byte startup source gap,Flash andOTA remain open. No hardware,HOST model or ISA execution,vendor API traffic,APP integration or newBIN. **Usable replacement firmware has not been successfully reverse engineered.** Deferred-state/callback-source diagnostics remain an unimplemented feature candidate.

[Audit receipt](audit-result-v1.json) · [Summary](summary.json) · [Original instructions](evidence-v1.json) · [C/C++](resident_dispatch_handlers.c)

## Reproduce

Provide pinned originalAPP,SDK/instruction references,prior native artifacts and the trap contract's saved official headers. Missing inputs are not downloaded.

```sh
python experiments/tsl9-resident-dispatch-handlers/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-dispatch-handlers/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1
```

Use fresh trial names. For retained artifacts,use `--replay experiments/tsl9-resident-dispatch-handlers/build/native-v1` in the first command and omit `--link-trial` in the second. Tool hashes pin Windows NDK LLVM;cross-platform compilation is unverified.
