# Conditional LLE / callback / ECALL C/C++

[繁體中文](README.md) · [Prior callbacks](../tsl9-resident-state8-callbacks/readme.en.md)

Five complete candidate bodies add **936 bytes /338 instructions**: callback 0x65620..0x656C6 (166B), conditional-RAM LLE 0x20002E34..0x20002E6C (56B), gateway 0x20002E28..0x20002E30 (8B), and register helpers 0x2000298E..0x20002B4C /0x20002B4C..0x20002C50 (706B). Another226 original APP bytes are references;no APP CODE is added. These are original-context register-bound C/assembly,not ordinary callable C APIs.

## Static evidence

The candidate startup writes0x20002E34 intoRAM slot2. Original APP initialization0x199E2..0x199F0 copies slot2 to liveGP+384. The APP LLE wrapper0x8498..0x851E allocates128 bytes and calls the pointer loaded fromGP+384.

LLE AUIPC/ADDI instructions form the actual gateway0x20002E28. The active branch saves oldMEPC toSP+0 and writes gatewayMEPC at0x20002E48..0x20002E56;the other branch usesSP+120 forRA. Both word slots fit128 bytes without overlapping the29 saved registers atSP+4..SP+116. These raw address forms preserve original encoding;they are not linker relocations. No original-address link was performed.

The gateway calls the real prior runner0x200007A0 then ECALL. Original APP restore0x8448..0x8496 readsMEPC fromSP+0,restores the same29 registers,releases128 bytes and MRETs. Vector carrier words0x804C/0x8058 contain0x8448;physical cause/mode dispatch remains unproved. MRET,ECALL and the opaque tail are distinct scope exits. Ending analysis atECALL does not prove that it cannot return. Callback0x65620 still tail-transfers through opaque pointer0x20003550 after releasing its own16-byte frame.

## Verification and limits

Actual C11/C++17 objects are identical;all936 original-context bytes match. The97 positive FUNC regions are compilation fragments,not97 logical functions. All52 primary Xwchc positive vectors and24 actual conditional operations are checked.

The retained nonloadable composition contains **9608 CODE+256 DATA bytes /3367 instructions**,800 positive FUNC regions and582 relocations. Every input byte,symbol and relocation is retained. Actual handlers0x57DAE/0x6020A remain undefined.

**This is conditional structural agreement;usable replacement firmware has not been successfully reverse engineered.** Installed ROM/RAM/ISA,initialization completion and the inherited4-byte copy gap,stable unsavedGP,frame/MMIO aliasing,calleeSP preservation,IRQ nesting,ECALL trap frame/vector mode and CSR0x804 semantics remain open. No target,HOST model or ISA execution,hardware access,vendor API traffic,APP integration or newBIN. Existing95.54% APP byte coverage is not functional completion.

Evidence: [audit](audit-result-v1.json),[summary](summary.json),[original instructions and sources](evidence-v1.json),[specification](spec-v1.json). IRQ/callback diagnostics remain unimplemented feature candidates.

## Reproduce

Provide the pinned original APP,SDK/instruction references and retained prior native artifacts. Missing inputs are not downloaded. From the project root with the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-lle-callback-gateway/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-lle-callback-gateway/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. For retained artifacts,use `--replay experiments/tsl9-resident-lle-callback-gateway/build/native-v1` for the first command and omit `--link-trial` for the second. Tool hashes currently pin Windows builds;cross-platform compilation is unverified.
