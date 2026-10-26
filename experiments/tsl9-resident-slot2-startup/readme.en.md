# SDK startup, slot2 and original APP entry

[繁體中文](README.md) · [APP callbacks/IRQ order](../tsl9-original-APP-library-binding/readme.en.md) · [LLE handler](../tsl9-resident-lle-callback-gateway/readme.en.md)

Five complete candidate startup stages add **234 CODE bytes /67 instructions**,compiled as original-register-context C11/C++17. Both objects are identical. Original bytes,14 relocations,two far calls and one no-link far tail agree. These are public SDK candidate references;installed ROM identity remains unproved.

## Slot2 provenance

Loader0x6DE0C..0x6DE7E writes the following before copying:

| Store PC | RAM word | Numeric value |
| --- | --- | --- |
| 0x6DE1C | 0x20000000 | 0x200007D0 |
| 0x6DE26 | 0x20000004 | 0x2000251C |
| 0x6DE3C | 0x20000008 (slot2) | 0x20002E34 |

The slot2 store dominates both copy calls and the final zero tail in the whole loader CFG. The complete **56-byte LLE handler at0x20002E34..0x20002E6C** already has a C/C++ body. Its sourceFlash0x430A4..0x430DC lies inside the first copy. Subsequent copy/zero destination ranges exclude this body;slot2 itself is outside these destinations.

## Copies and control transfer

| Stage | Flash source /RAM destination | Bytes |
| --- | --- | --- |
| Seed | 0x40280 → [0x20000010,0x20000040) | 48 |
| First copy | 0x402B0 → [0x20000040,0x20002E74) | 11,828 |
| Second copy | 0x6EAA4 → [0x20002E70,0x20002EFC) | 140 |
| Zero | [0x20002EF8,0x20003618) | 1,824 |

The seed loop is half-open. The word-copy helper receives source inA0,destination inA1,and **inclusive last destination word address inA2**,not an ordinary memcpy length. The copies overlap at0x20002E70..0x20002E74;the second copy and zero overlap at0x20002EF8..0x20002EFC. These original bounds are preserved.

Original APP0x18724..0x18734 prepares **MEPC=0x9008**,then jumps without link at0x18730 to0x40000. Candidate startup continues at0x6DE7E,settingGP=0x20004000 andSP=0x20010000. The loader releases its16-byte frame before tailing to the zero helper;normal return can reach **MRET at0x6DEBE**,not a hosted C return. These selected SDK stages do not explicitly rewriteMEPC;absence of interrupt/CSR interference remains a condition.

The actual complete APP main is0x9008..0x901A. Call0x900C reaches0x9250,whose call0x9268 reaches0x8E88 and the previously proved initializer slot2→GP+384 store. These98 bytes/31 instructions agree with the original BIN and both retained C/C++ original-address diagnostic ELFs. No APP code is added.

## Verification and limits

[C/C++](resident_slot2_startup.c) · [Numeric ABI assertions](startup_abi.c) · [Evidence](evidence-v1.json) · [Audit receipt](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-slot2-startup/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned local BIN/SDK references and retained native artifacts. The verifier downloads nothing. Native C11/C++17 compilation passed with Windows NDK LLVM;cross-platform verification is unconfirmed.

The candidate composition contains **20,346 CODE+256 DATA /6,973 instructions**,with unique original-PC CODE ownership,all input bytes/symbols/relocations retained and two independent ELF readers agreeing. **11 genuine named dependencies remain.** This is a relocatable analysis object,not an original-address APP integration.

Second-copy source **0x6EB2C..0x6EB30 remains missing:4 bytes**. Later destination zeroing does not prove the earlier source read succeeds. Valid memory,normal callee returns,stableGP/CSR/RAM,no asynchronous interference and matching candidate ROM remain unverified on hardware. Earlier IRQ exposure is not closed.

**Startup completion,live slot2 value and binding before every possible global dispatch remain unproved.** APP stays159 C/H files and95.54% byte coverage,not functional completion. No new BIN,target/HOST-model/ISA execution,hardware access or flashing. ROM/RAM/ISA/IRQ,stack/aliasing,callbacks and Flash/OTA remain open;usable replacement firmware has not been successfully reconstructed. A read-only startup pointer/missing-source evidence display is an unimplemented future UI candidate.
