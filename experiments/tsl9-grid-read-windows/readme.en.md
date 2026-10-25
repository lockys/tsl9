# Grid read-window C/C++ experiment

[繁體中文](README.md) · [Evidence](../../analysis/grid-read-windows-2026-10-25/readme.en.md)

One432-byte readonly pool/two genuine DATA labels. Experimental partial link only;accepted sources and coverage stay unchanged. No flashable BIN. The third table remains unresolved.

Set `LLVM_BIN` to the established LLVM tool directory:

```sh
python3 experiments/tsl9-grid-read-windows/audit-v1.py
python3 experiments/tsl9-grid-read-windows/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python3 experiments/tsl9-grid-read-windows/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-grid-read-windows/build/native-v1
```

Trials create new directories only;use `--replay` when the retained trial exists. Replay does not recompile or execute the target.
