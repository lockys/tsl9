# Secondary message DATA and partial component

[繁體中文](README.md) · [DATA C/C++](src/secondary_message_data.v1.c) · [Verification summary](summary.json) · [Nine CODE candidates](../tsl9-secondary-message-dispatch/README.md)

Two genuine readonly DATA objects add **40 bytes**. C11 and C++17 produce identical objects, with every byte equal to the selected original ID2966 V4.1.60 windows.

| Original range (exclusive end) | bytes | Established evidence |
|---|---:|---|
| `0x1A58C..0x1A5A8` | 28 | Original unsigned guard limits the index to 0..6; seven signed-relative cells map to six actual CODE entries |
| `0x19DD4..0x19DE0` | 12 | Call at `0x155BA` enters existing copy function `0x19BF0`, with A1=this window, A2=12, A0=SP+4 |

The fixed 12-byte content occurs once in each of 18 of the 22 local decoded firmware files. Field meanings, recovered declaration extents and global memory bounds are not inferred. No neighboring padding is selected. The caller has a 32-byte frame; destination `SP+4..SP+16` does not overlap saved RA at `SP+28`. This is a local layout fact, not a complete stack-budget proof.

## Combined result

`ld.lld -r --no-relax` partially links the nine CODE candidates, two DATA objects and accepted component. Both language components are identical:

- 68,648 CODE bytes and 3,962 DATA bytes: 72,610 allocated bytes, not a new formal coordinate-coverage measurement.
- 6,118 positive FUNC regions, 56 positive DATA objects, all 71 real CODE aliases and six real DATA labels retained.
- 52 existing CODE references and two DATA references bind to genuine providers. All 5,215 source/type/addend/target relocation roles survive.
- The same six compiler UND remain, with no ABS substitutes, stubs or invented data. This count is not a complete runtime dependency inventory; the existing lookup at `0x1AAE8` still lacks a global index bound.

## Reproduce locally

Set `LLVM_BIN` to the spec-pinned Android NDK 27.1.12297006 LLVM `bin`. Build the accepted parent component first, then create this stage's inputs from the repository root:

```sh
python experiments/tsl9-secondary-message-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --trial candidate-v1
python experiments/tsl9-secondary-message-data/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-secondary-message-data/integrate-v1.py --tool-dir "$LLVM_BIN" --trial component-v1
```

The default partial-link inputs are CODE `build/candidate-v1`, DATA `build/native-v1`, and the accepted component. The integration spec records paths and hashes. A fresh checkout must first build accepted inputs according to each stage's README; no newly generated `.o` is published in this milestone. `--trial` only creates a fresh directory and cannot overwrite retained results. For existing output, use `--replay <that trial path>` to check retained objects without rebuilding.

Original-coordinate placement and `src/` curation remain pending. Formal coverage stays **70,522 / 76,800 bytes = 91.83%**. No BIN, target/HOST-model/ISA execution, hardware access or vendor API request occurred. Original startup, ROM ABI, RAM/IRQ, Bluetooth and OTA compatibility remain unproved. An offline event/dependency inspector is a tooling proposal, not an implemented hardware feature.
