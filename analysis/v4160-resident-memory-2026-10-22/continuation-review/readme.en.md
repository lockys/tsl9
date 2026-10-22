# BLE initialization defaults and the post-copy callback boundary

[繁體中文](README.md)

Both retained candidate initialization functions are read in full: **228 bytes / 92 instructions**, V1.40 at 0x43D0A..0x43DEE and V1.31 at 0x43C7E..0x43D62, with exclusive upper bounds. They remain conditional reference implementations, not identified installed ROM.

The formerly unsupported bytes are conditional Xwchc `QK_C_LBU` encodings. Operands follow the retained SHA-256-pinned TableGen file; radare2 floating-point labels for these bytes are not accepted as their semantics.

After the 64-byte copy returns, A5 is formed from live S0 plus the configuration offset. Eight default stores touch configuration offsets 12 (halfword), 14 (byte), 16 (halfword), and 15, 18, 19, 20, 22 (bytes). All miss the complete `staCB` word at 52..55. This interval has no other call or explicit S1 destination. The offset22 test reads live S1, rather than the copied configuration.

The first subsequent indirect call freshly loads configuration field44; a zero pointer skips it. A nonzero pointer is called at V1.40 0x43DC4 / V1.31 0x43D38. Header order and the existing RV32 layout suggest the name `tsCB`/temperature; this round adds no compiled offsetof44 evidence. Actual original App AUIPC at 0x19A92, ADDI -674 at 0x19A96 and SW SP+60 at 0x19A9E put the numeric value **0x197F0** into App config+44. Connecting that source value to the invoked pointer still requires the mapped-copy, valid-memory and noninterference premises.

A preliminary static view of 0x197F0 shows a 128-byte frame, ADC/MMIO accesses and a nested call; its effects are not proved here. Initialization also calls 0x43BCA / 0x43B3E at V1.40 0x43DD8 / V1.31 0x43D4C. Default-store disjointness does not prove a zero callback word throughout initialization or later runtime.

```sh
python analysis/v4160-resident-memory-2026-10-22/continuation-review/check.py --project-root .
python analysis/v4160-resident-memory-2026-10-22/continuation-review/check.py --project-root . --candidate-root /path/to/retained-reference --firmware /path/to/ID-2966-V4.1.60-decoded.bin
```

The default checks metadata and closed files only. Explicit inputs reread both complete candidate bodies, the original App's 42-byte callback-setting slice, and reject six valid single-operand raw-byte controls preserving instruction shape: default load/store displacements and the callback-field displacement.

`ledger.json` records all typed rows, bytes, hashes and controls. These are static source/interval checks. There is no CPU-state execution, RV32/ISA emulation, MMIO or hardware operation, provider/BIN generation, or proof of installed ROM, IRQ, Flash/NV or BLE OTA compatibility.
