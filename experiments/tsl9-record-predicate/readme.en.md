# Record predicate 821E
[繁體中文](readme.zh-TW.md)

Reconstructs official42B/15i `[0x821E,0x8248)` as ordinary C arithmetic with only empty register/GP asm ports. Entire C11/C++17 function bytes equal the original BIN; no frame/stores/calls/UND/relocations. Selected `src/predicate.v2.c`; curated repository copy `src/native/receive/record_predicate.c`.

Reads [GP+84] pointer and pointer+4 bit3 before checking even an invalid index. If bit3 is zero and unsigned index<=2, reads a fresh GP+193+index byte and tests unsigned byte<3. A4/A5 residues are preserved. GP/pointer validity and flag identity remain unknown; no DND attribution.

Each formal `build/verified-v3/{c,cpp}/verification.json` passes65 negatives:46 raw ELF typed/metadata,2 whole-file padding,13 IR,4 source;63 do not rely on whole-file hashes. Complete IR,15 typed operands, all42 original bytes, two MD inputs and five actual recipes are checked.

[source-history.json](source-history.json) retains two finite source versions, failed outputs and verifier repairs. The initial failed verifier was not archived; do not claim otherwise. The known pre-root-repair verifier is preserved in `history/verify.pre-root-path-fix.py`. v3 only canonicalizes the Python executable path; source/flags are unchanged. Two observed Python executables have different hashes: use the same actual interpreter pinned in the receipt. A different interpreter correctly fails equality. Original v1/v2 outputs/receipts remain local and are not rewritten as v3.

```sh
python experiments/tsl9-record-predicate/verify.py --language c --out-dir experiments/tsl9-record-predicate/build/verified-NEW/c --llvm-bin "$LLVM"
python experiments/tsl9-record-predicate/verify.py --replay experiments/tsl9-record-predicate/build/verified-v3/c/verification.json --llvm-bin "$LLVM"
```

No target/ISA/MMIO/hardware execution. Nominal821E linking is not physical installation. `--require-firmware-ready` must reject. Full IRQ/ROM/memory/BLE OTA compatibility and new features remain unproved.
