# Packaging/forwarding entry and transport boundary

[繁體中文](README.md) · [C implementation and formal checks](../../experiments/tsl9-queue-filter/README.md) · [Original69 instructions](../queue-consumer-2026-10-23/next-filter.json)

This milestone reconstructs and independently verifies 188B of C/C++ for 82D2. Diagnostic ET_REL retains seven relocations. Downstream 8A56 and dynamic resident effects remain open; this is not an installed executable image.

A [genuine partial link of queue, filter and two GP providers](../../experiments/tsl9-queue-dispatch-component/README.md) contains 526B, 184 instructions and 19 FUNCs. Three call symbols now bind to real C definitions; six strong UND symbols and 32 pending RELAs remain. Symbol binding does not mean machine control immediates have been applied. This component and the earlier nine-span IRQ graph are separate proofs, not a complete firmware image.

Both C/C++ formal checks, independent read-only replays and rejection by the firmware-ready strict gate were verified. The [milestone index](summary.json) records source and artifact hashes. Filter receipts retain their exact bytes. Partial-link and curated-source receipts containing absolute local paths have explicit path-only public derivatives; the originals remain local.

| Evidence | Confirmed fact | Boundary |
| --- | --- | --- |
| `82D2..8304` | 64B frame, S0..S9/RA, initial table`2000C794` and selector0 | Table calculation requires original PC placement; full memory ownership unknown |
| `8308..8326` | Stride4; checks FFFE sentinel, kind2 and nonzero flag | Then-live S registers after opaque calls; two iterations are not guaranteed |
| `8328..8356` | Save flag to S4 before length check; pack ID/tag; fresh indirect `[S9+76]` call | Nonzero does not prove transmission |
| `8358..8368` | Fresh byte[S1+2], halfword[S0+2], SP+4; add2 to A3, A1=C0, C.JAL8A56 | On normal byte reads A3 is2..257; post-provider memory validity unknown |
| `836A..838C` | Then-live S2 controls cold loop; return then-live S4; cold path sets selector1 | C.JAL returns836A; neither a4-byte call nor a non-linking jump is equivalent |

The complete [8A56 transport framing body](next-transport.en.md) is now bounded: 280B/96 instructions including two indirect admission calls, checksum loop and tail provider. It is the next C reconstruction target. BLE/UART/CAN hardware attribution and seat/DND correspondence remain unproved.

Potential diagnostics, not yet implemented: offline frame length/checksum checks, visible routing conditions and separate records for nonzero flag, call occurrence, provider admission and observed transmission. These could help isolate update/data-transfer issues without changing the original protocol, routing layout or device behavior.
