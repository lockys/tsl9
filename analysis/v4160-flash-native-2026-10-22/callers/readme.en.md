# Other numeric destinations of the Flash quarter helper

[繁體中文](readme.zh-TW.md)

The fixed ID2966/V4.1.60 original BIN, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, contains six additional direct call slices to `0x9C0A`. Each consists of LUI, C.MV, ADDI and JAL: 14 bytes each, 84 bytes/24 instructions in total.

| Original JAL PC | Numeric A0 destination |
| --- | --- |
| `0x12E7A` | `0x08077900` |
| `0x12F0C` | `0x08077800` |
| `0x12F6E` | `0x08077700` |
| `0x13078` | `0x08077600` |
| `0x130FC` | `0x08077500` |
| `0x1315E` | `0x08077A00` |

Each slice copies its then-live SP into A1, constructs the constant in A0 and sets RA to call PC+4. This is conditional static dataflow. It does not prove execution reachability, physical SP, buffer contents, settings semantics or successful physical programming.

**Do not add either OTA receiver's address guard to the generic quarter helper.** These destinations are outside both retained numeric receiver envelopes: BOOT receiving Runtime at `0x08008000..0x08020000`, and Runtime receiving BOOT at `0x08001000..0x08008000`. Those are original branch constraints, not physical capacity or mapping measurements. High numeric addresses do not identify a chip/board or establish unused safe storage.

The 60 actual raw mutations in `report.json` are rejected semantically before the whole-file digest gate. A separate `compiled-crosscheck.json` records the observed linked source-image ELF check: all six slices and entire owners match original bytes. Instruction widths are walked from real section-backed FUNC entries. This is not ISA emulation or execution-reachability proof, and it does not invent assembler-discarded local labels.

Run `python callers/inspect_callers.py --project-root <project> --check` to recheck original source and retained evidence. Supply `--elf <actual-linked-ELF>` for that additional actual artifact check; without it, no archived-ELF replay is claimed. No network, real device identity, target execution, emulation, hardware or new BIN operation occurs.
