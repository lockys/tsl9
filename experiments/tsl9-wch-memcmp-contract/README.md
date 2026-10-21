# Candidate resident comparison semantic port

This C11/C++17 source reconstructs the bounded 72-byte comparison body observed
at linked RAM `[0x20000442,0x2000048A)` in the official **V1.40 and V1.31 references**,
conditionally under LLVM's `Xwchc` instruction profile. The 72 source bytes are
identical after mapping V1.40 flash `0x406F2` and V1.31 flash `0x406B2` through
their distinct initialization paths. Comparing the same flash address would
give different bytes. Neither candidate measures the ROM installed in TSL9.
The V1.40 marker itself fails
the original application's 21-byte version gate. Historical V1.31 prefix
matching does not establish this body's installation or ABI compatibility.

The code preserves read32/clear32 of `0x4002420C`, `FENCE.I`, the source-byte
read order, modulo-32-bit address arithmetic, distinct mismatch/equal exits,
and restoration on every normal return. Even a null input or zero length
performs MMIO effects and returns the candidate's Boolean value 1. This is not
the ISO C `memcmp` ordering-value contract. There is no fence after restore.

All target accesses pass through an explicit backend. Numeric addresses are
never dereferenced on the host. Unknown backend effects, reaching the custom
opcode without a selected Xwchc profile, or the host observation budget stop
without creating a return value
or pretending to restore state. The observation budget is not an original
firmware timeout. The API is ours, has no claim to the original ABI/register
clobbers, and must not be bound to a canonical native symbol.

`source-map.json` pins the captured candidate source and the independent
instruction-profile proof. `verify.ps1` runs synthetic semantic tests under
MSVC C11 or C++17 and compiles the same production source as freestanding
RV32IMAC. It never runs the RV32 object or any original firmware. The host
tests observe mocks only; they cannot prove MMIO/IRQ/hardware behavior.

From this directory, using PowerShell 7:

```powershell
./verify.ps1
./verify.ps1 -Cpp
```

This output is an unlinked `.o`, not a flashable BIN. The original native
application's 31 unresolved canonical contracts remain unresolved.
