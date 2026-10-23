# Next region: packaging/forwarding filter

[繁體中文](next-filter.md) · [Original instruction evidence](next-filter.json)

`[0x82D2,0x838E)` is the complete local range called at consumer12CB0:188B/69 instructions, SHA256 `7a49eb89a2c698b0a9d4a97083329c2a12e200c1f27fbdadec16784a6edb0e30`. RET at8388 does not exclude the reachable cold block838A..838E.

The64B frame saves S0..S9/RA. The initial PC-derived table is`2000C794`, initial index0, then cold path selects1, stride4. It checks `LHU[entry+2] != FFFE`, `LBU[entry+5] == 2` and `LBU[entry+4] != 0`. S4 is set at832C before the length>8 rejection at832E; a nonzero return does not imply successful forwarding.

The8356 C.JALR targets A5 with RA8358. At8368, **2-byte C.JAL** targets8A56 with RA836A; the next decoder/relocation checker must distinguish this from non-linking C.J. Opaque resident/8A56 effects on S registers, SP and aliases remain unknown. Later fresh reads must not reuse earlier C values. The188B body has not yet been reconstructed in C.

Only the first256B of direct target14D2E were inspected. Its seven-entry jump table and cases leave those bounds. The complete boundary is unknown; RET14DA8 is insufficient. Current V4.1.60 evidence does not establish seat or DND attribution.
