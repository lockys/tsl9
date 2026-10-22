# Status reads and flag updates:16FB6

[繁體中文](README.md)

The official ID2966 V4.1.60 handler `[0x16FB6,0x17002)` is76B/21 instructions. Captured vector slot39 contains`0x16FB6`. Its readable C core:

1. Fresh READ32 at`0x40010414`; if bit64 is set, WRITE32 of64 to that address, then fresh READ8 at live`GP+360`, OR1 and WRITE8 back.
2. Read the status word again; if bit128 is set, WRITE32 of128, then a separate fresh READ8 at the current`GP+360`, OR2 and WRITE8 back.
3. Execute MRET through the minimal architectural port.

The two reads and byte updates are never merged or replaced with snapshots. Actual volatile operations perform the C calculations/conditions; empty A4/A5/GP register ports preserve original boundaries without opcode carriers. Before normal MRET, absent second bit gives A4=0/A5=`40010400`; present second bit gives A4=128/A5=fresh flag byte OR2. Only A4/A5 are written locally; there is no extra frame, GP/SP/RA write or call.

## Evidence and limits

An initial candidate failed compilation because it required reserved SP. A revised candidate in local`build/probe-v1` is74B/20 instructions and fails full equality; its source snapshot and receipts are retained. Explicit original base/branch ordering in C makes both C11/C++17 objects in`build/probe-v2` match every original byte.

The formal component uses`rv32imac_zicsr`; the curated source uses a separately measured`rv32imac_zicsr_zifencei` profile. Both use`-Oz` and permit only A4/A5 allocation. Function code anchors match; the complete ELFs and flags are not claimed identical across these profiles. Tools and source are hash-pinned, without flag searching or dependency downloads.

From the repository root, use`python3 scripts/verify-curated-source.py` to check curated provenance, or`py -3` on Windows. Formal local receipts/public evidence are recorded in the [analysis summary](../../analysis/init-write-sequence-2026-10-23/summary.json).

Formal local receipts are`build/verified-v3/{c,cpp}/verification.json`:23 negative controls per language and4 actual ELFs preserving all76B. Original CRLF receipt bytes/hashes stay local. Explicit LF public wrappers retain all JSON content and do not claim byte-exact original receipts. UND/ABS providers are zero; local FILE/mapping ABS metadata is listed separately.

```sh
python3 experiments/tsl9-irq-flag-leaf/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --build-root experiments/tsl9-irq-flag-leaf/build/my-run
python3 experiments/tsl9-irq-flag-leaf/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --replay experiments/tsl9-irq-flag-leaf/build/my-run/c/verification.json
```

MRET is a privileged return, not an ordinary C return. Its state effects, vector mode, saved IRQ context, peripheral identity, physical RAM/ROM and complete APP/OTA compatibility remain unproved. An82-word captured vector view does not establish the IRQ count. **This is not a flashable BIN; no RV32/MMIO execution/emulation, hardware action or network operation occurs.**
