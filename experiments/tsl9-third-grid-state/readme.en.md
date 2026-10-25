# Read-only offline audit of the third table row

[繁體中文](README.md) · [Findings](../../analysis/third-grid-state-2026-10-25/readme.en.md)

Check original instructions, the accepted component, and five direct setter callers. Distinguish known initialization literals from unproved global bounds. No DATA provider, source-manifest change, or BIN.

```sh
python3 experiments/tsl9-third-grid-state/audit-v1.py
python3 experiments/tsl9-third-grid-state/audit-v1.py --full
```

Requires the existing local original-coordinate ELF and retained evidence. No recompilation, target execution, or network calls. On Windows, `py -3` can replace `python3`.
