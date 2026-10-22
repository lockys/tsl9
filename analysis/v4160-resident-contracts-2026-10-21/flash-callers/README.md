# 197BE Flash caller and resident-record contract

The original V4.1.60 write-like hook is supplied by the199E2 initialization record, not by a proved OTA command path. At19A88 its address is stored at record+60;1979A is at+56 and197F0 at+44. The record is64 bytes at sp+16 and includes08077C00 at+8.19AEC passes it to the function pointer loaded from nominal resident slot400A4; a zero return continues, while nonzero enters the19AF0 self-loop. Current614 code has no direct-control edge to197BE and exactly one original canonical HI materialization at19A80. Unknown ROM/dynamic callers remain outside that bounded negative finding.

The saved V1.40 WCH header identifies candidate offsets+8 as SNVAddr (bonding-information storage),+56/+60 as Flash read/write callbacks, and+18 as TxNumEvent. This corroborates a BLE persistence/bonding-storage interpretation; it does not prove the original V1.3 resident ABI, actual callback invocation, operation modes, permitted addresses, record lifetime or exclusive persistence use. In particular, the raw byte3 at+18 must not be relabelled an OTA/Flash mode. The saved RV32 layout-probe source is pinned, but this checker does not compile it or claim the candidate header is the installed ROM.

197BE's exact normal-return sequence is:

1. Save entry destination D in s0 and source pointer S (entry a2) at sp+12; entry a1 is unused by this wrapper.
2.197C8 calls18E98 to write the four controller keys.
3.197CE calls18EC4 with D, aligning the destination down256 and polling the erase operation.
4.197D8 calls18EF2 with a0=D,a1=S,a2=S. Its length is fixed256; entry a2 is not treated as a length. Under terminating polls, source LW18F1E and destination SW18F26 perform64 word operations. The offset starts at zero because18F0E's masked status value is zero when18F10's loop exits, then18F30 adds4 until256.
5.197DC calls18EB6 to set controller lock bit15;197E2 calls19764 with a0=1.
6.197EA sets a0=0 and returns, without checking controller result or proving hardware success.

19764's54 original bytes are a polled-timer sequence: clear status bit0 atE000F004, read the u8 at gp+382, multiply it by input a0, write compare low/high atE000F010/14, OR control with16 then33, poll status bit0 at1978C/19790, and finally clear control bit0. The saved WCH core header maps this region to SysTick CTLR/SR/CMP. The scale, time unit, actual hardware clock and polling termination remain unknown. No CSR operation or interrupt-state save/restore occurs in either197BE or19764. Surrounding resident interrupt exclusion is unproved. The initializer's later E000E104/E000E108 writes are separate enable-like setup, not a critical-section contract around each Flash operation.

1979A supplies a separate read-like hook: entry(A,N,B) becomes nominal4004C call arguments(B,A,u32(N<<2)) at197AE, followed by constant zero. This does not identify the resident as memcpy or prove a readable extent.197F0 can separately retain its364-byte peripheral save/configure/poll/read/restore behavior; its candidate temperature-sample callback name is not a physical ADC/RF or OTA proof.

The existing D `experiments/tsl9-contract-model/src/flash_page.c` is useful semantic reference but is pinned by its own verifier/fixtures to Runtime SHA32639d7d...e0f60bcc and BOOT650cbb... . The recorded offered Runtime label isV4.1.00; a server registered-version fieldV4.1.60 is not that payload's identity. Its Runtime helpers18BE4/18BEC/18C0A/18C18/18C46 and delta15C02 differ from the ID2966 artifact0ee64183...fb667 used here. Its full page wrapper additionally clears/sets CSR800 with mask88 and writes controller status49, then omits19764. Those operations must not be transplanted into197BE. The old RAM/OTA bridge is an old host-model coupling, not proof that the current resident hook participates in OTA.

The safe readable-model boundary is therefore V4.1.60-specific original PCs and this exact call order, with synthetic MMIO/source/timer/GP providers. Unknown bits, unavailable/unaligned source words, unsigned wrap, poll budgets, HALT and TRANSFER must remain explicit. An artificial budget halt is not an original timeout return. Original callback signatures, hardware success, interrupt exclusion and OTA reachability remain open.

`proof.json` includes exact per-operation MMIO PCs, raw instruction evidence, record offsets, call-register ledger, both actual ELF identities, old-model comparison and input hashes. Every selected instruction is checked against both actual current ELF modes. The checker only parses bounded retained code and metadata; it does not execute a model, RV32 code, emulator or compiler, contact a service, access hardware, or modify ROOT/D/old seals.

```powershell
python -X utf8 -B apk-analysis/tsl9-v4160-resident-contracts-2026-10-21/flash-callers/inspect.py --check
```

`--check` is read-only and byte-exact. A copied report can use an explicit existing absolute `--workspace`; old D model files are immutable inputs to this source-version comparison. Target-ready, firmware-BIN, hardware-success and OTA-route claims remain false.
