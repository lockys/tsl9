# V1.31 RF helper and sparse gate checkpoint

Offline research only; no hardware execution or flashable output. This checkpoint includes the instruction interpreter, RF composition, startup-copy model, sparse evidence gates, and their host tests. The normal connected model stops at the unrecorded second-copy word `[0x6eb2c,0x6eb30)`; the injected fixture is explicitly hypothetical, not evidence that the word exists or that the device executes successfully.

## External inputs and limitations

This branch is **not self-contained for a complete replay**. It intentionally excludes external SDK resources, locally derived reference segments, generated outputs and private material. The pinned official HEX must be obtained separately from the fixed WCH commit and placed at `analysis/v131-startup-source/wchble_rom.hex`; its URL and SHA-256 are in `analysis/v131-startup-source/README.md`. That README's description of the HEX as being in the directory applies only after provisioning it locally. RF provenance also requires `analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h` and the hash-pinned carrier plus its 17-segment `source-map.json` and binary files under `analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/`. These local derived files are not distributed here. The sparse link additionally needs a suitable RISC-V toolchain; its diagnostic ELF and APP inputs are not included. Consult the individual scripts for their exact paths and identity checks. Do not substitute guessed values for absent bytes.

## Host verification

From the repository root, with the external inputs provisioned locally:

```sh
python -B -m unittest discover -s tests -p 'test_rf_tx*py'
python -B -m unittest discover -s tests -p 'test_sparse_resident*.py'
python -B tests/test_v131_sparse_startup_copy.py
python -B experiments/tsl9-copy-instruction-interpreter/test_interpreter.py
python -B experiments/tsl9-copy-instruction-interpreter/test_rf_integration.py
python -B analysis/v131-startup-source/test_check.py
python -B analysis/v131-startup-source/test_dataflow.py
```

These tests were run with local external inputs; the interpreter's C differential was skipped without `COPY_C_ORACLE`. The C reference differential also requires its compiler/oracle setup. No full sparse ELF relink or hardware validation is claimed.
