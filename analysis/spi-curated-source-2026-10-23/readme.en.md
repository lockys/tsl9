# Selected SPI source promoted into src

[繁體中文](README.md)

The independently verified SPI source is now copied unchanged to [src/native/receive/spi_transfer_ports.c](../../src/native/receive/spi_transfer_ports.c). Both copies have SHA-256 `1f68851e9ae71d1ef56147e554fdaa53ae0918e2bfac73bad32a110549fe3182`. The inventory contains 49 C/header files and 23 native translation units.

The full C11/C++17 curation check passes **46 pairs / 92 objects**, including read-only replay. The previous 44 results, 88 objects, 88 MD files and dependency records are unchanged. Previous compiler commands differ only in build directory. All four new SPI objects equal the standalone native ELF.

Only SPI receives the new `rv32imac_zicsr` / A0,A3,A4,A5 profile; existing profiles and gates remain. Its dedicated gate requires 8 genuine FUNCs, 8 AX sections, 72 bytes, 5 defined RVC relocations and no UND/ABS provider. Resolved original72B equality, region adjacency and352B partial linkage remain the responsibility of the [separate experiment](../../experiments/tsl9-spi-transfer-leaf/README.md).

[summary.json](summary.json) records exact hashes and scope. The [public receipt](receipts/curated-source.json) is a path-only derivative. Its original remains local with SHA-256 `582f6d2aa8c3efb4e92c30b94cada79b106a3292377a4029659624ac6930b5fb`. Reversing the substitutions reproduces the complete original JSON. The public derivative is not an original replay receipt.

Local replay:

```sh
python3 -B scripts/verify-curated-source.py --replay build/curated-source/spi-20261023-v1/verification.json
```

No RV32/ISA/MMIO execution or BIN generation/flashing occurred. Legacy V4.1.00 HOST tests were not rerun. This proves source-copy/native-object consistency; packet/resident/startup/IRQ/physical-memory/OTA compatibility remains incomplete.
