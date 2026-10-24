# Actual record-provider and SPI linkage

[繁體中文](README.md)

Reuse 1,000B / 349 instructions / 67 architectural regions from eight existing C/C++ units, covering 81AA, 821E, 16B7C and 18CA4 with their necessary dependencies. All complete source objects receive positive static original-byte audits. Only the complete six-byte 81AA leaf is selected from its 24-byte object containing two functions. Other units retain all required regions, ordered by original PC.

[Analysis and limits](../../analysis/record-providers-2026-10-24/readme.en.md)

~~~sh
python3 experiments/tsl9-record-providers/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-providers/build/providers-v1
python3 experiments/tsl9-record-providers/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-providers/build/component-v1
python3 scripts/check-record-providers-publication.py
~~~

The main component has 5,636B code + 456B data, 356 RELA and 16 UND, with identical C/C++ bytes. The 95 C/H files, 68 code units and independent pointer-data source are unchanged; curation totals 138 comparisons / 276 objects. This VMA-zero ET_REL is not a flashable BIN. Physical MCU, ROM/ABI, memory/IRQ and OTA compatibility remain unproved. No target, HOST-model or ISA execution, hardware access, network access or legacy negative-matrix execution occurred.
