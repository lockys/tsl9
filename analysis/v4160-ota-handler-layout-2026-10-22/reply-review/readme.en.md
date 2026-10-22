# Actual reply-pointer consumers

[繁體中文](readme.zh-TW.md)

The original S reply pointer escapes the caller. Its numeric address has not been proved unobservable. This offline review changes no C/C++, ABI bridge, stack layout or firmware.

Original9D92/9D96 write the then-liveSP+12/+13 before UID processing;9DAC forms A2 from the post-call liveSP+12. Packet wrapper13E98 is28B: nonzero pointer and length tail-transfer to90B13B4C, otherwise it tails toTX8A56.

13B64 stores the source pointer at its own liveSP+12. At allocation call13B68 through slot70, A0 becomes length while A2 still contains the source pointer. Thus even a contents-only copy cannot establish that allocation ignores the address. After success,13B70 freshly reloads the pointer intoA1;13B6E freshly loads the copy target through liveS1+4C.13B80 passes post-copy liveS0, the allocated buffer, toTX. Unknown callees are not assumed to preserve S/SP or frame contents.

Small reply13F66 constructs its own one-byte source atSP+15 and enters13B4C. Page reply9B8E allocates1026B and copies a Flash page; its semantic third input is a full32 page index rather than the S reply pointer. Ambient-register and opaque-callee caveats still apply.

Both existing58B copy candidates perform forward byte loads/stores. For nonnull pointers they do not compare the source against a particular stack range, but first save/zero MMIO4002420C, executeFENCE.I and eventually restore MMIO. They are not pure memcpy implementations. Their installed identity is unproved.

A conditional packet-content projection requires allocation not to observe/retain ambientA2 or address-dependent history, the required live frame/slot state, an actually installed proved copy, equal two-byte contents at each fresh source read, no consequential alias/fault/asynchronous differences, and separate contracts for TX/release and subsequent continuations. These are sufficient conditions, not a demand for universal numeric-pointer or literalRA identity. They are not established for hardware. See[contracts.json](contracts.json).

Read-only checks of existing D/P C/C++568B archives confirm responseSP+6/+7 and savedS7 atSP+12. Forcing the source toSP+12 would corrupt savedS7. Equal48B frame sizes do not equate ten candidate save slots with seven original saves.

Evidence covers546 original bytes/209 complete instruction rows:113 App-consumer instructions independently equal the existing allocated ELF and LLVM text, plus96 originalTX rows checked against closed source evidence. Five raw operand counterexamples reject. Four existing D/P native archives and their read-only replays pass. No compilation, HOST rerun, RISC-V execution/emulation or BIN generation occurred.

```sh
python -B reply-review/check.py --project-root ROOT
python -B reply-review/review.py --project-root ROOT --firmware FW --folder ACTUAL_MODE --image-elf OLD_ADDRESS_WITNESS --candidate-root RESIDENT_CASE --receipt NEW.json
python -B reply-review/review.py --project-root ROOT --replay NEW.json
```

Default`check.py` validates sealed source, retained operands and counterexamples only: metadata_only=true, no generated native artifact read. Four optional review inputs explicitly select originalFW, existing568native, unchanged App-consumer ELF or candidate sources. Future layout objects need a separate review. Receipts are create-only; replay uses their recorded explicit paths without compiling or executing a target. Shell wrappers acceptPYTHON.

Only source and result metadata are sealed; generatedbuild/receipts are excluded. FullABI, installedROM, placement and hardwareOTA remain false. The next useful provider evidence concerns slot70 ambient inputs and memory footprint, not forced numericSP equality.
