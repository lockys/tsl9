# WCH historical reference coverage

A public GitHub history query for WCH's `EVT/EXAM/BLE/LIB/wchble_rom.hex`, with 30 entries per page, returned four commits on the first page. The 2023-12-01 `ec059e0` is the retained V1.31 reference; 2024-02-26 `9596a13` is another version. The remaining two public files were checked for basic record syntax, length, checksum, overlap and EOF:

| Official commit | HEX SHA-256 | Full V1.31 marker | Recorded bytes at `0x6EB2C..0x6EB30` |
| --- | --- | ---: | ---: |
| [`64be955`](https://github.com/openwch/ch32v20x/blob/64be9554615df522899579633530fd234d685682/EVT/EXAM/BLE/LIB/wchble_rom.hex) | `42766be9b9aea7a819b61ee6bdb6c49c47838b2177947a460364888c4b621c57` | 0 | 0 |
| [`b79c6ac`](https://github.com/openwch/ch32v20x/blob/b79c6ac80df7b75753498c0742a1f0e4502a0b44/EVT/EXAM/BLE/LIB/wchble_rom.hex) | `e18c0a5cdfb8c1b46d2961fe2e28ffe81ec36d96f971f529e9fde5ee810c5f0b` | 0 | 0 |

Neither file contains the full marker or any of the four bytes at that numeric location. This does not exclude other versions or equivalent contents at different addresses and cannot identify the installed resident. No other version was used to fill the gap.

Run `python experiments/tsl9-resident-historical-coverage/test_inspect.py` for one synthetic acceptance and four rejection cases, without network. `inspect.py` reads GitHub contents API base64 text from stdin and reports only hashes, counts and address coverage, not raw contents; replaying the real files requires their public API contents. No device data was read or transmitted.
