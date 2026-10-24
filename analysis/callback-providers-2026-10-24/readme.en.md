# Callback providers and readonly data integration

[繁體中文](README.md)

Reconstructed D272,B0FC,12B24,13D48,10630 and the actually registered B0D0 callback in [src/](../../src/native/receive/callback_providers.c): **558B / 188 instructions plus62B readonly data**. C11/C++17 preserve every selected original code byte, all seven relative dispatch words and both17-byte templates.

Integrated component: **12782B code +578B data,4464 original instructions,860 relocations,81 unresolved symbols**, identical in both languages. All prior12224B code and516B data carriers remain unchanged. Ten new aliases bind actual code entries; no stubs or ABS substitutes were added.

[Evidence](evidence.json) · [Results/hashes](summary.json) · [Pending providers](next-providers.json) · [Integration checker](../../experiments/tsl9-callback-providers/integrate-v1.py)

D272 retains a resident-slot40048 call with length19. B0FC retains its GP-relative initialization and B0D0 callback registration; B0D0 updates three byte counters under the original flag condition. 12B24 retains every table case, including code after its shared return, through12BC8. 13D48 retains state gates,GP344 timing storage and100/35 notification parameters; time units remain unknown. 10630 retains both17-byte templates,GP328 counter behavior and original lookup order without asserting safe index bounds.

Five old roots were resolved; five external calls bind actual retained parent code, while seven new entries remain exposed: **79→81** unresolved symbols. Next:1070A,1299E,129C4,12AA0,13346,135E6,16DD4.

The source collection has97 C/H files and70 code units. Including independent pointer data,142 comparisons/284 objects pass; all prior138 results and829 artifact records are unchanged. The manifest is an exact96-to97 extension. Frozen checkers remain unchanged; an old whole-manifest replay on the new manifest is not claimed. The failed native-v1 newline-escaping compile and rejected source remain UNACCEPTED; only native-v2 passed.

Replay locally from the repository root:

```sh
python3 experiments/tsl9-callback-providers/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-providers/build/component-v1
```

This remains a VMA-zero ET_REL partial object. Original code/data placement,RAM ownership,private ABI,physical MCU/installed ROM/IRQ and OTA compatibility are unproved; **not flashable**. No target/model/ISA execution,network/hardware access or BIN generation. Historical privacy findings remain unresolved; no commit/push.

Feature candidate: read-only callback/counter/notification diagnostics and firmware provenance. The original evidence is stronger, but no diagnostic UI or control-policy change has been implemented; physical meanings and time units remain unknown.
