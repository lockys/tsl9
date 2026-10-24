# Initialization tail,shared returns andscheduler integration

[繁體中文](README.md) · [Structured results](summary.json) · [New C/C++](../../src/native/startup/init_tail.c) · [Existing scheduler](../../src/native/receive/scheduler.c)

Original **17B92–17BC4 and17BF6–17C4E,total138B/47 instructions**,are reconstructed in10 architectural regions. Actual C11/C++17 preserve120 noncontrol bytes;five typed edges match after static original-VA encoding,covering all138 bytes. Constructor S0/RA/SP restore precedes the shared tail. GP+378 fresh reads,conditional frame,two returns andthree resident indirect calls remain.

The whole existing **9124–9250 scheduler,300B/115i/28 regions**,is integrated. Every original-VA encoded byte matches,with11 real control references andno direct UND. Only the old checker's positive object audit is called;historical negative matrices were not executed. Four resident transfers andcallee contracts remain unproved.

The actual partial component contains **2350B code+456B data/217 RELA/18 UND**. All parent1912B code anddata are preserved.17BF6 owns a realconstructor entry and9124 the complete original scheduler. All62 selected nonzero vector slots still bind realcode. These are component metrics,not whole-firmware completion. [18 direct dependencies](pending-providers.json) exclude additional dynamic/ABI unknowns.

[ROM-header correspondence](rom-header-correspondence.json) records saved WCH default table/type evidence:

| Word/slot | SDK interface profile | Original evidence |
| --- | --- | --- |
| 40048 | tmos_memset | Two calls withA1=0,A2=3/115 |
| 40080 | TMOS_ProcessEventRegister | Callback argument;returned lowbyte storedGP+379 |
| 20000000 | TMOS_SystemProcess | 8180 RAM callback |
| 4007C | TMOS_GetSystemClock | Retained clock wrapper;header documents0.625ms units |
| 20000008 | LLE_IRQLibHandler | Retained RAM+8→GP+384 initializer candidate |

These are **slot/interface-profile correspondences**,not recovered function entries orproven installed-ROM bytes/version. Original register ports andcall order remain;no guessed standard-library call replaces them.

Current `src/`:86 C/H files,59 code units and1 independent data unit.118 code-source comparisons cover236 objects;2 data comparisons cover4 more: **120 comparisons/240 objects**. Prior116 results and697 artifact records are unchanged.

The [next callback family](next-callback-family.json) contains a266B/102-instruction candidate at901A–9124,including pending90B0.901A/9070 share cross-range paths;their first RETs do not establish independent function boundaries.

Read-only BLE/TMOS task/deferred-work diagnostics are worthwhile candidates after tracing callbacks/flag consumers andproving ROM,RAM,IRQ/readout contracts. No new hardware feature was implemented.

[Five public receipts](publication-provenance.json) and [normal replay instructions](../../experiments/tsl9-init-tail/readme.en.md) preserve traceability. Complete curation stays local andthe frozen checker is unchanged.

**The VMA0 ET_REL remains unflashable on original hardware.** Physical MCU/ROM,original placement/RAM,full boot andBLE OTA remain unproved. No new BIN,hardware/network,commit orpush. Historical personal information remains unresolved in Git.
