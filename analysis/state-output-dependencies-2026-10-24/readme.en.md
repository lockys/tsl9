# State writes and callback parameters

[繁體中文](README.md) · [C/C++](../../src/native/receive/state_output_dependencies.c) · [Evidence](evidence.json) · [Summary](summary.json)

Three complete original functions add80B/24 instructions, verified as C11 and C++17. B6EA/D05C/10816 now resolve genuine old imports, reducing79 to76 without adding providers. All15734B code and674B data match the official ID2966 BIN after native original-address placement:16408B total.

| Original range (exclusive end) | Confirmed static behavior |
| --- | --- |
| B6EA–B6F4 | Store low8(A0) at0x2000BF0C; return. |
| D05C–D07C | Ordered bytes at0x2000BF38..3B:1,low8(A0),low8(0-A2),low8(A1), preserving unsigned32-bit subtraction. |
| 10816–1083C | Replace zero A0 with1; A2=low32(A0*1000). Set byte0x2000BFB8 to1; A1/A3=0,A0=existing callback1061C; tail9124. |

Existing1061C–10630 clears that same state byte and tails90B0. Callback execution, timing units, field meanings, physical RAM ownership and synchronization remain unproved; no vehicle feature is inferred from these raw values.

Current collection:106 C/H files,79 native code units,160 comparisons/320 objects. All105 earlier files and937 earlier artifact records are preserved. Static flow covers919 direct transfers,263 register-indirect transfers and317 potential return positions.76 real providers remain absent. The diagnostic ELF has entry0 and no PT_LOAD; it is not flashable firmware.

Excluded trial: copying verify-flow-v11.py accidentally changed the compressed JALR discriminator, undercounting68 indirect/call-return positions. Its output remains retained and is not accepted evidence. Accepted verify-flow-v12.py / state-output-dependencies-flow-v2 preserves the original discriminator.

Potential addition: an offline state-byte/callback-parameter inspector showing raw values and unknown units. Proposal only; no hardware behavior added. Next: remaining callback providers and original ROM/RAM contracts. No firmware/host/ISA execution, hardware, network, flashing, commit or push. Publication remains held for unresolved historical privacy findings.
