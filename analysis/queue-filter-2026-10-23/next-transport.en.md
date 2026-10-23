# Next region: transport framing at8A56

[繁體中文](next-transport.md) · [Original96 instruction rows](next-transport.json)

`[0x8A56,0x8B6E)` contains280B/96 instructions, SHA256 `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b`. The local CFG has96 nodes/101 edges; exits are8ACA RET,8B50 JR T1 and8B6C RET. The copy loop at8B52 remains reachable after an earlier RET. A new frame starts at8B6E.

It rejects unsigned A3>1039 before allocating a32B frame and retaining length/source/command in S registers. GP+150/154 halfwords select matching channels and exclude FFFE. Two fresh indirect admission calls through[40013C] select bank0/1 when A0==1. Resident identity and preservation remain unknown.

The common path derives bankbase`2000B18C` with stride1062. It writes magic halfword7F55 (little-endian bytes55 7F), command, high/low length bytes, payload and an8-bit additive checksum into the frame at bank+6. Metadata stores length+6 and offset0. Command and length use then-live S registers, rather than assumed pre-call values.

The copy condition is `uint16(index) < then-live S0`, while memory offsets use the full index. The1039 guard precedes admission calls and does not prove a post-call S0 bound. The tail freshly reads byte[GP+148+4*bank] into A0, sets A1=1, loads[40050] into T1 and jumps without linking RA. There are no CSR instructions. No target/ISA/MMIO execution or physical transmission was verified.
