# Settings-pointer address use in `0xFE6A`

The original function window `[0xFE6A,0xFF44)` contains 72 linearly decoded instructions. `0xFE6A` forms the `GP+84` storage address and loads the pointer; if the branch at `0xFE76` is not taken, `0xFE82` copies the storage address to `s0`, and `0xFEB4` reloads the pointer through `s0`. The other two uses of `s0` in this window save and restore it on the stack.

Of nine explicit stores in the window, three target the stack and six directly target `GP+288/291/292/296`; none directly targets `GP+[84,88)`. Thus, assuming stable GP, stack stores do not overlap the pointer and saved registers and memory satisfy their contracts, these **explicit in-function stores** do not modify the pointer. The function makes external calls; callee effects, other entries, exceptions, installed RAM and interrupts remain open, so global pointer invariance is not established.

Run `python experiments/tsl9-settings-pointer-fe6a/verify.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>`. It pins the candidate hash and checks all linear-window `s0` uses, explicit stores, key branch and a synthetic negative control without executing the firmware.
