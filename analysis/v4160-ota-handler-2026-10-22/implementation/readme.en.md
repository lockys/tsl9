# OTA handler formal compilation and evidence

[繁體中文](readme.zh-TW.md)

`verify_native.py` is the formal native producer. Shared sources/HOST CLI live in `experiments/tsl9-v4160-ota-handler`. Actual C11/C++17 each produce 776 bytes /285 instructions, frame112, nine true UND symbols and 23 relocations, versus original 530/169. No link, BIN export, target execution or hardware verification occurred. Complete original ABI and placement remain false.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root . --replay PATH/verification.json
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/check.py --project-root .
```

Published paths use `analysis/v4160-ota-handler-2026-10-22`. Shell wrappers honor `PYTHON` (default python3). Fresh output is create-only under model/build; `--build-root NEW` selects an explicit new directory. Replay rejects generation flags and starts no compiler.

Default `check.py` validates source/seal/selected metadata only and never claims build replay. Repeatable `--host-receipt PATH` / `--native-receipt PATH` explicitly read actual archives. `results.json` records W archive locations plus byte-identical metadata copies; those historical paths are not required by metadata-only publication checks.

Native recipes bind exact resource query/object/IR/disassembly commands, source/tool/resource identities, complete artifact sets, actual MD closure and every instruction byte. The original BIN is not a codegen input; true UND entries await real section-backed providers. No numeric providers were fabricated.

Formal HOST per language: 1 group /10 cases /8292 checks plus three compiled negatives. Independent HOST: 16 narratives /18 dispatches /898 checks plus four compiled negatives. These prove bounded named-state/effect projections, not physical fullraw8/frame/callee preservation. W's selected A3/A4/A5 repair does not establish other scratch residues.

Historical `probe.py` measured a superseded 752-byte draft. Four final metadata receipts are retained under receipts/; generated objects, IR, executables and logs remain excluded. Independent source/native/HOST reviews are separate. This partial milestone does not replace the existing full image or complete the overall reconstruction goal.
