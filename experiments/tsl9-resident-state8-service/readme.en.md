# State8 and provider candidate C/C++

[繁體中文](README.md) · [Calling state service](../tsl9-resident-scheduler-state-services/readme.en.md) · [Timer service](../tsl9-resident-timer-service/readme.en.md)

Five complete bodies total **1432 bytes/492 instructions**:

| Body | Original range (end exclusive) | Bytes/own frame |
| --- | --- | ---: |
| State8 service | Flash0x64F04..0x65164 | 608/64 |
| Callback setter | Conditional RAM0x2000078A..0x200007A0 | 22/0 |
| Register helper | Flash0x6434A..0x6440A | 192/0 |
| Register helper | Flash0x63C54..0x63D6A | 278/0 |
| Official slot9 timer start | Flash0x43728..0x43874 | 332/48 |

This is a public SDK V1.31 candidate; installed ROM identity is unproved. The [source](resident_state8_service.c) uses original registers and C/assembly, not an ordinary HOST-callable API. C11/C++17 objects are identical and every original-context byte matches:94 positive FUNC regions and70 relocations. Eleven conditional Xwchc ports are checked against primary definitions and28 official vectors.

## Observed flow

- The preceding608-byte reference now has a real native body. Local branches return0/1/2/3; these are **not hardware-success proof**. Every local normal return follows an original saved-word restore at0x4002420C. Physical IRQ semantics remain unknown.
- Buffer pointer0x20003564 is reused or allocated with size=`parameter byte29+2` (2..257), second argument73. Copy destination is buffer+2 and count is entry A1; byte1 receives the low8 length or zero. **Actual capacity, input range and aliases remain unproved.** No invented clamp is added.
- The setter stores A0 at0x20002EF8, sets flag0x20002EFC for nonzero input, and leaves the flag unchanged for null input. It does not invoke the callback. Real numeric CODE addresses0x65164/0x653A0 still identify **unprovided callback bodies**, not linker relocations. Named UND counts do not close them.
- A conditional timer call uses task byte0x20003570, event16 and interval literal1600. **Its return is ignored**; successful scheduling and physical time units are unproved.
- Timer start checks task count and a cached nonnull raw-clock pointer. Frequency is freshly read before/after the raw callback at0x4377C/0x437CC. The original64-bit product+800/denominator1600 helper arguments are retained; complete arithmetic semantics remain unproved.
- Existing timers update deadline offset8 **without resetting interval offset4**. New16-byte nodes contain task0,flag1=1,event2,interval4=0,deadline8,next12 and are appended through the actual next-pointer walk. Termination, ownership and callback effects remain open.
- Both register helpers have actual bodies and retain pointer accesses/constants. Entry0x6434A overwrites incoming A0 before using it; no hardware effect of that incoming argument is assumed.

Own frames balance on normal returns. State8+timer own frames total112 bytes, **excluding other callees, parents, reentry and IRQ stack**. Retained BLE/clock ABI assertions do not establish physical RAM layout.

## Actual partial composition and limits

Real prior allocator,copy,arithmetic and timer-lookup bodies resolve the unit's imports. Setter/register/timer providers also have actual CODE. Nonloadable C/C++ ET_REL objects contain **6554 bytes CODE+256 bytes DATA/2274 instructions**,549 positive FUNC regions, one OBJECT and402 relocations. Every input byte,symbol and relocation is retained.

Two genuine UND remain:0x57DAE/0x6020A, plus both numeric CODE callbacks and raw RAM/opaque callback contracts. The **4-byte startup source gap** and unproved arithmetic semantics remain. APP byte coverage stays **95.54%**, not functional completion. No original-address execution link, APP integration or new BIN is provided; physical RAM/ROM/ISA, IRQ, stack, Flash and original-hardware OTA compatibility remain unproved.

Evidence: [full audit](audit-result-v1.json), [summary](summary.json), [original instructions/official binding](evidence-v1.json), [specification and hashes](spec-v1.json). Timer-failure,buffer-capacity and callback-lifecycle diagnostics are unimplemented feature candidates.

## Reproduce

Provide the original APP, SDK/header/instruction references and retained native artifacts required by the spec,evidence and audit. Original SDK inputs/native artifacts are not included or downloaded automatically. From the project root with the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-state8-service/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-state8-service/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-state8-service/build/native-v1` for the first command and omit `--link-trial` for the second. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
