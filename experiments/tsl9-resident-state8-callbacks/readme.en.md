# State8 callback/runner candidate C/C++

[繁體中文](README.md) · [State8 caller](../tsl9-resident-state8-service/readme.en.md) · [Main scheduler](../tsl9-resident-scheduler/readme.en.md)

Eight complete bodies total **2118 bytes/755 instructions**:

| Body | Original range (end exclusive) | Bytes/own frame |
| --- | --- | ---: |
| Registered callback | Flash0x65164..0x653A0 | 572/48 |
| Registered callback | Flash0x653A0..0x65620 | 640/48 |
| Shared-pointer runner | Conditional RAM0x200007A0..0x200007D0 | 48/16 |
| Receive-status helper | Conditional RAM0x2000263A..0x200026BA | 128/0 |
| Register reset wrapper | Flash0x6440A..0x64422 | 24/16 |
| Register helper | Flash0x63B0E..0x63C54 | 326/0 |
| Register reset helper | Flash0x63E58..0x63EDA | 130/0 |
| Register-work helper | Conditional RAM0x200026BA..0x200027B4 | 250/16 |

This is a public SDK V1.31 candidate; installed ROM identity is unproved. The [source](resident_state8_callbacks.c) retains original registers and C/assembly, not an ordinary HOST-callable API. Actual C11/C++17 objects are identical and every original-context byte matches:154 positive FUNC regions and114 relocations.

## Observed flow and decoding

- Previously registered numeric CODE values0x65164/0x653A0 now have real bodies. They remain non-relocated numeric addresses; original-address execution linking has not been performed.
- Primary definitions verify **eight Xwchc families/52 positive vectors**, including24 stack vectors. At two sites radare2 split word0x879C into two invalid bytes. Formal bit fields establish `qk.c.lbusp a5,15(sp)`; no instruction is skipped or guessed. The45 actual custom ports remain conditional, without physical ISA proof.
- Each callback owns48 bytes, clears SP+15 before passing that byte to the real receive-status helper, and later reads it. Both known calls pass A1=0/A3=0. This is not whole-stack/alias safety proof.
- The runner loads a nonnull pointer from0x20002EF8, calls it, then freshly reads flag0x20002EFC. A zero fresh flag clears the pointer word, **without comparing it with the pre-call pointer**. Atomicity/lifetime remain open.
- Real event-setter calls use event literal2; successful scheduling is not asserted. Some branches call the opaque pointer0x20003550 without a local null guard, preserving actual A0=3/status-low8/descriptor arguments.
- Receive status retains local codes0/1/6/14, optional byte/halfword outputs and original signed DIV. These are not hardware-success codes. Register-work polling back edges remain, with unproved termination.
- The second callback registers **0x65620** through the real setter. That next-stage body remains unprovided.

Own frames balance at all local normal returns, assuming normal callees preserve SP. Whole-program IRQ,reentry and stack bounds remain open. Retained BLE/clock assertions do not establish physical RAM layout.

## Entry-evidence limits

The original conditional-RAM0x20002E28 bytes decode as JAL-runner followed by ECALL. **Entry,reachability,containing function and IRQ role remain unproved.** This is not presented as a verified IRQ call chain or a single function spanning the surrounding linear window.

## Actual partial composition

Nonloadable C/C++ ET_REL objects contain **8672 bytes CODE+256 bytes DATA/3029 instructions**,703 positive FUNC regions,one OBJECT and516 relocations. Every input byte,symbol and relocation is retained. Real prior event,state8 and setter bodies resolve the unit's imports; all eight new providers have actual CODE.

Genuine UND0x57DAE/0x6020A,numeric CODE0x65620,the runner invoker,opaque callbacks and descriptor/RAM contracts remain open. The **4-byte startup source gap** and unproved arithmetic semantics remain. APP byte coverage stays **95.54%**,not functional completion. No APP integration or new BIN is supplied; physical RAM/ROM/ISA,IRQ,stack,Flash and original-hardware OTA compatibility remain unproved.

Evidence: [full audit](audit-result-v1.json),[summary](summary.json),[original instructions/primary vectors](evidence-v1.json),[specification and hashes](spec-v1.json). Callback-lifetime/receive-status diagnostics are unimplemented feature candidates.

## Reproduce

Provide the original APP,SDK/header/instruction references and retained native artifacts required by the spec,evidence and audit. Original SDK inputs/native artifacts are not included or automatically downloaded. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-state8-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-state8-callbacks/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-state8-callbacks/build/native-v1` for the first command and omit `--link-trial` for the second. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
