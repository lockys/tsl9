# ID2580 BOOT reset → resident: offline source audit

[English](readme.en.md) | [Traditional Chinese](readme.zh-TW.md)

This audit reads the actual 12,288-byte ID2580/V1.0.00 BOOT, SHA256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`, at analysis base `0x1000`. It changes no original image or prior seal and executes no HOST model, target, MMIO, ISA/ESIL or network operation. It produces source evidence only, with no C provider, component or BIN.

The four bytes `6f10903d` at `0x1000` encode `JAL x0,0x2BD8`. Coverage is the complete **138 bytes / 37 instructions** at `[0x2BD8,0x2C62)`, plus the separate adjacent four-byte MRET at `0x2C62`. Including the vector, the source coverage is 146 bytes / 39 rows. Reset SHA256: `508c690e19a7da9fb6c880c11b696f4065aef3f7e2a7cb8097fb0ac33c91bbe3`.

[ledger.json](ledger.json) records every continuous PC, raw byte and register/immediate/control/memory/CSR operand. Sealed typed fields and the ORI extension are reused; CSR operands are decoded locally to remove the unpublished historical-helper dependency. A real static radare2 `pDj` read independently matches every raw byte and operand across 38 reset/MRET rows. ESIL text was never evaluated. Seven actual raw operand mutations are rejected without relying solely on a whole-image hash.

## Numeric effects and order

| Source | Local original effect |
| --- | --- |
| `2BD8..2BE8` | Set GP=`20004000`, SP=`20010000` |
| `2BE8..2C0C` | End-exclusive word loop copies `[3E90,3EF8)` to `[20004000,20004068)`:104 bytes/26 words |
| `2C0C..2C26` | End-exclusive word loop zeros `[20004068,200099A0)`:22,840 bytes/5,710 words |
| `2C28` | WRITE CSR `BC0`=31 |
| `2C2E` | WRITE CSR `804`=3 |
| `2C3A` | CSRRS SET MSTATUS mask `1888`; preserve other prior bits, rather than overwrite MSTATUS |
| `2C4A` | WRITE MTVEC=`103B` (`1038 OR 3`) |
| `2C4E` | JAL RA→`2C78`, link=`2C52`; clock lies outside this reset slice; see the separate source audit |
| `2C52..2C5E` | After a normal clock return to this continuation, independently form `1A52` and WRITE MEPC |
| `2C5E` | JAL x0→`40000`, without a new RA link or local return/fallthrough |
| `2C62` | Adjacent original MRET; **not** the previous JAL's fallthrough |

Only two local store instructions exist: copy store `2C00` and zero store `2C1C`. Under ordinary successful accesses and no interference, their local numeric write union is `[20004000,200099A0)`, excluding nominal slot `4004C`. This does not prove global absence of BOOT/Runtime slot writers, exclude physical aliases, or prove that clock/resident cannot write the slot.

The separate [clock audit](../boot2580-clock-2026-10-22/readme.en.md) bounds the entire callee: it writes SP/A2–A5 and restores its16B frame on ordinary return. That source projection is conditional on valid accesses and no asynchronous interference; it does not guarantee physical readiness or return. MSTATUS/MTVEC writes occur before clock. Vendor CSR semantics, interrupts/traps, MRET privilege behavior, actual RAM/stack/code mapping and coherence remain conditions.

## Slot boundary and next minimal offline gap

Original BOOT `2C5E→40000` and Runtime `18730→40000` jointly establish a nominal resident-entry dependency. Neither supplies the installed slot value. BOOT's file coordinates cover only `[1000,4000)`, Runtime's only `[8000,1AC00)`; neither file contains physical address `4004C`.

The retained public SDK candidate HEX files contain `32030020` at `4004C`, pointing to `20000332`. This is HEX data; candidate bootstrap copies the referenced code to RAM. It is not an observed BOOT slot-write/installation operation, and candidate identity is not original installed identity.

Clock's source boundary is now audited separately. The next scope is a conditional composition of this BOOT's **MEPC=1A52** with the existing candidate entry's no-own-MEPC-write/MRET contract. Do not substitute Runtime's MEPC=9008 or treat the adjacent MRET as evidence of BOOT return/startup. Existing local images/HEX suffice for that source work; no target/network operation is needed, and installed identity or hardware OTA stays unproved.

## Read-only check

```sh
python3 -B analysis/boot2580-reset-resident-2026-10-22/check.py \
  --project-root /path/to/tsl9-reversed \
  --firmware /path/to/ID-2580-V1.0.00-decoded.bin
```

Run from the project root; `--project-root` selects that source tree. It rereads BOOT, decodes every source row, checks retained independent static operands and seven raw negatives, without writing files or rerunning prior matrices. Optional `--r2-exe` recaptures the same static text using the existing tool. This source audit establishes no physical hardware validation.
