# Delayed settings-pointer reads

For the three earlier `GP+84` address formations that do not immediately load the word, the selected instructions show:

- `0x12C82` places the address in `s7`; at `0x12D78`, the pointer is loaded through `s7`, followed by a byte read at pointer offset 4.
- `0x133C0` places the address in `s4`; `0x13516` reads the pointer and offset 4. At `0x13574` and `0x13586`, the pointer is freshly read and an indirect slot is called to copy 16 bytes each from `p` and `p+96` to the stack.
- `0x18240` places the address in `a3`, and `0x1824A` loads the pointer. If the unsigned guard at `0x18256` passes and registers and data are valid, the slot call uses one of `p+16/24/32/40/48` as an 8-byte source, inside the assumed 112-byte settings area.

These are local instruction observations: the first two cross other branches and calls and require preserved registers and a valid stack that does not overlap the pointer. The last also requires the indirect slot to satisfy the candidate contract and return normally. Other paths, writes, exceptions and hardware differences are not excluded.

Run `python experiments/tsl9-settings-pointer-delayed-reads/verify.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>`. It checks the pinned image, 27 instructions, the numeric range and a synthetic negative control; it does not execute the target.
