# Conditional counter alias in the command path

At `0x142FC`, the address `GP+84` is saved in `s1`. If saved registers remain valid and earlier calls return normally, `0x14332..0x1433E` reads slot `0x4004C` and `p=*(GP+84)`, then calls the slot with `(p, s0+24, 16)`. At `0x14340..0x14350` it reads `p` and the slot again and calls `(p+96, s0+59, 16)`. Assuming a compatible byte-copy slot, valid memory and no interference, the first call overwrites counter `GP+176` from source byte 4 if its p equals `GP+172`; the second overwrites it if its p equals `GP+80`. The reads of p are separate and need not match.

These are **conditional alias cases**, not proof that p takes either value, that the command path is reachable, or that the installed slot implements the candidate copy. At `0x1441C..0x14430`, a separate conditional operation clears bit 3 of `p+4`; even if it aliases the counter, values already in 0–3 remain in range. Other writers remain possible.

Run `python experiments/tsl9-dispatch-counter-alias/verify.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>`. It checks the image hash, 21 selected instructions, arithmetic and a mutated-instruction negative control without target execution. Installed ROM, valid p ranges and the global counter bound remain unverified.
