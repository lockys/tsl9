# Conditional C model for the dispatcher branch

This [model](dispatch3.c) describes local branches at `0x14288..0x142C0`: command 162 transfers to `0x149FC`, commands other than 163 transfer to `0x14098`, and command 163 with length 76 requests a 76-byte allocation; only a nonzero result requests a 76-byte copy from the original `s0` pointer to that result. The model records synthetic addresses and requests only; it does not access those addresses or model subsequent execution and effects.

The pinned WCH header declares slot 15 at `0x40070` as `tmos_msg_allocate(uint16_t len)` and slot 6 at `0x4004C` as `tmos_memcpy`. The fixed V1.31 reference stores `0x20000236` and `0x20000332` in those slots. These are candidate interfaces, not proof of the installed ROM, allocation result, memory validity or successful copy. The model assumes normal returns and a valid, undisturbed original stack and registers.

Windows MSVC C11 and C++17 each test 1,538 synthetic cases. `python experiments/tsl9-dispatch3-model/verify_instructions.py --firmware <CANDIDATE_BIN> --resident <REFERENCE_BIN> --header <WCH_HEADER> --r2 <R2_EXECUTABLE>` checks 17 instructions, the two reference slots and the pinned header. This model is not integrated into the candidate BIN; no firmware or hardware is executed.
