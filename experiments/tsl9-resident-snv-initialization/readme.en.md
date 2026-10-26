# SNV and message initialization candidate C/C++

[繁體中文](README.md) · [Previous BLE initialization](../tsl9-resident-ble-initialization/readme.en.md)

Three complete public WCH SDK V1.31 bodies resolve the previous composition's three named imports. **Installed ROM/ISA identity remains unproved; no flashable BIN was produced.**

| Body | Candidate address range | Bytes |
| --- | --- | ---: |
| tmos_isbufset | Conditional RAM `0x200004BC..0x200004FA` | 62 |
| Message initialization | Flash `0x4329A..0x432A4` | 10 |
| SNV initialization | Flash `0x44022..0x440C2` | 160 |

[C/C++ source](resident_snv_initialization.c): **232 bytes/83 instructions**, 22 positive FUNC regions and18 relocations. Actual C11/C++17 objects are identical; every byte matches after original-address encoding. Four explicit conditional Xwchc ports are checked against primary definitions and28 official vectors. Adjacent functions are excluded.

## Observed behavior

- tmos_isbufset returns0 for a null pointer or zero length. It compares each byte with the full A1 register and returns1 when all match. It saves,zeroes and restores `0x4002420C`; physical MMIO semantics remain unknown.
- `0x4329A` only clears the word at `0x20003198` and returns.
- `0x44022` uses SNVAddr/SNVBlock/SNVNum at offsets8/12/14 in the64-byte configuration. readFlashCB at offset56 reads a local word,which is compared with SNVAddr. **The caller ignores the callback return value; valid output is not proved.**
- The non-skipped path allocates SNVBlock bytes through the real heap provider,fills with0xFF and loops over SNVNum. Each write address is `SNVAddr + SNVBlock * index`; A1 is `SNVBlock >> 2` and A2 is the buffer,whose first word is replaced with that address before writeFlashCB. Its return value is also ignored. Address/capacity validity,a buffer of at least four bytes,count units and callback effects require contracts. No Flash access was executed.
- Numeric1 covers disabled SNV,missing callbacks,an already matching first word and allocation failure. Numeric0 follows loop completion,a normal heap-release return and clearing two state words. These conditional instruction paths **do not prove successful persistence**.

The historical symbol `tsl9_candidate_system_task_initialize_44022` is retained to resolve the existing import. Observed SNV/Flash behavior does not confirm a system-task role.

## Partial composition and limits

An actual nonloadable ET_REL composition with the prior1336-byte candidate yields **1568 bytes/550 instructions**,138 positive FUNC regions and104 relocations in both C/C++. Six cross-input imports resolve against real bodies. Every input byte,symbol and relocation is retained.

**Zero named UND symbols does not close runtime dependencies.** Raw RAM,Flash/other callbacks and CODE pointers `0x432A4`/`0x43326` remain dependencies. This was neither linked into the APP nor linked for original-address execution. Physical RAM,IRQ,stack,Flash,ROM and OTA compatibility remain open. Formal APP byte coverage stays **95.54%**,not functional completion.

Evidence: [audit-result-v3.json](audit-result-v3.json),[summary.json](summary.json),[original instructions/vectors](evidence-v1.json),[original-header ABI assertions](config_abi.c). A possible addition is SNV initialization-stage and persistence diagnostics; it is not implemented.

## Reproduce

First provide the original APP,SDK carrier,official header and instruction references pinned in [spec-v1.json](spec-v1.json)/[evidence-v1.json](evidence-v1.json),plus the previous candidates' retained build artifacts. Original SDK inputs and native artifacts are not included in this commit. Nothing downloads them automatically. From the project root,using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-snv-initialization/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-snv-initialization/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-snv-initialization/build/native-v1` for the first command and omit `--link-trial` for the second. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
