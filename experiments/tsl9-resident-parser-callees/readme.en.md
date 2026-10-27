# Parser callees,mapped RAM helpers and message builders

[繁體中文](README.md) · [Complete caller parser](../tsl9-resident-task-parser/readme.en.md) · [Retained callback conditions](../tsl9-original-callback-provenance/readme.en.md)

[C/C++](resident_parser_callees.c) adds **16 complete bodies/2,492 CODE bytes/940 instructions**. Actual C11/C++17 objects match:191 positive FUNC regions,174 relocations(126 direct controls+24 HI/LO pairs),every original-VA-normalized byte equal.92 Xwchc ports use primary encoding definitions/52 official positive vectors. Original-context reconstruction,not recovered vendor C sources.

Supplies four actual parser gaps0x5E950/0x5EA9A/0x5EACA/0x5EE06 atcalls0x5F37C/0x5F512/0x5F88A/0x5F93C,plus necessary0x5ECF6/0x5E4B0,two tail entries,two builders and six RAM bodies. Uncalled neighboring functions are excluded.

## ROM source versus execution address

| Half-open execution range | Half-open candidate ROM source | Bytes |
| --- | --- | --- |
| 0x2000202C..0x20002078 | 0x4229C..0x422E8 | 76 |
| 0x20002078..0x200020B6 | 0x422E8..0x42326 | 62 |
| 0x200020B6..0x200020F4 | 0x42326..0x42364 | 62 |
| 0x200020F4..0x2000218A | 0x42364..0x423FA | 150 |
| 0x20002276..0x200022BE | 0x424E6..0x4252E | 72 |
| 0x200022BE..0x20002426 | 0x4252E..0x42696 | 360 |

All six bodies,total782 bytes,fit the retained first loader copy:source0x402B0,destination0x20000040,last destination word **inclusive0x20002E70**,11,828 bytes,exclusive end0x20002E74. Branches and two RAM-to-ROM HI/LO calls use actual execution PCs. ROM copies are not treated as execution addresses. **Candidate loader mapping does not prove installed ROM identity or physical RAM compatibility.**

## Original flow and widths

All16 CFGs are reachable with balanced own frames at normal exits. Reachable post-RET arms and real tails remain.0x6A730/0x6A796 are each4-byte no-link tails to0x52418/0x527FA;adjacent wrappers excluded.

Lookup roots fresh-read list heads0x20003484/0x2000347C. Numeric addresses also match earlier initializer word-zero requests,but **live lists/nodes,termination and alias safety are unproved**. Original comparisons and traversal remain,without added limits.

0x5EA9A reads record+84 as a byte gate and later a word argument,plusrecord+88 word. Original SNEZ/literal1 paths give conditional normal-return range0..1. Early returns allocate no frame;call path own frame16. Widths/control paths are not merged into a guessed struct.

0x200022BE loads base pointer0x20003504 and retains ordered base+0 word requests256 then0,plus all subsequent original accesses. No callee/own frame. Reachable post-RET NOP0x20002422 and jump0x20002424→0x200023AC remain. **Physical peripheral/operation meaning and retry termination remain unknown.**

## Message requests and open bounds

Both builders have own frame48,use the real prior allocator,retain null restore/RET versus nonnull copies,release the frame then tail to prior send0x43208:

| Builder | Request | Original copy requests |
| --- | --- | --- |
| 0x52418..0x524B0 | 49 bytes | allocation+10/6 bytes;+17/full32 incomingA3 length;final byte+48 store |
| 0x527FA..0x528B6 | 24 bytes | body=allocation+8;body+2/6 andbody+9/6 bytes;stride16 |

First builder stores low8 length atallocation+16 but copies full32 incomingA3. **Not every caller length bound is proved.** Numerically17+32=49;length32 includes byte+48,which the original writes afterward. No added clamp,padding or reordered writes.

Second builder header word0x010B3E91 encodes byte3 count1,but the loop retains fresh byte reads. A single16-byte body iteration requires stable header,valid memory/copy/private-callee contracts and no asynchronous alias. **The loop is not replaced with one constant iteration;no live heap safety or delivery proof.**

## Composition and use

[Compile-only assertions](callees_abi.c) check RV32 widths,source mapping,frame slots and numeric requests. C/C++ objects match,zero allocated bytes,no runtime provider.

Actual nonloadable ET_REL composition:**27,594 CODE+256 DATA/9,520 instructions**,1,821 positive FUNC regions,1,423 relocations. Every input byte/symbol/relocation retained,unique original-PC CODE ownership,two independent readers agree. Four real prior providers reduce named gaps **11→7**. Seven imports have real prior bodies,no new named gap/stub/opaque call. Numeric CODE pointers,callbacks,memory/IRQ effects remain open. Prior conditional callback proof is freshly verified,unchanged.

[Evidence](evidence-v1.json) · [Full audit](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-parser-callees/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Requires pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. APP stays159 C/H files/95.54% byte coverage,**not functional completion**. The4-byte startup source gap and ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain open.

No APP integration,BIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only lookup/source-map/copy-bound diagnostics remain an unimplemented UI candidate,no live record/key/MAC disclosure or live-state changes.
