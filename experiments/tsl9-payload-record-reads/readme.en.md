# Record-copy calls in the newly opened range

[繁體中文](README.md)

The newly opened `0x14056..0x14C8A` region contains seven direct calls to `0x82A8` not covered by the earlier selected-range scan. In address order their record indexes are **1, 11, 5, 6, 7, 3 and 4**; each sets `a0=1` before the call. None of these seven directly calls with index 14.

For the `a0=1` path, original-address instructions `0x82A8..0x82CA` pass `0x2000C1B8+12*index` as source, the caller's `a2` as destination, and length 12 to the target loaded from `0x4004C`. If the resident slot is a forward copy and source/stack destination are valid and not harmfully overlapping, the seven calls read records into the stack. This does not establish installed slot identity, actual reachability or the absence of other writers.

`python scripts/verify-payload-record-reads.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` checks both source builds for the seven direct calls, argument setup and key `0x82A8` instructions, and rebuilds the candidate BIN. It executes no firmware or hardware; indirect calls, other writing paths and actual device interference remain unexcluded.
