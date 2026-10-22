# A genuinely declared reply object

[繁體中文](readme.zh-TW.md)

The final candidate measures550B/186 instructions with a48B frame and eight saves,RA/S0..S6. Standard C11_Alignas(4)/C++alignas(4) declares an uninitialized volatile uint8_t response[4]. It does not point into a saved-register or spill area.

Actual IR has one[4 x i8]align4 allocation and4B lifetime start/end. The object start becomes the opaque-call pointer. Local stores touch only byte0/byte1; the upper half is not initialized or word-stored. Actual machine stores targetSP12/SP13, including a failure-path rewrite ofSP12, and the pointer isSP12. The entire4B interval12..15 fits the frame without overlapping any save/reload/otherSPword access. The lowest save isS6@16.

With common entrySPE, E−48+12 equals originalE−36. Thus the numeric reply pointer and independent declared storage projections pass. The seven original save addresses also match relative to entry. This does not admit the wholeABI.

The shared packet label correlates two paths: ownedS reply pointer with length2, and nullE reply with length0. The checker matches pointer/length phi predecessors explicitly. Backing size4 never becomes payload length4, and not every packet call has length2. Unknown allocation/callback code may observe additional registers or memory; installed read footprints remain unproved.

The only source changes against556B are an unsigned flash-base identity after the existing range guard and the native-only aligned4B declaration. HOST remains a uint32 identity; header, other algorithm, provider effects, full8register read/write bridges and memory clobbers are unchanged. Unchanged HOST/baseline builds were not rerun. Both codegen profiles are complete, with no new link/BIN.

The first552B/186-instruction profile already had eight saves but kept its2B object atSP14/15, missingE−36. Its snapshot is historical evidence. Only the second actual4B profile establishesSP12 ownership; save count alone was insufficient.

Four bounded controls reject a2B IR allocation, packet length4, a claimed8B backing whose tail overlaps saves, and an actualELF savedS6 reload from the wrong slot. The first three use actual IR text mutations/span checks; the fourth mutates an ELF operand. No CPU/ISA state execution occurs.

```sh
python -B object-review/check.py --project-root ROOT
python -B object-review/review.py --project-root ROOT --folder MODE --firmware FW --receipt NEW.json --controls
python -B object-review/review.py --project-root ROOT --firmware FW --replay NEW.json
```

Default checks read sealed metadata/source deltas only. Actual mode requires an explicit folder and official firmware; receipts are create-only outside producer folders. Replay is read-only without recreating controls. Only source/metadata are sealed, not generatedbuild archives.

AdditionalS6 saving and save order still differ from original. Physical callee/S/GP/SP/RA, IRQ/fault/asynchronous behavior, unknown callbacks, Flash/NV/BOOT and OTA remain unproved. Equal reply addresses do not replace these obligations. The550B candidate has not been integrated into the existing wired experimental image.
