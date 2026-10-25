# State requests and record rewriting

[繁體中文](README.md) · [Source](../../src/native/receive/state_request_records.c) · [Contracts](provider-contracts.json) · [Summary](summary.json)

Reconstruct11 complete functions:740B/256 instructions,covering FBA2 record rewriting,delayed consumption,paired callbacks,packed flags,private continuation and ROM-table wrappers. The82A8 access wrapper was already present and adds no duplicate coverage;installed ROM identity remains unproved.

FBA2 preserves GP+288/289/290 state branches,masked edits to bytes3/4/5/6,and three byte9 high-nibble increment sites. Some branches increment more than once;no folding is introduced. Preserve ED00(A1=7),the dynamic check-byte offset record[2]+2,and the12A08 tail. Bounds,field meanings and checksum algorithm name remain unknown.

228 comparisons/456 objects pass;51,698 original-coordinate bytes match,67.32% coverage. Seven imports resolve,D76C is exposed,and109 providers remain. Five callback references bind to real code;all seven existing guarded tables are rechecked.

Confirmed:bytes,branch order,static addresses,masks and callback roles. Inferred:state-request record transformation. Unknown:vehicle feature attribution,bounds,time units,physical ROM/RAM,private ABI,IRQ and OTA. No target/hardware execution or new BIN. Byte coverage is not feature completion or flash readiness.
