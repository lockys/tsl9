# Independent event-callback boundary review

[繁體中文](README.md) · [简体中文](readme.zh-CN.md)

The target is ID2966 V4.1.60 callback 8614..888C, 632 bytes. This bundle separates original call/frame evidence, conditional HOST algorithm tests, and the actual C/C++ native component's remaining gaps. No firmware, target CPU/ISA emulator, or hardware is executed.

`source.py` independently validates the original hashes, all 15 compressed indirect calls and their RA writes, 11 save slots, 11 fresh restores, and five PCREL addresses, with five raw operand negatives. All calls use A5 except 886A/A6; original RA is the instruction PC+2.

Only the low16 event bit15 controls the first sign test, while the retained event word and XOR result remain full32. Priority is bit15, bit3, task match, bit0, bit1, bit2. The bit0 gate requires exactly1; the bit1 gate tests the low bit. The pending difference is signed16 after modulo16 subtraction, whereas capacity is unsigned16 after subtracting3. No FFFE handle guard is present here. Resident slot identities and SDK semantics remain opaque, and source S/GP/SP dependencies are not silently replaced by standard callee-preservation assumptions.

`independent_host.c` passed 23 scenarios / 3,541 checks in each of C11 and C++17; three source mutations actually compiled and failed assertions per language. Synthetic byte memory and explicit providers cover fullword priority, non-B0 A4 residue, live message forwarding, distinct gate predicates, capacity underflow, signed differences, fresh decrements and sums, GP/connection changes after copy, six-argument A6 calls, fresh saved frames, and halted/transferred/unknown prefixes. Every launch uses the immutable HOST machine-format guard.

This is named algorithm-effect evidence. `defined_argument_mask` is an explicit argument projection, not every physical GPR residue. `return_address` records saved-frame contents, not the architectural RA inside every opaque call; HOST completion neither executes nor validates a restored return target. Synthetic SP mutation tests establish memory-address/content dependencies only.

The measured inline component is one FUNC658 / 241 instructions, still26 bytes over the original632. It has no unresolved provider, 15 RA-writing indirect calls and a48-byte frame; C/C++ native code agrees. Original RA/S0 save ordering differs, previously unused SP+0 saves S10, and resident return offsets differ. Unknown resident S-register dependencies, frame aliases and every fault/asynchronous prefix remain unproved. `native.py` checks this measured profile, complete ELF/disassembly byte coverage, IR widths and actual operand negatives; its successful diagnosis does not admit placement or the original ABI.

Metadata-only default, without firmware/build reads:

```sh
python -B ABI-review/check.py --project-root ROOT
```

Fresh C/C++ HOST tests and compiled negatives, then read-only artifact replay:

```sh
python -B ABI-review/run-host.py --project-root ROOT --language both --build-root OWNED_BUILD
python -B ABI-review/run-host.py --project-root ROOT --replay HOST_VERIFICATION.json
```

Native-only actual review and read-only replay, without HOST receipt or firmware input:

```sh
python -B ABI-review/review-native.py --project-root ROOT --folder NATIVE_MODE --receipt NEW_NATIVE.json
python -B ABI-review/review-native.py --project-root ROOT --replay NEW_NATIVE.json
```

Layered actual source/HOST/native review and exact read-only replay:

```sh
python -B ABI-review/review.py --project-root ROOT --firmware FW --host-receipt HOST_VERIFICATION.json --native-folder NATIVE_MODE --receipt NEW.json
python -B ABI-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

Only source and metadata are sealed. `summary.json` binds selected actual results. The preceding full image remains unchanged: this callback is not integrated. Original full ABI, placement and hardware/OTA admission remain false.
