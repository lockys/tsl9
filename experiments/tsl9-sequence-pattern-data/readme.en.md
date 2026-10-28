# Four paired-pattern channels and the candidate Boolean comparator

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ DATA](sequence_data.v1.c)

Follow-up:48B now have[curated SRC/original-coordinate backing](../tsl9-sequence-pattern-integration/readme.en.md),with95.67% static byte coverage. The archived checker below may reject the newer manifest;use the current integration entry.

The whole APP callback (**2,878B/912 instructions**) and whole candidate ROM comparator (**72B/23 instructions**) are checked. Forty-eight new readonly DATA bytes pass C11/C++17 compilation,original-byte comparison and an actual partial link. They are not yet curated into formal `src/` or placed at original addresses.

|Location|Confirmed static behavior|
|---|---|
|`0x12032`,`0x120A0..0x120A4`|Channel starts at0,increments through the mismatch loop and exits at4;comparison channels are0..3|
|`0x12046..0x1205E`|Loads state at `GP+332+channel`,passes `0x1A638+6*(2*channel+state)` with length6|
|Candidate slot `0x4003C`|Actual candidate target `0x20000442..0x2000048A`;valid nonnull equal buffers return1,a different byte returns0|
|`0x12072..0x12090`|A match increments state;first stage0→1 exits,second stage1→2 resets0 and hands off a channel+`0x80` marker|
|`0x1209C`|Mismatch clears the current channel state and advances to the next channel|

Four paired-pattern recognizers are a conditional semantic inference. `0x80+channel` is the low-byte marker handed to a common processing path;physical buttons or vehicle actions are not identified. A match in an earlier channel leaves later channels unvisited in this loop;do not simplify mismatch handling into an all-channel reset.

The candidate API does **not use standard C `memcmp` return conventions**. Null pointers or zero length also return1;the equality consequence requires valid nonnull six-byte buffers. It additionally saves/clears/restores MMIO `0x4002420C`,executes `fence.i` and contains a reference Xwchc `qk.c.lbu`. Actual native bytes,typed branches,whole CFG and all52 primary encoding examples are checked. Installed-ROM identity,physical Xwchc support and MMIO effects remain unproved.

Given state0/1 at each read,stable GP/saved-register contracts,valid buffers disjoint from the MMIO control word,and no alias/IRQ/DMA/nested-callback interference,only **8 records×6B=48B at `0x1A638..0x1A668`** are needed. The eight actual records form four pairs differing only in their first byte. This does not prove a global state invariant or original full declaration extent.

Byte width alone gives the conservative1,572-byte envelope `0x1A638..0x1AC5C`,including92 bytes beyond the provided APP and the deliberately withheld default word. **Only the conditional48 bytes are selected;no withheld payload or individual hash is read out/emitted.** This envelope does not prove an actual invalid read or firmware defect.

[`verification-v1.json`](verification-v1.json) records the whole48-byte frame/CFG,reaching definitions,candidate comparator and independent ELF-reader agreement. The new object contains one48-byte readonly OBJECT with zero CODE,relocations,named UND or ABS providers. C/C++ artifacts are identical. The partial component contains69,412 CODE and4,066 DATA bytes,preserving every input allocated byte,global symbol,typed relocation and all six UND.

Formal provenance stays161 sources and **73,430/76,800B (95.61%)**. No full `tsl9_registered_callbacks_static_data_1a638` provider alias,new BIN or physical hardware/ROM/RAM/IRQ/Flash/OTA compatibility is claimed. No target,HOST model,ISA emulator or hardware is executed.

With retained local artifacts and the fixed LLVM toolchain,replay without compiling:

```sh
python3 experiments/tsl9-sequence-pattern-data/verify-v1.py --tool-dir "$LLVM_BIN"
```

[Feature candidate](feature-candidates.json):offline diagnostics of pending stages,mismatch resets and marker provenance;not implemented and does not identify physical features.
