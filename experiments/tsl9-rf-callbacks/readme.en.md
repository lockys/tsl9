# RF task and status callbacks

[繁體中文](README.md)

Original17476–1753A covers196B,65 instructions and23 architectural regions. Actual C11/C++17 objects preserve144 non-control bytes and16 typed references;data-only original-VA encoding matches all196B. The16B task frame/shared exits,signed low16-bit event test,four indirect calls,frameless status callback andthree raw packet-byte comparisons are retained.

Encoded AUIPC/ADDI in constructor175E8 independently establish17476/174EE. Earlier16B-early manual addresses were corrected in authored analysis;original projections/receipts remain unchanged. Literal addresses are not proved diagnostic runtime bindings.

```sh
python3 experiments/tsl9-rf-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rf-callbacks/build/trial-v1
```

Offline compilation/normal static checks only. Direct173EE/17442,resident identity/ABI,original placement,physical hardware/IRQ/OTA remain unproved. No target/HOST-model/ISA execution orBIN generation.
