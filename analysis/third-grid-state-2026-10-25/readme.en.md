# State writers for the third lookup table

[繁體中文](README.md)

Capture **275 original instructions in 11 windows** and check all selected CODE: 64,544 bytes / 21,938 instructions. The row byte at `0x2000BF39` has these identified sources.

| Path | Confirmed coded behavior |
|---|---|
| Setter `0xD05C` | `0xD06E` stores the low byte of A0 without a mask; the five selected direct callers provide 1/3/5 |
| Word store `0xD0C8` | Three literal paths put 5/4/2 in the row byte; original joins and store roles are retained |
| Startup zero loop | Its coded interval includes the row; this does not prove installed startup or ROM behavior |
| Reset `0xD0EE` | Its 16-byte range includes the row; zeroing requires the installed `0x40048` slot to obey the archived SDK memset contract |
| Adjacent reset `0xCEAA` | Its 20-byte range ends at `0x2000BF38`, excluding the row |
| `0xC91E → 0xEBAC` | The preceding record's direct eight-byte write footprint ends at `0x2000BF38`, excluding the row; callee side effects remain open |

Selected direct calls occur at `0xA224`, `0xAC6C`, `0xD528`, `0xE1EA`, and `0xE6E8`. The accepted component has exactly these five direct references to the setter and no other selected address-taken reference. This does not exclude unselected data, indirect entries, or arbitrary pointer aliases.

Under these initialization and compatible-zeroing conditions, rows **0..5** need a conservative `0x1A078..0x1A0D8` read window: 96 bytes. Sixteen bytes already overlap the accepted pool, leaving a candidate 80-byte increment and a 512-byte three-window union. Neither original declarations nor global runtime bounds follow.

**No DATA provider or coverage increase is accepted here.** Arbitrary record aliases, non-adjacent address derivations, ROM/callee side effects, indirect entries, and asynchronous effects remain open. Accepted state stays **88.89% / 22 undefined providers**.

No BIN, target/HOST-model/ISA execution, hardware access, or backend requests. Physical/OTA compatibility remains unproved.

[Result](summary.json) · [Original instructions](evidence.json) · [Writer contracts](writer-contracts.json) · [Next steps](next-providers.json) · [Feature proposal](feature-candidates.json)
