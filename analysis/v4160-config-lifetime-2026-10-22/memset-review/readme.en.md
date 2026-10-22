# Candidate byte fill and conditional configuration interval proof

[繁體中文](README.md)

Both retained official candidates map slot40048 to RAM2000039C, from Flash4064C/4060C. Actual full leaf reads cover46 bytes/14 instructions, identical in both versions.

The leaf first READ32s4002420C, writes zero and performs FENCE.I, before testing A0. For nonnull A0 it computes low32(A0+A2); nonzero A2 enters a byte loop that **increments A0 before SB A1,-1(A0)**. On reaching end it returns through MMIO restoration. Null/zero-length still perform the MMIO prefix/restoration. Normal nonzero fill returns advanced A0, not the original-pointer semantics of libc.

Static fields show no nested call or S/GP/SP/RA destination. Explicit writes comprise destination bytes plus the fixed MMIO word. This does not establish normal physical RAM/MMIO/asynchronous behavior. Six valid operand-only raw controls across the two candidates are rejected.

## Conditional original-App derivation

Given the setup branch is reached, slot48 selects this reference leaf, App SP+16 is nonnull with64 valid bytes that do not alias MMIO/code, no asynchronous modification occurs and accesses complete normally:

1. Original19A38 requests A0=App currentSP+16, A1=0, A2=64. Its write intervalSP16..79 contains staCB atSP68..71.
2. The fixed308-byte body contains only one nested call thereafter and before19AEC:19AB4→18F56. The sealed[MAC helper proof](../mac-review/readme.en.md) writes onlySP8..13 without changingSP/S0.
3. Every later explicit SP-relative store misses68..71; the only non-SP store is the reviewed six-byte loop writingSP40..45. This is operand/interval reasoning, not CPU-state execution.
4. Therefore **under these premises, App config+52 is zero at the BLE_LibInit call entry**. Removing the premises, claiming installed/live callback zero, or extending this to its whole lifetime would be unsupported.

Version-gate reachability is not proved; V1.40 still differs from the original21-byte expectation. Inside BLE_LibInit, the pre-copy numeric200004BC call, liveS1 and other unknown effects form the next boundary. They may alter the source config/registers, preventing a claim that the allocator ignoresA2.

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --firmware FW --candidate-root REF
```

Original App/SDK fields reuse the sealed[configuration evidence](../../v4160-allocator-callback-2026-10-22/config-review/readme.en.md). No RV32 execution/emulation, hardware access, installation, vendor API or BIN generation occurs. Default metadata is distinct from actual target behavior.
