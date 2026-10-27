# Original APP callback provenance and initialization conditions

[繁體中文](README.md) · [Prior complete parser/C/C++](../tsl9-resident-task-parser/readme.en.md) · [Existing clock services](../tsl9-resident-clock-services/readme.en.md)

[C/C++ ABI assertions](callback_abi.c) and cross-unit proof connect four original indirect-call sites to configuration sources. **No new firmware CODE,provider or BIN;original indirect calls remain unchanged.**

Five complete existing APP bodies,total **972 bytes/325 instructions**:0x8E88,0x199E2,0x19B16,0x19B56,0x191C6. Whole CFGs/own frames checked;every original BIN byte equals both retained original-address C/C++ diagnostic artifacts,two independent ELF readers agree.

## Three conditional clock providers

APP0x19B56 zeros a16-byte caller config,then sets getClockValue=0x191C6,ClockMaxCount=0xFFFFFFFF,numeric frequency16000,accuracy1000,irqEnable0. Actual0x19BCC uses candidate slot16/word0x40074→TimerInit0x43F46.

Nonnull success-value path checks four nonzero fields;irqEnable0 bypasses the additional connection-count guard. Original copy16 writes0x20003234,then copies the first word to0x200031E0. Under successful path,copy/callee contracts and stable fields:

| Indirect call PC | Fresh pointer slot | Conditional original APP body |
| --- | --- | --- |
| 0x5F6D6 | 0x20003234 | 0x191C6..0x19220 |
| 0x5F708 | 0x200031E0 | 0x191C6..0x19220 |
| 0x4346C | 0x200031E0 | 0x191C6..0x19220 |

0x191C6 is an existing **90-byte/28-instruction,frame0 leaf**. Original bytes and both native diagnostics prove no encoded stores,callees,CSR requests or RA/SP/GP/saved-register writes. It rereads numeric MMIO halfwords0x40002818/0x4000281C and returns u32(high_last<<16|low_last). **Termination,coherent snapshot,physical MMIO semantics/read effects and actual frequency remain unproved.**

16000/1000 are original configuration values,Hz/ppm according to the candidate header,not measurements. Default/invalid TimerInit paths remain distinct from the nonnull-copy path. APP overwrites return status at0x19B3A;**making the call does not prove initialization succeeded.**

## Optional status callback after copy

APP0x199E2 requests zeroing64-byte config[SP+16,SP+80) at0x19A38. Primary staCB offset52 maps to[SP+68,SP+72). Later explicit local stores and six-byte MAC copy[SP+40,SP+46) avoid this word. No actual MAC contents observed/published.

Candidate BLE Init success-value path copies64 bytes to0x200031EC,so offset52 maps to0x20003220. With correct memset/copy contracts and no callee/alias/IRQ/other overwrite,the slot is conditionally zero;null guard0x434A4 skips optional call0x434AA.

**This applies only after completed BLE copy64 and stable state. It does not establish staCB before copy or during earlier heap calls.** The existing early-heap uncertainty receipt stays unchanged.

## C/C++ and open conditions

[requirements-v1.h](requirements-v1.h) contains conditional numeric requirements only. [Assertions](callback_abi.c) check primary clock/status function-pointer types,RV32 widths,clock16/BLE64 layouts and offset52. Actual C11/C++17 objects match,**zero allocated bytes/providers/imports/relocations**. Include closure allows only the two current sources,the exact hash-pinned official header and compiler resources.

Original APP local normal flow calls BLE and clock initialization before later RF calls. **No proof that all global dispatch follows initialization,and no observed live callback values.** Matching installed ROM,successful paths,valid stable memory,copy/memset/private-callee contracts and no asynchronous alias overwrite remain required. All live callbacks/whole-program effects are not closed.

SDK composition stays **25,102 CODE+256 DATA/8,580 instructions/11 named gaps**;four original indirect-call ports remain. APP stays159 C/H files/95.54% byte coverage,**not functional completion**. The4-byte startup source gap and ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain open.

[Evidence](evidence-v1.json) · [Full verification](verification-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-original-callback-provenance/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Requires pinned local APP/SDK,prior native artifacts and Windows NDK LLVM. No downloads;other platforms unverified. No target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only callback-source/initialization-condition display remains an unimplemented UI candidate,no live callback/hardware changes.
