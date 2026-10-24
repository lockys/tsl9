# Record decoder and status setter

[繁體中文](README.md)

Selected originalC6A8–C776 is206B/75 instructions;FAF8–FAFE is6B/2 instructions. Both entries are frameless. Retain fresh GP+220 word reads,unsigned masks/multiply,target-byte preserving writes andthe no-link12A08 tail.

The full word atGP+224 includes one byte beyond the preceding seven-byte copy. Do not narrow it or claim buffer bounds. Target offsets2,7,8 and4–6 remain raw fields; seat/do-not-disturb meaning is unproved.

Offline C11/C++17 compilation andpositive static checks only; no target,HOST-model orISA execution andno flashable BIN.

Actual C/C++ checks pass:212B/77i/17 regions;main4636B code+456B data/309RELA/20UND. See[analysis](../../analysis/record-decode-2026-10-24/readme.en.md).

~~~sh
python3 experiments/tsl9-record-decode/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-decode/build/trial-v1
python3 experiments/tsl9-record-decode/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-decode/build/component-v1
python3 scripts/check-record-decode-publication.py
~~~
