# Frontier for integrating the six Flash functions

[繁體中文](README.md)

The checker reads the previous milestone's actual `source-integrated.o` and all 8,276 RELA records as data. The six original carriers cover 262 bytes and exactly match the selected vendor V4.1.60 ranges. No RV32 is executed.

Within recorded relocations, twelve references from outside the six owned functions enter function starts: eight target the quarter wrapper and four come from the `0x197BE` caller. Five owned helper calls and six owned polling/loop branches also need explicit replacement. Future integration must account for those eleven records while preserving the other 8,265 roles and multiplicities. This milestone creates no integrated replacement object.

The program function occupies 94 bytes of its original 100-byte extent. The six bytes at `0x18F50..0x18F55` have no proved new storage owner. The checker emits no padding and borrows no adjacent bytes. Absence of external interior targets in this exact object's recorded RELA does not exclude numeric indirect references, installed ROM references or unknown runtime entry points.

`report.json` retains the object digest, 23 relevant relocations and five semantic negative controls. Re-reading the actual historical object requires an explicit matching input:

```sh
python analysis/v4160-flash-native-2026-10-22/integration-frontier/inspect_frontier.py --project-root . --merged-object /absolute/path/to/source-integrated.o --check
```

Publication includes sealed reports, not historical build directories. Checking member digests alone does not establish a fresh destination object review. Board identity, physical Flash capacity, asynchronous state and BLE OTA compatibility remain unknown. No new BIN is produced.
