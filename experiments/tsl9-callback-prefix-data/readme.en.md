# Readonly callback-path C/C++ DATA experiment

[繁體中文](README.md) · [Evidence](../../analysis/callback-prefix-data-2026-10-26/readme.en.md)

Fourteen fixed-length providers / 109 bytes. The experimental link has eight compiler-undefined providers; the accepted component still has 22. Four newly identified indirect CODE gaps are recorded separately. No flashable BIN.

Set `LLVM_BIN` to the established LLVM tool directory:

```sh
python3 experiments/tsl9-callback-prefix-data/audit-v1.py
python3 experiments/tsl9-callback-prefix-data/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python3 experiments/tsl9-callback-prefix-data/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-prefix-data/build/native-v1
```

Trials create new directories only; use `--replay` for retained outputs. Replay does not recompile or execute the target. Installed ROM contracts remain unproved.
