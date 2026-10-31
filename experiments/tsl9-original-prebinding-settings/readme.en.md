# Settings/defaults/Flash path before BLE library binding

[繁體中文](README.md) · [Early IRQ evidence](../tsl9-original-APP-early-IRQ/readme.en.md) · [SDK startup/slot2](../tsl9-resident-slot2-startup/readme.en.md)

Nine complete existing C/C++ functions cover **728 CODE bytes/240 instructions**,plus a4-byte initial RAM pointer. Original BIN,both original-address C/C++ diagnostic ELFs and two independent readers agree. **No new target code,compilation,BIN or hardware operation.**

## Conditional settings path before binding

Initializer call0x9264→0x131C2 dominates0x9268→0x8E88 in the complete normal-return CFG. Function0x131C2 requests a112-byte copy from numeric address0x08077A00 toRAM0x2000C29C through table0x4004C.

Candidate table0x4004C points to complete58-byte copy providerRAM0x20000332;0x40048 points to fill providerRAM0x2000039C. Matching installed ROM,private calling contracts,valid source/destination and asynchronous effects remain conditions. These are not assumed ordinary libc or observed Flash APIs.

The APP checks four bytes at0x2000C2A8..0x2000C2AC using `low8(byte-32)<=94`,equivalent toASCII32..126. A failing byte takes call0x13204→defaults0x1316A. A normal CFG path avoids that call;settings are not claimed to be written on every startup.

Defaults request fill0/112 bytes at0x2000C29C,then copy a4-byte literal to the address in incomingGP+84 plus12. The original reset128-byte data copy contains numeric pointer0x2000C29C at0x1ABB4. With successful copy,stableGP/pointer and no later overwrite,the destination is0x2000C2A8. This is not live RAM observation. **The excluded literal payload and standalone hash are not read into or included in the evidence/publication.**

Tail0x131BE releases its16-byte frame before writer0x13138. Writer call0x1315E reaches existing Flash transaction0x9C0A. Other settings fallback callees and their complete effects remain open.

## Copy112 and program256 have different extents

Writer0x13138 allocates272 bytes,copies **112 bytes to ownSP**,and savesRA atSP+268. It calls0x9C0A with destination0x08077A00/source ownSP.

Program leaf0x18EF2 replacesA2 with **256** and aligns destination down to256 bytes. Normal exit from its second fresh status poll givesA5=0. The loop reads one source word and writes one destination word at each offset,advancing4 until offset256. With standard semantics,valid memory,no faults and all polls completing,numerically this is64 CPU word transfers.

The source extent is **ownSP..SP+256**,within the frame and disjoint from savedRA. Only the first112 bytes are explicitly copied by the writer;the additional **144 bytes have no explicit fill/copy there**. Their initialization provenance remains unproved. This is an evidence gap,**not observed uninitialized contents,data disclosure or failed programming**. Do not invent zero padding,shorten the transfer or claim a fully initialized256-byte record.

## Flash transaction IRQ boundary

Function0x9C0A uses its own32-byte frame. It clearsCSR0x800 mask0x88 at0x9C1A,calls five complete status/unlock/erase/program/lock leaves,and sets the mask at0x9C3C before restoringS0. This is an unconditional set,not incoming-mask restoration. Complete leaves preserveS0/S1/GP/SP and contain no other calls/CSR requests. All calls and the final set dominate normal return.

This establishes another **conditional Flash/global-enable path before library binding**,not poll termination,physical Flash commit,NVM map/capacity,initial BB/LLE enable/pending,actual IRQ delivery or asynchronous alias closure.

## Limits of write status and return value

Original `0x9C0A..0x9C4A` calls unlock, writes `0x31` to `0x4002200C`, then calls erase, program and lock without conditional branches on their return values. Polls in complete leaves `0x18EC4` and `0x18EF2` test only bits `0x01` or `0x02` at `0x4002200C`; their checked bodies do not test other bits after reading status. The [WCH register definitions](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32v20x.h) label candidate FLASH_STATR `0x04` as programming error, `0x10` as write protection error and `0x20` as end of operation. This static comparison neither establishes an actual error nor makes a completed poll proof of a successful write.

If original control flow and all callees return normally and registers are not changed asynchronously, the two leaves clear the destination's low eight bits and neither the later lock nor wrapper overwrites `a0`. Thus on normal return through this `0x13138` path, `a0` remains numeric `0x08077A00`, not a success/error result established by the path. Other callers or external ABIs are not covered. The [offline checker](check-flash-return-status.py) pins three original instruction windows; it does not touch hardware, execute the target or read excluded regions.

## Use and status

[Settings C/C++](../../src/native/startup/main_initializers.c) · [Defaults/writer C/C++](../../src/native/startup/settings_defaults.c) · [Flash transaction C/C++](../../src/native/receive/ota_runtime.c) · [Evidence](evidence-v1.json) · [Receipt](verification-v2.json) · [Summary](summary.json)

```sh
python experiments/tsl9-original-prebinding-settings/verify-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned originalBIN,candidateSDK,official headers and retained Windows NDK LLVM native artifacts;no dependencies are downloaded. Cross-platform verification is unconfirmed. APP stays159 C/H files and95.54% byte coverage,not functional completion. SDK remains20,346 CODE+256 DATA/11 genuine named dependencies. The4-byte startup source gap and ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain open. **Usable replacement firmware has not been successfully reconstructed.**

Future feature candidate:offline compatibility preflight for a user-authorized NVM backup,showing settings validation and source-provenance gaps. Unimplemented;no automatic repair or hardware writes.
