# Resident copy reference C/C++

This is a finite data/effect reconstruction of the selected 58-byte, 18-instruction
copy body in the retained Dec2023 candidate carrier. It is not an instruction
interpreter, native ROM replacement, executable firmware or physical ABI proof.
The explicit `RP_DEC2023_133D3705` profile selects that carrier by evidence; default
`RP_PHYSICAL_UNKNOWN` refuses binding before any effect.

The candidate slot at `0x4004C` contains `0x20000332`, a RAM address. The relevant
prefix of its first initializer copy conditionally maps carrier source
`[0x405A2,0x405DC)` to RAM `[0x20000332,0x2000036C)`. The source proof is retained in
`source/` under this round's analysis directory and checks original carrier bytes,
the slot, initialization operands, all selected instructions and 23 raw mutants.
That mapping requires normal source reads and RAM writes with no replacement of
instructions; it does not establish completed initialization. The separately
identified missing four-byte load in the second initializer remains unresolved.

`rp_copy` requests READ32 at RAM PC `0x20000336`, clears `0x4002420C` at `33A`, and
observes `FENCE.I` at `33E` **before** either pointer or length guard. Null/zero
ordinary paths still restore the saved word and observe RET. Its hardware purpose
is unknown. It then copies fresh source bytes forward, computes destination before
incrementing its u32 index, and increments before WRITE8 at `362`. Overlap where
destination is above source therefore propagates modified bytes. There is no
snapshot, `memmove`, u16 length narrowing or second fence. Return scalar a0 remains
the incoming destination, including on null/zero paths.

Each value carries a bit-known mask. Ambiguous branches stop after the established
prefix; partial saved MMIO/data bytes are preserved and delegated to the provider.
Numeric addresses are never host pointers. All memory effects, FENCE.I and RET
need an explicit synthetic provider. HALT/TRANSFER and the host observation budget
retain preceding effects, including a cleared MMIO word. There is no invented
cleanup. A nonreturning write may already have applied effects; `stores_returned`
counts only store callbacks that returned normally. `index` has already advanced
at a failing write. These are host diagnostics, not hardware completion counters.
`result` denotes source a0, and only a normally returned activation supplies a
returned scalar. An accepted partial RET target remains a provider assumption.
`rp_new_activation` starts a distinct host invocation; it cannot resume a native
instruction or restore backend memory.

Thin `rp_uid_copy` and `rp_boot_copy` seams bind only the selected UB1C66/1C80 or
BOOT225E requests and normalized reference target `0x20000332`. UID copy preserves
its caller's modeled SP/S0/S1/S2/RA, because this leaf does not assign those
registers. Shared-memory stores may still alias saved-register words which UB
subsequently reloads. The BOOT request uses source JALR continuation `0x2260`.
Unknown/wrong targets and wrong callsites fail a host binding check before any
effect. These are deliberately explicit reference bindings, not original guards
and not a substitution for the older `RC_WCH_64BE955_V130` profile.

Run `./verify.ps1` and `./verify.ps1 -Cpp` with PowerShell. Optional `-Carrier`,
`-ProofRoot`, and `-Firmware` select the exact retained candidate, proof directory
and BOOT2580 fixture. Defaults resolve the workspace or delivered analysis tree.
The verifier pins all source/dependency bytes, replays the portable raw checker,
and builds/runs only our own synthetic host tests with MSVC `/W4 /WX` in C11/C++17.
The tests cover order, short circuits, overlap, u32 wrap/length, partial knowledge,
provider stops, nonreturning partial effects, budget and both thin bindings.

The original hardware, installed ROM, memory/startup/interrupt contracts and OTA
update compatibility are still unproved. No native BIN is created by this model.
