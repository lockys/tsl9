# Selector state and lookup data: offline reconstruction

The complete `EBAC..ECA8` state machine is reconstructed as C and compiled with four original readonly lookup objects as C11/C++17. Original-byte comparison covers 252 code bytes/81 instructions,26 direct transfers and 61 data bytes. Object lengths are 16,15,15,15; adjacent padding is excluded.

| Item | Confirmed static behavior |
|---|---|
| State memory | A2 addresses phase byte +0,count byte +1,previous-selector byte +2 and timestamp word +4. Other phase values return. |
| Phase zero | Compare selector with full-width A1 baseline. Use `(A0-58)&255 <=3`,count and previous selector to choose increment/wrap or sentinel 255. Preserve comparison widths and access order. |
| Phase one | If full input selector equals the stored byte,use unsigned32 `now-stored >499` to choose the next path; otherwise clear phase. Time units remain unknown. |
| Phase two | When input equals baseline,pass notification code four,then clear phase/count with one halfword store. Previous selector and timestamp remain. |
| Notifications | Pass original selector,count and codes zero..four through still-unprovided `E220`; do not attribute them to specific buttons or vehicle actions. |
| Four byte tables | Supply 16 bytes at `1A4E4` and 15 each at `1A518`,`1A528`,`1A538`,matching the previous high-nibble/signed REM15 index extents. Each has an XOR-affine index-bit relation; no particular CRC algorithm is asserted. |

Evidence: [original code and data](evidence.json), [reconstructed C](../../src/native/receive/selector_storage.c), [compiler and comparison](../../experiments/tsl9-selector-storage/build-v1.py). [繁體中文](README.md)

Whole-source proof passes 218 comparisons/436 objects. One code and four data imports are resolved; E220 is exposed; 122 remain. All 45,658 selected original-coordinate bytes match. Static flow covers 2,515 direct transfers with no ordinary continuation gaps. No unprovided callback-address reference remains in this selected component; indirect runtime targets remain unproved. Time units,feature attribution,private ABI and hardware/OTA remain unproved; no target or hardware execution and no new BIN.
