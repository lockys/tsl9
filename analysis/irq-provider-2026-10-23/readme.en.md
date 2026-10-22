# IRQ provider and nine-span receive graph

[繁體中文](README.md)

[src/native/receive/irq_provider.c](../../src/native/receive/irq_provider.c) reconstructs official ID2966 `[0x18D78,0x18E1C)` in C/C++. Six private regions cover164B/53instructions and match the entire original code span at nominal addresses. This is neither recovered original source nor ordinary C ABI. **Whole-device reverse engineering remains incomplete; no new flashable BIN was produced.**

| Evidence | Measured result | Boundary |
| --- | --- | --- |
| Provider component | 164B/53i,6genuine FUNC regions,3native RVC edges; nominal0UND/RELA | Physical MMIO identity/timing unknown |
| Nine nominal spans | 802B/280i,35genuine FUNC regions,32resolved symbolic controls;0UND/RELA | Ring's dynamic resident call remainsUNKNOWN |
| Formal C/C++ checks | Each language:125provider negatives,119raw-ELF graph negatives; complete replay passed | Strict readiness rejects; no hardware proof |
| Source curation | 53C/header files,27native units,54comparisons/108objects | Not a full firmware link; legacy HOST matrix not rerun |

All16static LW32,12SB8 and4SW32 instruction sites/order are checked across the provider's complete set of branches, rather than claimed as dynamic counts per call. Fresh reads, final A5 overwrite, A4 residue, two RETs and local preservation of A0/A1/A2/other GPRs are retained. v1 also measured164B but used A1 in two return blocks; v2 adds A5 value ports. Failed source/raw local measurements remain unchanged.

The nine spans are ring92, IRQ52, SPI72, register-read72, register-write76, packet142, receiver70, flag-consumer62 and provider164 bytes. All802original-address bytes match the official BIN; concatenated SHA256 is`1946d38e90500f279c650b7f80df32004f05507a2bafeaeceb372ab4b53ee169`. No original raw bytes or ABS symbols were substituted as fake providers.

**The RX LOAD spans25,172B, including five unvalidated gaps totaling24,370B.** This ELF is a linkage-evidence container, not a complete APP/BOOT or flat firmware image. `LW[0x0004004C] → JALR A5` remains dynamically unknown; no UND does not close every call ABI. The graph fully replays the old586B, IRQ52 and provider164 proofs, joining156input pins and11complete inventories (114inherited files), with56producer recipes.

Replay requires retained local build artifacts; public JSON alone does not contain compiled outputs:

```sh
python3 -B experiments/tsl9-irq-provider/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-irq-provider/build/verified-v3/c/verification.json
python3 -B experiments/tsl9-irq-provider/verify_receive_graph.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-irq-provider/build/receive-graph-verified-v3/c/verification.json
python3 -B scripts/verify-curated-source.py --replay build/curated-source/irq-provider-20261023-v1/verification.json
```

Windows may use`python`. Only the existing local Windows NDK LLVM18 producer was tested; other OS/toolchains remain unverified. No downloads or flag search occur. Both C/C++ replays exit0; strict readiness exits1. Current formal directories are bothv3; intermediate privacy/serialization versions remain local historical evidence, not current replay targets.

[summary.json](summary.json) records source/checker/receipt hashes and control classifications. Provider125negatives are97raw ELF,7parsed typed,16structural SSA,2full-IR pin and3MD controls, rather than125raw-ELF tests. Graph119negatives all reparse modified raw ELF with the whole-file hash gate disabled.

Four`receipts/provider-{c,cpp}.json`/`graph-{c,cpp}.json` files are byte-identical public copies of original LF receipts already using variable paths. [curated-source.json](receipts/curated-source.json) is an anonymized path derivative. The raw original remains local, SHA256`7cd1cf744430b0b98ad2862e59526515eac8f4f3bd9cb626bf2c32e595b1984f`. Only path strings/keys changed; inverse JSON equality was checked. Direct original-receipt replay is not claimed for the derivative. Original BIN/APK bytes, old receipts and Git history were not rewritten.

The curation receipt includes108inputs,325artifacts and108recipes/MD files. All52prior results and313artifact hashes remain unchanged. Next is the [314B queue consumer/dispatch](next-consumer.en.md). Length/field validity and ID0 occupancy remain diagnostic research leads, not proved hardware faults; no filter, clamp or layout changes were introduced.

No target/ISA/MMIO, hardware or third-party API execution occurred. Complete startup/resident/IRQ/fault/memory ownership/silicon/OTA compatibility remain unproved.
