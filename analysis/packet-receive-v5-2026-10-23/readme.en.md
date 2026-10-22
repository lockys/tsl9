# Packet receive v5

[繁體中文](README.md)

Official ID2966 V4.1.60 `[0x16A7C,0x16B0A)` is reconstructed with C arithmetic and explicit machine ports: both C11/C++17 emit142B/52 instructions with one12B restore. **This is pending-link component evidence. Rebuilt firmware has not been verified to flash and run successfully on the original hardware.**

| Check | Result |
| --- | --- |
| Genuine FUNC/allocation | entry14B,body116B,finish12B at partial offsets0/14/130, no padding |
| Original projection | All120B outside4JAL/2branch windows match; SHA `528b69f7ec290450aa7b0338bdfbf25b88571693b0f2142199ccdb37c34479f6` |
| Actual relocations | Six addend0 records:3SPI+1ring calls to2 genuine UND,2branches to definedfinish FUNC; no ABS substitutes |
| Limit | All6 control immediates remain unapplied; projection equality is not complete142B machine-code equality |
| Build/replay | Per language:2actual ELF,9inputs,10artifacts,5complete recipes,source/header MD closure,41negative controls; strict readiness rejects |

Receipts: [C](receipts/packet-c.json) / [C++](receipts/packet-cpp.json), byte-exact copies of producer-portable JSON. [verify.py](../../experiments/tsl9-packet-receive/verify.py) checks entire ELF,52typed operations,complete normalized IR,original projection and actual owners/relocations without firmware execution. IR normalization excludes only the first two producer-path lines and uses LF. Raw local IR/logs were not uploaded; original BIN bytes are unchanged.

v3 repairs the A1 initialization dependency; v4 repairs A4 DLC arithmetic,A0 residue and ID ordering. Both still emit154B/58i. v5 defines one genuine finish FUNC and symbolic reject edges. Earlier failures and receipts remain unchanged; [summary.json](summary.json) records raw hashes and line-ending differences.

Source: [v5](../../experiments/tsl9-packet-receive/src/packet_receive.v5.c); recipes and usage: [experiment](../../experiments/tsl9-packet-receive/README.md). Ordinary C ABI,alias/IRQ/fault,full ring/resident ABI,physical chip and OTA remain unproved. [Next ring target and feature leads](ring-next.en.md).
