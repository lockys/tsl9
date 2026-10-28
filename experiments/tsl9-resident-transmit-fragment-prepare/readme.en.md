# Transmit-fragment preparation and pool initialization order

[繁體中文](README.md) · [Project](../../readme.en.md) · [C/C++ body](resident_transmit_fragment_prepare.c)

One whole candidate body adds **250 CODE bytes/94 instructions** atRAM0x20000AC6..0x20000BC0,conditionally sourced fromFlash40D36..40E30. C11/C++17 match original instructions and13 control relocations. The sole normal import resolves to the existing copy helper;no new DATA or fake provider.

|Original behavior|Verified result|
|---|---|
|Null queue head+280|Return1 before adding a frame;nonnull normal paths return0|
|Remaining halfword exceeds record-byte limit78|Prepare a split;first fragment clears marker0x80,advances the node buffer by2,then copies limit bytes;retain the continuation branch|
|First whole fragment|Set prepared state1 and clear the marker;this path has no copy call or explicit node-buffer/remaining advance. Do not replace it with unconditional copying|
|Whole continuation|Copy,then update buffer/remaining using fresh head/length reads;state3. Split state is2|
|Frame and flags|Copy to the pointer atrecord+272 plus2;retain low flag bits,bit0x10 and the copied TxNumEvent offset18 comparison|
|Lifetime|No explicit head/tail unlink or descriptor release;prepared is not radio-delivered or acknowledged|

The new body matches the prior enqueue'shead+280,node buffer+4,remaining+12 andmarker+9. Its first-split buffer+2 preserves enqueue'sincoming−2 relationship. All source/destination spans and fresh reads must remain valid. Incoming RAM call/pointer binding,live limit and its frame-buffer bound are not proved.

Whole existing native references cover **1,414B/454 instructions**. The initialization chain is59E70→57962,then579DC→578A4 only when the controller list is initially empty. Record head/tail are published first. Pool allocation failure skips the pool-pointer store,but the constructor does not check that return and may still read out a record ID after normal return. This is static CFG/dataflow analysis,no negative-case execution,HOST model or hardware test. External synchronization,successful allocation and initialization order remain conditions.

RAM0x20001122..0x2000138E uses a nonempty queue as a scheduling guard;it is not the fragment preparer. A further308B APP config reference shows nominal BufMaxLen251 corresponds to the existing constructor's256B frame-buffer allocation,but does not bound the live byte atrecord+78.

Identical C/C++ compositions contain **45,144 CODE+412 DATA bytes/15,710 instructions**,3,223 positive FUNCs,2,566 relocations and zero named normal UND. Parent bytes,globals and symbolic relocation roles remain. Zero UND does not establish complete callback/startup/radio execution.

Formal APP provenance stays **162 files/73,478 of76,800B（95.67% static byte coverage）**,not functional completion. SDK code is not linked into the APP or finally placed at original addresses. The inherited4B startup-source gap remains. **No new BIN or physical ROM/RAM/IRQ/Flash/OTA compatibility proof.** No target,HOST model,ISA or hardware execution and no vendor API access occurred.

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [Unimplemented fragment-progress diagnostic candidate](feature-candidates.json)

With frozen local inputs and LLVM,read-only replay:

```sh
python3 experiments/tsl9-resident-transmit-fragment-prepare/verify-v1.py --tool-dir "$LLVM_BIN"
```
