# Record setup / control path

[繁體中文](README.md)

The four original routines at `0x93AA–0x94EE` are reconstructed as **324B /109 instructions /19 architectural regions**. Complete nominal-address C11 and C++17 code matches the original byte-for-byte. [record_program.c](../../src/native/receive/record_program.c) combines readable C memory/arithmetic operations with explicit physical-register, frame, PC-relative and control ports. These are not19 independently callable C ABI functions.

| Original range | Confirmed behavior |
| --- | --- |
| `93AA–93EE`,68B/19i | Read `[[GP+84]+2]` and byte`2000BEC0`; conditionally clear data and set bit0 of the16-bit value at`40000400` |
| `93EE–9410`,34B/12i | Write halfwords`FFFF→4000042C`, `0→4000043C`, then clear bit0 at`40000400` |
| `9410–9454`,68B/24i | If the old pointer is nonzero, call`[40068]`, clear`2000BECC/BEC8`; tail-transfer to`[40070]` with6×then-live S0 |
| `9454–94EE`,154B/54i | Unsigned19 guard,6B records and terminator. If registers retain entry values, ordinary records contain halfwords3000/40/80; the large branch writes3000/S0/0/0 |

Opaque transfers occur at`942A` (RA=`942C`) and`9452` (no new link; restored RA). Free/allocate and timer meanings remain candidates. Installed ROM, memory validity/ownership and physical purpose are unknown. S0/S1/SP are read fresh after opaque transfers: the entry guard cannot prove a post-call19-record bound. If the8-bit counter cannot equal post-call S1, the loop may not terminate. Different success/failure restore orders and every original-PC AUIPC are retained.

The actual genuine partial link is **2250B/778i/127 strong FUNC/109 pending RELA/2 UND**; missing direct providers are`12ABE` and`14D2E`. Diagnostic VMA0 AUIPC values do not point at original RAM and relocations remain pending: this object must not execute. The existing1588B nominal graph is unchanged. The new324B graph is proved separately, not promoted to complete firmware. Curation now covers66 C/H files,40 native units,80 comparisons and160 objects; all earlier78 result facts and old object identities are unchanged.

Trialv1 required a reserved SP after exposing S0 as a C output. Trialv2 reordered the A3 decrement before A5=0. Selectedv3 fixes this and matches all original bytes. Independent review found a nominal FUNC-owner escape in the first verifier; immutable old receipts/checker remain. Latest verify-v2 passes2600 negative controls per language and rejects the owner mutation in both. IR/LLVM logs are retained without claiming IR or LLVM semantic proof.

[Provenance](publication-provenance.json) identifies four exact portable receipts and one path-only derivative. A local ZIP retains62 original files, all member hashes checked. BIN/APK bytes and Git settings are unchanged. No target execution, ISA emulation, hardware access or firmware BIN generation occurs.

A possible future addition is post-call index/length consistency diagnostics; it needs the actual resident ABI and observation data and is not implemented. Original hardware, installed ROM, full startup/memory/interrupts and Bluetooth OTA remain unproved.

[Reproduction](../../experiments/tsl9-record-program/README.md) · [Summary](summary.json) · [Independent review](independent-review.json)
