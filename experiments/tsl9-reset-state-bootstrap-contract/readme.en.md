# APP zeroed state and candidate bootstrap write footprint

[繁體中文](README.md) · [Current formal reconstruction](../tsl9-event-word-table-integration/readme.en.md)

This milestone audits the existing execution layer without adding or recompiling firmware. All **138B / 37 instructions** of the APP primary reset match current native C11/C++17 original-coordinate ELFs. Five SDK bootstrap stages retain **234B / 67 instructions and 14 typed relocation roles**; their actual native bytes and roles are all present in the current SDK composition. These remain candidate SDK facts,not installed-ROM identity proof.

## Conditional initialization

Assuming original placement/register context,valid memory,normal execution,and no asynchronous interference:

- APP establishes GP=`0x20004000`,SP=`0x20010000`.
- It copies 128B from `[0x1AB60,0x1ABE0)` to `[0x20004000,0x20004080)`. This audit checks ranges without reading the initial-value payload.
- The word-zero loop at `0x186EE` covers `[0x20004080,0x2000C958)` with 8,758 stores. At `0x186F8`,the following bytes are therefore zero. This is an instruction/interval proof,not a live RAM observation.

| State | Half-open interval |
| --- | --- |
| Input counter,GP+176 | `[0x200040B0,0x200040B1)` |
| Four sequence states,GP+332 | `[0x2000414C,0x20004150)` |
| Seven-word index,GP+370 | `[0x20004172,0x20004173)` |
| Mode enable/mode/selector/countdown | `[0x2000BF38,0x2000BF3C)` |

## Original handoff and SDK writes

APP writes `MEPC=0x9008` at `0x1872C`,then makes a no-link tail transfer to `0x40000` at `0x18730`. The candidate bootstrap exits through **MRET** at `0x6DEBE`,using then-live MEPC. This is not a hosted C return.

Every one of the seven explicit memory-store instructions in the selected bootstrap is classified. The inclusive-last-word copy/zero interfaces become these half-open destination intervals;original overlaps remain intact:

| Write | Half-open interval |
| --- | --- |
| RAM slots 0/1/2 | `[0x20000000,0x2000000C)` |
| Seed | `[0x20000010,0x20000040)` |
| First copy | `[0x20000040,0x20002E74)` |
| Second copy | `[0x20002E70,0x20002EFC)` |
| Zero | `[0x20002EF8,0x20003618)` |
| Conservative loader own16-byte frame | `[0x2000FFF0,0x20010000)` |

All these intervals avoid the four watched state groups. This narrows known bootstrap write effects without covering the APP clock helper,asynchronous paths,or later callback/alias writes. The second copy still lacks source bytes `0x6EB2C..0x6EB30`,outside the APP. They were neither filled nor read;subsequent zeroing does not prove the prior source access succeeds.

## Remaining execution conditions

The `CSRRS mstatus` at `0x1870C` applies OR mask `0x1888`;it does not establish that exact final mstatus value. Under standard MIE-bit3 semantics,the instruction setting MIE precedes the mtvec write at `0x1871C`. Incoming IRQ state,pending/enable state,and interrupt exclusion remain unproved.

After zeroing,APP calls clock helper `0x1874A` at `0x18720`. This audit does not prove that helper leaves the watched bytes unchanged. Extending zeros through MRET or to first use still requires clock,IRQ/DMA/alias,callee,and valid source-memory conditions. **First-use lookup values,global counter/mode domains,and startup completion are not proved.**

The historical SDK native receipt differs only in its manifest input. Its exact159-source historical manifest is reconstructed,while every other source/tool/artifact input remains retained. Drift was not ignored,and no full SDK recompile is claimed.

## Replay

With the fixed local native artifacts and LLVM available,run from the repository root:

```sh
python3 experiments/tsl9-reset-state-bootstrap-contract/check-v1.py --tool-dir "$LLVM_BIN"
```

[Pinned inputs](inputs-v1.json) · [Verification receipt](verification-v1.json) · [Unimplemented startup diagnostic idea](feature-candidates.json)

Formal APP evidence remains **164 C/H files / 95.75% static byte coverage and six unresolved source providers**. Sources and native artifacts are unchanged. No new BIN,target/HOST-model/ISA execution,hardware access,or third-party API requests occurred.
