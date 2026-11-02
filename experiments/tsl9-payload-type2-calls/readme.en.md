# Type-2 calls in the newly opened dispatcher

[繁體中文](README.md)

The newly opened section contains four further direct calls to `0x13BA6` with type 2: `0x144AA`, `0x147CA`, `0x147F8` and `0x1492C`. The prior result that five jump-table cases pass only 0/3/4 must not be generalized to the entire dispatcher.

One bounded local path: upon normal arrival at `0x14486`, command `0xC0`, saved length `s2=1`, and a valid input whose first byte is 2 lead to `0x144AA`, calling the setter with `a0=s1,a1=2`. If the call and memory are valid and `s1` matches an unsigned halfword, it writes type 2 to the first matching entry; otherwise it writes nothing.

After its own guards pass, `0x1416E` can also call `0x13E0E` with `a0=s1,a1=1`; on a matching handle, that function sets the corresponding flag to 1 and clears type to 0. If the two calls succeed in this order, use the same matched entry and no intervening state change occurs, the previously analyzed local state `flag=1,type=2` can result. This is a conditional possibility across calls, not proof that a device accepts inputs, that the operation occurred, that the later lookup is reachable, or that global indexes are bounded. Authentication material is not disclosed.

`python scripts/verify-payload-type2-calls.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` checks the earlier jump table, four direct calls, local guards and original flag-setter instructions and rebuilds the candidate BIN; it executes no firmware or hardware.
