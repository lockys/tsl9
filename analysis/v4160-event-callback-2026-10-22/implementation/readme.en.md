# Callback implementation and evidence layers

[繁體中文](readme.zh-TW.md)

Formal HOST: model `verify_host.py --project-root ROOT --language both`. Formal native: `verify_native.py --project-root ROOT --tool-dir LLVM --language both`. Both accept a new owned `--build-root`, emit `BUILD/{c,cpp}/verification.json` and stdout receipt/hash results. `--replay RECEIPT` is read-only artifact inspection and forbids build options.

Model `verify.py` / POSIX `verify.sh` default to HOST; `--kind native` selects native. `probe_native.py` is a pinned generation substage, also supporting owned diagnostic source copies. The formal producer uses canonical source only. `compare_inline.py` reproduces the sole qualifier experiment from adopted source by removing `always_inline` for baseline and retaining it for the variant. It performs no profile sweep.

The historical first-native938+90=1,028-byte diagnosis predates A4 residue fixes. Corrected baseline is944+90=1,034; adopted inline output is658. Historical artifacts remain, but are not current formal source identities. Original632-byte placement still fails.

Native replay binds five actual exact LLVM recipes, canonical3 plus real resource-header MD closure, before/after source/tool identities, actual generation/log and complete artifacts. The independent native checker covers658B/241rows, volatile widths, fifteen A5/A6 calls and measured frame/RA gaps, with actual malformed-ELF controls. Passing means the diagnostic subset only. HOST replay binds the positive and five single-change compiled source mutants, exact compiler recipes, exits/logs, every native-machine guard and actual files.

Synthetic named state/frame/providers are distinct from physical native GPR/SP/RA behavior. The parameter mask is an explicit projection, not a complete raw-prefix proof. Saved-link bookkeeping does not track each JALR RA or execute restored addresses. Extra S10@SP0, save order, call return offsets and unknown resident preservation remain unresolved. No full image, BIN, hardware or OTA admission is made.

Default `check.py` is source/metadata only. Explicit `--host-receipt`, `--native-receipt` or `--require-local-builds` reads real archives. Selected JSON metadata is published; generated objects/ELF/IR/PE/logs/copied build sources remain local.
