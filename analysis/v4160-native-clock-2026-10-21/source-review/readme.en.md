# Native clock reconstruction: source contract

This review reuses the immutable ID 2966 V4.1.60 source proof for `0x18834..0x188E2` and `0x1973C..0x19764`. Its seal is `ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51`. The original source proof covers 214 bytes / 69 instructions, plus its separately identified reset-table evidence; its checker rejects 50 raw operand mutations. No new disassembler or duplicate decoder is introduced here.

## Query at 0x18834

The first READ32 at `0x40021004` supplies only selector bits 2 and 3. A selector masked value of 4 chooses 32000000; 8 chooses the PLL path; 0 and 12 both choose 8000000.

On the PLL path, READ32 at 0x18882 supplies the multiplier, and a separate READ32 at 0x18884 supplies source bit 16. These are independent samples. The multiplier is `((sample >> 18) & 15) + 2`, with 17 replaced by 18. When source bit 16 is zero, a fresh READ32 at `0x40023800` supplies bit 4: set chooses 8000000, clear chooses 4000000. When source bit 16 is nonzero, another fresh READ32 at `0x40021004` supplies bits 22 and 23. Both set chooses 16000000. Otherwise, yet another fresh READ32 supplies bit 17: set chooses 4000000; clear chooses 8000000. The original implements the final bit test as a 32-bit left shift by 14 followed by a signed sign test. A C implementation may directly test bit 17 of that same fresh sample; it must not convert the original sign test to an unsigned nonnegative comparison or invoke signed-left-shift undefined behavior. The product is low32(multiplier * selected base).

Every selected path joins the same effect sequence:

1. WRITE32 provisional scalar at then-current `GP+108`, at 0x18850.
2. Fresh READ32 at `0x40021004`, at 0x18858, supplies `(sample >> 4) & 15`.
3. Form table base from then-current `GP+64`, then READ8 unsigned from table base plus that index, at 0x18864.
4. Form a fresh scalar address from then-current `GP+108`, then READ32 that word at 0x1886C. Never replace it with the provisional local variable.
5. Logically shift that fresh word right by `table_byte & 31`. The mask is required for defined C shifts even when a live table byte exceeds 31.
6. WRITE32 the shifted word at then-current `GP+108`, at 0x18872.

The reset copy conditionally initializes the sixteen table bytes to `00 00 00 00 00 00 00 00 01 02 03 04 06 07 08 09`. This is not a live RAM capture or permission to replace the READ8 with a fixed table. The table can differ if reset, resident code or other writers differ.

## Derived fields at 0x1973C

READ32 a fresh word from then-current `GP+108` at 0x19740. Perform **unsigned** 32-bit division by 8000000, then mask the quotient to eight bits at 0x1974E. WRITE8 that held masked quotient to then-current `GP+382` at 0x19752. Multiply the held masked quotient by 1000 at 0x1975A; do not reload the byte. WRITE16 low16 of that product to then-current `GP+380` at 0x1975E. Truncating the quotient before multiplication is required; truncating only the final product changes behavior for large input words. Byte/halfword writes must retain their original widths and preserve adjacent storage.

The source caller invokes the query, then `0x9A42`, then the derived-fields function. The second function must read the global again rather than receive a cached return value from the query. Prior work reconstructing 0x9A42 establishes its own source effects; it does not turn this fresh read into a cached value or prove real interrupt behavior.

## Native C interface and ABI limits

Both original functions are leaves. Neither contains a call or SP operation, nor explicitly writes GP, RA, A0 or A1. Both return through live RA with bit zero cleared. Their temporary arithmetic changes A2/A3/A4/A5 as indicated by the immutable source proof; preservation of other register state is an instruction-body fact, not a recovered source-level prototype.

An ordinary C API accepting a context or GP argument typically uses A0 and possibly A1 under the C ABI. A C return value likewise uses A0. Declaring a function `void` does not force a compiler to preserve A0 or A1. Therefore such a native C component can reconstruct peripheral/data effects while still requiring a separately proved adapter before replacement at the original call sites. An ordinary C compiler can also create a stack frame and clobber caller-saved temporaries. No current source proof establishes original entry/exit ABI compatibility, IRQ safety, compiler layout equivalence or drop-in flashing.

The original forms GP-relative addresses separately at each documented instruction. A native C context with one fixed GP per call is an explicit ordinary-C interface assumption: the original body does not assign GP, but asynchronous or externally injected GP changes are outside that interface. Host MMIO callbacks may mutate external storage between effects without thereby proving general machine-register mutation handling. Document this boundary rather than claiming the C function models every live-register environment.

## Replay

```sh
python3 check-source-review.py --project-root /absolute/path/project --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin
```

The read-only wrapper accepts the working-tree `apk-analysis/` and published `analysis/` layouts. It pins the old source seal and every old member, checks the exact original image digest, then calls the existing source checker. No source evidence is rewritten. It performs no network request, target execution, ISA emulation, physical I/O or OTA action. No particular physical chip or clock frequency unit is established by this review.
