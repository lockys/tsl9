# C/C++ software-copy source DATA experiment

[繁體中文](README.md) · [Analysis evidence](../../analysis/record-copy-windows-2026-10-25/readme.en.md)

`src/record_copy_windows.v1.c` reconstructs 94+106 bytes from two original software-copy sources. Readonly DATA only; no executable firmware or proven physical feature names.

From the project root, run the read-only static check (Python 3.10+; tested on Windows):

```sh
python3 experiments/tsl9-record-copy-windows/verify-v1.py --static-only
```

On Windows, `py -3` can replace `python3`. Native measurements use the existing hash-pinned Windows LLVM tools. Set `LLVM_BIN` to that directory and choose a fresh output name:

```sh
python3 experiments/tsl9-record-copy-windows/verify-v1.py --tool-dir "$LLVM_BIN" --trial my-copy-data
python3 experiments/tsl9-record-copy-windows/verify-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-copy-windows/build/my-copy-data
```

PowerShell uses `$env:LLVM_BIN`. `--trial` creates a new directory; `--replay` does not recompile. No downloads, hardware operations or firmware/model execution. Toolchains on other hosts remain unvalidated.

Subsequent curation and diagnostic integration are documented in the [integration evidence](../../analysis/record-copy-integration-2026-10-25/readme.en.md). The v1 records here retain their standalone scope;flash readiness remains unproved.
