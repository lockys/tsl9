# Comparison model for the state-byte writer

`0x937E` calls `0x9E84`, saves its first returned 32-bit word on the stack, and reads its high 16 bits as a little-endian halfword. It then calls `0x9334`, subtracts the full returned 32-bit value from that halfword, and stores the `seqz` result, 0 or 1, at `GP+167`. This interpretation assumes a valid little-endian stack, normal calls and undisturbed registers. `0x9E84` itself requests data through the indirect slot `0x4004C`; two identified direct call sites are `0x9F06` and `0x9F42`.

The [portable C model](state167.c) only compares two supplied inputs; it does not obtain or infer device data, implement the resident or reproduce other effects. Windows MSVC C11 and C++17 each run 196,610 synthetic cases covering every high 16-bit value and wider comparison values. `python experiments/tsl9-state167-compare/verify_instructions.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` checks 21 instructions with a synthetic negative control; no firmware or device data is executed or read.

Actual source data, the indirect slot, other writers and the product meaning of the state remain unconfirmed; this model is not integrated into the candidate BIN.
