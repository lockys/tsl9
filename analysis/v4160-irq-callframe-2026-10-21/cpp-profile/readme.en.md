# One C++ profile removes extra unwind allocation

Adding **only `-fno-exceptions`** to the sealed C++17 native profile removes `.eh_frame` from both the actual object and linked ELF. No RTTI flag, optimizer change, register-allocation change or source change was made. The other flags remain -Oz, machine outliner disabled and only A0/A1/A4/A5 allocatable; SP and all other integer registers remain reserved.

| Measured result | Sealed C++ baseline | New C++ profile |
|---|---:|---:|
| Five function bytes | 300 | **same 300 bytes** |
| Each helper | 30 bytes / 12 instructions | identical |
| Initializer | 180 bytes / 65 instructions | identical |
| Object `.eh_frame` | 120 bytes | absent |
| Linked `.eh_frame` | 124 bytes, VA0 | absent |
| Total object allocation | 420 bytes | 300 bytes |
| Total linked allocation | 424 bytes | 300 bytes |
| All allocated bytes belong to five functions | false | **true** |
| Initializer fits original 144-byte slot | false | **false** |

This is the frozen **leaf initializer** from `experiments/tsl9-v4160-irq-native`, not a separately developed callframe implementation. The four helpers remain at original addresses 0x19124/0x19142/0x19160/0x1917E and still equal the original 120 bytes. The initializer remains at diagnostic VA0x30000, 36 bytes too large for its original 144-byte extent. Scratch storage suitability, original full-image integration, complete original ABI and OTA readiness remain unproved/false. Resolving the C++ metadata obligation does not resolve placement.

The portable runner verifies the prior immutable seal and exact checker/parser/baseline receipt hashes before importing them. It compares actual function bytes against the raw rows in that sealed C++ receipt, without requiring its ignored build archives. All five functions are byte-identical and their machine/normal-output/LLVM-IR proof results match: full byte coverage and encoded destinations, no SP/T0/A2/A3/hidden calls/writable data/undefined symbols, zero helper A1 writes, exact initializer20effects, seven ordered commitments and final normal output definitions. Thirty transcript controls are replayed. No new source-mutant compilations or other profiles are claimed.

```sh
python apk-analysis/tsl9-v4160-irq-callframe-2026-10-21/cpp-profile/verify_cpp_profile.py --project-root . --tool-dir /path/to/llvm/bin

sh apk-analysis/tsl9-v4160-irq-callframe-2026-10-21/cpp-profile/verify_cpp_profile.sh --project-root . --tool-dir /path/to/llvm/bin

python apk-analysis/tsl9-v4160-irq-callframe-2026-10-21/cpp-profile/check_cpp_profile.py --project-root .
```

`--clang`, `--linker`, `--objdump` and `--firmware` override local inputs. The pinned prior runner supplies the same workspace/published offline firmware resolver and exact hash checks. Fresh builds need the frozen native/public sources, the explicitly pinned prior checker/parser/receipt/seal sources, this new runner, the offline original image and local LLVM tools; they do not require old compiled archives. The direct Python CLI was run on Windows; the POSIX launcher is supplied as source and was not run through WSL/Git Bash.

`results.json` selects one byte-identical receipt outside `build/`. The read-only checker validates metadata and current source/dependency pins, then replays actual artifacts if available; add `--require-local-builds` to require that historical archive. Metadata validation is not fresh compilation. All generated ELF/IR/logs remain local, with no firmware BIN, target execution, ISA emulation, network, device access or old/model/P/D/sealed-file edits.
