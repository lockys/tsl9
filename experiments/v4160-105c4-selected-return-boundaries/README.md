# 0x105c4 selected-link return boundaries

This is an offline check of **selected raw instruction windows**, not a whole
control-flow analysis. It uses the 76,800-byte reference image at
`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`
(SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`).
The mapping `PC = 0x8000 + file offset` is an explicit assumption.

The earlier six-section selected-link observation includes these endpoints:

| Selected endpoint | Original bytes and static interpretation | Sequential address |
| --- | --- | --- |
| `0x105ce` | `8280`: `c.jr ra` | `0x105d0` is not an automatic fallthrough |
| `0x107d6` | `8296`: `c.jalr a3` | `0x107d8`, if the callee returns there |
| `0x10846` | `8297`: `c.jalr a5` | `0x10848`, if the callee returns there |
| `0x10956` | `eff07fee`: `jal ra,0x1083c` | `0x1095a`, if the callee returns there |
| `0x10bbe` | `6ff09fc0`: `jal x0,0x107c6` | `0x10bc2` is not an automatic fallthrough |
| `0x10bf6` | `e1b7`: `c.j 0x10bbe` | `0x10bf8` is not an automatic fallthrough |

Under normal return to these saved return addresses, `0x107d8` branches to
`0x10810` or continues to `0x107da`; `0x10848` moves `a0` to `s0` and the
branch at `0x1084a` chooses `0x10866` or `0x1084c`; `0x1095a` chooses
`0x109bc` or `0x1095c`. These successors are **outside** the six selected
sections; this experiment does not establish that any path is reachable.
The windows are hand selected and instruction boundaries are assumptions.
Actual indirect targets, return behavior, register preservation, memory
validity, the complete CFG, relocation/addrsig, ABI and full-image equivalence
remain unproved. It does not execute, emulate or flash the target.

From the repository root with Python 3:

```text
python -B experiments/v4160-105c4-selected-return-boundaries/verify.py --inspect
python -B experiments/v4160-105c4-selected-return-boundaries/verify.py --test
python -B -O experiments/v4160-105c4-selected-return-boundaries/verify.py --test
python -B experiments/v4160-105c4-selected-return-boundaries/test_cli.py
python -B -O experiments/v4160-105c4-selected-return-boundaries/test_cli.py
```

The five verifier tests check the pinned image, mutate every byte of the six
anchored windows, exercise image identity failures, and check limited decoder
forms and independently disassembled signed branch vectors. The three CLI tests
exercise output, arguments, missing/changed images and the verifier tests in a
temporary tree. Normal and optimized commands are separate. The branch/jump
decoders cover only the selected instruction classes; they are not a general
RISC-V disassembler. `--inspect` is a static check, not a build or acceptance
of the firmware. These commands are not asserted to run in CI.
