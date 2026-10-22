# SPI transfer leaf: offline native reconstruction

[繁體中文](README.md)

The selected [spi_transfer_ports.c](src/spi_transfer_ports.c) compiles as C11 and C++17 under the pinned LLVM recipe. [component.ld](component.ld) places its regions at `0x16896`. All 72 bytes / 25 instructions equal official ID2966 V4.1.60 `[0x16896, 0x168DE)`, SHA-256 `654d0f600794c1548c617d0f476ca4f0fa5aaf780f49be7c328b3df69e8878dc`.

This is a composition of eight C-generated machine regions and explicit architectural ports, **not independently callable ordinary C ABI functions**. C generates constants, volatile halfword accesses, truncation, masks and countdown arithmetic. Five compressed branch/jump instructions remain assembly ports. Local zero-displacement instructions receive standard ELF RVC relocations to genuine FUNC definitions. There are no copied opcodes, post-build object patches or ABS providers.

| Offset | Region | Bytes |
| --- | --- | --- |
| 0 | Entry: count=255, base | 8 |
| 8 | TX status / mask 2 | 8 |
| 16 | Low 16 bits, SH16, reset count/base | 16 |
| 32 | RX status / mask 1 | 8 |
| 40 | Fresh LHU16, low 8 bits, return | 10 |
| 50 | TX decrement / retry | 8 |
| 58 | Shared timeout: A0=0, return | 4 |
| 62 | RX decrement / retry / timeout jump | 10 |

Each stage reads status before decrementing `(count-1)&255` on a not-ready result, with at most 255 reads. Success leaves A0=data&255, A3=`0x40013000`, A4=1 and A5=256−RX read count. Both timeout exits leave A0=A4=A5=0. Only A0/A3/A4/A5 are written. `__builtin_unreachable` ends a C region; explicit branches and linker-verified fall-through define the actual machine edges. This does not establish ordinary C semantics across regions.

The retained single-function [spi_transfer.c](src/spi_transfer.c) also produces 72 bytes / 25 instructions, but its branch layout differs. Both ordinary and extreme probability hints produced identical code. It is not the selected implementation. LLVM expanded direct external compressed mnemonics; the strict footprint gate rejected that attempt. Explicit symbolic RVC relocations address that assembly issue without weakening the full-byte gate.

## Verification

Run from the project root with an existing LLVM 18 toolchain; no dependencies are downloaded. Override its location with `--llvm-bin`. Output directories must not already exist:

```sh
python3 -B experiments/tsl9-spi-transfer-leaf/verify.py --language c --out-dir experiments/tsl9-spi-transfer-leaf/build/my-check/c
python3 -B experiments/tsl9-spi-transfer-leaf/verify.py --language cpp --out-dir experiments/tsl9-spi-transfer-leaf/build/my-check/cpp
python3 -B experiments/tsl9-spi-transfer-leaf/verify.py --replay experiments/tsl9-spi-transfer-leaf/build/my-check/c/verification.json
```

Use `python` on Windows when appropriate. Formal builds are retained at `build/verified-v3/{c,cpp}`: each language has 2 actual ELFs, 8 inputs, 5 recipes, 10 artifacts and 36 negative controls. Both receipts pass read-only replay. `--require-firmware-ready` deliberately rejects with exit 1. The [public receipts](../../analysis/spi-transfer-native-2026-10-23/receipts/) are byte-identical original receipts created with path variables; local ELF/IR/MD/log artifacts are not published with them.

[pipeline.ld](pipeline.ld) supports a 352-byte **relocatable partial link**. Its diagnostic origin is not a device Flash layout. SPI references in the previous 280-byte pipeline can bind a genuine definition; packet-provider and complete runtime closure still require verification.

No target execution, ISA emulation, MMIO, BLE, CAN, flashing or firmware BIN generation occurred. Physical silicon/peripheral identity, complete IRQ/fault context, resident/startup and OTA compatibility remain unproved.
