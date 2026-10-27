# Task-0 deep dependency C/C++

[繁體中文](README.md)

Supply the previous `56972` and `2000156C` gaps and necessary supporting functions: **six complete bodies / 2,130 bytes / 713 instructions**, using register-context C/C++ with explicit instruction ports. Installed ROM and physical RAM mapping remain unproved.

| Candidate original interval | Bytes | Own frame |
|---|---:|---:|
| `435CE..436A8` | 218 | 32 |
| `55DEA..55E44` | 90 | 0 |
| `55F94..5605C` | 200 | 16 |
| `5627A..56326` | 172 | 16 |
| `56972..56CB2` | 832 | 16 |
| `2000156C..200017D6` | 618 | 48 |

Verify all original bytes, complete CFGs, own frames and reachable arms after returns. The RAM body traces actual SDK Flash bytes through the existing startup copy mapping. Its 38 Xwchc operations remain a conditional ISA interpretation, not physical chip identification.

Verified local behavior:

- `56972` reads input object `+10` first. Zero returns 1 before its own frame is allocated. The nonzero path increments the halfword at `+128`, retaining low16, and clears byte `+24`. Full protocol meaning remains unproved.
- `55DEA` reads through `A0+487` and writes the low byte of its result at `A0+78`. Retain three original signed DIV instructions without inferred units or replacement C arithmetic. Appropriate readable/writable memory is required; actual object allocation and physical RAM capacity remain unproved.
- After the return at `17D0` in `2000156C`, `17D2 → 17B6` remains reachable from the original entry and is retained.

Actual C11/C++17 objects are identical. Every original-address re-encoded byte, independent ELF readers and nonloadable partial linking pass. The union contains **40,874 CODE + 392 DATA bytes / 14,060 instructions**. Genuine bodies supply both previous UND symbols and all newly added static direct/far-call targets; **zero named UND symbols remain**.

Zero named UND **does not mean runtime closure**. New indirect call `43648` remains unjoined. This partial SDK object has **63 register-transfer sites: 51 with at least one evidenced conditional domain and 12 unjoined**. This excludes the entire APP, universal live values and physical effects; it is not functional completion.

APP static coverage remains **95.54%**. Four startup source bytes and physical chip, ROM, RAM, IRQ, Flash, OTA and complete behavior evidence remain missing. No target, model, emulator or hardware execution; **no BIN generated and flash compatibility remains unproved**.

Feature candidate: offline reports of object access ranges, field widths and memory preconditions, keeping compilation separate from allocation-size evidence. Proposal only, not implemented.

[C/C++](resident_task0_deep_component.c) · [Original instructions](evidence-v1.json) · [Checker](audit-v1.py) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

Read-only revalidation from the project root, using retained references, native objects and checked LLVM:

```sh
python3 experiments/tsl9-resident-task0-deep-component/audit-v1.py --tool-dir "$LLVM_BIN"
```

Use `py -3` on Windows if needed. Public text receipts do not replace references or build artifacts.
