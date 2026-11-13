# V4.1.60: bounded `0x2000beeb` replay

Offline, standard-library only. Run from the repository root; no Git, network, installation, compilation, or target execution:

```sh
python -I -B experiments/v4160-beeb-bounded-compact/verify.py --test
python -I -B -O experiments/v4160-beeb-bounded-compact/verify.py --test
python -I -B experiments/v4160-beeb-bounded-compact/verify.py --inspect
python -I -B -O experiments/v4160-beeb-bounded-compact/verify.py --inspect
```

`--test` uses the actual single file as `__main__`, prints full unittest IDs and fails on skips. No importing a project module or stale project pyc. `--inspect` reads and checks real inputs, prints actual candidates and fails if they differ from the fixed expected list. All checks remain active with `-O`.

Inputs are exactly `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` (76,800 bytes, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`), `src/source-manifest.json` (`30e7076ed9fa896f5745024ab6fa0a9f016124a2dd11ae12fe566e2107f06479`), `src/source-build-manifest.json` (`466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739`), `src/native/startup/reset_data.c` and `experiments/tsl9-runtime-reset-clock/src/reset_data.c` (both `02aad93670679ef0c8c472dc998e3d41963ba33d280a5ec6baa336a3173ed1ec`). The whole files and lengths are pinned, the two source files compared byte-for-byte, and the selected manifest entries, unit and source carrier literals checked. BIN PCs map to file offset `PC - 0x8000`.

## Bounded facts

- The checked `0xae9e` window loads `0x2000beeb`; if nonzero, it writes 6 and the loaded byte plus 3 (truncated to a byte) at `gp+188` and `gp+189`, then `0xaeb4` stores zero to `0x2000beeb`. `0xb0b0` stores the low byte of `a0` there. `0xb096` instead loads `0x2000bee9` using a negative immediate.
- The checked reset window computes `gp=0x20004000`, copies 128 bytes from `0x1ab60` into `[0x20004000,0x20004080)`, and zeroes words in `[0x20004080,0x2000c958)`, **if that path is reached and the loops complete**. The word at `0x2000bee8` covers `0x2000beeb`. The checked data carrier equals the 128 BIN initializer bytes, but the source model is not the original owner and nominal allocations are not hardware proof. At `0x1873e`, if reached, the pointer loaded from `0x20000004` is used by JALR, which clears target bit 0; its actual value and reachability are not established.
- The full BIN raw scan checks every even file offset with eight bytes available: adjacent 32-bit AUIPC/LUI followed by 32-bit ADDI, integer load or store using the same nonzero base register. It handles signed immediates and checks whether the effective access width covers the target. The exact results are `0xae9e load`, `0xaeb4 store`, `0xb0b0 store`, all width 1 at `0x2000beeb`.

These are **raw candidates**, not a proof of instruction boundaries, reachability, all callers or all writers. Compressed instructions, non-adjacent address construction, indirect accesses and other forms are outside the scanner. The tests exercise pinned window byte mutations, missing/tampered inputs, reset range boundaries and word coverage, negative load immediates, wrong PC, scan edges and odd JALR targets; they do not execute firmware or prove hardware behavior.
