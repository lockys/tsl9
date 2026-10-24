# Record queue, callback constructor and encoder

[繁體中文](README.md)

The new [C/C++ source](../../src/native/receive/record_queue.c) covers original `1787C–1798A`: **270B, 94 instructions and 14 architectural regions**. Actual C11/C++17 objects preserve 246 non-control bytes and seven typed references; data-only original-VA encoding matches all 270B. [Accepted receipt](evidence/standalone-trial.json)

## Static observations

- The queue retains its 16B frame and two fresh count loads whose original AUIPC expressions encode `2000C8AE`. A second count greater than15 skips copying.
- Original1789A encodes base `2000C8AC`. Copy arguments use then-live S0: destination `S0+3+7*byte[S0+1]`, original A0 source, length7, through slot4004C.
- After the opaque call, fresh then-live S0+1/S0+2 loads update index/count. The index increment is masked15. Then-live S1 selects normal return or a restored-frame no-link tail to17666 with A0=255.
- 178F8 retains a32B frame, zero/7 arguments through slot40048, original word/halfword/byte masking and store ordering, then calls1787C.
- Frameless17948 updates record bits10..15 using A0&63 and sets byte6 bit7. A1 selects return, enqueue, or halfword+4 OR1F00 before enqueue.

A16-slot/seven-byte ring-like queue is inferred. **The pre-copy index has no local mask.** A later mask15 cannot establish earlier bounds. Initialization, memory ownership, and callee effects on S0/S1 remain unproved; no initialization or bounds fixes were invented.

## Integration and limits

The1787C reference now binds its real30B entry within all270B. It exposes17666, leaving17 direct UND. The actual component contains **3000B code+456B data,270 nonzero FUNC regions,11 entry aliases and238 RELA**. All2730B parent code,456B data and62 nonzero vector bindings are retained. [Native evidence](evidence/native-c.json) / [Provider ledger](pending-providers.json)

Trial-v2 is accepted. Trial-v1 failed because the assembler shortened an original4B ADDI to2B; its local outputs remain unclaimed. Explicit full-width asm ports now retain original instruction width.

Default SDK slots correspond to memcpy/memset, not confirmed installed implementations. [Profile](rom-profile-correspondence.json) The VMA-zero ET_REL component does not establish original placement. Original literal callback addresses, including178F8, remain placement-dependent and are not proved runtime bindings.

Selected sources contain89 C/H files:124 code-source comparisons/248 objects plus2 independent pointer-data comparisons/4 objects, totaling **126/252**. These checks do not prove whole behavior, installed ROM, memory, startup/IRQ, physical hardware or BLE OTA compatibility.

## Next family and feature candidate

[Retained bounded decode](next-17666-frontier.json) spans17666–1787C:534B/187 instructions with candidate entries17666/176A0/176F8. It references existing90B0/9124 and pending1753A/C776; reuse actual definitions without duplicate linkage.

A future read-only offline record/queue inspector could show raw index, count, masks and uncertain-bound annotations. It remains a research candidate, not firmware functionality.

No target/HOST-model/ISA/ESIL execution, hardware/network access, new BIN, commit or push. [Build receipt](evidence/integration-build.json) / [Publication provenance](publication-provenance.json)
