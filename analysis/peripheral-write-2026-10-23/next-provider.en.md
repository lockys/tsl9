# Next: tagged provider16B7C
[繁體中文](next-provider.md) · [Original256B window](next-provider-window.json)

Read-only radare2 decoding of[0x16B7C,0x16C7C),256B/89 instructions, pins original firmware and decoder hashes. No ESIL or target execution.

Candidate function extent is[16B7C,16C72),246B: normal RET, loop cold block16C62 and early exits16C6C/16C6E. Another validation sequence starts16C72. This remains a candidate boundary; all external incoming references are not claimed.

Entry tests recordbyte11 for1/2, then[GP+84] pointer+4 bit3. Early exits precede the frame; main flow allocates64B and saves RA/S0..S3. Calls include8520,16994,168DE,1693E.16994 has a reusable separate register-read reconstruction; other providers still need review. Opaque calls do not establish ordinary C ABI.

Preserve early-return/frame separation, loop counts/order, then-live SP/S/A registers after each opaque call and post-RET paths. Reconstruct its execution layer before binding genuine providers. Tags do not establish physical external CAN part/count, seat or DND semantics.
