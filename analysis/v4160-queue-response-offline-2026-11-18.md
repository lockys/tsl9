# v4.1.60 queue response: offline progress

The selected response path 0x12d4c–0x12d76 has been modeled using pinned input bytes and an opaque synthetic indirect provider. The callback can change registers and memory, including SP. The model uses the post-callback SP for both response stores and does not assume a1/a2 are preserved. A separately run static disassembler matched the 13 selected instructions; two changed-immediate controls did not match. This is not an independent CPU execution.

A synthetic address analysis compares the response record with the dispatcher entry stack. If the dispatcher enters directly with the same post-provider SP, its two entry stores occupy SP-8 through SP-1, disjoint modulo 2^32 from the response record at SP+20 through SP+31. The result assumes successful accesses and says nothing about later stores, provider implementation, ABI, reachability, or device behavior.

Local ordinary and optimized Python runs passed nine response-model tests, two static-disassembly tests and seven address-analysis tests. They require local dependencies and the input image; no claim is made that these unpublished scripts or their dependency closure are available in this repository.

This is bounded offline research, not a complete reconstruction, production firmware, or a flashable image. Original firmware and existing local work were not modified for this report.