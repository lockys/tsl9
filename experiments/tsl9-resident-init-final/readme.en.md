# Complete the initializer external direct-target bodies

[繁體中文](README.md) · [Prior state constructor](../tsl9-resident-address-state/readme.en.md) · [Original initializer](../tsl9-resident-init-5362e/readme.en.md)

[C/C++](resident_init_final.c) adds two complete bodies, **38 CODE bytes/11 instructions**. Actual C11/C++17 objects match:2 positive FUNC regions,2 HI/LO relocations,every original-VA-normalized byte equal to candidate SDK bytes. These are not recovered vendor C sources.

| Complete half-open range | Bytes/instructions | Original effect |
| --- | --- | --- |
| 0x57AC4..0x57AD8 | 20/6 | A0=0x20003454,A1=0,A2=28;tail to RAM0x2000039C memset provider |
| 0x63704..0x63716 | 18/5 | Word zero to0x2000347C;byte zero to0x20003478;RET |

Both own frames are zero,no new CSR requests or opaque calls. Actual AUIPC t1/JALR zero,t1 at0x57AD0/0x57AD4 is a **no-link tail**,not replaced with a normal C call. New-body instruction relations preserve incoming SP/GP/RA/saved registers. Normal return still requires the original memset contract,valid memory,matching ROM/callee/IRQ/alias conditions.

The28-byte request is [0x20003454,0x20003470). Other requests are [0x2000347C,0x20003480) and [0x20003478,0x20003479). All lie inside the previous296-byte state request [0x200033B8,0x200034E0). **No additional physical RAM capacity or final-all-zero state proof.** Adjacent0x57AD8/0x63716 functions are excluded.

## Complete caller direct-target inventory

Original calls0x537B6/0x537BA use these providers.0x537C6 releases the16-byte frame before0x537C8 tails to prior0x5E758. Independent decoding of the complete caller gives all external direct targets:

0x43E24,0x55BD4,0x55C48,0x57AC4,0x63704,0x64298,0x5E758.

The audit checks each complete-body evidence,all bytes supplied by actual providers and equality with the entire caller target set. **All seven direct roots have complete bodies.** Recursive/indirect calls,callbacks,memory effects,asynchronous IRQ behavior and initialization success remain open.

[Compile-only assertions](init_final_abi.c) verify RV32 widths,numeric addresses and request bounds. Actual C11/C++17 objects match,zero allocated bytes,no runtime provider.

## Composition and use

Actual nonloadable ET_REL composition:**21,408 CODE+256 DATA/7,331 instructions**,1,377 positive FUNC regions,1,040 relocations. Two real missing providers lower named dependencies **11→9**. The memset import has a real prior provider;no new named dependencies or stubs. All input bytes/symbols/relocations retained,unique original-PC CODE ownership,two independent readers agree.

[Evidence](evidence-v1.json) · [Full audit](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-init-final/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Requires pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. APP stays159 C/H files/95.54% byte coverage,**not functional completion**. The4-byte startup source gap,physical ROM/RAM/ISA/IRQ/Flash/OTA compatibility and no-dispatch-before-binding remain open.

No APP integration,BIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only initializer coverage/zero-request diagnostics remain an unimplemented feature candidate;static coverage does not prove initialization success.
