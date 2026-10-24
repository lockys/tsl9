# Code and table integration for channel/feature dispatch

[繁體中文](README.md)

Selected 2,736B code and 60B relative tables retain 15 genuine table targets and 698 main-component references. The parent supplies the exact 26-byte clock bodies and existing C6A8 entry. C selection preserves every retained compiler body and reference.

~~~sh
python3 experiments/tsl9-dispatch-tables/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-dispatch-tables/build/providers-v2
python3 experiments/tsl9-dispatch-tables/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-dispatch-tables/build/component-v2
python3 scripts/check-dispatch-tables-publication.py
~~~

[Analysis and limits](../../analysis/dispatch-tables-2026-10-24/readme.en.md). Current receipts are providers-v2 and component-v2. The first duplicate-definition attempt is retained unaccepted; component-v1 records the pre-alias 83-UND stage. No legacy verify()/negative function, target, HOST-model or ISA execution, hardware or network access occurred. This is not a flashable BIN.
