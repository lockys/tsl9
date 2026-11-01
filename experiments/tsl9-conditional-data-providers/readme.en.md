# Conditional DATA-reference links

[繁體中文](README.md)

On top of the [conditional TX RAM model](../tsl9-conditional-tx-storage/readme.en.md), three DATA references are linked to actual compiled source sections:

| Nominal address | Actual section and checked range |
| --- | --- |
| `0x1AB48` | Eight-byte counter data covers 16-bit reads for index 0–3 |
| `0x1A638` | Forty-eight-byte sequence data covers six-byte windows for channels 0–3 and states 0–1 |
| `0x1A078` | Interior of a 432-byte grid object; modes 0–5 each have a uniquely owned 16-byte row |

Run `python scripts/verify-conditional-data-providers.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`. C/C++ candidate aliases point to actual sections rather than absolute address witnesses. With these conditions and the RAM model, the strict link retains three external names: resident `0x40000`, code entry `0x14056`, and default data `0x1A69C`. When numerical witnesses are used for comparison, all 73,551 selected Flash bytes remain unchanged.

**This does not prove complete providers.** Global index/mode/state bounds, RAM ownership and hardware behavior remain unverified; accesses beyond these windows may reach other data or go out of bounds. Outputs are diagnostic ELFs with zero `PT_LOAD`, not BINs, and must not be flashed. The default build does not apply these conditional aliases.
