# Conditional address check for a missing resident word

[繁體中文](README.md)

The retained WCH V1.31 reference HEX omits the last four bytes `[0x6EB2C, 0x6EB30)` of the candidate loader's second copy source `[0x6EAA4, 0x6EB30)`. This is an **absence of file records**, not evidence that physical Flash is absent or erased. See the [dependency ledger](../tsl9-six-dependency-ledger/readme.en.md) for instruction windows, copy-helper and coverage evidence.

The [WCH CH32V208 datasheet V2.6](https://datasheet.lcsc.com/datasheet/pdf/036eca5d5805c8189aa2b0396c0860e1.pdf?productCode=C5187528), sections 2.1 notes 1–2 and 2.5.2, describes up to 480 KiB Code Flash with zero-wait and non-zero-wait areas; actual size depends on the model. In a **conditional numeric model** of a contiguous maximum `[0, 0x78000)`, the gap lies within that range. Only with additional assumptions of program-Flash boot mapping and a valid offset would it correspond to the high address `[0x0806EB2C, 0x0806EB30)`. The gap is also outside the candidate APP `[0x8000, 0x1AC00)`, so the APP BIN alone cannot fill it.

The checker pins the reference source map, verifies 17 segment files, and checks coverage and boundaries. It does not read hardware, fill the gap, execute target instructions, or establish boot mode, mapping, readability, missing contents, or the device's resident image. Strict linking still lacks `tsl9_boot_resident_40000`; this is not evidence for flashing.

```sh
python experiments/tsl9-resident-missing-word-map/verify.py --reference-dir analysis/wch-resident-candidate-2026-10-21/carrier-dec2023
```
