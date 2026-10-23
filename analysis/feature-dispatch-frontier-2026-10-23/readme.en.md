# Complete feature-dispatch boundary

[繁體中文](README.md)

The candidate whole body at`14D2E–154A6` spans1912B/666 instructions. Its first and only RET at`14DA8` does not end the body: reachable dispatch blocks follow. The older36B entry fragment is not a whole-function reconstruction.

- The7-entry signed-relative table at`1A6B8` handles modes0–6; unsigned mode>6 takes the default.
- The8-entry table at`1A6D4` uses`(byte[S0+5]>>2)&7`. Neither computed JR writes RA.
- There are21 direct call sites and59 direct tails, with71 distinct external targets.
- There are725 internal edges retaining repeated table entries,723 after deduplication. A syntactic overapproximation assuming normal call returns and both branch outcomes covers all666 instruction starts. This is not runtime reachability proof.
- Every direct tail restores S0→RA→SP; the common RET restores RA→S0→SP. No ordinary callee-saved ABI is assumed across opaque calls.

[summary.json](summary.json) records original byte/table hashes, every call/tail and restore PC. Every decoded byte was checked against the original local BIN. The script processes data without executing instructions.

The previous2250B component's two direct missing providers describe only that component's current frontier. Expanding12ABE introduces two backends; expanding14D2E exposes the71 targets above. Two UND symbols do not imply only two unknown functions remain in the firmware. Complete C reconstruction, hardware/installed-ROM identity, startup/memory/IRQ and OTA compatibility remain unproved.

Read-only reproduction from the repository root:`python3 scripts/analyze-feature-dispatch.py --replay analysis/feature-dispatch-frontier-2026-10-23/summary.json`. It requires the pinned existing radare2 and original BIN;`--r2` selects the executable. Nothing is installed or downloaded.
