# Single negative command-switch experiment

[繁體中文](readme.zh-TW.md)

Only the five outer full32 command if-tests in compact568 became switch/cases. Unknown-command no-op, effects, locals, shared terminal reply labels, all eight-register bridges and native flags remain unchanged. Sources were copied via apply_patch into this scope/build/source/src; previous models/seals were untouched.

Actual C11/C++17 each produce568 bytes /193 instructions /frame48 /nine true UND /20 RELA. Payload SHA `b486c6eed0d3465c8947fd338e790f1441f29c64827a47b20e1fada18ff863af` equals the sealed baseline byte-for-byte. No improvement; no new model is promoted. The baseline was not rebuilt, unchanged HOST suites were not rerun, and no further variants or flag sweeps followed.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/dispatch-probe/check.py --project-root .
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/dispatch-probe/check.py --project-root . --receipt PATH/verification.json
```

Published case paths may use analysis/v4160-ota-handler-layout-2026-10-22. Default checking reads seal/baseline source pins/selected metadata only and does not claim actual archive replay. Explicit --receipt requires real retained sources, object/IR/MD/logs under the same project root; missing files reject. Historical W locations are not default publication dependencies. Build/source and archives are excluded, so an archive-free publication check is not actual replay.

probe.py retains the four exact diagnostic recipes: resource query, MD object, IR and complete M/A/C/Zicsr objdump. Outputs are create-only with source/tool/resource before-after pins and complete artifact inventory. It can replay existing local archives; it is not a promoted producer. source-change.patch records the pure C dispatch change.

The original530-byte region remains38 bytes too small. Complete ABI/placement remain false. No link, numeric providers, BIN, RV32 execution/emulation, hardware or network action occurred.
