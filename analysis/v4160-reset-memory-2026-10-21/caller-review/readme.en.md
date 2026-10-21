# Reset memory helper caller review

**A new C leaf memory helper ending in RET is not a drop-in replacement for original reset fallthrough.** It needs a linked entry adapter, correct register results and a proven continuation through the original CSR/clock/ROM boundary. A0 and A1 remain live at that unresolved ROM boundary; a memory-only or ordinary `void` C result cannot establish their values.

This read-only audit covers original ID2966 runtime SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. It retains **372 original bytes / 130 instructions**: reset `0x186AA..0x18734` (138/37) and clock `0x1874A..0x18834`, including its cold tail (234/93). Existing reset/clock source maps and the resident candidate map are pinned as references. The old sixty-fifth-round 148-byte / 40-instruction independent-reset proof covers a **relocated native layout**; it is not substituted for the original reset's PC pairs or instruction count.

## Original normal context

The first four reset instructions establish GP=`0x20004000` and SP=`0x20010000` using their own source-PC AUIPC/ADDI anchors. The memory slice `0x186BA..0x186F8` is **62 bytes / 17 instructions**, entered and exited by fallthrough. It has no CALL or RET. It copies 32 words from `[0x1AB60,0x1ABE0)` to `[0x20004000,0x20004080)`, then writes zero to 8,758 words in `[0x20004080,0x2000C958)`.

| Register at memory fallthrough `0x186F8` | Original normal value | Next relevant use |
|---|---|---|
| A0 | `0x2000C958` | Preserved to unresolved ROM boundary |
| A1 | `0x2000C958` | Preserved to unresolved ROM boundary |
| A2 | `0x20004080` | Overwritten at clock `0x1875E` before read |
| T0 | `0x3A1`, last word read from `0x1ABDC` | Immediately overwritten by LI at `0x186F8` |
| RA | Unchanged incoming value | Overwritten by clock JAL at `0x18720` before a normal read |
| GP | `0x20004000` | Remains unchanged through the inspected reset/clock path |
| SP | `0x20010000` | Used by the clock's real 16-byte frame |

The copy/zero counts and endpoint values are arithmetic consequences of the static loops under their normal fixed context, not evidence from executing RV32. The memory slice does not assign other GPRs or access SP. Its source postcondition and the narrower local liveness observation are different claims: A2/T0/incoming RA are locally killed before use, but that does not prove arbitrary asynchronous observers cannot see them.

## Clock and CSR continuation

The original sequence is: write CSR `0xBC0=31` at `0x186FA`; write `0x804=3` at `0x18700`; set MSTATUS bits `0x1888` at `0x1870C`; write MTVEC=`0x803B` at `0x1871C`; call clock `0x1874A` at `0x18720`, setting RA=`0x18724`; then, if clock returns, write MEPC=`0x9008` at `0x1872C` and terminal-jump to `0x40000` at `0x18730`. SET_BITS is not an assignment of the whole MSTATUS value. These instruction operands do not establish custom CSR meanings, privilege availability or an interrupt exclusion guarantee.

Clock has no CALL and no explicit A0/A1/T0/GP/RA reference. Its RET at `0x1882E` implicitly reads the incoming RA. A2's first occurrence is its definition `LUI A2,0x20` at `0x1875E`; it therefore kills the memory slice's A2 before use. Clock subtracts 16 from SP at `0x18754`, accesses frame offsets 8 and 12 (nominally `0x2000FFF8` and `0x2000FFFC`), and restores SP at `0x1882C` before RET. Poll paths can remain pending without a source timeout, so normal return is a premise, not a guarantee supplied by this audit.

At the original terminal jump, normal source state includes GP=`0x20004000`, SP=`0x20010000`, A0=A1=`0x2000C958`, A2=`0x20000`, T0=`0x9008`, RA=`0x18724`, MEPC=`0x9008`. A3–A5 are clock-path results rather than values established by the memory helper. The installed ROM and its required inputs are not bound. A known resident candidate is only a candidate; its own initialization cannot establish the actual ROM's input deadness or acceptance.

## What the adapter still needs to prove

The adapter must supply a real C-helper return link and route the return to `0x186F8` or an explicitly linked equivalent. A normal JAL link is the actual call site's next PC; it is not automatically `0x186F8`. Restoring final SP alone does not prove any new stack writes are valid or equivalent. The native helper and adapter need audited register write sets, GP/SP behavior, memory bounds and no hidden calls or unresolved libc helpers. Source A0/A1 results must be produced or separately adapted before the unresolved ROM boundary.

Local normal-path deadness permits a narrowly stated treatment of old A2/T0/incoming RA; it does not prove full reset-entry, asynchronous interrupt or ROM ABI equivalence. Relocating the clock call also changes its natural RA link. The original ROM-boundary RA is `0x18724`; either preserve the required boundary or prove that the installed ROM ignores the difference. A leaf helper test cannot settle that issue.

Keep the source CSR/control sequence and the terminal non-linking ROM transfer. The adjacent MRET at `0x18734` is not normal fallthrough after the original jump, and directly entering main `0x9008` does not reproduce the unresolved ROM initialization. An absolute symbol at `0x40000` also does not provide a resident implementation. Installed ROM identity, physical RAM/stack, MMIO/clock, interrupts, privilege, complete linked placement and OTA compatibility remain unproved.

`audit.py --image <original-BIN> --r2 <radare2-path>` emits the retained source audit. It performs no original execution, ISA emulation, network or device I/O. `caller-contract.json` separates source values, local liveness and remaining integration obligations; `verification.json` retains the original instruction evidence.

