# v4.1.60 dispatcher continuation: offline semantic check

The existing dispatcher continuation at `0x14b8c–0x14b9c` was examined against the pinned v4.1.60 reference image. It already has an instruction-oriented assembly transcription; this work does **not** add 16 bytes of source coverage or replace the formal build.

A bounded callback-based C projection models its control flow. For unsigned `s2 <= 1`, it branches without a byte read. Otherwise, assuming a successful read at the address in `s0`, it selects one of three continuations for byte values zero, one, or other. This is a continuation of a shared dispatcher frame, not a stand-alone firmware function.

For each of C11 and C++17, the local test compared all 32 projected registers, stop PC, and synthetic read events across 3,072 input cases. Six compiled negative controls produced their expected mismatch counts. The same checks passed in ordinary and Python optimized modes. A separate bounded static check pinned the image hash and selected upstream instruction windows, and checked specific branch, call and address calculations; it passed three tests in both modes. These tests compare a host model with a handwritten limited decoder; the C-side event PC is supplied by the test.

The result does not establish source-level equivalence for arbitrary compiler profiles, all callers, physical memory layout, callback side effects, fault behavior, ABI, device reachability, or a flashable reconstruction. No device was contacted. The candidate source and test files remain in local checkpoints and are not included in this report.
