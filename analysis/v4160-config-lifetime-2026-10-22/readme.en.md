# Genuine C/C++ reply storage at the original position and config-entry lifetime

[繁體中文](README.md)

This round improves the OTA C/C++ pointer contract and narrows original-App write footprints. **No new BIN or target execution. The existing568-byte component/77,824-byte experimental image remains unchanged and unvalidated for flashing.**

## Actual C/C++ improvement

Two motivated profiles first materialize the complete Flash base after its range guard, avoiding separate constant/page values across the copy call and removing an extraS7 save:552B/eight saves. An explicitly aligned4-byte volatile native reply object, without extra initialization, then yields **550B/186 instructions/48-byte frame**.

Actual IR has one4-byte align4 alloca/lifetime4. The entireSP12..15 object is independent; saves startSP16. Local S reply writes onlySP12/13, optionally rewritingSP12 on failure, with length2. Empty E remains pointer0/length0, with correlated phi predecessors checked. Given equal entrySP, SP12−48 matches originalentry−36.

Original seven common save locations remain; new C additionally savesS6@16 and changes save order/internal callRA. Unknown providers may observe the whole frame, registers or bytes beyond the two-byte reply. Owned storage and equal numerical pointers do not prove the complete ABI. The original530-byte extent still leaves a20-byte excess.

[C/C++ code](../../experiments/tsl9-v4160-ota-reply-object/readme.en.md) | [Actual compilation/replay](implementation/readme.en.md) | [Independent object/IR/control review](object-review/readme.en.md)

## Local original-App footprints

- [MAC helper](mac-review/readme.en.md):18F56..18F88,50B/14 instructions. Two factory-address READ32s precede six storesA0+0..5, with no nested call/SP/S0/GP/RA change. The66B/24-instruction caller copies six bytes toSP40..45; other stores missstaCB68..71. Four raw controls.
- [Candidate fill leaf](memset-review/readme.en.md): both slot40048 values selectRAM2000039C,46B/14 instructions. MMIO save/zero/FENCE.I/restore also occur on null/zero length; normal return is advancedA0. Six valid raw controls.
- Given setup reachability, the reference leaf is actually called, SP+16 is nonnull with64 valid nonaliasing bytes, no MMIO/code alias or asynchronous modification occurs and accesses complete normally: fill writesSP16..79, includingstaCB68..71. Afterwards only the reviewed MAC call/six-byte copy and disjoint explicit stack stores remain. **App config+52 is therefore zero at19AEC BLE_LibInit entry under those premises.**

This is source-field/interval reasoning, without CPU-state execution. It establishes neither version-gate reachability nor installed ROM or permanent callback zero. Pre-copy numeric200004BC and liveS1 inside BLE_LibInit may change the source/registers and remain the next boundary.

## Verification and remaining conditions

Default metadata is distinct from explicit actual FW/candidate/ELF reads. The MAC ELF view checks only its50-byte subset, without claiming whole-image provenance. Native C/C++ compilation uses pinned Windows LLVM; Python/POSIX-shell interfaces are portable, without Linux/macOS/CI native proof.

Unchanged HOST algorithm/whole baseline compilation are not repeated. No RV32 execution/ISA emulation, BLE/UART/CAN/Flash, vendor API or device-ID transmission occurs. Historical seals/all BINs remain. Only independently verified new components/evidence are committed.

Physical board/installed ROM/BOOT, RAM/IRQ, Flash/NV ownership, complete unknown-callee/alias/async ABI and BLE OTA acceptance/recovery remain unproved. A proposed offline NV/ROM condition summary should distinguish premise-dependent values from hardware observations; it is not an implemented hardware feature.
