# Packet receive: rejected offline candidates

[繁體中文](README.md)

[packet_receive.c](src/packet_receive.c) is candidate v2; [packet_receive.v1.c](src/packet_receive.v1.c) preserves v1 evidence. Neither passes the original-function gate or belongs to curated `src/`. Neither is a flashable firmware implementation.

v2 fixes the real incoming-A1 overwrite ABI bug and matches the first34 original bytes. It still has154B/58 instructions versus142B/52, with remaining exit-residue/order differences. See the [analysis and anonymous receipts](../../analysis/packet-receive-native-2026-10-23/README.md). Raw build evidence remains local. No target or ISA execution occurred.
