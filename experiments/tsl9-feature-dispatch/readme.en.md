# Complete feature dispatch: bounded static reconstruction

[繁體中文](README.md)

Three C units reconstruct all1912B of14D2E–154A6, the10B829E mode getter, and60B of signed-relative tables. The same source actually compiles as C11 and C++17.210 FUNC symbols are architectural regions, not ordinary C ABI functions.

The new component has1922B/669 instructions,208 direct controls,4 PC-relative and30 table relocations. Data-only relocation encoding at recorded original addresses reproduces every original code/table byte. Genuine integration yields5088B code plus60B tables,401 FUNC,386 pending RELA and70 real direct UND providers. Current source curation passes96 comparisons/192 objects across74 C/header files and48 native units; all previous90 facts and541 artifact records remain unchanged.

No ABS provider or missing implementation is supplied. All ET_REL section VMAs remain zero under ld-r despite the ORIGINAL-ADDRESS contract filename. These are diagnostic objects with no executable loading configuration, never firmware BINs.

C owns free-bank/GP memory, constants and bit operations. Reserved S0/SP/RA, some fresh S0-relative reads, control and PC effects are explicit architecture ports. Actual reserved-SP compiler failures remain. No ordinary ABI, post-call frame preservation or packet lifetime is assumed.

## Verification and reproduction boundary

Current verify-v2.py checks actual source/dependency/tool identities, complete symbol roles and unique names, global ABS exclusion, all allocations, genuine tables and original bytes. Parent revalidation admits exactly three manifest extensions and proves all selected old sources unchanged; it is not replay of the old whole-manifest receipt.

Frozen v1 retains10173 historical negative controls per language. Independent review exposed an incomplete same-name symbol-role gate; v2 strengthens uniqueness/roles/ABS checks and pins parent proof data. Actual baseline artifacts pass. A later independent malformed-input review was stopped by a safety check, with no rerouting. V2 ran no new negative matrix; historical counts do not validate the new checks.

For locally retained original graph-v2 inputs:

```sh
python3 scripts/verify-curated-source.py --replay build/curated-source/feature-dispatch-20261023-v2/verification.json
python3 experiments/tsl9-feature-dispatch/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-feature-dispatch/build/graph-v2/c --mode c
python3 experiments/tsl9-feature-dispatch/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-feature-dispatch/build/graph-v2/cpp --mode cpp
```

Full replay requires retained raw build/parent receipts; anonymous public derivatives are not original replay inputs. The pinned Windows toolchain was tested; other platforms require new evidence. General source compilation uses scripts/verify-curated-source.py with an existing LLVM directory. Nothing downloads tools or executes target/HOST model/ISA/hardware/vendor APIs.

## Remaining scope

Two literal PC-derived pointers identify executable callback1069E, indirectly called by1083C. Its nonzero path registers107C0 through9124 and expands the resident frontier. The70 direct UND count does not cover this dependency. See the [callback evidence](../../analysis/feature-dispatch-2026-10-23/callback-frontier.json).

Installed ROM, physical MCU/controller, complete startup/memory/IRQ/clock, Flash and OTA compatibility remain unproved. No new BIN was generated or flashed. A strictly offline filter/request-route inspector remains a proposed feature, not implemented hardware diagnostics.
