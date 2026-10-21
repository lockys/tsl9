# Selected BOOT ID2580 command source

This package pins the selected 12,288-byte BOOT, SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`. Its analysis base is `0x1000`; this is a retained-file coordinate, not a measured physical load. The complete command body is `[0x21BE,0x235C)`: **414 bytes, 144 instructions**, body SHA-256 `44702abb50c4489f378bb1036d8cf949817301e2e07d8af8434f7d6e119438d5`.

`source-map.json` contains every body PC, file offset, width, raw instruction and decoded direct-control operand, plus all local successors, seven delegated direct call sites, one loaded-pointer call, two delegated tails and the local return. All 144 starts are reached in the static graph when both branch outcomes and normal-return continuation edges are considered. This is a bounded control graph; it does not execute instructions or prove feasibility of every graph path. `retained-source.json` contains only the 239 selected rows for this body and four bounded dependency views, **650 source bytes total**, instead of requiring the older 927-row tree at replay.

`contract.json` is the numeric/live-memory adapter specification. In particular:

- W reads active at live `GP+139`, requires `n=1026`, reads page low byte at `payload+1` before high byte at `payload`, and accepts unsigned page `0..95` at alias `0x08008000+page*1024`. Unaligned source requests `READ32(0x4004C)` before calling that loaded pointer with a 1024-byte copy request. It then requests four `0x20E6` program operations of 256 bytes. Readback at `0x2282` reads Flash before the live source read at `0x2288`; a mismatch returns silently.
- U clears active before delegated UID validation. Raw UID result zero means match; the length supplied is `uint8(n-1)`. A match tails to `0x2ABA` with `(context,'U',0)`. It does not activate W.
- S stores payload/length at then-current `SP+8/+12`, calls UID, and reloads both from then-current SP before branching on the UID result. It reads mode only afterward. Success writes active one, calls cancellation and selector-2 metadata, then reloads both stack slots again. Metadata's numeric return is ignored; HALT/TRANSFER does not become a normal return. Failure clears active, writes `0xFF` to the freshly reloaded payload and echoes through `0x2AA0`.
- E reads active, overwrites the incoming payload/length registers before using them, clears active, requests the `0x192C/200` and `0x20E2/400` callbacks, then requests an empty E response. This body has no E UID, length or mode check. R has no local page-read case and returns through the unmatched-command path.

UID, the loaded copy pointer, program256 (`0x20E6`), cancellation, metadata (`0x2184`), scheduling and response (`0x2AA0`/`0x2ABA`) remain delegated boundaries. This package does not implement their memory, Flash, timer or transport effects. The observed register interface is not an original C signature. Normal callee-save behavior is an explicit adapter assumption; the source itself uses live SP/GP, and this report does not validate physical stack/RAM, resident ABI, installed BOOT version or IRQ behavior. No real UID bytes or packets were read or generated.

The checker independently decodes control/load/store fields and rejects **18 in-memory raw operand mutations** through the same bounded semantic gates. It also checks the complete BOOT hash, every retained raw row, each source span and the exhaustive u16 page arithmetic. The historical seals were verified when extracting these rows. Their hashes remain provenance records; ordinary portable replay does not need the older evidence tree.

From any working directory, use an existing exact BOOT file and this copied source package:

```powershell
python -B "<source-package>\inspect-source.py" --check --firmware "<absolute-ID-2580-V1.0.00-decoded.bin>" --source-root "<source-package>"
```

Optional additional historical-chain validation in the original evidence workspace:

```powershell
python -B "<source-package>\inspect-source.py" --check --firmware "<absolute-BOOT>" --source-root "<source-package>" --verify-historical --workspace "C:\Users\locky\Documents\Codex\2026-10-13\rea-https-github-com-morluto-rea"
```

`--check` is entirely read-only and compares both generated JSON files byte for byte. `--write` is restricted to this checker's own directory and refuses a sealed package. No network, target execution, ISA emulation, hardware operation, new provider, ROOT change or D change is performed.
