# The original final eight bytes are not padding

[繁體中文](README.md)

The new component is 624 bytes, while the original callback occupies 632 bytes at `0x8614..0x888C`. Placing it at the original entry would numerically leave eight bytes at `0x8884..0x888C`. That does not authorize retaining, clearing or padding them.

`check.py` authenticates the official ID2966 firmware SHA-256 and uses the pinned original operand decoders to read three instructions: an indirect call through A5 at `0x8884` (returning to `0x8886`), `A0 = S0 XOR 8` at `0x8886`, and a jump to `0x866C` at `0x888A`. This is original executable call/return code, not storage proved unused. See [original-tail.json](original-tail.json).

```sh
python3 -B analysis/v4160-callback-registers-2026-10-22/tail-plan/check.py --project-root /absolute/re-tsl9 --firmware /absolute/re-tsl9/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

The checker only reads original files. It generates no replacement instruction, padding or BIN, and does not execute or emulate firmware. Full ownership of the original tail, control flow and ROM return ABI remain unresolved; placement is not admitted.
