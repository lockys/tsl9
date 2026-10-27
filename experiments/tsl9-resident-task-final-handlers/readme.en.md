# Remaining task0x60516 handlers and scheduler index banks

[繁體中文](README.md) · [Prior callees/RAM mapping](../tsl9-resident-parser-callees/readme.en.md) · [Original task](../tsl9-resident-callback-registration/readme.en.md)

[C/C++](resident_task_final_handlers.c) adds **five complete bodies/2,254 CODE bytes/801 instructions**. Actual C11/C++17 objects match:187 positive FUNC regions,163 relocations(143 direct controls+ten HI/LO pairs),every original-VA-normalized byte equal.53 Xwchc ports use primary definitions/52 official positive vectors. Original-context reconstruction,not recovered vendor C sources.

| Complete half-open body | Bytes/instructions | Own frame |
| --- | --- | --- |
| 0x5F98E..0x5FBAE | 544/199 | 16 |
| 0x5FCDC..0x6014E | 1138/389 | 32 |
| 0x6014E..0x6020A | 188/74 | 16 |
| 0x5FBAE..0x5FC70 | 194/66 | 32 |
| 0x43874..0x43932 | 190/73 | 48 |

Three prior gaps are called by task0x60516 at0x6068E/0x60620/0x605AC. Two helpers are actual callees. Adjacent0x5FC70/0x6020A functions are excluded. All CFG instructions are reachable,own frames balance at normal exits,late arms after earlyRET remain.

## Frame-released parser tail

0x5FCDC has ordinary returns and a no-link parser tail.0x60016 preserves the record argument,originalRA/saved registers are restored,0x60028 releases32 bytes,then0x6002A jumps to prior complete0x5F234. Original JAL-zero bits,arguments and order are checked,no normal C-call substitution or extra frame.

All **13 resolvable encoded call sites** in the complete original task have selected/prior providers;no other unresolved indirect call site appears in that task body. Numeric CODE pointers,later callback dispatch,transitive memory/IRQ effects and physical success remain outside that result. **No runtime closure claim.**

## Original16/48 index boundaries

Prior0x43414 scans0..15 and0x43A14 removes0..47. New0x43874 scans16..47. All three fresh-read numeric table-pointer slot **0x2000322C**,with **12-byte stride**:

| Routine | Numeric indices | Half-open extent relative to table base |
| --- | --- | --- |
| 0x43414 | 0..15 | [0,192) |
| 0x43874 | 16..47 | [192,576) |
| 0x43A14 removal | 0..47 | [0,576) |

Stable pointer,valid memory and original private-callee contracts give a numeric disjoint union **48×12=576 bytes**. **Actual576-byte allocation,ownership/lifetime,equal bases across calls and concurrency safety remain unproved.** Index constants do not prove physical RAM capacity.

For an empty entry,the new helper forms low8(ID>>4) andlow16(1<<(ID&15)),then calls real prior0x43728. Original nonzero return writes two record words/optional byte ID;zero continues scanning. No guessed generic SUCCESS convention. The helper encoded outcomes0/2/8 do not prove hardware timing or event delivery.

It saves word0x4002420C,writes zero,FENCE.I,and retains restore requests on each outcome. **Physical atomicity/IRQ isolation remain unknown.** Original packet widths,comparison/copy/range/peripheral requests remain;no packet execution or synthetic inputs.

## Composition and use

[Compile-only assertions](handlers_abi.c) verify RV32 widths,frame slots,index banks and576-byte numeric union. C/C++ objects match,zero allocated bytes,no runtime provider.

Actual nonloadable ET_REL composition:**29,848 CODE+256 DATA/10,321 instructions**,2,008 positive FUNC regions,1,586 relocations. Every input byte/symbol/relocation retained,unique original-PC CODE ownership,two independent readers agree. Three real prior providers lower named gaps **7→4**. Thirteen imports have real prior bodies,no new named gap/stub/opaque call. Remaining four named gaps belong to callback0x58C52:0x58498,0x58788,0x588B4,0x58988.

[Evidence](evidence-v1.json) · [Full audit](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-task-final-handlers/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Requires pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. APP stays159 C/H files/95.54% byte coverage,**not functional completion**. Prior callback/source-map conditions are freshly verified,not upgraded to live hardware facts. The4-byte startup source gap and ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain open.

No APP integration,BIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only scheduler-bank/static-call diagnostics remain an unimplemented UI candidate,no live table/callback/register changes.
