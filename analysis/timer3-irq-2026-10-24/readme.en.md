# TIM3 IRQ: offline C/C++ reconstruction

[繁體中文](README.md) · [Structured results](summary.json) · [Source](../../src/native/irq/timer3_irq.c)

Original **979E–9958,442B/138 instructions**,is reconstructed as32 architectural regions with explicit adjacency. Actual C11/C++17 objects preserve376 noncontrol bytes;24 typed control edges match after static original-VA encoding,covering all442 bytes. No target or ISA execution.

C unsigned operations and volatile accesses retain explicit register/control ports. Original16B frame,S0/S1/S2 saves/restores,AUIPC,signedDIV,MRET andcompressedJALR remain. Live-register boundaries prevent C operations moving across physical S-register ports. These are not ordinary independently callable C functions.

Four whole existing C/C++ helper regions totaling60B are selected:the three81B0 clock-wrapper regions and93EE disarm leaf. Every original byte matches;no fake provider or replacement implementation is added.

Real vector45 is bound. The partial startup component contains **1748B code+456B data/181 RELA/2 UND**,preserving all parent1246B code and data. All62 nonzero slots in the selected carrier bind real code;physical IRQ count/context and whole firmware are unproved. Direct gaps are main9008 andresident40000;dynamic calls are outside that count.

Current `src/`:84 C/H files,57 code units and1 independent data unit.114 code-source comparisons cover228 objects;2 data comparisons cover4 more: **116 comparisons/232 objects**. Prior112 results and673 artifact records are unchanged.

[Pointer/SDK boundaries](pointer-boundaries.json) distinguish literal word40068,then-liveS2+12,andclock word4007C. S2 originally computes2000BEBC,but unknown providers are not assumed to preserve it. Saved WCH headers correspond to TIM3 autoreload/channel3 compare;this is software-profile inference,not physical MCU,pin orload attribution.

Stride6 with three halfwords,phase/index paths andperiod/compare values suggests a timed waveform/sequence. Offline timing preview,and later optional notification patterns,are worthwhile candidates. Buzzer/light/load identity,time units andlive table contents remain unknown;no hardware feature was implemented.

The [next main candidate](next-main-candidate.json) selects only **9008–901A,18B/8 instructions**:16B frame,RA save,calls9250/8180,andreturn. The larger [284B decode window](next-main-frontier.json) contains several function returns andmust not be treated as one main function.

[Five public receipts](publication-provenance.json) and [local replay instructions](../../experiments/tsl9-timer3-irq/readme.en.md) preserve traceability. Complete curation remains local,the frozen checker is unchanged,andhistorical negative matrices were not executed.

**This VMA0 ET_REL is not flashable on original hardware.** Physical MCU/ROM,dynamic providers,IRQ ABI,original placement/RAM,main/full boot andBLE OTA remain unproved. No new BIN,hardware/network access,commit orpush. Historical personal information remains unresolved in Git.
