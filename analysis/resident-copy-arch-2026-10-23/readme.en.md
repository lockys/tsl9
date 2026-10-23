# Resident copy candidate: 58B architectural reconstruction

[繁體中文](README.md) · [English](readme.en.md)

The selected [source](../../src/native/resident/copy_arch.c) reproduces all 58B/18 instructions of the public WCH V1.31 copy candidate when compiled as C11 or C++17 and linked at conditional RAM address `0x20000332`. Candidate source address is `0x405A2`; its `[0x4004C]` contains `0x20000332`. Source SHA-256: `d004661257866b3c8e11ad424dffc47c969f640f9d2bc87c6835aae9be9be660`.

This is SDK-candidate evidence. Original Runtime `[0x8000,0x1AC00)` and BOOT `[0x1000,0x4000)` do not include the slot. No installed-device resident dump is available. The cached V1.40 header names tmos_memcpy at `0x40000+0x34+6*4=0x4004C`; it does not establish the installed version or ABI. Header SHA-256 is `fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e`, from this [fixed official commit](https://github.com/openwch/ch32v20x/blob/baef0054588f4826548429ff4e7a9257d752ef2f/EVT/EXAM/BLE/LIB/wchble_rom.h#L2777).

The [implementation contract](../../experiments/tsl9-resident-copy-arch/README.md) retains MMIO/FENCE.I, register and fault-prefix instruction ordering. Linked code SHA-256: `558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36`; ELF SHA-256: `a7a4157ed51c60ad5d21e88ec913079b379c83dad40add0968f60fe4f95ed317`.

The [v3 receipt](evidence/candidate-v3.json) records 50 bounded negative controls per language and all18 LLVM address/byte rows. An [independent review](independent-review.json) rejects38/38 provenance/PHDR mutations; v3 fixes v2's missing p_align=3 rejection while preserving both earlier versions. Curation passes76 comparisons/152 objects over64 C/header files and38 native units.

[Publication provenance](publication-provenance.json) retains three portable receipts byte-for-byte, one compiler receipt as a newline-only JSON derivative and curation as a path-only JSON derivative. Original receipts and raw logs remain local. Complete JSON value equality is checked; public derivatives do not claim raw-receipt replay.

Historical source-package replay fails at `seal member drift:README.md`: actual README4704B vs sealed4750B. Other sealed members, source bytes and the23-operand gate match. The failure is retained; no old receipt/seal is repaired, and fresh byte verification does not depend on full-package replay.

Installed resident identity, complete startup, physical ISA/IRQ/MMIO and OTA compatibility remain unknown. No HOST model, ISA emulation, hardware/BLE/CAN/UART/Flash or network operation occurred. No flashable BIN was added; the prior740B transmit-chain proof is unchanged.
