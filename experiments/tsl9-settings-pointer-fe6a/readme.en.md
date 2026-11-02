# Settings-pointer address use in `0xFE6A`

The original function window `[0xFE6A,0xFF44)` contains 72 linearly decoded instructions. `0xFE6A` forms the `GP+84` storage address and loads the pointer; if the branch at `0xFE76` is not taken, `0xFE82` copies the storage address to `s0`, and `0xFEB4` reloads the pointer through `s0`. The other two uses of `s0` in this window save and restore it on the stack.

Of nine explicit stores in the window, three target the stack and six directly target `GP+288/291/292/296`; none directly targets `GP+[84,88)`. Thus, assuming stable GP, stack stores do not overlap the pointer and saved registers and memory satisfy their contracts, these **explicit in-function stores** do not modify the pointer. The function makes external calls; callee effects, other entries, exceptions, installed RAM and interrupts remain open, so global pointer invariance is not established.

Run `python experiments/tsl9-settings-pointer-fe6a/verify.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>`. It pins the candidate hash and checks all linear-window `s0` uses, explicit stores, key branch and a synthetic negative control without executing the firmware.

## Call targets

The complete short functions `0x828C`, `0x81EE` and `0xA9DE` each read a fixed byte and return without stores. `0x81B0` saves to the stack and calls slot `0x4007C` indirectly; explicit stores in `0x90B0` include three stack saves and two cleared table fields. Its table starts at `0x2000BE08` and normal control flow scans at most 15 entries of 12 bytes. Assuming preserved index and saved registers and valid memory, neither field store overlaps `GP+[84,88)`. `0x90B0` can still call `0x40068` and tail-transfer through `0x4005C`, so its complete effects remain open.

Run `python experiments/tsl9-settings-pointer-fe6a/verify-callees.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` to check these functions and locations; stack aliasing, resident slots, exceptions and hardware remain unverified.
