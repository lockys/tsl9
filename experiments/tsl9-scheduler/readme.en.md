# Offline C/C++ reconstruction of the original scheduler

[繁體中文](README.md)

The whole9124–9250 span contains300 bytes,115 instructions and28 architectural regions. The same [C source](src/scheduler.v1.c) was compiled as C11 and C++17. Data-only original-address encoding of all11 real control relocations matches every byte against official ID2966 V4.1.60.

There are15 slots at2000BE08 with stride12: byte flag,callback word and argument word at0/4/8. An occupied zero-A2 scan still falls into the general search after15 entries. Multiplication takes its low32 bits before unsigned division by625; physical time units are unknown. Variable C shifts use the count's low5 bits and retain low16 truncation. Fresh physical S-registers after resident calls are not assumed bounded or preserved.

Two indirect calls use40068/40058; two tails use40050/4022C. Their targets and ABI remain unknown. C owns free-register arithmetic/constants/masks/ordinary memory. Frames,reserved-S operations/loads/stores,PC and control are explicit architectural ports. These regions are not ordinary C ABI functions or a universal semantic proof.

```sh
python3 experiments/tsl9-scheduler/build-v1.py --tool-dir "$LLVM_BIN" --trial YOUR_NEW_TRIAL
python3 experiments/tsl9-scheduler/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-scheduler/build/trial-v1
```

Existing pinned tools and the official BIN are required. No dependency downloads,network,hardware,HOST model,ISA or target execution and no new malformed-input/negative matrix. IRQ,concurrency,memory validity,resident behavior,startup,physical hardware and OTA compatibility remain unproved. This is not flashable firmware.

Potential additions: passive slot occupancy,full-table counts and registration/update results. These are proposals,not implemented or hardware-validated features.

## Genuine integration and reference association

Both languages partially link5702 code bytes and60 table bytes,460 FUNC/423 RELA. The previous `tsl9_callback_external_9124` UND is now a real definition;74 symbols remain unresolved. VMAs are0 and there is no executable loading layout or firmware BIN.

100 source comparisons/200 objects pass. All prior98 results and589 artifact records remain unchanged. Parent validation checks one exact manifest file/unit extension and all other producer inputs; it does not claim old whole-manifest replay.

```sh
python3 experiments/tsl9-scheduler/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-scheduler/build/graph-v1
python3 scripts/check-scheduler-resident-references.py
```

The [retained reference association](../../analysis/scheduler-2026-10-23/resident-reference-association.json) maps the historical header's slots to set-event,start-task,start-reload-task and message-deallocate declarations. V1.31 and V1.40 candidate images have different actual pointer values. These names/prototypes are reference-level candidates; no candidate address or implementation is bound into the reconstruction. Reference checks require retained local WCH data. Installed ROM/library identity and resident ABI remain unknown.
