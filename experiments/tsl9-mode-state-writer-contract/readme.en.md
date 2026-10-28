# Mode state writer provenance

[繁體中文](README.md) · [Previous lookup contract](../tsl9-third-provider-lookup-contract/readme.en.md)

Offline verification covers **8 complete original functions, 3,104 bytes / 1,023 instructions**, matching the existing C/C++ original-coordinate ELFs. No firmware source bytes or flashable BIN were added.

## Confirmed

Addresses below assume nominal APP placement at `0x8000` and the original register context. Physical RAM mapping remains unproved.

- `0xD05C..0xD07C` writes `1`, `low8(A0)`, `low8(-A2)`, `low8(A1)` to `0x2000BF38..0x2000BF3B`. The mode store at `0xD06E` has no local range check.
- Exactly five directly encoded transfers target this entry within the selected 69,412 CODE bytes. Complete CFGs prove these constant arguments; indirect transfers and excluded CODE are outside this inventory.

| Call / tail PC | Mode argument |
| --- | --- |
| `0xA224` | 3 |
| `0xAC6C` | 1 or 3, defined at `0xAC12` and `0xAC64` |
| `0xD528` | 5 |
| `0xE1EA` | 3 |
| `0xE6E8` | 3 |

- The word store at `0xD0C8` assigns `[enable, mode, selector, countdown] = [1, 2/4/5, 0, 1]` through three original branches.
- `0xD0EE..0xD104` passes the same state address, `A1=0`, and `A2=16` through an indirect tail loaded from slot `0x40048`. The arguments are proved; the installed callee identity and zeroing effects are not.
- The `0xE220..0xEBAC` CFG includes five original relative jump tables. All 756 table bytes match existing positive native DATA. Treating every `jr` as a function exit would omit actual switch arms.

## Next concrete gap

Under the [original lookup formula](../tsl9-third-provider-lookup-contract/readme.en.md), a mode value of 1 or 3 at the read combines with a column bounded by `&15` to address these rows. Each 16-byte row is currently absent from formal DATA coverage:

| Conditional mode | Half-open interval | Missing bytes |
| --- | --- | --- |
| 1 | `[0x1A088, 0x1A098)` | 16 |
| 3 | `[0x1A0A8, 0x1A0B8)` | 16 |

This milestone checks address and coverage metadata only. Neither row payload was read, and actual reachability of every column is not claimed. These use contracts support a later row-by-row DATA reconstruction assessment, without gap filling or provider aliases.

## Still unproved

The explicit local write values form the set 1 through 5; **this is not a global mode domain**. The setter accepts any incoming A0 low byte. Aliases, indirect callers, excluded CODE, IRQ/DMA, initialization effects, and coherence between writes and reads remain open. Do not clamp the mode or declare a complete lookup provider from these observations.

The formal baseline remains 162 C/H files and 73,478 / 76,800 bytes (**95.67% static byte coverage**), with 6 unresolved APP source providers. This is not feature completion, boot evidence, hardware compatibility, or a successful flash claim.

## Reproduce

From the repository root:

```sh
python experiments/tsl9-mode-state-writer-contract/check-v1.py
```

[Pinned inputs](inputs-v1.json) · [Verification receipt](verification-v1.json) · [Checker](check-v1.py) · [Unimplemented diagnostic candidate](feature-candidates.json)

All checks are offline static analysis. No target, HOST model, or ISA execution, hardware access, or third-party API requests occurred.
