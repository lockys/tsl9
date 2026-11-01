# OTA page evidence for the TX candidate

[繁體中文](README.md)

The [checker](check.py) reads only the third 1 KiB page of the ID2966 V4.1.60 official image and TX-integrated candidate: zero-based page index 2, nominal addresses `[0x8800,0x8C00)`. It reads no other pages or excluded APP ranges. The 93 differences on that page all lie within the reviewed TX range `[0x8A56,0x8B6E)`, with first and last at `0x8A7F` and `0x8B6B`.

The official page SHA-256 is `d835e10c8861c681e9c371f7ba99e885ca4d8db33a435d1f03555ce36d41347f`; the candidate page SHA-256 is `72d7f81f1d65031c55869b541b90e76d22b85d5ca340aaf46acc5346fcf2350e`. These cover 1024-byte payloads without the OTA index. Equality outside TX comes from the [existing full-image static review](../../analysis/v4160-tx-image-integration-2026-10-22/readme.en.md), not newly reading other pages.

Morphe RAW parsing uses 1024-byte payloads with two big-endian index bytes; its selection debug log records full-file and transfer-payload SHA-256. A future trustworthy candidate-selection digest and successful page 2 readback could narrow uncertainty about the transferred candidate, but would not prove execution after restart, all functions, resident compatibility or safety. This check does not execute firmware, flash hardware or generate a new BIN.
