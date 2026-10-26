# Secondary message candidate: original coordinates and static flow

This page is a candidate-stage snapshot. Both units are now curated into SRC;see the [integration report](../secondary-message-integration-2026-10-26/readme.en.md) for complete source and new coordinate evidence.

[繁體中文](README.md) · [Verification summary](summary.json) · [CODE C/C++](../../experiments/tsl9-secondary-message-dispatch/secondary_message_dispatch.c) · [DATA C/C++](../../experiments/tsl9-secondary-message-data/src/secondary_message_data.v1.c)

The combined candidate is now placed at original addresses: **72,610 / 76,800 bytes = 94.54%** equal the corresponding official ID2966 V4.1.60 bytes. This candidate address-byte coverage is not yet curated into `src/`. Formal coverage remains **70,522 bytes / 91.83%**; neither measure proves feature completion or hardware compatibility.

| Established item | Measured result |
|---|---|
| Original-coordinate CODE / DATA | 68,648 / 3,962 bytes, 6,174 positive owners, 48 adjacent-only spans |
| C11 / C++17 diagnostic ELF | Identical hashes, all 5,215 relocation roles retained |
| Instructions / direct transfers | 23,314 / 4,576 |
| Ordinary next / call-return positions | Zero ordinary gaps; all 1406 return positions have real CODE backing |
| Guarded jump tables | 13; the new seven-cell event table reaches six genuine CODE entries |
| Source addresses | Two new DATA HI/LO pairs and five callable address pairs bind real positive providers |
| Independent decoding | Every header/section field, file-backed byte, symbol and relocation agrees |

The combined source has 828 ELF sections, beyond the old v3 reader's 512 ceiling. This new version explicitly selects reviewed v5 (ceiling 2,048), preserving older verifiers. Only eight exact, unreferenced, non-ALLOC `.comment` mapping markers are excluded; no runtime contents are removed.

The generic end scan still records the original EBREAK at `0x8034` followed by vector DATA at `0x8038`. Specialized flow analysis treats it as a trap rather than ordinary fallthrough; its handler/resume target is unproved. The 905 register-indirect transfers include RETs. Actual runtime targets and global reachability are not all established.

The same six compiler UND and four literal-only dependencies remain explicit. The existing lookup at `0x1AAE8` still lacks a global index bound; UND counts do not enumerate all runtime gaps. Adjacent padding, the private body at `0x14056`, and protected default payload are not supplied or replaced by stubs.

## Reproduce locally

First build inputs from the [DATA / partial-link stage](../../experiments/tsl9-secondary-message-data/readme.en.md). Set `LLVM_BIN` to the spec-pinned LLVM `bin`, then create these trials from the repository root:

```sh
python experiments/tsl9-original-layout/build-v63.py --tool-dir "$LLVM_BIN" --trial secondary-message-v1
python experiments/tsl9-original-layout/verify-flow-v63.py --trial secondary-message-flow-v1
```

Trials cannot overwrite existing directories. To check retained artifacts, use the corresponding `--replay experiments/tsl9-original-layout/build/<trial>`. This milestone publishes text sources, verifiers and receipt summaries, with no newly uploaded ELF, `.o` or BIN.

The diagnostic ELF has entry=0 and PT_LOAD=0. Six unimplemented targets remain hidden NOTYPE reference constants, with no ABS FUNC provider. **No flashable BIN is produced.** No target/HOST-model/ISA execution, hardware access or vendor API request occurred. Original startup, ROM ABI, RAM/IRQ, Bluetooth and OTA compatibility remain unproved.

Next, curate the two candidate units into `src/` and independently verify the complete source closure before updating formal coverage. An offline event/dependency inspector is a possible tooling addition, not an implemented hardware feature.
