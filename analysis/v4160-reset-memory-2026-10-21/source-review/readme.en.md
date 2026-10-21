# Reset memory slice: original source contract

The exact ID 2966 V4.1.60 image SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`, 76800 bytes mapped at 0x8000. The selected slice is `0x186BA..0x186F8`: **62 bytes / 17 instructions** (fourteen 4-byte instructions and three compressed 2-byte instructions), SHA-256 `aea8841ab98f92a2372b602ee5c7667e626faac48814dd49d86893392f7273ac`.

The existing ID2966 reset-contract source map identifies the enclosing 138-byte reset body `0x186AA..0x18734` and 128-byte initializer `0x1AB60..0x1ABE0`. Their hashes are reused and checked. The older sixty-fifth-round reset analysis concerns a different image (`32639d7d...`, reset at 0x183FE); its addresses, 136-byte initializer and bounds are not evidence for this image. The sealed clock-query source proof independently covers the first 52 reset bytes `0x186AA..0x186DE`; the present small raw decoder adds exact coverage of the complete memory slice without replacing those immutable scopes.

## Entry context and three GP reads

The preceding original PC-relative pairs at 0x186AA/0x186AE and 0x186B2/0x186B6 form GP=0x20004000 and SP=0x20010000 respectively. These are static address calculations, not observed register state or proof of real RAM validity. The selected memory slice never writes GP, SP or RA. It is not a callable C function: it has no call, RET or RA link formation, and ordinary completion falls through to 0x186F8, the next instruction outside the slice.

Three separate instructions read the then-current GP:

| PC | Assignment |
|---|---|
| 0x186C2 | A1 := GP |
| 0x186C6 | A2 := low32(GP+128) |
| 0x186DE | A0 := low32(GP+128) |

The body does not modify GP, so an uninterrupted original execution retains it; neither static code nor a C interface establishes absence of external register/trap effects. A reconstruction claiming to represent arbitrary live-GP changes must preserve these separate formation points. A fixed-GP ordinary C interface must document its narrower input assumption.

## Forward word copy

0x186BA/0x186BE form A0=0x1AB60 from their own original PC-relative pair. 0x186C2 captures the destination in A1, and 0x186C6 separately forms the exclusive bound in A2. At 0x186CA, **unsigned** A1>=A2 skips to 0x186DE. Otherwise each iteration performs exactly:

1. 0x186CE READ32 from then-current A0 into T0.
2. 0x186D2 WRITE32 then-current T0 at then-current A1.
3. 0x186D6 A0 := low32(A0+4).
4. 0x186D8 A1 := low32(A1+4).
5. 0x186DA branches back while unsigned A1<A2.

Do not snapshot all source words before writing. This is a forward word copy; overlapping source/destination can change future reads. It is not a generic overlap-safe `memmove`, and C `memcpy` cannot justify overlapping behavior. No source/destination validity, alignment or nonoverlap check exists in this slice. Read and store faults, asynchronous mutation and physical memory effects remain unproved.

With initial destination d and bound e already reduced to unsigned 32 bits, d>=e skips the copy and leaves incoming T0 untouched. If d<e and `e <= 0xFFFFFFFC+(d&3)`, ordinary arithmetic reaches the first cursor >=e after `ceil((e-d)/4)` iterations without destination wrap. If e exceeds that largest value in d's residue class modulo four, repeated +4 wraps and can never reach >=e under unchanged registers; the source has no iteration limit. Large copy counts can also wrap the source address. A synthetic budget or safe-C refusal is an explicit boundary, not evidence of original completion.

## Zero-fill and continuation outputs

At 0x186DE, A0 is reassigned from the **third** GP read, regardless of whether the copy ran. At 0x186E2/0x186E6, the original PC-relative pair assigns A1=0x2000C958. At 0x186EA, unsigned A0>=A1 skips directly to 0x186F8. Otherwise 0x186EE performs WRITE32 zero at A0, 0x186F2 advances A0 by four modulo 32 bits, and 0x186F4 repeats while unsigned A0<A1. The zero-fill has no READ32 and does not alter T0.

Let z=low32(third GP+128), E=0x2000C958. If z>=E, zero-fill is skipped and final A0=z. If z<E and all stores succeed without external GPR mutation, final A0 is the first value in z's modulo-four class >=E, after `ceil((E-z)/4)` writes. Because E is below 0xFFFFFFFC, this zero-fill cursor cannot wrap before reaching E..E+3. A misaligned z can cause misaligned stores or overshoot the exclusive bound by up to three; no hardware support or successful completion is proved for such inputs.

At the slice's normal continuation 0x186F8:

- A1=0x2000C958, including copy/zero skip paths.
- A2=low32(second GP+128), unchanged after 0x186C6.
- A0 is the final zero-fill cursor or the skipped z above; the earlier source cursor is overwritten.
- T0 is incoming T0 if copy skipped, otherwise the final successfully read copy word, subject to the stated register-effect assumptions. Zero-fill does not clear it.
- All other integer registers, including A3..A7, GP, SP and RA, are untouched by this slice. Possible explicit destinations are x5/T0 and x10/A0, x11/A1, x12/A2.

For all three GP samples equal to 0x20004000, copying performs 32 READ32/WRITE32 pairs, then zero-fill performs 8758 WRITE32 operations over `0x20004080..0x2000C958`. Final A0=A1=0x2000C958 and A2=0x20004080. The final initializer word in the exact file is at 0x1ABDC, bytes `a1 03 00 00` (929). Thus T0=929 is conditional on the original mapped initializer supplying those same reads and normal completion; it is not a physical register observation. The next original instruction at 0x186F8 assigns T0=31, but that lies outside the selected slice and must not be folded into its output contract.

## Reconstruction and proof limits

Word widths, read-before-write order, unsigned comparisons, modulo-32 arithmetic, three address formations and continuation residues are source requirements. An ordinary C entry/return ABI or an adapter that uses/restores other registers needs separate proof. This slice alone does not initialize CSR state, clock hardware, an interrupt controller, resident firmware or OTA. It does not prove the image's physical memory map, ROM identity or flash compatibility. A range checker only establishes static source identity and selected operands, never successful hardware execution.

```sh
python3 check-source-review.py --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin --review-root /absolute/path/source-review
```

The read-only checker verifies the whole original digest, full reset/initializer context hashes, all 17 independently bit-decoded instructions and 17 raw instruction mutations rejected without using the whole-image digest for those controls. No network, device I/O, target execution or ISA emulation occurs.
