# Notification dispatcher and five jump tables

[繁體中文](README.md) · [Source](../../src/native/receive/selector_notifications.c) · [Contracts](provider-contracts.json) · [Summary](summary.json)

Reconstruct original E220..EBAC:2,444B/789 instructions,with five readonly relative-offset tables of756B/189 entries. C11 and C++17 objects match original code/data; guards and every table target are checked against actual mapped instructions. Original calls,branches and explicit private-register assembly ports remain. This is not complete original-source recovery.

Whole-source220 comparisons/440 objects pass;48,858 original-coordinate bytes match. E220 is supplied and16 downstream helpers exposed;137 providers remain. FE08 has both direct-call and callback-address references.

Confirmed:static bytes,data roles and transfer positions. Inferred:notification codes drive nested selector dispatch. Unknown:human button/seat meanings,private ABI,physical RAM/IRQ and OTA compatibility. No target,hardware or new BIN execution/generation. Diagnostic ELFs are not flashable firmware.
