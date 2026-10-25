# Official memory / ROM requirements audit

[繁體中文](README.md) · [Machine-readable evidence](evidence.json) · [C/C++ checks](../../experiments/tsl9-memory-rom-contract/readme.en.md)

**Confirmed: the current V4.1.60 image cannot reuse the old V4.1.00 initialization settings unchanged.** Values below come from decoding AUIPC/ADDI, loads, stores and branches in two digest-pinned official images. Firmware was not executed.

| Startup requirement | ID2581 V4.1.00 | ID2966 V4.1.60 |
|---|---:|---:|
| Reset entry | `0x183FE` | `0x186AA` |
| Initial GP | `0x20004000` | `0x20004000` |
| Initial SP | `0x20010000` | `0x20010000` |
| Initializer source | `0x1A7E0` | `0x1AB60` |
| Copied initializer length | 136B | 128B |
| Zero start | `0x20004088` | `0x20004080` |
| Zero end, exclusive | `0x2000C950` | `0x2000C958` |
| Copy plus zero RAM span | 35,152B | 35,160B |
| Zero length | 35,016B | 35,032B |

Current-image evidence locations: entry `0x8000`, GP/SP setup `0x186AA–0x186B6`, initializer source `0x186BA–0x186BE`, copy/zero loops `0x186C2–0x186F4`. All 38 instructions in the retained startup source-map slice were byte-checked; the addresses and both versions' loop boundaries were independently decoded. This public evidence excludes initializer payload contents.

V4.1.60 sets vector base `0x8038`, `mtvec=0x803B` and initial MEPC `0x9008`, then jumps outside the image to `0x40000`. The saved WCH SDK default function table starts at `0x40034`; indices 5/6 give slots `0x40048`/`0x4004C`, named `tmos_memset`/`tmos_memcpy`. These are **function-pointer storage slots**, not function entries. Installed ROM contents, indirect call targets and private ABI remain unconfirmed.

**Compilation:** C11 and C++17 numeric requirement checks passed. Both ET_REL objects have no nonempty allocated sections, relocations, undefined symbols or program headers. No firmware code was added. Reconstruction byte coverage remains **69.69%**; this audit adds 0 reconstructed firmware bytes.

**Unproved:** exact chip/PCB identity, physical RAM/Flash capacity and ownership, ROM identity/ABI, interrupt mode/priorities, clocks/pins, stack/heap high-water bounds, and complete OTA/device functionality. The 13,992B gap to initial SP is only arithmetic, not available stack space. The 64 KiB RAM bounds are conditional candidate bounds. No BIN or hardware connection was created; old candidate images are not flashability evidence.

Next priorities are selector providers `0xAB08`, `0xAB7C` and `0xECA8`, retaining `0x1AB48` as an unprovided table-content dependency. A worthwhile future feature is a **firmware SHA-256-based memory/ROM compatibility report**. Only its offline check exists; App and device integration have not been implemented.
