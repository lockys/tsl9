# SPI write and bit-modify providers

[繁體中文](README.md)

C11/C++17 reconstruction of `[0x168DE,0x16994)`: 182 bytes, 68 instructions and 20 private architectural regions. C owns masks, constants and volatile MMIO word stores. Architectural ports preserve physical registers, frame/slot accesses and call ordering. Regions are not ordinary C ABI functions.

## Confirmed flow

- `0x168DE`: a 32-byte frame saves S0@24, S1@20, RA@28. Selector bits0/1 independently write16/1 to `0x40010814`, without RMW. Calls to the genuine `0x16896` provider first use A0=2, then a freshly reloaded address at then-live SP+12. A pre-test S0!=S1 guards payload reads; each byte is read before incrementing S0 and calling the provider. Zero length still makes two provider calls, without payload reads; physical transmission is not proved.
- `0x1693E`: a 32-byte frame saves RA@28. The same selector writes precede A0=5 and sequential calls with fresh full-width address/mask/value from then-live SP+4/+8/+12. No byte truncation or preservation of A3 across calls is assumed.
- Both exits restore RA before unconditionally writing17 to `0x40010810`. The first restores S0 before that write and S1 after it. A0 retains the last provider result. Selector0 still performs the exit write.

## Native and linked evidence

`build/verified-v1/{c,cpp}/verification.json`: actual182B/68i, 20FUNC, 13pending RELA, one strong UND naming the genuine SPI provider, and zero global ABS. All nonrelocation bits match the original. Each language passed133 controls with whole ELF/IR hash checking disabled:68 instruction,20 weak-binding,13 addend,27 IR-port and5 scalar/SSA-wiring mutations. Additional checks retain exact SSA operands, volatile stores, full IR, actual MD closure, recipes and artifact identity.

`build/nominal-v3/{c,cpp}/verification.json`: the existing72-byte SPI C source was freshly compiled and linked with the182-byte providers at original PCs `[0x16896,0x16994)`. **All254 bytes/93 instructions/28FUNC match the original BIN, with zero UND/RELA/global ABS.** Each language ran four actual compile/IR/link/read steps and 97 controls: 93 raw-instruction changes plus entry, section-permission, LLVM-address and LLVM-byte changes. The gate checks original entry/AX permissions, no writable load segment, sole allocated code section and file mapping; receipts retain complete ELF metadata, all LLVM address/byte rows and per-command consumed-input hashes. Recursive artifact snapshots include the reused write object. Original SPI and write-provider proofs were actually replayed read-only. This is a local diagnostic ELF, not complete firmware.

Initial nominal-v1 linked successfully, but its checker reused an MD target name of native.o while the actual object was spi.o. The original checker is retained in `history/nominal.pre-md-fix.py`. A check of the actual spi.o target and same two-file include closure fixed the issue; a fresh nominal-v2 build and read-only replay passed. Independent review found that v2 needed stronger entry/permissions, LLVM field and reused-input checks. Its checker is retained in history/nominal.pre-metadata-fix.py and raw receipts stay local. A fresh v3 build closes those checks. C source, flags and machine code stayed unchanged. Strict firmware gating returned1 as intended.

From the repository root, using an existing hash-matching Windows LLVM and fresh output folders:

```sh
python -B experiments/tsl9-spi-write-providers/verify.py --build --out-dir experiments/tsl9-spi-write-providers/build/local-native-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-spi-write-providers/nominal.py --build --out-dir experiments/tsl9-spi-write-providers/build/local-nominal-v1 --llvm-bin "$LLVM_BIN"
```

The nominal script currently replays local build/verified-v1 and existing SPI verified-v3 evidence before linking. It does not download or fabricate missing original artifacts on a fresh clone. Existing1162-byte composition and246-byte tagged-candidate evidence remain unchanged; the new providers have not joined that composition.

## Inference and gaps

Cached WCH GPIOA/SPI1 addresses correspond to the observed MMIO; physical silicon, pin roles and board composition remain unproved. Opcodes0x02/0x05, earlier read0x03 and three control addresses motivate external CAN-register protocol research without establishing a controller model or count.

The SPI leaf returns A0=0 for both timeout and successful received zero. Explicit timeout/raw-status diagnostics may be useful, but the real read wrapper must be traced before asserting an upper-layer defect. No behavior was changed. **Physical MMIO, asynchronous IRQ, whole startup/ROM/OTA compatibility remain unproved; no flashable BIN or completed reverse engineering is claimed.** No target, ISA, host-model or hardware-I/O execution occurred.
