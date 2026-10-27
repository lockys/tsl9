# Required candidate initializer0x5362E

[繁體中文](README.md) · [NVM layout](../tsl9-NVM-record-layout/readme.en.md) · [Caller/callback registration](../tsl9-resident-callback-registration/readme.en.md) · [RF register initializer](../tsl9-original-RF-tx-path/readme.en.md)

New [C/C++ body](resident_init5362e.c) covers the complete **0x5362E..0x537D8,426 CODE bytes/138 instructions**. Actual C11/C++17 objects agree:20 positive FUNC regions,14 direct controls and one real far HI/LO call pair,total16 relocations,reproduce original SDK bytes. Twelve Xwchc byte/halfword ports are checked against retained official encoding definitions/52 positive vectors;installed ISA identity remains unproved.

Original-register-context C arithmetic/volatile accesses retain explicit ISA/control ports. This is not recovered vendor C source or an ordinary standalone C API.

## Boundary/frame

Own frame16 savesS2/S1/S0/RA at0/4/8/12. The single normal exit is no-link tail0x537C8→0x5E758,after restoring all words/releasing the frame. Reachable post-epilogue arms0x537CC/0x537D2 jump back into the body and are retained. A different64-byte-frame function starts at0x537D8 and is excluded.

## Requests and real dependencies

- 0x5364A writes zero to word0x200034E4.
- Real far call0x53650/0x53654 targets existing RAM memset provider0x2000039C,with address0x200033B8,value0,count296,end0x200034E0. It is not an opaque callback.
- 0x53668 stores low8(incomingA0) at0x2000319F,conditional on callee private-register preservation. A boolean initialized flag,valid task ID or success meaning is not assigned.
- 0x537B2 calls existing complete RF register initializer0x64298. Constants,branches,fresh accesses and later calls remain original,without invented frequency/timing units.

Six genuine unavailable callees are explicit:**0x55BD4,0x55C48,0x43E24,0x57AC4,0x63704,0x5E758**. No stubs or claims of closed effects/normal returns.

## Conditional caller and callback order

Complete caller0x60856..0x6089A reads0x2000319F. A zero value takes call0x43C4E then0x60870→this initializer,incomingA0 coming from the preceding callee's result. The nonzero path skips both calls.

After normal return/skipping,both callback stores dominate caller normal return:

| Store PC | RAM word | Numeric CODE pointer |
| --- | --- | --- |
| 0x60880 | 0x2000343C | 0x5E8BC |
| 0x60892 | 0x200034F8 | 0x60516 |

The first word is inside the requested296-byte zeroing span. This proves encoded request/binding order,**not live callback values,callee noninterference,atomic initialization or absence of dispatch before binding**. The final stores alone do not establish all RF/IRQ callbacks are ready.

## Partial link and limits

Actual C/C++ nonloadable ET_REL compositions contain **20,916 CODE+256 DATA/7,163 instructions**,1,340 positive FUNC regions and1,011 relocations. All input bytes/symbols/relocations are retained,original-PC CODE ownership is unique,and two independent readers agree.

A real body resolves prior0x5362E;two imports use actual existing providers. Six new real gaps make genuine named dependencies **10−1+6=15**. UND count is not runtime closure. This unit has no genuinely opaque callback site;other indirect calls/raw-memory contracts in the composition remain open.

[Numeric assertions](init_abi.c) compile in C11/C++17 for RV32 widths,own frame and state extents,without allocated bytes/providers/imports. They do not prove physical RAM ownership.

## Replay

[Evidence](evidence-v1.json) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-init-5362e/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned local SDK/APP,prior native artifacts and Windows NDK LLVM;no downloads. Other platforms are unverified. APP stays159 C/H files/95.54% byte coverage,not functional completion. No APP integration,newBIN,target/HOST-model/ISA execution or hardware access.

The4-byte startup source gap,settings writer additional144/123-byte initialization gaps,NVM mapping and ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain open. **Usable replacement firmware has not been successfully reconstructed.** Read-only initialization phase/callback binding diagnostics remain an unimplemented future UI candidate,without RF/IRQ parameter changes.
