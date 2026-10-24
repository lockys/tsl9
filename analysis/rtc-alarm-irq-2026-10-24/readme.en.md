# RTC alarm IRQ: offline C/C++ reconstruction

[繁體中文](README.md) · [Structured results](summary.json) · [Source](../../src/native/irq/rtc_alarm.c)

Five original spans totaling **78B/23 instructions** are reconstructed in C/C++ with explicit register/control assembly ports. Actual C11/C++17 objects pass:62 noncontrol bytes match directly;four relocations match after static original-VA encoding,covering all78 bytes. No instruction or register-state execution was performed.

| Original range | Size | Observed operations |
| --- | --- | --- |
| 19BD4–19BF0 | 28B/8i | Store1 to GP+392,three calls,MRET;no added frame |
| 18E86–18E90 | 10B/3i | Word store of incoming A0 to40010414 |
| 19272–19282 | 16B/5i | Repeated halfword read40002804,test0x20 |
| 19282–19296 | 20B/6i | Halfword read,complement mask,halfword write |
| 19296–1929A | 4B/1i | No-link tail jump to19282 |

Addresses,widths,vector57 and masks correspond to saved WCH RTC/EXTI headers. This is software-profile evidence,**not physical MCU or wake-feature proof**. GP+392 receives a constant1 flag;it is not an event counter,and its consumer remains unknown. Original polling has no timeout;it is retained without asserting termination.

Real vector57 now owns the genuine28B entry. The partial startup component is **1246B code+456B data/157 RELA/3 UND**. All parent1168B code and data are preserved;no fake or ABS providers were added.61 nonzero slots bind real code;the remaining external vector entry is979E. Main9008,resident40000 and dynamic callback/IRQ contracts remain open;UND counts do not capture every unknown.

Current `src/`:83 C/H files,56 code units and1 independently verified pointer-data unit.112 code-source comparisons cover224 objects;2 data comparisons cover4 more: **114 comparisons/228 objects**. Prior110 results and661 artifact records are unchanged.

[Four public receipts](publication-provenance.json) and [normal replays](../../experiments/tsl9-rtc-alarm-irq/readme.en.md) retain traceability;the complete curation receipt stays local. The frozen checker is unchanged and historical negative matrices were not executed.

The [next timer frontier](next-timer-frontier.json) selects a442B/138-instruction candidate at979E–9958 within a fixed512B window,including six direct and two indirect calls. Direct edges remain inside the window;callee returns,complete procedure extent and IRQ ABI remain unproved.

A worthwhile future feature is read-only RTC alarm/pending-state diagnostics,after tracing GP+392 consumers and proving IRQ,RAM ownership and safe readout contracts. No new hardware feature was implemented.

**This VMA0 ET_REL is a partial component,not a flashable image.** Physical hardware,ROM,final placement/RAM,full boot andBLE OTA remain unproved. No new BIN,hardware or network access. Historical personal information remains in Git;no commit/push.
