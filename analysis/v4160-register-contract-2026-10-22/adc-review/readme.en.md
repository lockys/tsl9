# Bounded original-firmware dependency contract at 0x188E2

[繁體中文](README.md) · [English](readme.en.md)

This is static source analysis of original ID2966 V4.1.60. No instruction execution, processor emulation, compiler, linker, BIN generation, network, or hardware access is used. `ledger.json` records original bytes and all decoded operand fields. `check.py` reuses the sealed earlier callback and decoder; no new encoder or old-scope changes are introduced.

The actual callback establishes S1=`0x40012400` at `0x19824/0x19828`, moves it into A0 at `0x19878`, and calls `0x188E2` at `0x1987A`. The previous restricted 0x8520 path and the two earlier 0x19124/0x1908C proofs remain unchanged.

The complete source-derived range `0x188E2..0x1892E` exclusive contains 76 bytes / 25 rows. It subtracts 16 from SP and saves RA at new SP+12. If entry A0=`0x40012400`, it constructs A0=mask `0x200`, A1=1, calls the sole small dependency `0x19160` at `0x188F8`, then reconstructs A0=`0x200`, A1=0, restores RA/SP and tail-jumps to the same dependency at `0x18906`. The second fully covered branch accepts `0x40012800` and mask `0x400`, with the linked call at `0x1891C`. Other inputs restore RA/SP and return at `0x1892C`. There is no encoded loop.

The only dependency, `0x19160..0x1917E`, contains 30 bytes / 12 rows. When A1 is nonzero it freshly reads 32 bits at `0x4002100C` (`0x19166`), ORs A0, and writes 32 bits (`0x1916A`). When A1=0 it freshly reads the same address (`0x19172`), ANDs ~A0, and writes 32 bits (`0x1917A`). These are two separate read/modify/write operations; they do not prove restoration of the first complete register value, since other bits can change between reads. This leaf has no nested calls, frame, or RA writes. Neither function writes S0–S11, GP, or TP.

Under valid nonaliasing 16-byte stack storage, normal memory/MMIO access completion, intact code, and no asynchronous register/stack changes, this bounded chain restores entry SP/RA and preserves S/GP/TP. Accepted-input branches return the second fresh read AND ~mask in A0 and A1=0; A4/A5 are scratch. The unmatched branch leaves A0/A1 unchanged. A2/A3/A6/A7 have no own writes. These facts do not establish preservation across the entire callback.

Bounds follow the actual call entry, all decoded branches, the separately closed tail dependency and final RET; no original FUNC-size oracle is used. The next actual entry `0x1892E` starts with a read of A0+4. In the optional existing ELF, 0x188E2 is a NOTYPE/size0 symbol in a 462-byte owning section. The checker compares only the 76-byte entry slice and 30-byte leaf slice. This proves neither whole-ELF provenance nor installed firmware identity.

Default checks read metadata; both actual-read flags remain false:

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin --image-elf /absolute/ADDRESS-WITNESS-ONLY.elf
```

Explicit FW mode requires SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` and 76800 bytes. It rereads 106 new source bytes / 37 rows and the 364-byte earlier callback. Five negative controls flip actual source bytes while retaining the opcode and every other operand field: branch destination, mask, SP restoration, MMIO offset, and store source register. All are rejected by the source contract. No controls are executed; the old 94-case matrix is not rerun.

ADC/reset semantic names remain address/context inferences. Physical chip identity and hardware effects remain unproved. The next unclosed source call is `0x19896→0x1892E`; the ADC chain is not fully closed. Config word52 lifetime after callback, full ABI, BLE OTA, BOOT, hardware compatibility and flashability remain unproved.
