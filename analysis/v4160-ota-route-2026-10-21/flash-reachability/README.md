# ID2966 V4.1.60 OTA to flash: original static route

The original conditional route is record19DFC+4→888C frame receiver→8A48 call14056→14094 call9C4A. The resident consumption of that record and GATT ABI remain unproved. These instructions are absent from the current614 native allocations; they are original-source evidence, not an executed device path.

9C4A has a gap-free530B/169-instruction local CFG. W requires active byte GP+169 and payload1026B. Its big-endian u16 page is accepted only0..27, destination08001000+page*1024. Four calls at9D00 reuse9C0A, which unlocks, clears status49, erases and programs256B, then locks. The handler compares256 u32 words; success calls9B8E with page/readback1026B, mismatch returnsFF. Opaque allocator/copy/TX/free calls, memory aliases, controller completion and actual ACK transmission remain unknown. This Runtime path must not be substituted for the separately reviewed BOOT echo protocol or treated as a75-page Runtime flasher.

All known confirmed original direct callers:18E90:{9C26};18E98:{9C1E,197C8};18EB6:{9C38,197DC};18EC4:{9C2C,197CE};18EF2:{9C34,197D8}. 197BE has no confirmed direct caller and is an opaque-record conditional hook; its flash chain omits18E90. Its zero return does not prove hardware success. 9C0A callers are9D00,9E7A,12E7A,12F0C,12F6E,13078,130FC,1315E. The checker distinguishes actual instruction boundaries from arbitrary2-byte aligned candidates, including false upper-half decodes.

New E requires active, exact length15, mode0 and92F2 return0 identity match. R requires exact16 and14 identity bytes atpayload+2. The saved older Runtime active-only E is compared using its own original bytes/hash, without transferring its addresses or ABI into this image. No UID value is read or printed.

Recompute offline: `python inspect-flash-route.py --check`. It checks source/receipt/object pins, all7238 actual RELA against raw controls, source-bit guards, all65536 u16 page values, raw CFG/r2 agreement and the frozen independent protocol proof. Numeric formulas and static call chains are not physical validation. No network, target execution/emulation, hardware, ROOT/D writes or BIN production occurred.
