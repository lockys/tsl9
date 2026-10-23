# Original821E record-predicate contract

[繁體中文](next-821e-contract.md) · [15 rows / full CFG](next-821e-contract.json)

The official ID2966 V4.1.60 primary extent is`[821E,8248)`,42 B /15 instructions, SHA256 `4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd`. Fresh r2 and actual BIN bytes agree. The local CFG has15 nodes /16 edges, one RET at8246 and all rows syntactically reachable. This function has no call, frame, CSR or post-RET cold block.

The180-byte window`[821E,82D2)` is not one function. It contains821E..8248(42 B/15i),8248..828C(68 B/26i),828C..829E(18 B/5i),829E..82A8(10 B/3i),82A8..82D2(42 B/16i). The8248 call/tail/cold returns and82A8 directional resident tail do not belong to821E. The known preceding820C clear helper and82D2 filter are separate bounds.

The actual order is LW[GP+84] for a pointer, LBU[pointer+4] for config, A5=0, A4=config&8. Nonzero bit3 returns0. Otherwise A4=2 and a second A5=0 precede the full32-bit unsigned index>2 rejection. The accepted path freshly forms GP+192+index then LBU **+1**, so the state byte is**GP+193+index**. SLTIU byte,3 produces0/1; MV A0=A5 and RET finish the leaf.

Incidental residues are part of the contract: A4=8 on the config-bit path and2 otherwise; A5=A0=0/1 on every normal return. Own code writes only A0/A4/A5, with no memory store or GP/SP/RA/S-register change. This follows from actual instructions, not an ordinary C ABI assumption. Numeric GP, pointer validity and IRQ/fault effects remain unknown.

**Config pointer/byte loads precede the index guard.** Index>2 must not remove those reads, and index must not first be truncated to a byte. The state comparison is unsigned byte<3, with GP+193 rather than GP+192. Caller12A22 sets A0=0, satisfying the index gate on normal execution; a clear bit3 then selects GP+193. This leaf's own code preserves caller S0/SP, without proving other callees do so.

Readable C can supply volatile reads, bit mask, unsigned conditions and0/1 computation; fresh GP/fixed A0/A4/A5 ports retain physical registers and residues. Later native measurement must preserve both LI A5,0 instructions, read order, late GP sample and all15 typed rows, with no extra frame/call/UND. This contract did not compile or claim completed native equality.

The bounded name is a config/state eligibility predicate. Older-version names or matching algebra do not establish seat/DND/CAN semantics. Offline diagnostics must keep config/index/state known or unknown separately and never turn a failed read into disabled. No target/ISA/ESIL/hardware/network/compiler/Git execution;`firmware_ready=false`.
