# Next provider: 0x18D78

[繁體中文](provider-next.md) · [Instruction evidence](provider-decode.json)

Official ID2966 `[0x18D78,0x18E1C)` covers 164B/53 instructions, SHA256 `678a3cbf42bc02d5c730973675858a18e538af9fdc1cb74dd9296f220f487ae3`. This is bounded static RV32 decoding, not a readable C reconstruction. The historical `.4byte` carrier in `callee_native.c` is neither readable C nor an ABI proof.

There are no calls or writes to SP/RA in this span, and two RETs. This supports local SP/RA preservation for this entry, without proving complete interrupt context, other entries, physical MMIO or silicon identity.

Direct instruction evidence:

- A5 = A0 + (A1 << 4). Each following word read is fresh; do not combine/cache them.
- `[A5+432] & 4` is stored at output+8. The zero path freshly reads that word, shifts by21 and stores a word at output+0. The nonzero path freshly reads it, shifts by3 and stores at output+4 before rejoining.
- Another `[A5+432] & 2` goes to output+9. `[A5+436] & 15` goes to output+10; a separate read shifted by8 goes to output+19.
- Each byte from `[A5+440]` and `[A5+444]` is derived from a separate word read and shift0/8/16/24, then stored at output+11..18. The last read overwrites A5; preserve that ordering/register effect.
- A1=0 selects a fresh LW/OR32/SW at `[A0+12]`; otherwise `[A0+16]`, followed by RET. Physical register/bit5 meanings remain unverified.

The IRQ adapter supplies A0=`0x40006400`, A1=0 and A2=SP+12. The last output+19 store is SP+31, inside its32B frame. This conclusion is specific to this direct call and bounded paths; ring's dynamic resident call remains unproved.

Feature research leads: output+10 is masked only with15 and the adapter adds no <=8 check. The nonzero output+8 path writes output+4 but leaves output+0, which the adapter later reads, untouched. These are local length/field-validity dependencies, **not proof of hardware overflow, malformed packets or support for a particular extended format**. Hardware configuration, reachable inputs and caller/provider conventions remain open. No filter, clamp, layout or runtime behavior was changed, and no MMIO/device execution occurred.

Next reconstruct C volatile word reads, shifts and byte/word stores, preserving fresh-read counts, cold blocks and both real RETs. Then verify actual native objects and nominal linkage to IRQ. Do not substitute original raw bytes as a fake provider to claim C reconstruction.
