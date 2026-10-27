# Task transition,parser and message delivery chain

[繁體中文](README.md) · [Prior initializer](../tsl9-resident-init-final/readme.en.md) · [Original task callbacks](../tsl9-resident-callback-registration/readme.en.md)

[C/C++](resident_task_transition.c) adds **six complete bodies/1,378 CODE bytes/479 instructions**. Actual C11/C++17 objects match:83 positive FUNC regions,69 relocations(55 direct controls+seven HI/LO pairs). Every original-VA-normalized byte matches;17 Xwchc ports use primary encoding definitions/52 official positive vectors. These are not recovered vendor C sources.

| Complete half-open body | Bytes/instructions | Own frame | Actual role |
| --- | --- | --- | --- |
| 0x5F0D2..0x5F234 | 354/121 | 80 | Original task transition,poll and subsequent setup |
| 0x5EE98..0x5F0D2 | 570/191 | 48 | Original buffer/record parsing,branches and message request |
| 0x6A79E..0x6A7BC | 30/9 | 0 | Stack/A6/A7 width normalization,no-link tail to builder |
| 0x52906..0x52A02 | 252/98 | 80 | Allocate,write/copy,release frame,tail to send |
| 0x43208..0x4329A | 146/50 | 16 | Candidate tmos_msg_send checks,enqueue and event request |
| 0x2000021C..0x20000236 | 26/10 | 0 | Append through metadata next pointers |

All CFG instructions are reachable,own frames balance at normal exits. Reachable branches after RET remain;adjacent functions excluded. Original register/call/return ports remain,not a hosted C library.

## Actual caller and effects

Original task0x60516 calls0x5F0D2 at0x606B4/0x60708,with related state-byte comparison165(record+10). The root reloads record pointer0x20003438 and base pointer0x2000353C;0x5F112/0x5F114 repeatedly reads base+100 until zero. Original polling,widths,masks and order remain. **No physical-register semantics or termination proof.**

0x5F11C writes original word AND0xFFFFDFFF. The base is reloaded before0x5F138 writes the earlier original word to the new base+12. Equal bases or atomicity are not assumed. Retry arm0x5F228..0x5F234 afterRET0x5F226 remains complete.

## Wrapper,stack and allocation

0x6A79E reads incomingSP+0/+4/+12 as unsigned halfword/byte/byte,then writes words back. A6/A7 retain low8 bits before no-link tail0x52906. After its80-byte frame,the builder readsSP+80/84/88/92/96,corresponding to callerSP+0/4/8/12/16,not new local frame fields.

Allocation request:**36+unsigned8 length(maximum291)**. Actual allocation/heap/buffer/callback validity remains unproved. Null allocation restores/returns without send. Non-null arm retains copy requests:destination+10/6 bytes,+25/6 bytes,+36/length. Original stores,+31 length and+32 pointer remain.

Independent decoding of all stores/copy extents finds **no explicit initialization of prefix byte21 in this builder**. Its live value and allocator/callee initialization were not observed;no disclosure or bug claim. Success releases80 bytes at0x529DE before tail0x529E0→send.

## Send,queue and event request

Official candidate header tmos_msg_send is jump-table slot12;actual0x40064 contains function-pointer word0x43208,not a branch opcode. Encoded outcomes:null pointer→5,task rejection→3,metadata rejection→5,enqueue/event-request path→0. These are instruction outcomes,not live delivery proof.

Send saves word0x4002420C,writes zero,FENCE.I,and preserves original restore requests. Success writes task metadata atmessage−2,uses queue root0x20003198,then requests event bits0x8000. **Physical lock/atomicity,callee effects and delivered events remain unproved.**

RAM enqueue zeros message−8 next word,sets an empty root or follows next pointers to append. No added traversal limit or logic fix. Cycle/alias/invalid-pointer termination and safety remain unknown. Full source[0x4048C,0x404A6) maps toRAM[0x2000021C,0x20000236),inside the prior first loader copy. This does not identify installed ROM.

## Verification and use

[Compile-only assertions](task_abi.c) verify RV32 widths,36-byte prefix,291-byte numeric bound and stack offsets. C/C++ objects match,zero allocated bytes,no runtime provider.

Actual nonloadable ET_REL composition:**22,786 CODE+256 DATA/7,810 instructions**,1,460 positive FUNC regions,1,109 relocations. Every input byte/symbol/relocation retained,unique original-PC CODE ownership,two independent readers agree. One actual task provider lowers named dependencies **9→8**. All seven imports have real prior bodies;no new named dependency,stub or opaque call. Transitive/indirect memory effects remain open.

[Evidence](evidence-v1.json) · [Full audit](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-task-transition/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Requires pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. APP stays159 C/H files/95.54% byte coverage,**not functional completion**. The4-byte startup source gap,physical ROM/RAM/ISA/IRQ/Flash/OTA compatibility and no-dispatch-before-binding remain open.

No APP integration,BIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only offline queue-path/rejection diagnostics remain an unimplemented feature candidate,without new RF/vehicle-control/live-queue writes.
