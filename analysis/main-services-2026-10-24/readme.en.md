# Main services and peripheral setup reconstruction

[繁體中文](README.md)

The [source](../../src/native/startup/main_services.c) covers five whole original functions:974B/328 instructions. The same C source compiles as C11 and C++17 and matches original bytes. The main component has22840B code+714B data,1419RELA,1936 nonzero FUNC regions and71 real aliases. Region counts are not original feature counts.

| Original range | Confirmed static behavior |
| --- | --- |
| 9334–937E | A32B frame processes12 supplied bytes from seed0x5AA5,calling9290 three times per iteration. The9290 body is still missing;no live device identifier was read. |
| 12506–1264E | Slot40048 clears24/36/12B;slot40080 receives callbacks119C8/11442 and its low8-bit returns are stored. Numeric400154/400168 requests and their order are preserved. |
| 14C8A–14CC8 | Clears10B at nominal2000C794,then writes two0xFFFE halfwords and four zero bytes. This starts at the previous nominal settings extent's end. |
| 154A6–1552A | Clears6B at GP+352,calls26 original entries,restores RA/SP and tail-jumps to18604. The following neighboring function is excluded. |
| 17040–171BA | Registers callback16F00;DIVU divides the u32 at GP+108 by8,000,000,subtracts one,truncates to16 bits and writes4000082C. A fresh halfword read is shifted right once into4000083C. GPIO-like calls and the18B descriptor/enable sequence for40013000 are retained. |

The [initialization contract](initialization-contracts.json) retains exact arguments,PCs and nominal addresses;[evidence](evidence.json) retains original instructions. ROM API meanings and timer/SPI/GPIO names remain candidate interpretations. Actual clocks,pads,external peripherals and the MCU model are unproved;this does not identify a particular WCH part in TSL9.

C/C++ diagnostic ELFs are identical. All23554 selected bytes match the official BIN at their nominal addresses in93 adjacent-only spans,without unknown gap fill. Entry0 and PT_LOAD0 mean this is **not flashable firmware**. Flow checks cover7912 instructions,1257 direct transfers,7336 ordinary next positions and532 call-return positions. Runtime targets for419 register-indirect transfers,10 MRETs,and the8034→8038 EBREAK/vector-data boundary remain unproved.

Five old entries are resolved and31 genuine dependencies exposed,so unresolved providers increase from70 to96:92 direct-control providers,three callback-address-only providers,and one opaque4B default-data provider at1A69C. No empty stubs,guessed values or ABS FUNC providers are supplied. See [remaining providers](next-providers.json).

There are117 C/H files,182 source comparisons and364 objects. The previous116 C/H files,178 comparisons and1069 artifact records are unchanged. The [summary](summary.json) distinguishes accepted layout trialv3 from two stopped trials with stale verifier counts;those stopped trials are not reported as passes.

A possible feature is **read-only startup diagnostics** for callback selectors and clock/period/compare values. It is not implemented;ROM API identity,board mapping and an appropriate disclosure interface must be established first. No firmware,HOST model,ISA emulation or hardware is executed. Complete startup,ROM,memory,interrupt and OTA compatibility remain unproved.

Public sources/contracts contain no local user paths. Original build receipts remain local. Historical privacy issues remain;an incremental scan is not a claim that the entire repository/history contains no sensitive information.
