# Record profile processing: offline reconstruction

Four complete functions at `0x18232..0x18604` have been reconstructed as C and compiled separately as C11 and C++17. Object comparison covers 978 bytes, 310 original instructions, 43 direct transfers and three code-address references. The reconstruction retains register-bound C and private architecture operations; it is not a portable restoration of complete original source.

| Entry | Observed behavior |
|---|---|
| `0x18232` | Return when the unsigned index exceeds nine. Select indices 0..4 or 5..9, copy eight record bytes, check marker `0x5A`, then extract and compare fields from data channels 16/17. |
| `0x18430` | Clear corresponding state for input bits zero/one when existing flags allow it; notify an existing handler. |
| `0x184AA` | Extract four fields and clamp them to 10..250, 30..470, 5..75 and 10..50. Build a record with marker `0x5A`, copy eight bytes and call the existing settings writer. The eighth byte is not explicitly initialized in this body and remains unchanged in the reconstruction. |
| `0x185D8` | Update mode only when input byte two equals three or four; conditionally tail-transfer to an existing handler according to another state word. |

Evidence: [original instructions](evidence.json), [compiler and experiment](../../experiments/tsl9-record-profiles/build-v1.py), [reconstructed C](../../src/native/receive/record_profiles.c). [繁體中文](README.md)

Physical units, vehicle-feature attribution, private ABI and hardware/OTA compatibility remain unproved. No target, host model, emulator or hardware execution; no new BIN. Whole-source proof now passes 210 comparisons/420 objects. Two old imports are resolved without new dependencies; 141 remain. All 43,223 selected original-coordinate bytes match the official BIN. Static flow covers 2,357 direct transfers with no ordinary continuation gaps; indirect runtime targets remain unproved.
