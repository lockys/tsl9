# Next gap: receive queue and resident indirect call

[繁體中文](ring-next.md)

The confirmed bounded original ID2966 range is `[0x12BC8,0x12C24)`,92B/32instructions,SHA `d3d9af9bcec8af13dfd424d3bfb2bd79f8fc3fd61308cb6ec0d7c18b1b78b13b`. Complete global entry/xref coverage is unproved.

- A16B frame savesRA/S0/S1 atSP+12/+8/+4.
- Position-dependent AUIPC derivesRAM`0x2000C038`. It scans32slots of12B,selecting the first`LHU slot[0]==0`.
- It writes`SH A0,0(S0)` and`SB A2,2(S0)`,then freshly loads a32-bit function pointer from`0x0004004C`.
- At`0x12C0C`,bytes`8297` areRV32C`JALR A5`,linkRA=`0x12C0E`. A0=slot+3,A1=inherited payload pointer,A2=full incoming length. A misleading r2 ESIL link description is not ISA evidence.
- After the indirect call,`0x12C0E` uses **then-live**S0/S1 for`SB S1,11(S0)` before restoring the frame. Ordinary C callee preservation cannot be assumed.
- A full table leaves incomingA0; success leaves the resident callee's A0. A copy-like provider is an inference; its actual identity and preservation contract are absent from this APP evidence.

Reconstruction must preserve original-place AUIPC,A6 zero extension,fresh pointer load,physical indirect call and post-callS0/S1. Verify these ports and actual linkage before composing packet; do not substitute an assumed`memcpy`.

Unimplemented feature leads:

1. Queue-full/drop counters: the bounded original range exits after32slots without a confirmed diagnostic channel. A counter needs proved RAM ownership and safe read-only output.
2. ID0 occupancy diagnostics: packet's11-bit ID arithmetic permits0,while ring treats16-bit ID0 as empty. This suggests possible zero-ID ambiguity; inspect the consumer and actual upstream inputs before claiming real packet loss. A new occupancy field would change layout/consumer contracts and is not being added now.

All evidence is static. No target execution,ISA emulation or vehicle/hardware operation occurred.
