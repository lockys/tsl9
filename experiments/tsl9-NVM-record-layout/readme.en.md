# Six original NVM records and numeric memory requirements

[繁體中文](README.md) · [Settings/Flash chain](../tsl9-original-prebinding-settings/readme.en.md) · [Memory/ROM contract](../tsl9-memory-rom-contract/readme.en.md)

Seven complete existing C/C++ functions cover **628 CODE bytes/189 instructions**:initializer0x131C2 and six writers. Original BIN,both original-address C/C++ diagnostics and two independent ELF readers agree. New sources are compile-only numeric requirements,with **no new executable target CODE,APP integration or BIN**.

| Record | Numeric source | RAM destination | Copy bytes | Initializer guard | Writer | Additional CPU source bytes without initialization proof |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `0x8077a00` | `0x2000c29c` | 112 | ASCII ×4 | `0x13138` | 144 |
| 1 | `0x8077900` | `0x2000c494` | 256 | `0x5A` at +255 | `0x12e54` | 0 |
| 2 | `0x8077800` | `0x2000c30c` | 256 | `0x5A` at +255 | `0x12ee6` | 0 |
| 3 | `0x8077700` | `0x2000c594` | 256 | `0x5A` at +255 | `0x12f48` | 0 |
| 4 | `0x8077600` | `0x2000c694` | 256 | `0x5A` at +255 | `0x13052` | 0 |
| 5 | `0x8077500` | `0x2000c40c` | 133 | `0x5A` at +132 | `0x130d6` | 123 |

Independent decoding pairs every read destination/count with its writer source/count. Earlier reads dominate later reads in the complete normal-return CFG. Fallbacks remain conditional;successful completion of all accesses on every startup is not claimed.

Record0 checks four ASCII bytes32..126 atRAM0x2000C2A8..0x2000C2AC. Other records compare their last copied byte with0x5A. Every guard lies inside its copied record. **Marker agreement does not establish full contents,CRC or backup integrity.** Seat/lock/product meanings are not assigned from these numbers.

## Numeric RAM/NVM ranges

RAM payload totals **1,269 bytes**,with nonoverlapping numeric buffers spanning[0x2000C29C,0x2000C794),1,272 bytes. The three-byte gap is[0x2000C491,0x2000C494). All fit the original reset zero interval[0x20004080,0x2000C958). This does not prove physical RAM,ownership,DMA/alias safety or stable contents after IRQ activity.

Six writer destinations form contiguous256-byte aligned numeric pages **[0x08077500,0x08077B00),1,536 bytes**. Under an additional flat contiguous Flash assumption based at0x08000000,the required end offset is0x77B00/490,240 bytes. **That flat map/capacity assumption is unproved.** Literals alone do not identify chip capacity,aliasing,ROM/data-Flash roles or physical writable regions.

### Two candidate erase granularities

**Candidate write-protection grouping.**

Under numerical sector arithmetic using 4 KiB sectors numbered from `0x08000000`, all six settings pages lie in **sector 119**. WCH's [reference manual V2.2 section 32.6](https://cdn.icstop.com/upload/pdfs/9e/c8/9ec8bf12faf8342b9fb46b48d65fa73a.pdf) says option-byte `WRP3` bit 7 controls sectors 31–127. If that description applies to the device, sector 119 shares its write-protection control with other sectors. This protection grouping is not the same as the candidate fast erase's 256-byte page granularity.

Section 32.4.7 of the same manual also gives a general statement that each `FLASH_WPR` bit represents 4 KiB; the apparent difference between the descriptions requires clarification before assigning the physical GBU6 protection mapping. The device option bytes, protection state, mapping and write results were not read or confirmed; no protection settings were changed. The [checker](check-erase-page-reference.py) verifies sector arithmetic only.

On 2026-10-31, the [official WCH CH32V20x Flash header](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x_flash.h) defines `FLASH_WRProt_Sectors31to127` as mask `0x80000000`, while listing individual bits for sectors 0–30. This official source supports the section 32.6 grouping interpretation, but its comments mix page and sector terminology and main may change. It does not by itself resolve the section 32.4.7 wording difference, confirm device options, or prove an actual write result.


[WCH reference manual V2.2 section 32.2.1](https://cdn.icstop.com/upload/pdfs/9e/c8/9ec8bf12faf8342b9fb46b48d65fa73a.pdf) states that fast-programming-related functions must reside in zero-wait Flash. The notes to [CH32V208 datasheet V2.6 Table 2-1](https://atta.szlcsc.com/upload/public/pdf/source/20230601/07AAED594F3221B9A55F84D1BC470848.pdf) identify the listed Flash size as the zero-wait region and list 128/144/160 KiB configurations paired with RAM sizes. If the device uses the corresponding contiguous low mapping, the original APP's candidate fast-erase/program functions `0x18EC4..0x18F56` fit all three zero-wait ranges. This conditional result concerns **function placement**, not a requirement that the programming destination reside in zero-wait Flash.

Numerical compatibility does not establish actual option settings, instruction mapping or successful Flash operation; one interval does not cover the entire call chain, instruction fetches or interrupt conditions. The manual also requires exiting enhanced read mode before programming or erasing; the device mode and compliance remain unknown. The checker pins reconstructed instruction sources and checks function-address arithmetic without modifying Flash.


WCH's *CH32F/V20x_V30x_V31x Reference Manual* **V2.2**, [Figure 1-12 and section 1.3](https://cdn.icstop.com/upload/pdfs/9e/c8/9ec8bf12faf8342b9fb46b48d65fa73a.pdf), depicts CH32V208 code Flash at `0x08000000` with a 480 KiB maximum, and says program-Flash boot maps it to the low address area while retaining access at `0x08000000`. This supplies **conditional documentary support** for the earlier low/high mapping hypothesis; it is not a measurement of the actual device boot mode or each offset. WCH's [official manual page](https://www.wch.cn/downloads/CH32FV2x_V3xRM_PDF.html) lists a newer version; the figure and text checked here are V2.2 and the versions have not been compared in full.

If the illustrated 480 KiB maximum is interpreted as a contiguous range beginning at `0x08000000`, its exclusive end is `0x08078000`; all six settings pages fit this **maximum numerical range**, with 1,280 bytes between the final page end and that limit. This does not establish the actual GBU6 capacity, Flash/RAM allocation, page ownership, writability or aliasing, and cannot by itself supply a missing provider or justify flashing. Real hardware and other document versions remain unverified. The [checker](check-erase-page-reference.py) verifies interval arithmetic without reading the device.

The locally retained WCH CH32V20x [Flash reference driver](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_flash.c) V1.0.2 describes ordinary `FLASH_ErasePage` as 4 KB and `FLASH_ErasePage_Fast` as 256 bytes. The fast operation clears the address low eight bits and uses control bit `0x20000`, start bit `0x40`, and busy bit `0x01`. The reconstructed APP instructions at `0x18EC4..0x18EF2` also contain that alignment, set of control bits and polling. This is a static comparison to a candidate driver; it does not establish the device controller or complete API is identical.

The six destinations occupy distinct 256-byte numerical intervals but share the same 4 KB-aligned numerical interval `[0x08077000,0x08078000)`. Ordinary 4 KB erase cannot therefore be equated with this candidate fast-erase path, and 256-byte alignment alone does not establish the actual erase extent. Physical mapping, erase granularity, content preservation and write success remain unverified. The [static cross-check](check-erase-page-reference.py) reads existing local reference source and reconstructed source only; it does not execute the target.

## Copy112/133 versus CPU program256

### Status handling in the settings write chain

The original-address reconstruction in `src/native/startup/settings_defaults.c` at `0x13154..0x1316A` calls `0x9C0A` and then restores the stack and returns without branching on its return register. In `src/native/receive/ota_runtime.c`, `0x9C0A..0x9C4A` calls unlock, writes `0x31` to `0x4002200C`, then calls erase, program and lock without an intervening error-status branch. This observation is limited to this chain; other callers may verify independently.

The reconstructed candidate erase and program leaves `0x18EC4..0x18F56` poll bits `0x01` or `0x02`; no timeout counter or separate write-protection-error branch appears in those leaves. In WCH's [CH32V20x Flash driver](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_flash.c), `FLASH_GetStatus` separately checks the write-protection error and `FLASH_WaitForLastOperation` has a timeout. These are different functions: this comparison does not establish that the APP uses that WCH API or predict physical error behavior. Status clearing, bus mapping and the physical implementation remain unverified; a normal return alone does not prove successful persistence.

All writers allocate272 bytes,saveRA atSP+268,copy their record through table0x4004C to ownSP,and call0x9C0A. The previously verified program leaf reads256 source bytes,conditional on callee contracts,valid memory,no faults and poll completion;physical Flash commit remains unproved.

Four256-byte copies numerically cover the CPU source extent,not verified source contents. The112-byte writer leaves **144 additional bytes**,and the133-byte writer leaves **123 additional bytes** without explicit local fill/copy. Their initialization remains unknown. Both extents stay inside the frame and avoid savedRA. No stack contents or disclosure were observed. **Do not invent padding/old values,shorten programming or claim fully initialized pages.**

## Compile-only C/C++ requirements

[Header](requirements-v1.h) values are checked against independently decoded original instructions. [C/C++ assertions](layout-contract-v1.c) verify alignment,record counts,RAM nonoverlap/gap,reset-zero containment,source/savedRA extents and both additional source ranges. Actual C11/C++17 objects are identical,with **no allocated bytes,providers,imports,relocations or executable entry**. Objects are never executed.

[Evidence](evidence-v1.json) · [Receipt](verification-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-NVM-record-layout/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned local BIN,prior native artifacts and Windows NDK LLVM;no dependencies are downloaded. Add `--build-trial <fresh-name>` to compile a new numeric-contract trial. Other platforms are unverified.

APP stays159 C/H files/95.54% byte coverage,not functional completion. SDK stays20,490 CODE+256 DATA/10 genuine named dependencies. The4-byte startup source gap and physical ROM/RAM/ISA/IRQ/NVM/Flash/OTA compatibility remain open. No target/HOST-model/ISA/hardware execution. **Usable replacement firmware has not been successfully reconstructed.** Offline range/marker compatibility reporting for an authorized NVM backup remains an unimplemented candidate,without automatic migration or hardware writes.
