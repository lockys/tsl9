# V4.1.60 Flash register and instruction prefixes

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

Fresh C11/C++17 builds using the unchanged LLVM 18.0.2 RV32IMAC_Zicsr/ILP32 profile produce
six functions at their original entries: quarter/status/unlock/lock/erase/program are
64/8/30/14/46/100 bytes, totaling 262 bytes and 99 instructions.
Both component ELFs have SHA-256
`575b2e1009437c77d71081fffeaa32988ff10b23c78decb01e9ad976c5e6c9c7`.

All five leaf functions (198 bytes) are now byte-identical to the original pinned ID2966 image.
This includes every instruction boundary, operand, immediate, branch and the two ADD operand orders.
The quarter wrapper retains its prior compiler output: three stack-save instructions have a different
order, accounting for its six differing bytes. Its normal contract remains separately checked.

The readable C algorithm still owns all fresh volatile 32-bit I/O, forward 64-word copying, unbounded
native polls and normal outputs. Small native primitives express original register/event sites:
split unlock key construction, A4 erase effects, A5 program RMWs, A3 mask before A0 alignment,
and the two ordered address ADDs (A3=A1+A5 and A3=A0+A5). HOST address primitives retain the same
uint32 addition. No original opcode, whole-function assembly, padding, object patching, flag search
or source-code generation from the original BIN is used. The BIN is a verification reference only.

Relative to the previous de159...68be1 whole image's Flash component, 62 differing bytes reduce to
the wrapper's six. This milestone produces only a component ELF. It does not replace that whole image,
generate a firmware BIN or apply an ABI scheduling pass.

```sh
python3 -B experiments/tsl9-v4160-flash-register-prefix/verify.py --project-root . --language both
python3 -B experiments/tsl9-v4160-flash-register-prefix/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B experiments/tsl9-v4160-flash-register-prefix/verify_native.py --project-root . --replay /path/to/native/c/verification.json
```

Python 3.9+ and installed local compilers are required; tools are never downloaded.
Adjacent .sh wrappers accept the same arguments and honor PYTHON. Both runners accept a new
--build-root. Native compilation accepts --clang/--linker/--objdump. --firmware is forwarded to both
build and replay and requires the pinned original hash
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
An alternate-reference archive needs the same explicit path during replay. An explicit replay
language must match the receipt. Build/tool overrides are rejected during replay.
A real C build with an alternate-location reference and subsequent replay passed; wrong default
reference, language and replay overrides were rejected. Published analysis paths use analysis/v4160-...;
the working checkout uses apk-analysis/tsl9-v4160-....

Each language passed 5 groups, 481 cases and 247191 synthetic host checks plus six compiled behavior
counterexamples. Every host launch, positive and negative, verifies PE/ELF/thin Mach-O format,
architecture and width against the current Python executable and runtime pointer width, rejecting
RISC-V ELF243 or mismatched/unknown formats before launch. Universal/fat macOS Python is currently
rejected. Only Windows host execution was performed; shell portability and parsing fixtures do not
claim live Linux/macOS validation.

Native verification covers every disassembly byte, CFG including loops, encoded GPR destinations,
volatile i32 IR, exact six allocations/no writable/EH/hidden helper/UND, original entries and five
linked JALs. All five leaves require exact original bytes, without a commutative-ADD exception.
99 raw instruction mutations and three actually compiled native constraint mutations are rejected
per language. Six MMD rules bind their targets, primary source and three-file application dependency
closure; compiler resource headers are excluded. Each language retains 57 actual artifacts for
read-only replay. Inputs, tools and proof code are pinned before and after compilation.

Unknown/HALT/TRANSFER and bounded HOST diagnostics preserve external-effect prefixes only. They
do not add cleanup, invent native timeouts or prove nonreturn physical register states.
Leaf byte identity is a static fact. The wrapper still has different save ordering; whole-component
instruction-prefix, asynchronous/interrupt/fault, ROM, physical board/chip/Flash capacity, power-failure,
BLE/OTA and flashability claims remain false or unknown. No RV32 execution, ISA emulation, hardware
or network operation occurs. This is a partial readable reconstruction, not complete recovered source.

Published files include source, separate-language documentation and selected receipt JSON, not build
archives. implementation/check.py reports missing archives; --require-local-builds requires actual
artifacts instead of treating metadata as a fresh build or artifact replay. Whole-image integration and
any separate validated ABI scheduling layer require their own evidence.
