# C behavior model for the dispatcher continuation

The [model](dispatch2.c) describes local branches, state-byte reads, scheduler requests and exit addresses at entries `0x14230` and `0x1425E`. The former matches the command's low byte against `170/171`; the latter uses full unsigned 32-bit comparisons. When a path requests scheduling and the state byte is zero, the model records callback `0x13F88` and delay 300; it does not claim scheduling succeeds or the callback runs.

The model assumes the original dispatcher stack and registers are valid and state reads and scheduler calls return normally. It does not reproduce other registers, external effects, device timing or physical functions and is not used to replace candidate BIN machine code. See the [source continuation](../tsl9-ota-dispatch2-source/readme.en.md) for original-instruction linking and byte comparisons.

On Windows MSVC, C11 and C++17 each passed 131,082 cases covering all 256 byte commands, all 256 synthetic state-byte values and several wider values. `python experiments/tsl9-dispatch2-model/verify_instructions.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` checks 36 original instructions. On a system with a C compiler, build and run the test with `cc -std=c11 -Iexperiments/tsl9-dispatch2-model experiments/tsl9-dispatch2-model/dispatch2.c experiments/tsl9-dispatch2-model/test_dispatch2.c -o test-dispatch2`; this POSIX command has not been tested.

`0x81AA` only reads an unsigned byte at `GP+167`; its product meaning is not established. If reset clearing completes, GP is `0x20004000`, and no later write changes this byte before the read, that read returns 0. This does not prove the actual device state or scheduler success.
