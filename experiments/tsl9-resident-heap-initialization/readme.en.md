# Heap initialization candidate C/C++

[繁體中文](README.md) · [Allocation/release candidates](../tsl9-resident-heap-core/readme.en.md)

This study reconstructs **148 bytes/49 instructions** from public WCH SDK V1.31. It is not flashable firmware; installed ROM identity is unproved.

| Candidate Flash body | Bytes | Role |
| --- | ---: | --- |
| `0x430E0..0x43104` | 36 | Traverse the candidate heap and sum free block sizes |
| `0x43104..0x43174` | 112 | Initialize small/large regions and sentinel,then call that accounting helper |

[Source](resident_heap_initialization.c) has10 positive FUNC regions,5 relocations and5 explicit conditional Xwchc ports. Actual C11/C++17 objects are identical; all148 bytes match after original-address encoding. Two independent ELF readers agree. See [instruction evidence](evidence-v1.json) and [actual native receipt](native-proof-v1.json).

## Configuration and limits

The candidate reads MEMAddr/MEMLen from configuration at `0x200031EC`. Its first node is MEMAddr+544,the region boundary adds min(MEMLen>>3,512),and the sentinel is MEMAddr+MEMLen-8. Block sizes are stored as halfwords. This helper does not itself validate input bounds,physical RAM,ownership or list termination.

[Original-header ABI assertions](config_abi.c) pass under both RV32 C11/C++17:64-byte structure,alignment4,MEMAddr/MEMLen offsets0/4 and staCB offset52. Adding52 to the candidate configuration base gives the allocator's callback storage `0x20003220`. **Callback value and actual invocation remain unproved.** ABI assertion objects allocate zero runtime bytes.

The [existing APP reconstruction](../../src/native/startup/resident_startup.c) sets configuration memory length to `0x7000` (28 KiB) and calls through pointer `0x400A4`. Installed ROM,the complete configuration-copy call chain,RAM ownership and IRQ contracts remain unproved. This module has not been linked with preceding candidates or the APP. Formal APP byte coverage remains **95.54%**,not feature completion.

## Verify locally

Use the pinned Windows NDK LLVM tools in [spec-v1.json](spec-v1.json). From the project root,set LLVM_BIN to that tool directory and use a new trial name:

```sh
python experiments/tsl9-resident-heap-initialization/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
```

For retained artifacts,replace `--trial native-v1` with `--replay experiments/tsl9-resident-heap-initialization/build/native-v1`. This only cross-compiles and reads files;no target/HOST model/ISA execution,hardware access or new BIN occurs.

Heap usage and allocation-failure diagnostics are a feature candidate only,pending installed RAM,callback and IRQ ownership evidence.
