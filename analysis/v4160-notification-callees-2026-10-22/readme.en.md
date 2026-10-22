# Bounded candidate evidence for one notification helper

[繁體中文](README.md)

This side investigation predates the OTA handler implementation and reads two retained official ROM candidates. V1.40 `0x45228..0x4525E` and V1.31 `0x45194..0x451CA` each contain a54-byte /22-instruction wrapper with an optional RAM helper and a tail delegation. They are not measurements of installed TSL9 ROM.

The optional56-byte RAM helper is bounded and checked. Tail targets `0x44866`/`0x447D2` remain open, so full transitive ABI is not claimed. Correct LUI plus signed-ADDI builder addresses are `0x44E44`/`0x44DB0`. See [candidate-review](candidate-review/readme.en.md) for raw evidence, profile conditions, field controls and explicit local-source checks.

No additional ROM C model or vendor-ROM firmware package is created. Main implementation work moves to the [original App OTA command body](../v4160-ota-handler-2026-10-22/readme.en.md), instead of substituting whole-candidate-ROM traversal for App C/C++ reconstruction. There is no target execution/emulation, download or hardware operation.
