# Static source for callback registration and buffer arguments

[繁體中文](README.md)

This check reads official ID2966 V4.1.60 bytes, authenticates the complete 384-byte initializer at `0x8E88..0x9008` and 632-byte callback at `0x8614..0x888C`, then decodes 27 selected actual operands. It is not a CPU state model, target execution or proof of ROM semantics.

## Source observations

- AUIPC/ADDI at `0x8E9C/0x8EA0` forms A0=`0x2000B18C`, with A1=0 and A2=2124. The indirect call at `0x8EA6` returns to `0x8EA8`. The count equals two 1062-byte ranges. A5 was loaded at `0x8E90` from S0+`0x48`, after S0 was set to `0x40000`. These arguments suggest initialization, but unknown callee behavior and candidate SDK types do not prove zero filling.
- AUIPC/ADDI at `0x8EC8/0x8ECC` forms A0=`0x8614`; the indirect call at `0x8ED0` returns to `0x8ED2`. A1 and later arguments retain live residues after prior opaque calls. Do not silently declare a one-argument function.
- The byte store at `0x8ED2` writes the low eight bits of returned A0 to `GP_after+0x9D`. Callee GP preservation is unproved; this cannot automatically be entry GP+`0x9D`.

The second A5 load at `0x8EC4` is exactly `LW(S0_live+0x80)`. Several opaque/direct calls intervene. A nominal `0x40080` slot requires S0 preservation across them. The source supports passing the callback address to an indirect ROM call and storing its returned byte; it does not observe successful registration, callback execution or physical BLE transmission.

The same initializer also forms A0=`0x8614` at `0x8F82/0x8F86` and `0x8F98/0x8F9C`, then calls at `0x8F8A/0x8FA0`. Returned bytes go to GP_after+`0x94/0x98`; subsequent halfword stores write live S1 to GP+`0x96/0x9A`. S1 was set to -2 at `0x8F7A`, but intervening opaque calls mean the nominal `0xFFFE` value requires S1 preservation. These fields match the callback's two context/connection records without proving candidate ROM registration types.

## Reproduce and limitations

The callback adds traceable source locations for the existing update wait-reason proposal: the zero-return branch at `0x87A6`, low-bit test at `0x87C8/0x87CA`, and nonzero branch at `0x8814` can lead to retry handling. The call at `0x87F8` only proves arguments context,2,2; milliseconds are unproved. The success path updates a 16-bit consumed length at `0x8824` and submits event value1. These sites can guide offline diagnostics, but no App UI or hardware feature is added and unknown ROM codes must not be labeled confirmed Bluetooth errors.

```sh
python3 -B analysis/v4160-event-callback-2026-10-22/entry-plan/check.py --firmware /absolute/ID-2966-V4.1.60-decoded.bin --report /absolute/new-registration-report.json
```

The research-workspace entry uses `apk-analysis/tsl9-v4160-event-callback-2026-10-22/entry-plan/`. Twenty-seven actual operand bit changes enter operand validation directly, bypassing the file-digest gate. Reports are create-only; original BIN bytes remain unchanged.

REA 6.4.0 MCP connects, but native analysis providers are unavailable on this Windows host: Ghidra/IDA need configuration and Hopper is unsupported. Existing LLVM static disassembly corroborates the selected instructions. No installation, RV32 execution/emulation, network call or hardware operation occurs. Full initializer semantics, installed ROM/BOOT and OTA remain unproved.
