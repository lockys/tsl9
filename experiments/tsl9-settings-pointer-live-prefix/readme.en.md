# Local prefixes of settings-pointer address registers

For the 14 cases in the [GP scan](../tsl9-settings-pointer-gp-scan/readme.en.md) that retain the `GP+84` storage address after an immediate load, scan linearly after the load until the first use of that register, a control-flow change, or a 24-instruction limit. Seven overwrite the register before the first branch or call; seven encounter a control-flow boundary first. No store, copy or transfer of the address register occurs in these local prefixes, but branches, exceptions, calls, memory aliasing and prior aliases in other registers are outside the check.

The seven boundary cases are `0xAC7C`, `0xBDC6`, `0xDF26`, `0xFE6A`, `0x155D4`, `0x171EC` and `0x142FC`. For example, `0xFE6A` reaches a branch at `0xFE76`, so a later address copy is outside this prefix conclusion. The other three cases did not have an immediate load; see [delayed reads](../tsl9-settings-pointer-delayed-reads/readme.en.md).

Run `python experiments/tsl9-settings-pointer-live-prefix/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER> --r2 <R2_EXECUTABLE>`. The check uses hash-pinned inputs, radare2 decoding and four synthetic classifier controls; it does not execute firmware or establish the complete CFG, global pointer invariance, ROM, hardware or flashability.
