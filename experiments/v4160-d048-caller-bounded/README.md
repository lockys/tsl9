# D048 caller reference-byte check

Offline regression against the pinned 76,800-byte reference BIN, assuming its
linear base is `0x8000`. At `0x13928`, bytes `ef900ff2` decode as
`jal ra, 0xd048`; the following bytes `230ca100` encode `sb a0, 24(sp)`.
The test checks these bytes, the JAL immediate and register, the BIN digest,
and finite one-bit and truncation negatives. It does not execute firmware.

This verifies a reference byte window, not reachability, a complete caller
set, original source-level intent, data ownership, ABI, or full-image
reconstruction. The following instruction is checked as exact bytes, not by
an independent instruction decoder.

Run from the repository root:

```
python -B experiments/v4160-d048-caller-bounded/test_caller.py
python -O -B experiments/v4160-d048-caller-bounded/test_caller.py
```
