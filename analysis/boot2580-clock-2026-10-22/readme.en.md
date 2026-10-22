# BOOT clock source audit

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

Official ID2580 BOOT `[0x2C78,0x2D62)` and ID2966 Runtime `[0x1874A,0x18834)` are **byte-identical234B/93 instructions**, SHA256 `e0debe8b77025cfb56144045a0aa7524b7a2cd2ad0bd3daa2d880408ad9758f5`. File offsets are0x1C78 and0x1074A respectively.

[ledger.json](ledger.json) retains93 raw/operand rows,43 memory-access sites and14 read-modify-write pairs. Both original files were reread and all93 rows independently recaptured using existing radare2. No instruction, HOST model or MMIO executes.

## Bounded source contract

- No subcalls or CSR instructions. Own writes affect SP/A2–A5; normal return restores the16B frame.
- Numeric MMIO addresses are40021000/04/08; live stack fields are SP+8 and SP+12.
- First poll uses fresh counter/ready fields.4096 is the ordinary unaliased equality terminal;0x20000 is the ready mask.
- Status is read again after that poll; cold tail and both same-value writes remain observable. The final two polls have no software timeout.
- The leaf has no explicit numeric4004C store. Physical aliases, MMIO side effects, interrupts and other writers remain possible.

## Offline replay

```sh
python3 -B analysis/boot2580-clock-2026-10-22/check.py --project-root .
# Optional: add --r2-exe "/path/to/r2" for fresh static disassembly
```

`original_fields.py` retains only the existing raw-operand checking function; `original-runtime-rows.json` retains its source rows. Neither includes the old HOST test/report entry. Inputs stay inside this checkout rather than the historical workspace.

The readable behavior basis is [clock_contract.c](../../experiments/tsl9-v4160-clock-contract/src/clock_contract.c); see [boot-clock-init](../../experiments/tsl9-boot-clock-init/readme.en.md) for the new native component. Source equality establishes neither installed resident identity, physical frequency, complete ABI/IRQ nor OTA compatibility.
