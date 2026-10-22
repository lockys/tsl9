# Local paths

[繁體中文](local-paths.zh-TW.md)

Scripts derive the project root from their own location, without a user account name or dependence on the current directory. Legacy scripts use the variables below; newer verifiers also accept their existing `--tool-dir` and other path arguments.

| Variable | Purpose |
| --- | --- |
| `TSL9_LLVM_BIN` | Existing directory containing clang, ld.lld and llvm-objdump |
| `ANDROID_NDK_HOME` / `ANDROID_NDK_ROOT` | Search for one usable NDK prebuilt/bin when no LLVM directory is set |
| `TSL9_R2` | Existing radare2 executable; otherwise use PATH |
| `TSL9_ANALYSIS_WORKSPACE` | Retained workspace required only by historical reviews |
| `TSL9_PYTHON` | Python for legacy PowerShell entries; otherwise discover it on PATH |

Keep variable values in your own shell/local configuration, outside Git. Paths may contain spaces. Missing, invalid or ambiguous tool locations produce an actionable error; no download or search through other accounts occurs.

Run `python3 scripts/project_paths.py --select project-root` to inspect resolution. This reads local paths without running firmware or connecting hardware.

Path changes alter script source hashes. Old receipts remain historical evidence and do not validate modified scripts; rerun the required checks to create new receipts.
