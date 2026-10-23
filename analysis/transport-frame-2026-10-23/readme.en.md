# Transport reconstruction evidence

[繁體中文](README.md) · [C implementation and checks](../../experiments/tsl9-transport-frame/readme.en.md) · [Original instruction contract](original-contract.en.md) · [Independent native review](final-native-review.json)

The `8A56..8B6E` span is reconstructed as 280B/96 instructions, retaining the post-RET copy loop, two admissions and final non-linking tail. C/C++ formal checks, independent raw-bit review, read-only replay and strict rejection passed. These are offline results, not proof of original-device compatibility.

The genuine C object is now [partially linked with the existing dispatch component](../../experiments/tsl9-transport-dispatch-component/readme.en.md): 806B,280 instructions and32 FUNCs. The filter's `C.JAL 8A56` binds a real definition; five strong UND symbols and41 pending RELAs remain. This is symbol-level binding. Machine control immediates, original placement and full firmware composition are still unresolved.

Correction: the previous `analysis/queue-filter-2026-10-23/next-transport.md`, its English version and `summary.json` described the admission cell as `0x40013C`. Both original `LUI 0x40; LW +316` pairs actually address **`0x4013C`**. Frozen old evidence is retained unchanged. Current raw-operand derivation, v6 source, formal mutations and correction history use the correct address. Historical v1/v2 candidates contained the same error and were never promoted as current source.

| Evidence | Confirmed | Open boundary |
| --- | --- | --- |
| Guard/admission | Initial unsigned1039 guard; fresh `[4013C]`; RA returns8A90/8AB6 | Post-call S0 bound, provider identity and full ABI |
| Header/copy | Nominal table2000B18C, stride1062,7F55, command/length/additive byte checksum; full32 index | Original table placement, RAM ownership and termination after arbitrary opaque effects |
| Finish | Restore RA/S1..S3 before metadata; S0 restored late; SP+32 before `JR T1` | Fresh `[40050]` effects, physical interface and observed transmission |

Potential additions, not implemented: offline frame length/checksum diagnostics; separate admission, framing, tail-call and physical-transmission records; version-specific GP/table layout labels. This span does not establish seat or DND attribution.

Original receipts remain local. Public path-only derivatives explicitly record original SHA256 and inverse JSON equality, and are not represented as byte-exact replays of the originals.

Eight authored analysis documents also had a duplicate terminal LF removed and one document-reference SHA updated. [Publication provenance](publication-provenance.json) records byte-reversible checks and the local originals backup; machine code and formal-verifier inputs were unchanged.

The next direct provider is `12A08`. Its [initial182B window](next-provider.json) contains three entries; [independent extent analysis](next-provider-contract.en.md) selects only the102B/35-instruction `12A08..12A6E` span, including its post-RET cold path, for the next C reconstruction. It checks status/ID/tag and dispatches to further providers. Physical interface identity remains unproved.
