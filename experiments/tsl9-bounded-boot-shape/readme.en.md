# Bounded BOOT and image-shape check

[繁體中文](README.md)

The [checker](check.py) rechecks 14 instruction anchors in the retained ID2580 candidate BOOT and reads only the first APP byte and file size of official ID2966 and the TX candidate. Both APP files are 76,800 bytes and start with `0x6F`. Under the previously analyzed BOOT's 1,024-byte page and 0–95 numeric page limit, all 75 page indices 0–74 fit; adding two index bytes gives 1,026 bytes per page.

These are **shape conditions against the analyzed candidate BOOT**. They do not identify the installed BOOT, establish full-image equality, signature or integrity acceptance, flashability, or successful restart. Instruction and limit semantics come from the [prior BOOT review](../../analysis/v4160-tx-image-integration-2026-10-22/image-plan/readme.en.md); this checker pins anchors without independently disassembling them. It reads no other APP byte or excluded APP range, executes no target and contacts no hardware.

Run: `python -B experiments/tsl9-bounded-boot-shape/check.py`.
