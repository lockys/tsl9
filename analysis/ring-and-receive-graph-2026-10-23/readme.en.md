# Ring and receive graph at original addresses

[繁體中文](README.md)

The official ID2966 V4.1.60 ring insertion is now curated in [src/native/receive/ring_insert.c](../../src/native/receive/ring_insert.c). It combines C/C++ with explicit machine ports, rather than recovered original source or ordinary C ABI functions. **Reverse engineering remains incomplete; this is not flashable firmware.**

| Evidence | Measured result | Boundary |
| --- | --- | --- |
| Ring v3 | C11/C++17 nominal links match all 92B/32 instructions; 40 negatives per language | Dynamic resident target and preservation contract unknown |
| Receive partial link | 494B/178 instructions, 19 FUNCs, 23 pending relocations; 48 raw-ELF negatives per language | 22 references bind real definitions, sole UND is ring; machine immediates remain pending |
| Seven nominal spans | 586B/210 instructions, 24 FUNCs, all 26 symbolic control sites resolved; 86 raw-ELF negatives per language | Only seven code spans match; LOAD gaps/full image unproved |
| Source curation | 51 C/header files, 25 translation units, 50 comparisons, 100 objects | Local LLVM18; no target execution or legacy HOST rerun |

The five ring regions cover `[0x12BC8,0x12C24)`. PC `0x12BD2` participates in deriving queue base `0x2000C038`; arbitrary placement is not supported. There are 32 slots of 12B. ID16/length8 are written before a fresh `LW32[0x0004004C]` and indirect call through A5, retaining A1/full A2 inputs. The post-call tag write uses then-live S0/S1. Pointer validity, length bounds, resident identity and preservation remain unproved. v1 failed compilation because SP was reserved; v2 used the wrong provider-address scratch register. Both remain historical and are excluded from v3 success claims.

The nominal graph contains ring92, SPI72, register-read72, register-write76, packet142, receiver70 and flag-consumer62 bytes. All bytes in these original-address spans match the official BIN; their concatenated SHA256 is `ea0695de5c5abe95f730285256d89dd5e63f265b7d83f5a70687e08f6e4e828f`. **The RX LOAD spans 17,528B, including 16,942 unvalidated gap bytes. Do not convert this container to a flat firmware BIN.** No UND/RELA means these 26 symbolic sites resolve; the indirect resident call at `0x12C0C` remains unknown.

Replay with existing local `LLVM_BIN` tools; Windows may use `python`:

```sh
python3 -B experiments/tsl9-ring-insert/verify.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-insert/build/verified-v1/c/verification.json
python3 -B experiments/tsl9-packet-receive/verify_pipeline.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-packet-receive/build/pipeline-verified-v2/c/verification.json
python3 -B experiments/tsl9-ring-insert/verify_receive_graph.py --llvm-bin "$LLVM_BIN" --replay experiments/tsl9-ring-insert/build/receive-graph-verified-v1/c/verification.json
```

Both C/C++ replays exit 0. `--require-firmware-ready` rejects with exit 1. Replay requires the original local build artifacts; public JSON alone does not contain those outputs. See the [ring experiment](../../experiments/tsl9-ring-insert/readme.en.md) for fresh-build commands.

Receipt provenance and privacy:

- [summary.json](summary.json) records source, checker and receipt hashes.
- `receipts/ring-{c,cpp}.json`, `pipeline-{c,cpp}.json`, and `graph-{c,cpp}.json` are byte-identical copies of original LF receipts already using variable paths.
- [curated-source.json](receipts/curated-source.json) is a public path derivative. The raw original remains local at `build/curated-source/ring-20261023-v1/verification.json`. Only path strings/dictionary keys map to `${PROJECT_ROOT}`, `${LLVM_BIN}` and `${CLANG_RESOURCE}`; inverse JSON equality was checked. Its raw-original SHA256 is retained, without claiming direct original-receipt replay for the derivative. Historical original receipts and BIN/APK bytes were not rewritten.

[Next boundaries](next-boundary.md) are the unreconstructed 52B IRQ adapter and 314B queue consumer. ID0's conflict with the empty-slot sentinel is a research lead, not a confirmed hardware packet-loss result; no format change was implemented.

No target/ISA/MMIO, BLE/CAN/UART/Flash, hardware, downloads or third-party API operations occurred. Full startup/resident ABI/IRQ/memory ownership/chip/OTA compatibility remain unproved. No complete firmware BIN was produced.
