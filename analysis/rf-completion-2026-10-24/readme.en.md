# RF completion, retry and relative block layout

[繁體中文](README.md)

The new [C/C++ source](../../src/native/receive/rf_completion.c) covers173EE–17476: **136B,45 instructions,seven architectural regions**. Actual C11/C++17 objects preserve126 non-control bytes andthree typed references;data-only original-VA encoding matches all136B. [Receipt](evidence/standalone-trial.json)

Original ordering is retained:stop event2 through4005C,clear state bytes,load the saved callback,andconditionally restore S0/RA,clear its word,pop SP andtail through captured T1 withthen-live S0. The null callback uses its own restore/return. Frameless17442 decrements/masks/stores a byte before choosing completion orrescheduling event1/timeargument2 through40058. There is no pre-decrement zero guard;wrap is retained without claiming bounded hardware retries. [SDK profile](rom-profile-correspondence.json) is not installed ROM/ABI proof.

The main component binds the actual26B/24B entries within all136B: **4166B code+456B data,347 nonzero FUNC regions,15 genuine aliases,281 RELA and17 direct UND**. All4030B parent code,456B data and62 vector bindings are retained. [Evidence](evidence/native-c.json) / [Provider ledger](pending-providers.json)

Selected sources contain93 C/H files:132 code comparisons/264 objects pluspointer-data2/4,total **134/268**. These are source/original-byte checks,not whole behavior orhardware execution.

## Six-unit RF relative layout

Six existing actual curated objects were composed in original block order: **1550B/538 instructions,103 real regions,five aliases and56 RELA**,corresponding to173EE–179FC. Every region iscontiguous;53 internal reference sites andsix internal AUIPC/ADDI function-address expressions map toactual native symbol offsets. Data-only original-VA encoding matches thewhole original range. [Evidence](evidence/rf-relative-c.json) / [Build receipt](evidence/rf-relative-build.json)

The isolated RF object still has three external providers:90B0,9124,C776. The first two already exist inthe main component andwere not duplicated here. Table1AAE8 isnot included.

**Absolute original placement isnot proved.** The initial requested173EE VMA wasnot retained byLLD-r:actual ET_REL remained VMA0. That requirement failed;its local output remains unclaimed. No ELF header patch orfake provider was used. The accepted check proves only relative offsets/internal address correspondence. RAM AUIPC,external placement,the final image,installed ROM/IRQ,hardware andBLE OTA remain open.

[Next bounded C776 candidate](next-c776-candidate.json) contains114B/42 instructions andfour external targets,not aproved complete ABI. Passive retry/completion diagnostics remain a future candidate requiring memory/concurrency/callee evidence,not firmware functionality.

No target/HOST-model/ISA/ESIL execution,hardware/network access,newBIN,commit orpush. [Main build receipt](evidence/integration-build.json) / [Publication provenance](publication-provenance.json)
