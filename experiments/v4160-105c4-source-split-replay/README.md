# 0x105c4 source-byte split replay

This bounded experiment replaces one exact definition in a **memory copy** of
`src/native/receive/feature_state_records.c` with an `extern` declaration. It
never writes the formal source and does not publish or compile the split output.
It is a building block for a separate local selected-link experiment, not a
formal integration or an executable firmware reconstruction.

The input is 55,715 bytes, SHA-256
`19a1c39ee7831f42960454d02393512520c425ea1ad90f9e08b0f8d4e3b32db3`.
At byte offset 5968 its 325-byte exact block must occur once. Replacing it with
60 bytes yields 55,450 bytes, SHA-256
`d7f29f5420dc209f206eb424a527b6c9ed8000eb392ee25a35e2be2b1b90aada`.
Both input and result are checked before success. These pins identify these
specific bytes; they do not prove trust or equivalence for other versions.

From the repository root, using Python 3 with its standard library:

```text
python -B experiments/v4160-105c4-source-split-replay/verify.py --inspect
python -B experiments/v4160-105c4-source-split-replay/verify.py --test
python -B -O experiments/v4160-105c4-source-split-replay/verify.py --test
python -B experiments/v4160-105c4-source-split-replay/test_cli.py
python -B -O experiments/v4160-105c4-source-split-replay/test_cli.py
```

`--test` runs four tests in its current interpreter; the normal and `-O`
commands are distinct. The tests exercise every byte of the selected block,
ambiguous/changed inputs, and reachable offset, length and result-hash guards.
`test_cli.py` uses temporary copies to check CLI success, invalid arguments,
changed or absent source, and a file inventory with sizes, modification times
and hashes before and after each invocation. It does not observe transient writes,
other locations or restored metadata; it is not a filesystem sandbox. Its children
use the same optimization setting as the test runner, so both commands matter.

The original block is an assembly-based register-level region, while the
replacement is only an extern declaration. This check does **not** establish
C/C++ types, calling conventions, relocation or `.llvm_addrsig` preservation,
link equivalence, reachability, runtime behavior, or equality with any BIN.
It does not execute, emulate or flash the target.
