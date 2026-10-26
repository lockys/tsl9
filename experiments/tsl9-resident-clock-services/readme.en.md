# Clock-service candidate C/C++

[繁體中文](README.md) · [Timer service](../tsl9-resident-timer-service/readme.en.md) · [RAM layout](../tsl9-resident-task-layout-contract/readme.en.md)

Five complete bodies total **474 bytes/168 instructions**. This is a conditional public SDK V1.31 candidate; installed ROM identity remains unproved. The [source](resident_clock_services.c) uses original register context and C/assembly, not an ordinary HOST-callable C API.

| Function | Original range (end exclusive) | Bytes |
| --- | --- | ---: |
| TMOS_TimerInit | Flash 0x43F46..0x44022 | 220 |
| Provider registration | Flash 0x43B0A..0x43B28 | 30 |
| Delta provider | Flash 0x43D62..0x43DE4 | 130 |
| Default counter getter | Conditional RAM 0x20000986..0x200009BA | 52 |
| TMOS_GetSystemClock | Flash 0x43520..0x4354A | 42 |

**Actual checks:** identical C11/C++17 objects, 33 positive FUNC regions, 19 relocations, and every original-context encoded byte matched. Seven conditional Xwchc byte/halfword ports are checked against primary definitions and 28 official vectors. Compiled bleClockConfig_t assertions establish size16, alignment4 and offsets0/4/8/10/12; assertion objects allocate no runtime bytes.

## Observed flow

- Nonnull configs require nonzero callback, MaxCount, Frequency and Accuracy. Nonzero irqEnable additionally requires the BLE connection sum to be at most2. Optional rcCB runs before validation; normal return0 is not hardware-success proof.
- Accepted configs copy16 bytes to0x20003234; the raw callback is also stored at0x200031E0. When WaitWindow is zero, **ClockFrequency at offset8**, times1400, and1,000,000 form arithmetic-helper arguments; the low8 bits of returned A0 are stored. Helper0x6DF1A is unresolved; division semantics remain an inference.
- Registration installs0x43D62 at0x20003230, calls it immediately, then stores its return into baseline0x200031B4. The delta provider itself also updates that word. Reinitialization baseline semantics remain open.
- The delta provider forms the full64-bit raw-counter times1600 product and Frequency helper arguments, then follows equal/increasing/wrap branches. Actual unsigned operations are retained; no guessed arithmetic-helper implementation is substituted.
- The public getter adds a nonnull provider result to0x200031B0. The official header documents **0.625ms** units; this is not a measured physical frequency.
- The default getter temporarily clears bit14 of0x4002420C, reads0x200031B8/0x40024268, restores the original MMIO value and returns u32 `(software_word<<26) | ((~counter_word)>>6)`. Physical MMIO/IRQ semantics remain unproved.

Own frames are32/16/32/0/16 bytes, balanced on normal returns. These exclude callbacks, callees, IRQ and whole-program stack bounds. Numeric CODE pointers0x43D62/0x20000986 have real bodies but are not linker relocations; original-address execution linking was not performed.

## Original APP arguments

Three existing APP bodies total280 bytes; **no APP CODE is added**. Function0x19B56 clears the16-byte config, then supplies callback0x191C6, MaxCount0xFFFFFFFF and nominal **16000Hz/1000ppm**; irqEnable starts at zero. Callees, IRQ and aliases must still preserve the caller's configuration.

Call0x19BCC invokes official slot16 TimerInit. The outer caller overwrites its status at0x19B3A without using it. The existing90-byte counter callback0x191C6..0x19220 performs repeated-equal high/low halfword reads at0x40002818/0x4000281C, rechecks high and conditionally rereads low before composing32 bits. Retry termination, coherent snapshots and actual frequency remain unproved.

## Composition and limits

The real copy provider resolves this component's copy import. Actual nonloadable C/C++ ET_REL objects contain **3512 bytes/1242 instructions**, 312 positive FUNC regions and224 relocations, retaining every input byte, symbol and relocation. RAM0x2000061A/0x20002610 and Flash0x63DD0/0x6DF1A remain genuine imports, along with raw RAM/callback dependencies.

The previous **4-byte startup source gap** remains. No APP integration or new BIN is provided. Physical RAM/ROM/ISA, IRQ, stack, Flash and original-hardware OTA compatibility remain open. APP byte coverage stays **95.54%**, not functional completion. Clock-range, baseline and reinitialization diagnostics are unimplemented feature candidates.

Evidence: [full audit](audit-result-v1.json), [summary](summary.json), [original instructions](evidence-v1.json), [specification and hashes](spec-v1.json).

## Reproduce

Provide the original APP, SDK/header/instruction references and prior native artifacts listed by the spec, evidence and audit. Original SDK inputs and native artifacts are not included in this commit and are not downloaded automatically. From the project root, using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-clock-services/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-clock-services/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts, use `--replay experiments/tsl9-resident-clock-services/build/native-v1` for the first command and omit `--link-trial` for the second. No target, HOST model or ISA execution, hardware access or vendor API traffic was performed.
