# Required RF initializer bodies and polling

[繁體中文](README.md) · [RF send/retry](../tsl9-original-RF-tx-path/readme.en.md) · [Original initialization bridge](../tsl9-original-RF-bridge/readme.en.md)

Provide five genuine missing callees and their two helpers: **4,090 bytes /1,298 instructions in seven complete bodies**. C/C++ preserves original register context and required assembly ports; these are not ordinary host-callable APIs.

| Candidate body | Original range, end exclusive | Bytes /own frame |
| --- | --- | ---: |
| Register initialization | 0x660CE..0x66242 | 372 /16 |
| Register sequence/poll | 0x662DA..0x6636E | 148 /0 |
| Register sequence | 0x6636E..0x663A6 | 56 /0 |
| Large setup/calibration-like body | 0x6645C..0x67198 | 3388 /80 |
| Register-bit setup | 0x67198..0x671AA | 18 /0 |
| Register-write/software-loop helper | 0x66098..0x660CE | 54 /0 |
| RAM polling helper | 0x20002DF2..0x20002E28 | 54 /0 |

Calibration is an inference from setup/readback patterns. Physical register and chip identities remain unproved.

## Actual callers and guards

Original initializer0x64298 calls0x660CE at0x642FE. This call dominates its local tail in the complete normal-return CFG.

Common reset0x641B0 calls the other four entries at0x64246/0x6424A/0x6424E/0x64252 in order,**conditionally rather than on every path**. Two separate reads of byte0x2000351B compare against4; pointer word0x20003504 compares against0x40024300. All three guard fallthroughs are necessary to enter that call path. This does not establish asynchronous stability or callee termination/register preservation.

## Polling and the late branch

- Helper0x66098 reloads pointer word0x20003590 and writes raw values0x1101,0,0x1101 at pointed offset12,with two software loops initially20. Physical reset meaning and duration are unproved.
- Body0x662DA writes raw80 to offset100 through pointer word0x2000353C,and polls that word plus another block's offset156/bit8.
- The RAM helper uses raw6000 and polls offset100 plus another block's offset144. Bits26 and25 come from **distinct volatile reads**; do not combine them into a mask on one observation.
- At0x664D0,the large body compares word0x20003588 against0x12345678. The matching path reaches late arm0x67190 after the textual return,clears the word,and jumps to0x665B0,skipping three earlier polling-helper calls before continuing later setup. No runtime control or calibration-skipping option is added.

80/6000 are original numbers,**not proved time units or termination guarantees**. MMIO capacity,side effects,aliasing and asynchronous effects remain open. None of these writes was executed on physical hardware.

## Verification and limits

Actual C11/C++17 objects are identical. All4,090 original-context bytes,whole CFG own frames,52 official Xwchc positive vectors,four actual ports and two ELF readers pass. The25 FUNC regions are compiler fragments,not logical functions. Every input byte/symbol/relocation and unique source-PC ownership is retained.

The unique composition contains **18,526 CODE+256 DATA bytes /6,330 instructions**,1,194 FUNC regions and894 relocations. Five genuine missing callees are supplied,so remaining named dependencies fall from **19 to14**,without adding new ones. Zero named imports in a unit does not close RAM/MMIO/polling behavior.

Formal APP stays159 C/H files and95.54% byte coverage,not functional completion. No APP integration,newBIN,target/model execution or hardware access. The4-byte startup source gap,physical ROM/RAM/ISA/IRQ,whole-program stack/aliasing,Flash andOTA compatibility remain open. **Usable replacement firmware has not been successfully reconstructed.** Initialization/polling provenance diagnostics remain an unimplemented observation-only UI candidate.

[C/C++](original_RF_reset_path.c) · [Original instructions](evidence-v1.json) · [Audit](audit-result-v1.json) · [Summary](summary.json)

## Reproduce

Provide pinned local inputs,prior native artifacts,Windows NDK LLVM and official headers required by the trap audit. Missing inputs are not downloaded.

```sh
python experiments/tsl9-original-RF-reset-path/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-RF-reset-path/build/native-v1
python experiments/tsl9-original-RF-reset-path/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

For new artifacts replace `--replay` with `--trial`,and add `--link-trial` to the second command;names must be unused. Cross-platform compilation is unverified.
