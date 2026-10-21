# Host executable guard follow-up

[繁體中文](readme.zh-TW.md)

This addendum supersedes the current host-runner entry in the earlier independent review. Its 17 sealed files remain byte-identical under seal `173c8790e2deaad0ae6ac29bea2cabdbc8be2c13b68edefc3d5beb37c545488c`. The old review pinned host runner `d1f470a8539eb9815eaa65230a6da974f7dd21b2c009950516e0e3d250cc377e`; that checker should reject the changed runner. No historical receipt is relabeled as a fresh result.

The compiler selection helper accepts an explicit compiler override. A successful compile alone cannot establish that its output is a host executable: a cross-compiler could produce RV32 code. The corrected runner reads and validates executable format/machine before launching each positive or behavioral-negative test. It explicitly rejects RISC-V ELF machine 243, rather than relying on an operating-system launch failure. This is a format gate for the owned test artifacts, not a general untrusted-program sandbox or a proof of executable behavior.

An earlier guard draft stopped safely because `platform.machine()` was empty in this shell environment. The final runner derives the process architecture solely from the currently running `sys.executable` header, the operating system, encoding and Python pointer width. The test artifact never determines the host architecture. The independent probe confirms that an empty `platform.machine()` does not change admission. Windows PE was actually exercised; Linux ELF and thin Mach-O support were reviewed as source, not claimed as physical platform runs. Unsupported interpreter formats fail closed, including a macOS universal interpreter where a supported thin header is required.

Fresh guarded C11 and C++17 host receipts each retain the exact 5 groups, 481 cases and 247191 checks plus six compiled behavioral controls. `review.json` binds the final runner, selected receipts and independent guard observation. The independent audit inspects the actual final guard order and uses actual host PE and RV32 component bytes. The RV32 rejection is tested through the runner with process spawning intercepted; the component is never launched. Guard observations distinguish a rejected format from an actual compiled test's semantic assertion failure.

All C/header/test inputs and native verification tools remain identical to the previous review. Its independent expected-effect fixture (12 scenarios/8964 assertions and twelve compiled controls per language) and native component proof (256 bytes/98 instructions, six functions) are reused as historical source-bound evidence. The old independent `run-effects.py` remains immutable and archival; it lacks the new gate and is not rerun. Native compilation and the full historical effect matrix are not repeated for this runner-only change.

The original limitations remain: the program alignment point and wrapper save order differ from the original; physical nonreturn GPR prefixes and asynchronous equivalence are unproved; the six-byte program tail remains unowned. There is no new firmware BIN, complete-image integration, hardware/Flash/ROM/OTA validation or product-feature implementation.

From the project root:

```sh
python apk-analysis/tsl9-v4160-flash-native-2026-10-22/review-v2/check-review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin
```

In published layouts, use the corresponding `analysis/v4160-flash-native-2026-10-22/review-v2/check-review.py` path. This command reads the retained evidence, current input hashes and actual original bytes, and repeats the 20 source-byte controls without executing instructions. It reports `actual_archived_artifacts_replayed:false` unless `--archive-root` is explicitly supplied with the retained v2 host artifacts. Selected receipt JSON files do not stand in for missing executable/compiler archives. Historical absolute Windows paths describe the actual run; fresh builds use the guarded model `verify.py` entry with explicit project/build paths. No original or rebuilt RV32 code is executed by this review.
