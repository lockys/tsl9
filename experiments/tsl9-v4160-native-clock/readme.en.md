# Readable native clock reconstruction

This component reconstructs V4.1.60 `0x18834` (174 bytes) and `0x1973c`
(40 bytes) as ordinary readable C, also compilable as C++17. The existing
214-byte / 69-instruction source proof with 50 raw negative controls is reused
unchanged. No original instructions are executed.

`src/native_clock.c` selects the direct or PLL clock, reads each RCC sample
separately, reads the live GP at four query sites, reads the live shift-table
byte, then reloads the clock word before applying `shift & 31`. The derived
function reads GP at three sites, performs unsigned division by 8,000,000,
truncates the quotient to eight bits, and writes byte/halfword outputs.
It never substitutes a fixed GP, copied shift table, or cached clock word.

## Offline verification

Python 3.10+ and a native C11/C++17 compiler (MSVC, GCC or Clang) are required.
The checkout must include the original image and the sealed earlier source
proof. Nothing is downloaded by this verifier. From the repository root:

```sh
sh experiments/tsl9-v4160-native-clock/verify.sh --language both
```

Alternatively, run `python3 -B experiments/tsl9-v4160-native-clock/verify.py
--language both`. `PYTHON` selects Python for the shell entry; `CC`/`CXX` select
single compiler executables. `--tests-only` explicitly skips the raw source
proof and records this limitation. Host verification has six groups and
269,618 checks per language, including all 16 prescaler indices × 256 shift
bytes, five PLL source paths × 16 multipliers, unsigned quotient boundaries,
live GP changes, and a changed global value between volatile accesses.

Generated build receipts pin inputs, compiler and host executable hashes.
The host executable runs only our synthetic memory-adapter tests. Native
RV32 compilation and structural verification use the separate clock
`native-review` verifier; they do not execute the resulting code.

## Limits

These are new ordinary-C interfaces. `void` does not preserve the original
A0/A1 or other caller-saved registers. Register, interrupt, stack and caller
ABI integration remain unproved. Branching native structural evidence is
not an all-path machine-code equivalence proof. No original entry aliases,
fixed original placement, boot integration, complete firmware image or BIN
is supplied. Hardware identity, ROM dependencies, OTA acceptance and physical
behavior remain unverified. No BLE/UART/CAN/Flash operation is performed.
