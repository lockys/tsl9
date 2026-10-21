# Placement ownership and incoming-reference audit

This is an offline audit of exact ID2966 V4.1.60 source bytes and the existing source-image carrier. It creates no new BIN and does not execute or emulate firmware. The 76800-byte original SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.

## Exact ownership

| Role | Original half-open range | Bytes |
|---|---|---:|
| Reset memory slice | 0x186BA..0x186F8 | 62 |
| Clock query | 0x18834..0x188E2 | 174 |
| Derived fields | 0x1973C..0x19764 | 40 |
| Interrupt initialization | 0x9A42..0x9AD2 | 144 |
| RCC helper | 0x19124..0x19142 | 30 |
| RCC helper | 0x19142..0x19160 | 30 |
| RCC helper | 0x19160..0x1917E | 30 |
| RCC helper | 0x1917E..0x1919C | 30 |

The union is 540 bytes across eight disjoint ranges. IRQ initialization is **144**, not 176 bytes; its four original helpers are **30**, not 22 bytes each. Those two incorrect assumptions accidentally preserve the same aggregate total while assigning 32 bytes to the wrong locations. Aggregate arithmetic is not a placement proof.

The memory slice is only part of the 138-byte `.text.tsl9v4160.reset` owner. Entry at 0x186BA follows the SP-setting instruction at 0x186B6. Exit includes the conditional branch at 0x186EA to 0x186F8 and fallthrough after 0x186F4 to that continuation. The slice has no RET. Its enclosing prefix, remaining CSR/clock/ROM sequence and continuation must remain correct; the full reset owner cannot simply be discarded.

## Actual full layout evidence

The pinned carrier `source-image-merged.o` has SHA-256 `646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97`, 691 allocated sections and 8280 RELA records. The source-layout numeric witness ELF has SHA-256 `66fbf4cf1d9731f5fcd4f71c66ec1c67fc4fd2487f710125ed6488cbde2e8420`. The checker confirms 690 file-backed image allocations exactly cover and reproduce the original 76800 bytes with no gaps or overlaps. The remaining allocation is 35160-byte RAM NOBITS at 0x20004000; it is not spare image storage.

The **full** binding script is `experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002/original-image-layout.ld`, 126450 bytes, SHA-256 `651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b`. It contains 691 explicit address bindings and 691 SIZEOF assertions. `verify-image-fidelity.py` lines 139–141 generate it; line 153 links with `ld.lld --no-relax -T <full-layout> -T <numeric-ROM-script> <object> -o <witness>`. All actual allocated section addresses and sizes are checked against the full script. The tiny `ADDRESS-WITNESS-ONLY.ld` supplies only ROM=0x40000; it is not this layout map and supplies no ROM implementation. The true undefined carrier symbol remains `__tsl9v4160_rom_entry`.

These ELF sections and symbols are reconstruction evidence, not recovered original firmware debug symbols. Their original-address mapping is supported here by exact whole-image byte equality, not by physical execution or hardware readiness.

## Available static references

All 8280 RELA records and 24585 instruction boundaries within carrier executable allocations are inspected. The eight selected ranges receive 33 RELA references and 34 admitted direct-control references. Sixteen direct references cross selected-range boundaries:

| Destination | Incoming source PCs |
|---|---|
| 0x18834 | 0x9254 |
| 0x9A42 | 0x9258 |
| 0x1973C | 0x925C |
| 0x19124 | 0x9A6A, 0x1986E |
| 0x19142 | 0x9A5E, 0x19B68 |
| 0x19160 | 0x9A88, 0x9A92, 0x188F8, **0x18906**, 0x1891C |
| 0x1917E | 0x99F2, 0x99FC, 0x9A74, 0x9A7E |

The 0x18906 transfer is JAL with rd=x0, a tail transfer rather than an RA-forming call. Every helper has callers outside 0x9A42. Inlining the six main calls therefore does not make the helper entries free or removable.

The remaining admitted direct references are internal branches/jumps. Important interior targets include reset copy/zero loop labels, query branch blocks, and each helper's clear branch at entry+14. Two RELA references are PC-relative low-part anchor links into the reset slice, not runtime calls. The 29 named selected symbols include seven function definitions, local branch/anchor labels and assembler mapping markers; none justifies treating all symbols as independent callable entries. Full records are retained in `reference-inventory.json`.

No admitted direct transfer from outside a selected range targets its interior. No adjacent LUI/AUIPC-plus-supported-low-instruction address pair points into the selected ranges. No four-byte numeric window at any byte offset, including bit-zero-normalized JALR values, names a selected address. Those are bounded negative observations, **not absence of computed references**.

A separate scan of every original halfword finds 39 valid direct-encoding candidates: the 34 admitted records plus five candidates starting in the second half of known 32-bit instructions. These five are not admitted incoming references. The audit also retains all 939 known indirect-transfer source addresses, including 552 canonical RET encodings, and a digest of their complete records. Multi-instruction arithmetic, loaded/callback targets, external resident/ROM code and unexpected interior entry remain unresolved. Static inventory does not establish reachability or exclude such targets.

## Placement gate and remaining work

The bounded controls reject a 78-byte reset leaf in its 62-byte slot, an 80-byte fragment in that slot, a 196-byte query in its 174-byte slot, and the false 176-byte IRQ ownership claim. Eight reference-transcript mutations are rejected by the same exact-inventory binding gate, including dropped other/tail callers and invented free-padding/computed-target absence. These are four ownership controls and eight transcript controls, **not compiled native tests**.

A 38-byte fields body or the previous 118-byte IRQ body fits its respective byte count but does not thereby satisfy original register ABI, continuation or reference requirements. Separate ABI work has identified problems with the prior ordinary-C IRQ/helper register contract; those old sizes are not accepted slack for integration. Any new contract-correct component must be measured from its actual object, then placed with entry/continuation bindings, all incoming references, internal PC-relative uses, alignment, branch reach, adapter/veneer cost and original memory content accounted for. No bytes are declared free and no candidate placement is accepted by this audit.

```sh
python3 check-placement.py --firmware <exact-original> --object <pinned-carrier.o> --witness <pinned-witness.elf> --elf-parser <reviewed-elf32.py> --layout <full-original-image-layout.ld> --reference reference-inventory.json
python3 check-negative-gates.py
```

The ELF parser is reused read-only from the reset-memory compiler review and pinned by hash. Explicit paths make replay independent of shell and checkout directory. The original object/witness/full-layout artifacts must be available; their hashes alone do not recreate missing files. Python performs only file inspection and bounded arithmetic. No original/rebuilt RV32 execution, ISA emulation, network, device I/O or OTA occurs.
