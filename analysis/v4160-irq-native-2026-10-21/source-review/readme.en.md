# Branch-first IRQ C core: independent host review

This review tests the frozen `experiments/tsl9-v4160-irq-native/src/interrupt_registers.c` and `native_io.h` through `TSL9_IRQ_REGISTERS_HOST_TEST=1`. The public header and void host callbacks are reused from `tsl9-v4160-interrupt-registers`. It is a C/C++ behavior review, not another raw-firmware decoder or a native-register proof.

The independent synthetic oracle is reused **unchanged** from the prior placement code review: `independent-tests.c` SHA-256 `e40f4b8e986e705d6c8c29a34c793ce74d7c37a506e0ddedfecd80a1e2b783b4`, sealed under `cf4881fc4618d32fa3d982659f733b649a4bee1445ffa52232feb249cbfed279`. Replaying this separate oracle against the new core avoids copying or silently changing the previous evidence. The runner verifies the old seal and every member before use, and pins all new source/header inputs.

## What the host test establishes

Each mode passes 4 groups / 3820 cases / 138312 assertions. The helper matrix varies full 32-bit data, masks and enabled words across all four RCC addresses. Nonzero values including 2, 3, 0x100, 0x7FFFFFFF, 0x80000000 and 0xFFFFFFFF select the enabled branch while their exact bits remain in the A1 observation. Enabled outputs are `(before|mask, enabled, 0x40021000, before)`; disabled outputs are `(before&~mask, enabled, before, 0x40021000)`. The output base is not the full peripheral address.

The main oracle supplies six deliberately distinct fresh read values and checks all twenty external effects in order and at their original widths: CSR clear, six READ32/WRITE32 pairs, six PFIC writes, CSR set. Six helper boundary observations and one final boundary observation are checked separately. It verifies last-clear A0 and normal A1=0, A4=128, A5=0xE000E000. Synthetic CSR drift between effects checks setting then-current bits rather than restoring an entry snapshot. Every callback is bounded and treats peripheral addresses only as numeric values.

Twenty-two mutants are actually compiled and assertion-rejected per language, 44 across C11/C++17. They include truthiness and exact-enabled-bit faults, base/address and sampled/modified-word output faults, wrong OR/clear semantics, helper offset, truncated dynamic masks, cached branch reads, write-before-read, wrong width, wrong main A0/A1/A4/A5, CSR mask/order and omitted PFIC write. Two of these are host-header mutations that preserve the output callback tuples but corrupt RCC/main return values, proving that the return-value checks are distinct from output observations. Compilation failure is never counted as a behavior rejection.

No source-level mismatch was found within this normal numeric-I/O/output/return interface. `receipts/` retains selected byte-identical JSON metadata outside excluded `build/`; actual local EXEs, objects, logs and generated mutant sources remain historical working artifacts and are not published payloads.

## Limits and replay

The host macro substitutes base/literal/memory/CSR primitives and the returned-A0 bridges. These tests therefore do **not** validate production assembly, the native `+r` bridge, actual A0/A1/A4/A5 registers, preservation of A2/A3, stack/RA/IRQ behavior, compiler outliners, original placement or hardware/OTA compatibility. The four helper native identities and main native structure require the separate native review. Host success is not promoted to those claims.

```sh
sh verify.sh --project-root /absolute/path/project --language c
sh verify.sh --project-root /absolute/path/project --language cpp
# Direct backend, also usable from Windows:
python3 run-review.py --project-root /absolute/path/project --language c
```

The runner requires Python 3.10+ and an installed compiler located through `scripts/portable_verify.py`. It accepts working `apk-analysis/tsl9-...` and published `analysis/v4160-...` peer layouts. Local execution used Windows/MSVC; shell syntax is provided as a portable entry, with no claim of local WSL/Git Bash or Linux/macOS execution. No network, device I/O, RV32 execution or ISA emulation occurs.

`python3 check-review.py --project-root <project>` only binds the frozen inputs, immutable peer seals and selected receipt hashes. It reruns neither compilers nor host tests, and does not establish new native evidence.
