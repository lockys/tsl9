# Three-span native tagged-transmit composition

[繁體中文](README.md)

Five genuine C sources (fill, tagged dispatcher, SPI write, register read, SPI leaf) were freshly compiled as C11/C++17 using their fixed profiles and linked at original PCs:

| Span | Start | Bytes |
|---|---|---:|
| Fill | 0x8520 | 168 |
| SPI + write/modify + read | 0x16896 | 326 |
| Tagged dispatcher | 0x16B7C | 246 |

**740B/260 instructions/58 strong FUNC; zero UND/RELA/global ABS.** Every code byte equals its corresponding official ID2966 V4.1.60 range. This is a three-span code projection. The executable ELF LOAD spans 59,218 bytes including gaps; those gaps and padding are not a whole original image.

`build/nominal-v1/{c,cpp}/verification.json` records12 actual compile/IR/link/read commands per language, actual MD closure, per-command consumed-input hashes, all260 LLVM address/byte rows, full ELF metadata and recursive read-only proof replay. Fill, tagged, SPI-write and SPI-leaf formal evidence was actually re-evaluated. All five native sources were freshly compiled. Each language passed264 controls:260 raw instructions, entry and three writable-section mutations.

The fill contract also checks 31 computed cases (16 unique destinations) against actual SB/RET boundaries, original AUIPC PCs and alignment link RA=0x85BA. All15 direct JALs resolve to genuine provider bodies, without ABS stand-ins or raw-opcode carriers.

```sh
python -B experiments/tsl9-tagged-native-chain/check.py --build --out-dir experiments/tsl9-tagged-native-chain/build/local-v1 --llvm-bin "$LLVM_BIN"
python -B experiments/tsl9-tagged-native-chain/check.py --out-dir experiments/tsl9-tagged-native-chain/build/local-v1 --llvm-bin "$LLVM_BIN" --strict-firmware
```

The first folder must be fresh. Retained local original fill verified-v1, tagged verified-v2 and SPI-write nominal-v3 evidence is required; missing artifacts are not downloaded or fabricated. Strict mode performs the same checks then returns1 because firmware gates remain open.

**Unresolved:** tagged still freshly loads an unknown resident target from `[0x4004C]`; zero UND describes direct ELF symbols only. Physical placement, ROM/memory/IRQ and asynchronous behavior, whole startup and complete OTA image remain unproved. The prior1162-byte composition remains unchanged and was not merged with this740-byte chain. No target/ISA/host-model/hardware execution or flashable BIN.
