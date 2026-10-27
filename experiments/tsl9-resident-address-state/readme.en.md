# Initializer tail and six-byte state constructor

[繁體中文](README.md) · [Prior providers](../tsl9-resident-init-leaves/readme.en.md)

[C/C++](resident_address_state.c) supplies four complete bodies, **364 CODE bytes/129 instructions**. Actual C11/C++17 objects match:25 positive FUNC regions,21 relocations and every original-VA-normalized instruction byte. Register/control/call ports remain original;these are not recovered vendor C sources.

| Half-open body | Bytes/instructions | Confirmed instruction behavior |
| --- | --- | --- |
| 0x43E8E..0x43EB2 | 36/16 | 16-bit range with signed×unsigned high32 MULHSU,low16 result |
| 0x43EB2..0x43ED2 | 32/14 | 32-bit range with unsigned×unsigned high32 MULHU |
| 0x53868..0x5397C | 276/94 | Six-byte copy,candidate construction,masks,comparison and retry |
| 0x5E758..0x5E76C | 20/5 | Two zero stores followed by no-link tail to0x53868 |

Range helpers use the real prior0x433A8 provider. Do not substitute modulo or conflate MULHSU/MULHU. Own frames are32/32/32/0 bytes.

## Original execution chain and fields

Initializer0x537C6 releases its16-byte frame before0x537C8 tails to0x5E758. This tail clears a byte at0x20003480 and a word at0x20003484,then0x5E768 jumps without link to the constructor,preserving incomingRA/SP.

Actual far-call pair0x53888/0x5388C uses the real RAM0x20000332 copy provider:6 bytes from0x20003204 to0x200034A0. Primary candidate header bleConfig_t has size64,MacAddr offset24,size6,verified by C11/C++17 assertions. Provenance requires the prior config copy,matching ROM,valid stable memory,callee/IRQ/alias conditions. **No actual MAC contents or standalone hash were observed/published.**

| Half-open RAM field | Instruction evidence |
| --- | --- |
| [0x200034A0,0x200034A6) | Six-byte source copy |
| [0x200034AC,0x200034B2) | First candidate;0x538CA ORI −64 gives last-byte high bits11 |
| [0x200034B2,0x200034B8) | Second candidate;0x53926 ANDI63 gives last-byte high bits00 |

Fields are numerically disjoint and inside the prior296-byte state request. Reachable retry arm0x53966..0x5397C follows normalRET0x53964 and is retained. Range upper is0x3FFF,not4095.

Three halfword comparisons use candidate offsets250/252/254 versus copied232/234/236. Original signedLH values are masked before comparison. Mismatch at0x53934 or0x53944 returns early;only equality of all three at0x53954 retries. The second comparison does not dominate all returns. Original guards and short-circuit CFG remain.

**Retry termination,random distribution/entropy,global uniqueness,physical BLE address role and pairing effects remain unproved.** No live values observed;no guards removed based on algebraic assumptions.

## Verification and limits

[Compile-only assertions](address_abi.c) verify RV32 widths,primary config layout,field disjointness and own32-byte frame slots. C/C++ objects match with zero allocated bytes and no runtime provider.

Actual nonloadable ET_REL composition:**21,370 CODE+256 DATA/7,320 instructions**,1,375 positive FUNC regions,1,038 relocations. All input bytes/symbols/relocations retained,unique original-PC CODE ownership,two independent readers agree. One real prior dependency0x5E758 is supplied,**12→11 named dependencies**. Both current imports have real prior providers;no new named dependencies or stubs. Other indirect calls/memory effects remain open.

[Evidence](evidence-v1.json) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-address-state/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Requires pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. APP remains159 C/H files/95.54% byte coverage,**not functional completion**. The4-byte startup source gap,ROM/RAM/ISA/IRQ/Flash/OTA compatibility and no-dispatch-before-binding remain open.

No APP integration,BIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only field/mask/retry diagnostics remain an unimplemented feature candidate.
