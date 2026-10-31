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

The locally retained WCH CH32V20x [Flash reference driver](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_flash.c) V1.0.2 describes ordinary `FLASH_ErasePage` as 4 KB and `FLASH_ErasePage_Fast` as 256 bytes. The fast operation clears the address low eight bits and uses control bit `0x20000`, start bit `0x40`, and busy bit `0x01`. The reconstructed APP instructions at `0x18EC4..0x18EF2` also contain that alignment, set of control bits and polling. This is a static comparison to a candidate driver; it does not establish the device controller or complete API is identical.

The six destinations occupy distinct 256-byte numerical intervals but share the same 4 KB-aligned numerical interval `[0x08077000,0x08078000)`. Ordinary 4 KB erase cannot therefore be equated with this candidate fast-erase path, and 256-byte alignment alone does not establish the actual erase extent. Physical mapping, erase granularity, content preservation and write success remain unverified. The [static cross-check](check-erase-page-reference.py) reads existing local reference source and reconstructed source only; it does not execute the target.

## Copy112/133 versus CPU program256

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
