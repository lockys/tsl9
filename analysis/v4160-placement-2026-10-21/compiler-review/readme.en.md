# IRQ register constraints: native compilation blocked

The frozen readable C implementation explicitly preserves the original A2/A3 boundary and commits exact A0/A1/A4/A5 values. Its primary native profile uses RV32IMAC_Zicsr, ILP32, **-Oz**, and allocates only A0/A4/A5. A1 is reserved except for explicit fixed-register commitments; all other integer registers, including SP, are reserved. The local Android NDK Clang 18.0.2 fails all five functions in both C11 and C++17 with:

```text
Stack pointer required, but has been reserved.
```

No object or linked ELF is emitted. Consequently no new native size, encoded register preservation, native output pattern, slack or original-placement result is claimed. In particular, old 118/22-byte IRQ/helper results from a different register contract cannot be used as a budget for this candidate.

Exactly three additional bounded diagnostic profiles were authorized and tried. They form a 2×2 matrix with the original profile; all four profiles keep -Oz and preserve the A2/A3/SP/GP restrictions.

| Source | Allocator | C11 | C++17 |
|---|---|---|---|
| Frozen original | A0/A4/A5 | five allocation errors | five allocation errors |
| Value-returning A0 `+r` commitment; return it directly | A0/A4/A5 | five allocation errors | five allocation errors |
| Frozen original | A0/A1/A4/A5 | five allocation errors | five allocation errors |
| Same value-returning diagnostic | A0/A1/A4/A5 | five allocation errors | five allocation errors |

The diagnostic source copies exist only inside the local build archive. The parent C/header files are unchanged. No branch-first rewrite, stack wrapper, allocation expansion to A2/A3 or alternate optimization was tested or adopted. The value-returning experiment removes a separate return SSA lifetime, but that alone and its combination with A1 allocation did not resolve compilation. The exact allocator root cause remains unconfirmed; the compiler's actual diagnostic is retained.

A concrete next implementation question is the helper's source lifetime layout: the observed optimized IR computes both OR and AND_NOT expressions, selects the result and stores it **before** branching to the two register-commitment blocks. A readable branch-first C formulation with calculation, store and commitment inside each arm may change that lifetime overlap. It has not been tested here and is a next implementation action, not an established fix or a reason to weaken the register contract.

The same frozen profile can emit optimized LLVM IR. The separate bounded IR checker confirms **20 ordered CSR/MMIO effects**, six fresh 32-bit RCC RMW expressions, **seven exact full-register commitments**, and the final fresh RMW return. Each standalone helper tests the full 32-bit enabled flag, uses one fresh read/store, and commits the exact nonzero A1 value plus the branch-specific physical base/before pair. Six IR transcript controls per original C/C++ result reject missing/wrong commitments, CSR mask, PFIC width, RMW mask and final return. These are IR/source facts, not native machine proof. The value-returning diagnostic IR is retained and hashed; it is not passed through the original input-only commitment checker.

`results.json` selects eight byte-identical receipt copies. `final-audit.json` seals the source checker, CLI, metadata and separate language documents. Local failed compile logs, IR and disposable source variants remain under `build/`; build archives are not needed for fresh reproduction.

```sh
# Reproduce the frozen primary profile, retaining the explicit negative native result.
python apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-review/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both

# Read-only metadata/source check; replay local historical logs/IR if present.
python apk-analysis/tsl9-v4160-placement-2026-10-21/compiler-review/check_review.py --project-root .
```

The primary CLI reports `expected_native_blocker_reproduced: true` and **`native_verification_passed: false`**. Its successful process exit means the recorded blocker and separate IR evidence were reproduced, not that native firmware compiled. If a different supplied compiler changes the outcome, the CLI refuses to silently treat that as a proved native result. `--clang` may name an explicit local executable. Add `--require-local-builds` to the read-only checker to require the selected historical archives; metadata validation is not fresh compilation.

The diagnostic source CLI is `probe_commit_return.py` (`--allow-a1` selects the final combined profile); `probe_allocator_a1.py` reproduces the original-source A1 allocation diagnostic. All take `--project-root` and `--tool-dir`, use local tools, and retain an honest failed native result. No target execution, ISA emulation, network, hardware access, image patching, firmware BIN or OTA operation occurs. A future implementation must resolve allocation while actually proving the original register and normal-output contracts before any layout integration.
