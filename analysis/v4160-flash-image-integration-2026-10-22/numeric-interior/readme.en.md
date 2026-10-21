# Literal interior references for eleven functions

[繁體中文](README.md)

This supplemental offline inventory examines every byte offset in the original official image, the previous IRQ image and the new eleven-function candidate for literal little-endian 32-bit values inside the eleven original function extents, excluding their entry addresses. Extents come from the sealed entry-order integration plan. Every input must match its complete SHA-256 and 76,800-byte size.

Each image has 1,030 selected values and 76,797 possible four-byte carrier positions, including unaligned positions. Values use original VMAs and the same VMAs plus `0x08000000`; examining these numeric forms does not establish a hardware mapping. Ten synthetic detector controls cover both forms, all four alignments, and exclusion of function entries.

See `report.json` for actual results. This supplements recorded relocations and direct branch inventories. No literal hit does not rule out computed, separately encoded, encrypted, ROM or runtime references, and cannot justify ignoring the lost program `+8` instruction boundary. No original or rebuilt target execution, ISA emulation, BIN generation, hardware or OTA validation occurs.

Run `python scan.py --project-root <project> --original <official-BIN> --previous <previous-IRQ-BIN> --candidate <eleven-function-BIN> --check`, or pass the same arguments through `sh scan.sh`. Native Windows Python evidence does not establish shell, Linux or macOS execution.
