# Type writes from five dispatcher cases

[繁體中文](README.md)

When command `0xD0` reaches the existing five-entry relative table at `0x1A6A4`, and indexes 0–4 enter the respective targets normally, each path calls `0x13BA6` with `a0=s1`. Their `a1` values in index order are **0, 3, 3, 4 and 3**.

The callee compares `a0` to two halfwords and, on a match, writes the low byte of `a1` to the first matching type at `0x2000C799` or `0x2000C79D`; if neither matches it writes nothing. Thus, assuming normal calls, valid memory and no interference, these five local writes do not set the selected type to 2. This connects the newly opened dispatcher with the existing type-2 precondition analysis; it does not exclude other calls, subsequent writes or asynchronous changes and does not prove actual reachability or feature behavior.

`python scripts/verify-payload-jump-effects.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` revalidates the jump table and complete candidate BIN, then checks 15 case-argument instructions and 14 setter instructions in both builds; no firmware or hardware is executed.
