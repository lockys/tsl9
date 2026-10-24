# Main,application loop andinitialization: offline reconstruction

[繁體中文](README.md) · [Structured results](summary.json) · [C/C++ source](../../src/native/startup/main_family.c)

Three original ranges are reconstructed andchecked with actual C11/C++17 outputs:

| Range | Size | Observed structure |
| --- | --- | --- |
| 9008–901A | 18B/8i | 16B frame,RA save,calls9250/8180,restore andreturn |
| 8180–81AA | 42B/15i | Loop,then-liveS2+0 callback,17002/12C58,watchdog write |
| 9250–9290 | 64B/19i | 14 ordered calls,RA/SP restore,no-link tail17BF6 |

Total **124B/42 instructions in23 architectural regions**.52 noncontrol bytes match directly;20 typed edges match after static original-VA encoding,covering all124B. Explicit frame/S-register/RA ports remain. These are not ordinary independently callable C functions;entry/callee ABI is unproved.

The existing whole9F4C **40B/15i** C/C++ leaf is linked with allfive ordered word writes. [Watchdog/callback boundaries](watchdog-boundaries.json) correspond to a saved WCH IWDG header;exact timeout,physical MCU andruntime servicing remain unknown. Application setup writesS2=20000000,S1=40003000,S0=AAAA,then uses live registers. Unknown providers/IRQs are not assumed to preserve them.

The actual partial component is **1912B code+456B data/201 RELA**,preserving all parent1748B code anddata. main9008 owns genuine18B code;all62 selected nonzero vectors remain bound. Unfolding the real caller exposes [17 concrete dependencies](pending-providers.json),including initialization/receive providers andresident40000. Dynamic callbacks are additional unknowns;the application is not closed.

Current `src/`:85 C/H files,58 code units and1 independent data unit.116 code-source comparisons cover232 objects;2 data comparisons cover4 more: **118 comparisons/236 objects**. Prior114 results and685 artifact records are unchanged.

The [next tail frontier](next-tail-frontier.json) shows17BF6 using resident pointer word40048,calls90B0/1798A,andbackedge17B92. Its96B window is not a complete function;the first linear return cannot establish the boundary. Recognizable initializer addresses are candidates,not proven runtime callbacks.

Read-only main-loop/watchdog/reset-cause diagnostics are worthwhile future features,after proving RAM,IRQ,clock andsafe readout contracts. No hardware feature orwatchdog behavior change was implemented.

[Five public receipts](publication-provenance.json) and [replay instructions](../../experiments/tsl9-main-family/readme.en.md) retain traceability. Complete curation stays local,the frozen checker is unchanged,andhistorical negative matrices were not executed.

**This VMA0 ET_REL remains a partial component,not flashable on original hardware.** Physical MCU/ROM,memory/original placement,full boot andBLE OTA are unproved. No new BIN,hardware/network access,commit orpush. Historical personal information remains unresolved in Git.
