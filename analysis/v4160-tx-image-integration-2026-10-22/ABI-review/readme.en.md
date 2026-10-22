# Independent TX full-image ABI and artifact review

[繁體中文](README.md) · [简体中文](readme.zh-CN.md)

This verifies a real new full-image static contract. TX has an honest allocated assembly entry FUNC8, readable C/C++ body FUNC270, and real C return leaf FUNC2. No aggregate FUNC280 or ABS code provider is fabricated. This does not prove the complete original hardware ABI, unknown ROM behavior, asynchronous behavior, or Bluetooth flashing.

The verification-only `baseline.json` records roles, allocation metadata and hashes measured from the preceding actual twelve-function image. `prepare-baseline.py` is an optional historical provenance audit, not a runtime prerequisite. Default and fresh actual checks do not require archived baseline objects. Original firmware bytes are validation input only.

Actual checks cover 691 allocations and every LOAD, all 690 non-TX partial/linked owners, complete 76,800-byte scatter, and all 76,520 bytes outside TX unchanged. The new image has 93 changed bytes entirely within TX; original whole-image hash equality is deliberately not required. New provider payloads match the previously independently reviewed source-owned component, without generating bytes from it.

All 8,258 non-TX relocations retain their exact semantic roles, with only the explicit FUNC280-to-FUNC8 target-size projection at nine TX references. Total RELAs are 8,261 = 8,246 outside thirteen selected allocation regions + 15 owned. The checker validates the allocated RAM provider and real HI/LO anchor.

The 30 recorded encoded boundary references comprise 29 owners outside selected regions and one selected page-reply call at 9BE0. They preserve width, target, rd, link and RA; 13EAC remains JAL x0. This is not an enumeration of every call in the image. Other selected internal calls remain covered by all non-TX relocation/byte comparisons.

The actual IRQ/quarter, page-reply, and TX source-owned scheduling stages retain their pre/post objects and receipts: 14, 28, and 50 file bytes change respectively. Final scheduling is explicitly separate from compiler output. Nine actual ELF/BIN countercases reject fabricated roles, PCREL changes, address-significance changes, wrong link registers, changed instructions, LOAD geometry and exported bytes.

`selected-c.json`, `selected-cpp.json` and `summary.json` retain actual review metadata. No compiled build artifacts are sealed or distributed here.

## Commands and evidence levels

Metadata-only default; no firmware read or actual build replay:

```sh
python -B ABI-review/check.py --project-root ROOT
```

Actual review of a freshly generated producer folder and explicit original firmware, writing a create-only receipt; then read-only exact replay:

```sh
python -B ABI-review/review.py --project-root ROOT --firmware FW --folder MODE --receipt NEW.json
python -B ABI-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

The folder must contain all new TX providers, pre/post scheduling artifacts and receipts, full ELF and exported image. `review.sh` without arguments selects metadata-only; otherwise it forwards actual-review arguments. `PYTHON` may select an interpreter.

Actual mode returns `actual_build_artifact_replay=true` and `static_full_image_contract_passed=true`. Metadata default explicitly reports no actual replay or current full-image check. Separate source-review establishes the 46-TU/45-MD/67-recipe source and compiler provenance.

## Limits

The static loop CFG and entry/frame predicates require corresponding live GPR/memory responses and source-role inputs; arbitrary code-as-data and unknown computed interior entries are not excluded. Unknown ROM implementation/clobbers, every fault/interrupt/asynchronous prefix, physical chip compatibility, BOOT acceptance, OTA packaging and real device behavior remain unproved. `original_full_ABI_admitted` and `hardware_OTA_proved` remain false.
