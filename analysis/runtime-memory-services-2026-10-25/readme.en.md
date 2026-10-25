# ROM memory-service wrappers

[繁體中文](README.md) · [C/C++ source](../../src/native/receive/runtime_memory_services.c) · [Instruction/argument evidence](provider-contracts.json) · [Summary](summary.json)

Reconstruct14 complete wrappers:280B/91 instructions. Each loads a pointer from0x40048 into T1,sets a destination,A1=0 and an A2 length,then tail-jumps.0x40048 is pointer storage,not a function entry. The shape matches the saved WCH SDK default tmos_memset profile;installed identity,private ABI and actual memory effects remain unproved.

| Original entry | A0 destination | A2 length (B) |
|---|---|---|
| `0xA37C` | `GP+172*` | 5 |
| `0xB0BA` | `0x2000BEE0` | 12 |
| `0xB5E0` | `0x2000BEEC` | 16 |
| `0xCEAA` | `0x2000BF24` | 20 |
| `0xD196` | `GP+232*` | 4 |
| `0xD4F4` | `0x2000BF5C` | 12 |
| `0xD75A` | `GP+252*` | 5 |
| `0xE0A4` | `0x2000BF68` | 28 |
| `0xF0B0` | `0x2000BF84` | 12 |
| `0xFA50` | `GP+276*` | 5 |
| `0xFB0C` | `GP+284*` | 3 |
| `0xFF44` | `GP+288*` | 4 |
| `0x10158` | `0x2000BFA8` | 12 |
| `0x10276` | `GP+304*` | 4 |

`*` GP is a live register;numeric span checks assume the startup value0x20004000. The142B sum is static,not observed execution. All conditional ranges fit the current startup zero span. E0A4 also contains five state bytes used by D76C/D7A4;this is address containment,not verified clearing or vehicle behavior.

238 comparisons/476 objects pass;55,872 original-coordinate bytes match,72.75% coverage. Fourteen imports resolve,leaving71 compiler undefined symbols;unknown indirect ROM targets are outside that count. No new data or BIN,no firmware execution or hardware connection.

## Readonly offline inspector

Requires Python3.10+ only;no compiler or reverse-engineering engine. From the repository root:

```sh
python3 experiments/tsl9-runtime-memory-services/inspect-rom-memory-calls.py --json
```

Windows may use `py -3`. The tool accepts only the digest-pinned ID2966 V4.1.60 BIN and downloads nothing or connects hardware. Optionally pass an existing pinned SDK header with `--sdk-header "$TSL9_SDK_HEADER"`;without it,the output marks the header unchecked. The tool uses only the standard library. Windows was exercised this round;other platforms were not run.
