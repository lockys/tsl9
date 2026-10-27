# Three required initializer leaf providers

[繁體中文](README.md) · [Original caller initializer](../tsl9-resident-init-5362e/readme.en.md) · [NVM layout](../tsl9-NVM-record-layout/readme.en.md)

New [C/C++](resident_init_leaves.c) supplies three complete bodies,**90 CODE bytes/28 instructions**. Actual C11/C++17 objects match:10 positive FUNC regions,six direct-branch relocations and every original SDK byte. No own frames,callees,CSR requests or new custom instructions. Original register/control ports remain;these are not recovered vendor C sources.

| Body | Complete range | Bytes/instructions | Actual effect |
| --- | --- | --- | --- |
| 0x43E24 | 0x43E24..0x43E6A | 70/22 | Fresh unsigned halfword0x2000323E → numeric bucket0..7 |
| 0x55BD4 | 0x55BD4..0x55BDE | 10/3 | incomingA0 word → 0x200034E0 |
| 0x55C48 | 0x55C48..0x55C52 | 10/3 | incomingA0 word → 0x200034E8 |

Adjacent registration/search functions are excluded. Setters preserveA0 and do not force zero in general;the actual initializer callsites explicitly supply zero.

## Complete unsigned16 partition

One original freshLHU and six unsigned branches/finalSLTIU are independently decoded:

| Inclusive input | A0 result |
| --- | --- |
| 0..20 | 7 |
| 21..30 | 6 |
| 31..50 | 5 |
| 51..75 | 4 |
| 76..100 | 3 |
| 101..150 | 2 |
| 151..250 | 1 |
| 251..65535 | 0 |

These symbolic intervals cover unsigned16 without overlap,no HOST-model/ISA execution or generated test inputs. Physical units and protocol-field identity remain unproved.

Original caller0x5362E calls0x43E24 at0x536FE. No interveningA0 write precedes original qk.c.sb a0,3(s0) at0x53718,storing to state0x200033BB. Matching ROM/callee/memory/IRQ/alias conditions give a0..7 byte range. Live values,initialization success and hardware compatibility are not inferred.

## Conditional308-byte zero requests

Previous proof retained the296-byte memset request,standalone zero word and call order. Calls0x5365A/0x53660 explicitly supplyA0=0 to the newly supplied real setters:

| Original request | Half-open numeric interval |
| --- | --- |
| memset0/296 | [0x200033B8,0x200034E0) |
| 0x55BD4 word store with callerA0=0 | [0x200034E0,0x200034E4) |
| Original initializer zero word | [0x200034E4,0x200034E8) |
| 0x55C48 word store with callerA0=0 | [0x200034E8,0x200034EC) |

The requests numerically cover **308 contiguous bytes**. Both setters preserveSP/GP/RA/saved registers and have no other callees/CSR effects. Valid memory,original ROM/callee contracts,no faults/asynchronous interference and alias conditions remain required. Later nonzero initializer fields/callback stores stay original. **No all-zero final308-byte state,RAM ownership,atomic initialization or no-dispatch-before-binding proof.**

[Compile-only assertions](leaves_abi.c) verify RV32 widths and the308-byte numeric extent in C11/C++17. Objects match,with no allocated bytes/providers/imports/executable entry.

## Partial link and use

Actual C/C++ nonloadable ET_REL compositions contain **21,006 CODE+256 DATA/7,191 instructions**,1,350 positive FUNC regions and1,017 relocations. Every input byte/symbol/relocation is retained,original-PC CODE ownership is unique,and two independent readers agree. Three real providers lower genuine named dependencies from15 to **12**,without new code imports or stubs. Other indirect calls/runtime memory effects remain open.

[Evidence](evidence-v1.json) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-init-leaves/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. APP stays159 C/H files/95.54% byte coverage,not functional completion. The4-byte startup source gap,writer144/123-byte initialization gaps,NVM map and ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain open.

No APP integration,newBIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Raw bucket/initialization request-span display remains an unimplemented read-only UI candidate,without live-field/RF/IRQ changes.
