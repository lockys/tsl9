# Record decoder and status setter linkage

[繁體中文](README.md)

Added [record_decode.c](../../src/native/receive/record_decode.c): originalC6A8–C776 is206B/75 instructions, plusFAF8–FAFE at6B/2 instructions. Both C11 andC++17 reproduce all212 original bytes after static original-VA encoding:184 noncontrol bytes and10 typed references.

The main component contains **4636B code+456B data**,388 nonzero FUNC regions,21 genuine entry aliases,309RELA and20UND. C/C++ component hashes match. Allprevious4424B code and456B data remain unchanged, alongwith62 selected nonzero vector bindings. Genuine code resolves C6A8 andFAF8;12A08 reuses the whole dispatcher already present in the parent.

| Static observation | Evidence and limits |
| --- | --- |
| C6A8 record handling | bit9 gate,conditional three-byte writes,raw numeric branches,preserved targetbyte7 highbit andbyte8 upper6bits;possible no-link12A08 tail |
| FAF8 status write | Frameless A0 low-byte write toGP+284 followed byreturn;physical status semantics unproved |
| Memory | Fullword atGP+224 readsonebyteoutsidepreceding7Bcopy;targetwritesreachoffset8. Originalwidthretained,notaproofofboundsorownership |
| Next providers | Existing actual C/C++ objects foundfor81AA,821E,16B7C,18CA4;fulloriginal-rangereuse auditsremainpending |

The [field map](static-field-map.json) separates instruction facts from a stable-source snapshot inference. Rebuilt code retains fresh reads; do not collapse them into one snapshot. Seat,DND,temperature andphysical units remain unknown. A possible newfeature is an **offline raw-record preview**,not implemented.

Use the replay commands in the [experiment](../../experiments/tsl9-record-decode/readme.en.md). [Summary](summary.json), [pending providers](pending-providers.json), [next objects](next-providers.json), [publication provenance](publication-provenance.json).

**This unresolved VMA-zero ET_REL is not a flashable BIN.** Physical MCU,installed ROM/ABI,original placement,memory/IRQ andBLE OTA compatibility remain unproved. No target,HOST-model orISA execution,hardware access,commit orpush occurred. Historical privacy findings remain.
