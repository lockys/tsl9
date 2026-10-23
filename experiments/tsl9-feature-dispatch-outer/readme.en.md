# Outer dispatch and mode getter

[繁體中文](README.md)

Selected src/outer.v2.c covers14D2E–14D5E,153BA–154A6 and829E–82A8:294B/101 instructions/21 architectural FUNC plus28B signed-relative metadata. C11/C++17 objects agree;41 relocations comprise25 controls,2 PC-relative and14 data bindings. Thirteen direct providers remain at this unit boundary.

Reserved S0/frame effects and five fresh S0-relative halfword reads are explicit ports after an actual compiler rejection. Free-bank memory, constants, shifts and table lookup remain C. Metadata uses real ADD32/SUB32 targets, not ABS substitutes. No ordinary C ABI or hardware/OTA compatibility is proved.

See the [complete integration and limits](../tsl9-feature-dispatch/readme.en.md). Original failures and receipts remain local; no target/HOST model/ISA/hardware/network executes.
