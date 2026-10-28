# APP/BIN readiness from actual artifacts

[繁體中文](README.md) · [Project](../../readme.en.md) · [Checker](check-v1.py) · [Actual report](report-v1.json)

**Not ready:the retained diagnostic ELF is not a flashable BIN.** This audit replays the formal162-source original-coordinate evidence and inspects actual C/C++ objects,ELFs and frozen receipts. It adds no firmware bytes and executes no target.

|Gate|Current actual evidence|
|---|---|
|Formal APP sources|73,478 of76,800B;95.67% static byte coverage,not functional completion|
|APP gaps|3,322B:3,128 currently excluded plus194 other unselected bytes in34 spans. No missing payload/individual hash output or padding|
|Six source providers|Still UND in the actual object. The legacy`compiler_UND` field does not mean six standard compiler runtime helpers|
|Artifact format|Actual ET_EXEC,entry0,PT_NULL and zero PT_LOAD. Six hidden NOTYPE ABS values are reference coordinates,not provider implementations|
|Resident ROM/ABI|The candidate SDK is not linked into APP and retains18 ordinary UND. CODE atcoordinate40000 is not installed-device ROM identity|
|Startup/IRQ/RAM|Physical profile/trap binding,RAM capacity,stack/heap/APP-global ownership remain unproved|
|Flash/OTA/functions|No artifact-matched physical boot/required-feature proof for a rebuilt image. Transfer/readback completion is a separate result|

Actual APP reference obligations:

|Reference|Classification/remaining obligation|
|---|---|
|40000|Resident ROM/ABI dependency;do not assume the entire ROM must be rebuilt into APP merely to remove UND|
|14056|Currently excluded APP CODE entry|
|1AB48|DATA provider with8B positive backing at the reference;full use contract remains undefined|
|1A078|DATA provider referring inside an existing432B pool;the import remains undefined|
|1A638|DATA provider with48B conditional backing;full provider/global invariant remains unproved|
|1A69C|Currently excluded4B default DATA;no content or individual hash output|

**Two different four-byte issues must stay separate.** Archived SDK startup sourcegap`[6EB2C,6EB30)`is outside APPdomain`[8000,1AC00)`. It is not four additional missing APP bytes,nor physical ROM-read failure proof. Identify original entry,ROM ABI and coordinate domains before adding SDK reconstruction counts to any APP claim.

Resolve actual APP provider/scope obligations,classify necessary unselected spans,establish device ROM/RAM/IRQ/Flash/OTA evidence,and only then produce a loadable artifact. **No fake functions,ABS-as-implementation,gap padding or relabeling a diagnostic ELF.**

With frozen local inputs and LLVM,read-only replay from the project root:

```sh
python3 experiments/tsl9-app-bin-readiness-audit/check-v1.py --tool-dir "$LLVM_BIN"
```

This version inspects the frozen current artifacts:**exit2 means evidence inspected but not ready;exit1 means changed inputs or audit error**. The report contains both`evidence_audit_passed=true`and`firmware_ready=false`;the first alone is not readiness. No ignore-gaps option is supplied. Changed inputs require new verifiable evidence. Windows can use`py -3`and`$env:LLVM_BIN`.

No formal src/native artifact,MCP/Skill or Git-setting changes,target/HOST-model/ISA/hardware execution or vendor API access. The [feature candidate](feature-candidates.json)is separate transport/artifact/boot/function evidence in the updater;App integration is unimplemented.
