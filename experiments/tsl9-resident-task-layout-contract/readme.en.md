# Conditional task-allocation RAM bounds

[繁體中文](README.md) · [Existing SDK C/C++](../tsl9-resident-message-queue/readme.en.md) · [Callback CPU-store contract](../tsl9-tscb-store-contract/readme.en.md)

This study checks existing C/C++ allocation arithmetic and ABI. **No target CODE or flashable BIN is added.** The actual C11/C++17 assertion objects are identical and allocate0 runtime bytes. The2264-byte SDK composition and95.54% APP byte coverage are unchanged.

## Established numerical relations

- Original APP `0x19A54 →0x19A66 →0x19A70` stores0x0E3F at stack+36. The configuration pointer is stack+16. Little-endian encoding and compiled ConnectNumber offset21 identify the supplied byte as0x0E. **Its value at the later SDK task call is not proved unchanged.**
- SDK code `0x43B90..0x43BBA` computes `n=3*((c>>2)+(c&3))+14` and requests `576+6*n` bytes. Integer bounds for byte c give14≤n≤212 and660≤request≤1848,without capacity-byte or allocator16-bit truncation.
- If task initialization still reads c=14,then n=29,request=750 bytes and rounded payload=752 bytes. The partition is576 record bytes,116 handler-table bytes,58 event-array bytes and2 rounding bytes.

## Conditional original-address example

The APP declares arena base0x2000418C and length0x7000. **Assuming valid writable RAM and pristine initialized heap metadata at the first allocation**,the real heap instructions imply:

| Region | Half-open range | Bytes |
| --- | --- | ---: |
| 48 records of12 bytes | `0x200045B4..0x200047F4` | 576 |
| 29 handler words | `0x200047F4..0x20004868` | 116 |
| 29 event halfwords | `0x20004868..0x200048A2` | 58 |
| Alignment remainder | `0x200048A2..0x200048A4` | 2 |

The initialized large block has27600 payload bytes. The436-byte queue/event reconstruction does not change this allocation. The first752-byte split leaves a free node at0x200048A4,with26840 payload bytes from0x200048AC to sentinel0x2000B184. These are numerical deductions,**not physical RAM-capacity or exclusive-ownership proof**.

For registration indices0/1/2 and bit0..15,all record fields at `12*(16*task+bit)` fit the576-byte region. Three handler stores also fit. General event-array bounds additionally require registered-count≤capacity.

## Open assumptions

SNV initialization runs before the three callback registrations. An earlier instruction clears the40-byte state region,but **the task-count byte read at0x43C06 is not proved still zero**. Callback,IRQ,DMA or alias effects on heap,pointers and capacity remain open. RAM ownership,whole-program stack/IRQ,installed ROM/ISA,Flash and OTA compatibility are not closed.

[Compile-only assertions](layout_assertions.c)check original-header offsets,RV32 pointer width and the observed12-byte record layout. They define no function,runtime object or substitute provider. Capacity/registered-count consistency diagnostics are possible additions,not implemented features.

Evidence: [verification-v1.json](verification-v1.json),[summary.json](summary.json),[pinned inputs](spec-v1.json).

## Reproduce

Provide the original APP,SDK/header/instruction references and preceding retained native artifacts required by the spec and existing SDK audit. Original SDK inputs and native artifacts are not included in this commit. Nothing downloads them automatically. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-task-layout-contract/verify-v1.py --tool-dir "$LLVM_BIN" --trial abi-v2
```

Trial names must be fresh. With retained artifacts,omit `--trial abi-v2`. The earlier abi-v1 include-scope failure is retained locally. abi-v2 permits only the exact source,pinned official header and compiler resources. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
