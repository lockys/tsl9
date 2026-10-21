# Interrupt initialization source evidence

The ID 2966 V4.1.60 image supplies five complete functions: entry `0x9A42` and its four distinct direct callees. The retained raw source covers 264 bytes and 94 instructions. The independent RV32I/C bit decoder agrees with radare2 on every instruction's address, width and original bytes. This is static evidence; it does not execute the original binary or prove hardware compatibility.

Read [the source contract](contract.md) for exact register, stack, CSR, call and MMIO ordering. [Retained instructions](retained-instructions.json) contain both independently decoded operands and separate tool mnemonics.

```sh
python3 inspect-source.py --check --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin --source-root /absolute/path/source
```

The read-only Python 3 checker verifies the whole original image digest and all five complete ranges, then rejects one raw instruction mutation at each of 94 instruction addresses without relying on the whole-image digest for those negative controls. It needs no radare2 installation at replay time. No network, device access, ISA emulation, original/rebuilt RV32 execution or OTA operation occurs. Correct output does not authorize flashing.
