# Complete task parser,scheduler records and masked bit count

[繁體中文](README.md) · [Prior task/message chain](../tsl9-resident-task-transition/readme.en.md) · [Original caller](../tsl9-resident-callback-registration/readme.en.md)

[C/C++](resident_task_parser.c) adds **four complete bodies/2,316 CODE bytes/770 instructions**. Actual C11/C++17 objects match:170 positive FUNC regions,140 relocations(120 direct controls+ten HI/LO pairs),every original-VA-normalized byte equal.27 Xwchc ports use primary encoding definitions/52 official positive vectors. Original register/control ports remain;these are not recovered vendor C sources.

| Complete half-open body | Bytes/instructions | Own frame | Scope |
| --- | --- | --- | --- |
| 0x5F234..0x5F96C | 1848/597 | 112 | Complete original task parser and late arms |
| 0x43414..0x43520 | 268/97 | 48 | Scan,allocate and link scheduler records |
| 0x43A14..0x43A8C | 120/43 | 32 | ID-derived stop-task arguments and record clearing |
| 0x57AD8..0x57B28 | 80/33 | 0 | Count32+5 effective bits from five bytes |

All CFG instructions are reachable,own frames balance at normal exits. Prior512-byte parser capture was incomplete. Reachable arms afterRET0x5F322 remain through0x5F96A→0x5F8DA. Adjacent34 bytes[0x5F96C,0x5F98E) are unreachable from this root and belong to a distinct frame0 function;excluded.

## Actual caller and dependencies

Task0x60516 retains the record argument at0x606F8 and calls0x5F234 at0x606FE. Buffer pointer isrecord+120;receive-status provider remains real priorRAM0x2000263A. Original low-nibble/length/field branches,copy/compare requests,64-bit arithmetic helper and callback ports remain. No parser execution or generated packets.

This unit supplies the missing0x5F234 root and three actual callees,but exposes four **genuinely missing deeper bodies**:0x5E950,0x5EA9A,0x5EACA,0x5EE06. They remain named imports for original calls,no stubs or invented effects. Seven other imports have real prior providers.

| Actual indirect call PC | Fresh pointer slot |
| --- | --- |
| 0x5F6D6 | 0x20003234 |
| 0x5F708 | 0x200031E0 |
| 0x4346C | 0x200031E0 |
| 0x434AA | 0x20003220(optional allocation-failure callback) |

Original compressed JALR-through-A5 bits and loads are checked. Actual callback values,targets,returns and effects remain unknown;no guessed direct providers substituted.

## Scheduler numeric contracts

0x43414 saves word0x4002420C,writes zero,FENCE.I,and retains original restore requests. It loads record-array pointer0x2000322C and scans **16 entries with12-byte stride**. An available entry requests16-byte allocation;success retains node/list/record stores and optional output index. Encoded results:2/11/8/0. Original next+12 traversal has no cycle limit;termination/alias safety unproved.

0x43A14 retains **ID0..47** check and12-byte record stride. A nonzero entry uses real prior0x439A8 stop-task withtaskID=ID>>4,event=low16(1<<(ID&15)),then clears entry+0/+4 words. The third word has no explicit clear. Encoded results:0/2.

Original numeric extents differ:16×12=192 and48×12=576. Both remain unchanged. **Shared capacity,physical RAM ownership and full scheduler compatibility are unproved.** Control-word save/zero/FENCE.I/restore requests do not prove physical atomicity or IRQ isolation.

## 32+5-bit count

0x57AD8 reads unsigned bytes in offset order **1/2/4/0/3**. Four bytes form32 bits;the fifth retains low5 bits. Original loops visit32 and8 positions;the latter has three zero high bits afterAND31. Conditional unsigned8 result range:**0..37**,without accumulator overflow at that bound. No callee,CSR or own frame.

This follows original instructions/counters,no HOST-model/ISA execution or synthetic inputs. Valid original memory accesses remain required;five loads are not a proved atomic snapshot. **The input is not confirmed as a physical BLE channel map or another specific domain field.**

## Verification and use

[Compile-only assertions](parser_abi.c) verify RV32 widths,112/48/32-byte frame slots,192/576-byte numeric extents and37-bit bound. C/C++ objects match,zero allocated bytes,no runtime provider.

Actual nonloadable ET_REL composition:**25,102 CODE+256 DATA/8,580 instructions**,1,630 positive FUNC regions,1,249 relocations. Every input byte/symbol/relocation retained,unique original-PC CODE ownership,two independent readers agree. Eight prior named gaps minus supplied parser plus four actual deeper gaps gives **11**. This is a fuller call graph,not compatibility completion. Four opaque sites remain original;transitive/memory/IRQ effects stay open.

[Evidence](evidence-v1.json) · [Full audit](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-task-parser/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Requires pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. APP stays159 C/H files/95.54% byte coverage,**not functional completion**. The4-byte startup source gap,physical ROM/RAM/ISA/IRQ/Flash/OTA compatibility and no-dispatch-before-binding remain open.

No APP integration,BIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only offline37-bit-mask/scheduler-record diagnostics remain an unimplemented feature candidate,no live callback/RF/record writes.
