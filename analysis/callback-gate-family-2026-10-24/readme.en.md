# Callback gates and original register configuration

[繁體中文](README.md) · [C/C++](../../src/native/receive/callback_gate_family.c) · [Evidence](evidence.json) · [Summary](summary.json)

Eight complete original functions add370B/121 instructions. C11/C++17 outputs match original-address code.9AF0/B5B4/D314/D3E8 and main initializer9B4E now resolve genuine old imports:76 to71, without new providers.

| Original range (exclusive end) | Confirmed static behavior |
| --- | --- |
| 9A24–9A42 | Preserve32B frame; construct halfword/word descriptor atSP+4 and call18F88. |
| 9AD2–9AE4 | Set byteGP+168 to1; write32-bit value2 at0x40010814. |
| 9AF0–9B02 | Fresh byteGP+168 read; if zero, write32-bit value2 at0x40010810. |
| 9B4E–9B8E | ClearGP+168; config byte3 bit4 through word(GP+84) conditionally submits callback9AD2 with argument5000. Call9A24 with A0=0x40010800,A1=2,A2=16; tail9AF0. |
| B5B4–B5C6 | Fresh byte0x2000BEEF greater-than1 boolean. |
| D314–D322 | Fresh halfword0x2000BF5C nonzero boolean. |
| D3E8–D3F6 | Fresh byte0x2000BF5F nonzero boolean. |
| 18F88–1904A | Complete lower/upper8-bit mask loops,word offsets0/4/16/20 and mode40/72 paths,including19038–1904A after the first RET. |

ExistingD322 reads the same halfword and returns0 or2; reused without duplication. Getters perform separate reads, without a coherent-snapshot claim. The adjacent independent function at9AE4 is excluded from9AD2. A GPIO-style structure is an inference; physical MCU/pins/peripherals,units,ROM and synchronization contracts remain unproved.

The native component has16104B code+674B data. All16778B match the officialID2966 BIN after original-address placement.107 C/H files,80 native code units,162 comparisons/324 objects; all106 earlier files and949 artifact records are retained. Static flow:938 direct transfers,270 register-indirect transfers,320 potential return positions. This is not a complete CFG or observed execution. Diagnostic ELF entry0/PT_LOAD0 is not flashable firmware.

Potential addition: offline comparison of raw config bits,GP state and callback arguments across official versions,with unknown units explicit. Proposal only. Next:8E88/9958/9F12/9E84 and original runtime contracts. No firmware/HOST/ISA execution,hardware or network. Commit/push remain held for unresolved historical privacy findings.
