# Newly opened dispatcher path and two precheck gates

[繁體中文](README.md)

The previous check identified that the conditional calls at `0x1416E` and `0x144AA`, in order and matching the same entry, can produce `flag=1,type=2`. If that entry's halfword is also not `0xFFFE` and its state persists until later checks, it passes the three active-entry tests in `0x82D2` and `0x838E`; both examine two entries at base `0x2000C794` with four-byte stride.

If each active path completes normally, necessary callees preserve registers, and no interference occurs, both routines return nonzero. The identified call sites `0x12CB4` and `0x123A8` branch away from their respective later paths on a nonzero result. This connects newly opened state writes to the preconditions of previously analyzed `0x1A078`/`0x1A638` paths. It does not prove the device received commands, that the two calls see the same state, or that all other entrances behave the same way.

`python scripts/verify-payload-active-gates.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` rechecks the preceding path and candidate build, then checks the original instructions in both gates and call sites along with synthetic positive/negative controls. It executes no firmware or hardware.
