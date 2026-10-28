# Counter DATA and the candidate ROM fill path

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ DATA](counter_data.v1.c)

Three whole APP functions (**592B/201 instructions**) and the whole candidate RAM fill function (**46B/14 instructions**) are checked. Eight new readonly C/C++ DATA bytes equal the official BIN and have an actual partial link. They are not yet curated into formal `src/` or placed at original addresses.

|Location|Confirmed behavior|
|---|---|
|`0xA0FA`,`0xA344`|Both direct writes to `GP+176` store `(old_byte+1)&3`|
|`0xA158`|Reads one16-bit value at `0x1AB48+2*counter`|
|`0xA37C..0xA38E`|Tail through slot `0x40048` with `A0=GP+172,A1=0,A2=5`;the caller does not implement clearing|
|Candidate `0x2000039C..0x200003CA`|Actual candidate table target;saves/clears MMIO `0x4002420C`,executes `fence.i`,fills bytes,then restores that MMIO word|

If the installed slot really equals this candidate,the RAM destination is nonzero/valid/nonwrapping and disjoint from the MMIO control word,MMIO accesses complete normally,and faults/interfering writes are absent,the length5 fill covers `GP+[172,177)`,including the counter at `GP+176`,and clears it to0. This is a static consequence of the candidate body;installed ROM identity and physical MMIO effects remain unproved.

The selected69,412 CODE bytes/23,602 instructions contain the two direct writes above,three direct reads and196 GP ADDI address takes. This inventory does **not** close dynamic aliases,SDK/IRQ/DMA writes or withheld CODE. It does not prove a global0..3 counter invariant.

In the whole CFG,`0xA0FA` does not dominate `0xA158`:a CFG path bypasses the store;runtime feasibility is unproved. Byte width alone gives the conservative512-byte envelope `0x1AB48..0x1AD48`,including328 bytes outside the provided APP. This is not a table declaration size,actual invalid read or firmware defect proof.

Given a completed known masked store or candidate fill,a counter still in0..3 at the read,and normal entries/stable GP/valid disjoint memory,only the8-byte window `0x1AB48..0x1AB50` is needed. Only that window is reconstructed. No `tsl9_input_state_decoders_static_data_1ab48` provider alias,other504 bytes,physical feature or packet semantics are inferred.

[`verification-v2.json`](verification-v2.json) records whole CFG/stack checks,reaching definitions,actual SDK native bytes/typed branch relations and independent ELF-reader agreement. The new DATA object has one8-byte readonly OBJECT. C11/C++17 results are identical. The actual partial component contains69,412 CODE and4,018 DATA bytes,preserving every input allocated byte,global symbol,typed relocation and all six UND.

Formal provenance stays160 sources and **73,422/76,800B (95.60%)**. There is no new BIN or physical hardware/ROM/RAM/IRQ/Flash/OTA completion claim. No target,HOST model,ISA emulator or hardware is executed.

With retained local artifacts and the fixed LLVM toolchain,replay without compiling or target execution:

```sh
python3 experiments/tsl9-input-counter-data/verify-v2.py --tool-dir "$LLVM_BIN"
```

[Feature candidate](feature-candidates.json):offline diagnostics separating counter provenance,CFG bypasses and candidate ROM side effects;not implemented.
