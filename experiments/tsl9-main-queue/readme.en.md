# Actual C/C++ main-queue and receive linkage

[繁體中文](README.md)

Reuse 1,464B / 509 instructions / 59 regions to bind 12C58 and 17002. The newly exposed 12ABE and 14D2E dependencies remain explicit. The C selector omits only the disarm definition already supplied by the parent; all retained bodies and typed references match the complete source.

~~~sh
python3 experiments/tsl9-main-queue/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-queue/build/providers-v1
python3 experiments/tsl9-main-queue/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-queue/build/component-v1
python3 scripts/check-main-queue-publication.py
~~~

[Analysis and limits](../../analysis/main-queue-2026-10-24/readme.en.md). This unresolved VMA-zero ET_REL is not a flashable BIN. No target, HOST-model or ISA execution, hardware or network access occurred.
