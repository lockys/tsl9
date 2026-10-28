# Third DATA provider:the lookup uses the original mode

[繁體中文](README.md) · [APP/BIN gates](../tsl9-app-bin-readiness-audit/readme.en.md) · [Checker](check-v1.py) · [Full contract](verification-v1.json)

The whole **CEDC..CF96 body,186B/56 instructions/frame0**,is checked through its original CFG,reaching definitions and actual C11/C++17 original-coordinate ELF bytes. Formal C/C++ already contains this body;this milestone adds its DATA-use contract,no reconstruction bytes.

|Location|Confirmed behavior|
|---|---|
|CF7C..CF86|`mode&7`writesA3 and record4 flags. It does not mask lookup-mode registerA4|
|CF3E..CF5A|Address is`1A078 + 16*effective_mode + ((fresh_record4+1)&15)`|
|CF66..CF7A|Branch on the old selector. Old1..254 forces effective mode0 even after storing the next modulo3 selector|
|CF8A..CF92|When countdown decrements to0,clear enable and continue the current lookup;do not invent an immediate return|

Logical RAMbytes2000BF38/39/3A/3B are called enable/mode/selector/countdown here as analysis labels,not proved product-setting names. Physical RAM mapping,alias and IRQ/DMA/reentrant coherence remain unproved.

With byte-width bounds only,A4 before the shift comes from an unmasked mode load or forced0;column is0..15. The conservative envelope is **1A078..1B078,4,096B**,including **1,144B beyond the supplied APP** and currently excluded default DATA. Do not read the entire envelope to supply a table or infer eight rows from the record-flag`&7`.

This static envelope **does not prove original declaration size,feasible values or an actual out-of-bounds defect**. Original mode0 and conditional mode5 each have16B of existing positive DATA backing. No new DATA or full-provider alias is added. Closing provider1A078 still needs an actual mode-at-read/use contract or independent legitimate requirements;no global invariant is assumed.

No lookup-envelope DATA,payload/individual hashes or excluded-default content was read/output. Formal src/native artifacts remain unchanged:**162 sources,95.67% static byte coverage,six APP source UND**. BIN readiness remains incomplete;no new BIN or physical compatibility proof.

Read-only replay from the project root:

```sh
python3 experiments/tsl9-third-provider-lookup-contract/check-v1.py
```

Exit0 means only this static contract matches frozen actual evidence. Use the [readiness checker](../tsl9-app-bin-readiness-audit/readme.en.md)for artifact readiness. No target,HOST-model,ISA or hardware execution and no vendor API access. The [read-only diagnostic candidate](feature-candidates.json)is unimplemented.
