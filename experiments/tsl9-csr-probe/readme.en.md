# Core identifier diagnostic component: not flashable

[繁體中文](README.md)

This experimental function reads `marchid` and `mimpid`, then sends a 12-byte record to a caller-supplied synchronous callback: `T9D`, version 1, then two little-endian 32-bit values. It does not read UID, VIN, MAC, or peripheral MMIO. The callback must copy the record before returning because its stack buffer is temporary.

The [WCH QingKe V4 manual](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf) lists both CSRs as machine-mode read-only. That does not establish the installed core, calling privilege, observed values, or the full MCU part number.

**The compiled output contains function code only: no boot entry, BLE transport or OTA firmware structure. It cannot be flashed or run independently.** The integration site, memory, callback and notification contracts remain unverified. It is not connected to the app and has not observed a device. Matching C and C++ builds are offline evidence, not device validation.

The local experimental `NOT-FLASHABLE-diagnostic-component.bin` is 90 bytes, SHA-256 `52a636714bf33832c99b2883e76e16d3380cef5ad66580fa700ef98e356c8cd2`. If a single 12-byte binary record is obtained later through a validated integration, `python experiments/tsl9-csr-probe/decode_probe.py record.bin` decodes it offline; it does not capture hardware logs.
