# Core identifier diagnostic component: not flashable

[繁體中文](README.md)

This experimental function reads `marchid` and `mimpid`, then sends a 12-byte record to a caller-supplied synchronous callback: `T9D`, version 1, then two little-endian 32-bit values. It does not read UID, VIN, MAC, or peripheral MMIO. The callback must copy the record before returning because its stack buffer is temporary.

The [WCH QingKe V4 manual](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf) lists both CSRs as machine-mode read-only. That does not establish the installed core, calling privilege, observed values, or the full MCU part number.

From the manual's `marchid` bit encoding and `mimpid` definition, **if the core follows its WCH-V4C format**, the candidate values are `0xDC68D883` and `0xDC688001`. The offline decoder reports `matches_wch_v4c_manual_pattern: true` when both match. This is a core-encoding comparison, not proof of CH32V208GBU6, resident ROM version or any physical measurement. A mismatch alone does not exclude other manual versions or implementations.

**The compiled output contains function code only: no boot entry, BLE transport or OTA firmware structure. It cannot be flashed or run independently.** The integration site, memory, callback and notification contracts remain unverified. It is not connected to the app and has not observed a device. Matching C and C++ builds are offline evidence, not device validation.

The local experimental `NOT-FLASHABLE-diagnostic-component.bin` is 90 bytes, SHA-256 `52a636714bf33832c99b2883e76e16d3380cef5ad66580fa700ef98e356c8cd2`. If a single 12-byte binary record is obtained later through a validated integration, `python experiments/tsl9-csr-probe/decode_probe.py record.bin` decodes it offline; it does not capture hardware logs.

`diagnostic_transport.c` is a separate candidate adapter: its caller supplies the transmit function, connection and command, and it passes the same record in the four-argument order observed at original `0x8A56`. It does not choose a command or patch the firmware. The interface, memory and saved-register contracts must match on the actual device, and the sender must finish copying the stack payload before returning. The original sender has connection and other guards; invoking it does not prove notification delivery. This offline component is not flashable firmware.

The candidate rejects connection `0xFFFE` before reading CSRs: prior original-code analysis shows that `0x8A56` treats this as an empty-slot sentinel and it cannot pass either connection-slot guard. Other values still need to match an actual connection and notification configuration; this check does not establish connection or delivery. See the [original transmit guards](../tsl9-six-dependency-ledger/readme.en.md).

`NOT-FLASHABLE-transport-component.bin` contains this 118-byte function; offline C and C++ builds match, SHA-256 `9687a6159704a4dee8e2b89d34ae5704f1564d53fb04e5d1e95a5a1862469d1e`. Disassembly checks the sentinel guard, two CSR reads and four call arguments. The original device, BLE notifications, app reception and OTA are not tested. **Do not flash.**

At `0x1870C` the original reset ORs `0x1888` into `mstatus`, setting MPP bits 12:11 to 3. The [WCH QingKe V4 manual](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf) states that MPP=3 retains machine mode on MRET. If the installed resident matches the candidate, startup and MRET complete and MPP remains unchanged, this supports the required CSR privilege at APP entry; it does not prove the privilege at a later call site or the values on the device.

## Candidate for memory configuration

The [WCH V2.2 reference manual section 32.4.6](https://cdn.icstop.com/upload/pdfs/9e/c8/9ec8bf12faf8342b9fb46b48d65fa73a.pdf) describes `FLASH_OBR` at offset `0x1C` as a read-only option status register and lists CODE/RAM configurations of 128/64, 144/48 and 160/32 KiB for CH32V20x_D8W. Together with the peripheral base in the [WCH header](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h), this gives candidate address `0x4002201C`.

The manual labels the field `[9:8]` but describes its configurations using three-bit patterns `00x`, `01x` and `1xx`; that inconsistency remains unresolved. `FLASH_OBR` also contains other status, so its entire word must not be treated as a memory configuration or shared as device protection information. The current program **does not read this register** and makes no claim about the device's RAM/Flash selection. Confirm the applicable version, field semantics and device access conditions before considering a narrowly masked field.

Direct visual inspection of [page 598 of the WCH V2.2 PDF (printed page 594)](https://static.chipdip.ru/lib/820/DOC059820997.pdf#page=598) confirms the graphic simultaneously shows `[9:8]`, `[2:0]`, and three-bit patterns; the inconsistency is present in the page, not just text extraction. The inspected PDF SHA-256 is `29575ed31788d4a3576a039a9c8cc3410280a36d73bcbf6509805203449d232d`. This does not establish a correct interpretation on the device.

The [WCH official download page](https://www.wch.cn/downloads/CH32FV2x_V3xRM_PDF.html) lists V2.5 for CH32V208GBU6; the table in the [English manual mirror, section 32.4.6 (printed page 603)](https://ch32-riscv-ug.github.io/CH32V20x/datasheet_en/CH32FV2x_V3xRM.PDF#page=608) still labels the field `[9:8]` while using three-bit patterns. The newer version therefore does not resolve the ambiguity. This is a document comparison, not a device register read or proof of its memory configuration.

In the same manual, [section 32.6 table 32-4 (printed pages 609–610)](https://ch32-riscv-ug.github.io/CH32V20x/datasheet_en/CH32FV2x_V3xRM.PDF#page=614) separately specifies three-bit option-byte `USER[7:5]`: for CH32V20x_D8W, `00x` = 128/64, `01x` = 144/48 and `1xx` = 160/32 KiB (CODE/RAM). The [pure function](decode_user_memory_mode.py) decodes only a caller-supplied three-bit integer; tests cover all eight synthetic values and do not read a device or option bytes. The table does not prove the exact correspondence between `FLASH_OBR[9:8]` and `USER[7:5]`, the actual device configuration, or flash readiness.

Compared with the [18-version startup-clear analysis](../tsl9-six-dependency-ledger/readme.en.md), assuming one contiguous RAM region beginning at `0x20000000`, the reset exclusive endpoints `0x2000C94C..0x2000C958` exceed a 32 KiB region by 18,764–18,776 bytes and a 48 KiB region by 2,380–2,392 bytes, but fit within a 64 KiB region. Initial SP `0x20010000` is the exclusive upper bound of the 64 KiB region, not a directly readable byte. This is conditional: remapping, aliases and other actual memory arrangements are not excluded; it proves neither the device mode nor successful startup. The pure `reset_extent_comparison` calculates these assumptions without accessing hardware or firmware.
