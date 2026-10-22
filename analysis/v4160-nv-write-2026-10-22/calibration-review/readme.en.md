# Conditional relation between polling input and clock fields

[繁體中文](README.md)

Actual ID2966 source checking covers the complete `0x1973C..0x19764` body (40 bytes / 11 rows) plus the 4-byte unsigned load at `0x19770`. The latter is a subset of the separate timer review, not additional unique coverage. Existing sealed standard-field readers and retained original rows are reused without rerunning the old clock-query or HOST suites or executing native code.

The source freshly reads the word at live GP+108, divides it unsigned by 8000000 and masks the quotient to byte q. It writes q to GP+382, then low16(q*1000) to GP+380. Truncation precedes multiplication. The timer freshly reads an unsigned byte at live GP+382 and uses low32(byte*full input).

Connecting the timer's read to the earlier q requires the same GP and no intervening code, alias or asynchronous modification of that byte. Actual frequency word, initialization reachability/order, GP preservation by all intervening calls and complete byte lifetime are unproved. Physical clock and time units are also unproved.

Seven actual raw-bit controls alter the frequency offset, DIVU/DIV, quotient mask, byte destination, multiplier, halfword width or timer-byte offset and must be rejected. Retained pure arithmetic examples distinguish unsigned high-bit inputs, byte wrap and low32 product wrap; they are not CPU/ISA execution or hardware measurements. q may be zero, but that alone establishes neither a hang nor a physical delay.

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /original/ID2966.bin
```

Default mode checks metadata; explicit firmware mode reads the original and replays controls. No network, MMIO/native/CPU/ISA/ESIL, old HOST matrix, hardware or BIN generation occurs. Proposed offline diagnostics could display zero calibration, wrap and unproved lifetime conditions without changing original polling or inventing timeout success. Shell runtime remains unverified; denied Git Bash startup is not retried.
