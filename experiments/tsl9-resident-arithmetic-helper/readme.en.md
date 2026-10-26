# Clock arithmetic-helper candidate C/C++

[繁體中文](README.md) · [Clock services](../tsl9-resident-clock-services/readme.en.md) · [Timer service](../tsl9-resident-timer-service/readme.en.md)

The complete0x6DF1A..0x6E2AC body contains **914 bytes/296 instructions**, with its actual **256-byte lookup table** at0x6E95C..0x6EA5C. This is a public SDK V1.31 candidate; installed ROM identity is unproved. The [C/C++ source](resident_arithmetic_helper.c) retains original register context, C/assembly and a real const byte table, not an ordinary HOST-callable API.

## Verified

- Identical C11/C++17 objects; every CODE/DATA byte matches after original-address encoding. There are81 positive FUNC regions, one real OBJECT and65 relocations. Three AUIPC/ADDI pairs reference the real table object; no helper stub is substituted.
- All256 original table entries equal their unsigned index bit length. The three byte-load indices use unsigned buckets and shifts0/8/16/24, statically bounded to0..255. Three conditional Xwchc ports are checked against primary definitions and28 official vectors; physical ISA identity remains unproved.
- Every instruction is reachable in the complete static entry CFG. It is acyclic, with no external calls, memory stores or SP operands. The maximum conservative CFG path to return is98 instructions, **not a hardware timing measurement**.
- Each real clock caller at0x43FCC/0x43D94/0x43DC6 explicitly sets A3=0. WaitWindow supplies denominator1,000,000; delta paths use live ClockFrequency, whose nonzero/stability contract remains required.

## Inference and unknowns

The32-bit DIVU/REMU instructions, base65536 normalization and quotient corrections **fit an unsigned64-bit division candidate**. A full-input mathematical semantic proof has not been completed; DIVU alone does not prove the complete helper equals `uint64_t / uint64_t`. The original includes a zero-divisor path; no target/model execution or negative test of that path was performed.

Compile-only assertions establish RV32 pointer and unsigned32/64-bit sizes, not the helper's register ABI. No target, HOST model or ISA emulation was executed.

## Actual partial composition

The complete real body resolves the existing tsl9_candidate_external_flash_6df1a import. Actual nonloadable C/C++ ET_REL objects contain **4426 bytes CODE+256 bytes DATA/1538 instructions**,393 positive FUNC regions, one OBJECT and289 relocations. Every input byte, symbol and relocation is retained.

RAM0x2000061A/0x20002610 and Flash0x63DD0 remain genuine imports, along with overall raw RAM/callback contracts. The **4-byte startup source gap** remains. No original-address execution link, APP integration or new BIN is supplied. APP byte coverage stays **95.54%**, not functional completion. Physical RAM/ROM/ISA, IRQ, stack, Flash and original-hardware OTA compatibility remain unproved.

Evidence: [full audit v2](audit-result-v2.json), [summary](summary.json), [original instructions/table](evidence-v1.json), [specification and hashes](spec-v1.json). Clock normalization/baseline diagnostics are unimplemented feature candidates.

## Reproduce

Provide the original APP, SDK/header/instruction references and prior native artifacts required by the spec, evidence and audit. Original SDK inputs and native artifacts are not included in this commit or downloaded automatically. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-arithmetic-helper/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-arithmetic-helper/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts, use `--replay experiments/tsl9-resident-arithmetic-helper/build/native-v1` for the first command and omit `--link-trial` for the second. No hardware access or vendor API traffic was performed.
