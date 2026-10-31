# GATT UUID original-coordinate diagnostic trial

[繁體中文](README.md)

This trial compiles the existing `write_UUID.c` as C11 and C++17, then joins the two-byte `FFF1` candidate to the retained APP relocatable component and original-coordinate diagnostic layout. It verifies all 73,538 prior bytes, owners and relocations and the six genuine unresolved providers. Only `0x1AB44..0x1AB46` is added, yielding 73,540 diagnostic bytes. This is not formal `src/` manifest integration or a complete GATT table.

```sh
python experiments/tsl9-gatt-uuid-original-coordinate/verify.py --tool-dir /path/to/llvm/bin --output-dir /existing/parent/new-trial
```

The output directory must not exist. Retained local frozen objects and the original BIN are required; only the permitted two-byte UUID is read from that BIN, never excluded regions. C/C++ diagnostic ELFs must match, have entry zero and no `PT_LOAD`. Strict linking with the genuine unresolved input must fail on the same six providers. No BIN is generated and no target is executed; reference coordinates do not provide ROM or prove hardware compatibility.
