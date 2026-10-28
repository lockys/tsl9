# Original APP residual data-access audit

[繁體中文](README.md)

Add an offline checker separating **an owned base address from a fully backed access range**. Original C/C++, link layout and coverage remain unchanged; no new BIN.

The actual C/C++ diagnostic covers 73,374 / 76,800 bytes (**95.54%**). Of 3,426 missing bytes, 3,128 are within existing withheld ranges and 298 remain otherwise uncovered. The latter are not automatically justified padding or data to insert.

Source symbol `1A078` remains one of six compiler imports. Its base lies at offset 416 in the real readonly owner `19ED8..1A088` (432 bytes), leaving only **16 bytes** inside that owner.

Original instructions and compiled original-coordinate C/C++ agree for complete consumer `CEDC..CF96`. Ordinary-entry dataflow gives mode from a byte load or zero and nibble masked with `&15`. The read expression is:

```text
1A078 + 16*mode + nibble
```

Using only conservative byte/nibble domains yields **`1A078..1B078` / 4,096 bytes**. This envelope extends 1,144 bytes beyond the supplied APP image and intersects existing withheld data. **It is neither an original array declaration nor proof that all indices are reachable or that the firmware is defective.** A narrower global mode invariant, all entry paths and actual backing remain unproved.

Accordingly, do not resolve the provider merely from base ownership, invent an alias/full extent or extract the whole envelope. Retain all six imports. The checker emits addresses, counts and conditions, never withheld payload or individual withheld hashes.

[Gap map](gaps-v1.json) · [Access contract and receipt](verification-v1.json) · [Checker](verify-v1.py) · [Input index](inputs-v1.json) · [Summary](summary.json)

Retained references, native objects and checked LLVM are required. Read-only invocation from the project root:

```sh
python3 experiments/tsl9-APP-residual-access-audit/verify-v1.py --tool-dir "$LLVM_BIN"
```

Use `py -3` on Windows if needed. Source checks cover 159 C/H files, 266 comparisons and 532 retained objects. No target, model, emulator, hardware or network execution. **Passing validates the evidence and remaining gaps, not physical or OTA compatibility.**
