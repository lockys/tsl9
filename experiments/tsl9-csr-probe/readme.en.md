# Core identifier diagnostic component: not flashable

[繁體中文](README.md)

This experimental function reads `marchid` and `mimpid`, then sends a 12-byte record to a caller-supplied synchronous callback: `T9D`, version 1, then two little-endian 32-bit values. It does not read UID, VIN, MAC, or peripheral MMIO. The callback must copy the record before returning because its stack buffer is temporary.

The [WCH QingKe V4 manual](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf) lists both CSRs as machine-mode read-only. That does not establish the installed core, calling privilege, observed values, or the full MCU part number.

**The compiled output contains function code only: no boot entry, BLE transport or OTA firmware structure. It cannot be flashed or run independently.** The integration site, memory, callback and notification contracts remain unverified. It is not connected to the app and has not observed a device. Matching C and C++ builds are offline evidence, not device validation.

The local experimental `NOT-FLASHABLE-diagnostic-component.bin` is 90 bytes, SHA-256 `52a636714bf33832c99b2883e76e16d3380cef5ad66580fa700ef98e356c8cd2`. If a single 12-byte binary record is obtained later through a validated integration, `python experiments/tsl9-csr-probe/decode_probe.py record.bin` decodes it offline; it does not capture hardware logs.

`diagnostic_transport.c` is a separate candidate adapter: its caller supplies the transmit function, connection and command, and it passes the same record in the four-argument order observed at original `0x8A56`. It does not choose a command or patch the firmware. The interface, memory and saved-register contracts must match on the actual device, and the sender must finish copying the stack payload before returning. The original sender has connection and other guards; invoking it does not prove notification delivery. This offline component is not flashable firmware.

The candidate rejects connection `0xFFFE` before reading CSRs: prior original-code analysis shows that `0x8A56` treats this as an empty-slot sentinel and it cannot pass either connection-slot guard. Other values still need to match an actual connection and notification configuration; this check does not establish connection or delivery. See the [original transmit guards](../tsl9-six-dependency-ledger/readme.en.md).

`NOT-FLASHABLE-transport-component.bin` contains this 118-byte function; offline C and C++ builds match, SHA-256 `9687a6159704a4dee8e2b89d34ae5704f1564d53fb04e5d1e95a5a1862469d1e`. Disassembly checks the sentinel guard, two CSR reads and four call arguments. The original device, BLE notifications, app reception and OTA are not tested. **Do not flash.**

At `0x1870C` the original reset ORs `0x1888` into `mstatus`, setting MPP bits 12:11 to 3. The [WCH QingKe V4 manual](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf) states that MPP=3 retains machine mode on MRET. If the installed resident matches the candidate, startup and MRET complete and MPP remains unchanged, this supports the required CSR privilege at APP entry; it does not prove the privilege at a later call site or the values on the device.
