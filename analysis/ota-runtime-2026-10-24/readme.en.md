# Original update state and controller routines

[繁體中文](README.md) · [C/C++](../../src/native/receive/ota_runtime.c) · [Evidence](evidence.json) · [Summary](summary.json)

Ten complete original functions add1052B/363 instructions,verified as C11/C++17.92BA/9C0A/13E0E resolve three old imports; six actual response/callback dependencies change74 UND to77. Full14056 dispatch remains unimplemented; its authentication comparison values are excluded from this milestone. Original identifier checks remain intact.

| Range | Confirmed static behavior |
| --- | --- |
| 92BA–9334 | Original ROM read tuples and14-byte comparison; no physical identifier values read or retained. |
| 9C0A–9C4A | 32B frame,original CSR0x800 clear/set0x88 and controller calls. No snapshot/restore of prior CSR state. |
| 9C4A–9E5C | Complete48B frame,U/S/W/R/E branches after the firstRET,state/length/identifier guards and readback. |
| 13E0E–13E98 | Original records at0x2000C794 and0xFFFE empty value,including post-RET paths. |
| 18E90–18F56 | Five full controller functions,base0x40022000,lock/poll/word-write paths retained. |

W requires nonzeroGP+169 and1026 bytes:two-byte page index plus1024 bytes. Address=(0x20000+4+page)<<10,with uint32(destination−0x08001000)<=0x6F00. Static encoded-address arithmetic gives first page0x08001000,last page0x08007C00,end-exclusive0x08008000. Four256-byte operations precede word comparison across1024 bytes; mismatch follows original reply value255.

This window does not establish equivalence to the APP analysis VMA0x8000. BOOT/APP roles,physical aliases and the bootloader receiver remain unproved. No locally namedBOOT comparison BIN was found; image compatibility is not claimed. R requires16 bytes;E requires15 with initial byte0 and original14-byte comparison. S/U retain original low8-length arithmetic without changing guards.

E retains command69/zero-length reply shape and raw callback arguments200/400,with units unknown. An E alone proves neither failure nor success. Reboot/version/readback/physical behavior need separate evidence. No firmware,HOST or ISA execution,hardware packets,unlock/write operation or identifier capture occurred.

Code19708B+data714B:all20422B match officialID2966 at original addresses.111 C/H files,84 code units,170 comparisons/340 objects; all110 earlier sources and997 artifact records retained.1128 direct transfers:1054 measured/74 reference-only; three additional address-only providers,total77 UND. Not full CFG or physical-device proof.

Potential tool: offline image-region/update-flow inspection before transfer evaluation,proposal only. Next:reply framing and scheduled callbacks. Entry0/PT_LOAD0 diagnostic ELF remains nonflashable. Publication remains held for historical privacy findings; no commit/push.
