# Readable reset memory initialization

This C11/C++17 component reconstructs ID2966 V4.1.60
`[0x186BA,0x186F8)`: 62 original bytes / 17 instructions. It reads GP
separately for the copy destination, copy bound and zero-fill start. It copies
32-bit words forward with each read immediately followed by its write, then
zeros words to `0x2000C958`, using unsigned bounds and wrapping address
arithmetic. With the original fixed GP=`0x20004000`, it copies 32 words from
`0x1AB60` and clears 8,758 words.

The normal output commitments are A0=post-clear cursor, A1=`0x2000C958`, and
A2=second GP sample+128. Original A0/A1 survive the clock body to the unknown
ROM handoff; an ordinary C calling convention cannot discard them. Original
T0 from the final copy is immediately overwritten at `0x186F8`, so this helper
does not claim to preserve that snapshot. The source's normal SP address is
`0x20010000`; this helper never initializes SP or proves physical RAM.

## Offline host verification

```sh
sh experiments/tsl9-v4160-reset-memory/verify.sh --language both
```

Or run `python3 -B experiments/tsl9-v4160-reset-memory/verify.py --language both`.
Python 3.10+ and a C11/C++17 compiler are required. `CC`/`CXX` select single
compiler executables; `PYTHON` selects Python for the shell entry. The verifier
downloads nothing. It validates the original image and sealed raw source,
including the surrounding 138-byte reset and actual 128-byte initializer.
It copies that initializer as data into a fresh ignored build directory and
passes only its local ASCII filename to our host tests.

Each language has five groups / 338 cases / 133,601 checks. They cover the
normal original data, independently varied GP samples, copy lengths 0–32,
small and normal zero-fill ranges, unsigned skip/wrap cases, live overlapping
forward-copy data and final cursor residues. Unaligned numeric requests are
synthetic callback tests, not physical alignment/trap validation. Test inputs
are deliberately bounded and terminating. Some altered-GP copy domains in
the original do not terminate; the rebuilt C adds no arbitrary timeout or
fixed 32-iteration shortcut. `--tests-only` omits the raw proof but still
requires the identified original initializer data.

## Native interfaces and limits

Native builds use three compiler-specific live-GP primitives and explicit
A0/A1/A2 commitments. The allowed allocator registers are T0 and A0–A2;
actual native ELF checks must verify this, no stack access and no hidden
`memcpy`/`memset` helpers. The native compiler review is under
`analysis/v4160-reset-memory-2026-10-21/compiler-review/`.

The default leaf has a new RET interface. The original slice instead falls
through into CSR setup at `0x186F8`. An optional native fragment uses a real
compressed jump to `__tsl9_reset_resume_186f8`; that symbol remains an explicit
continuation obligation. A numeric address witness supplies no implementation.
Neither variant proves an original entry adapter, CSR/clock/ROM integration,
asynchronous state, hardware or OTA compatibility. Nothing replaces an
original image; no RV32 code is executed or emulated and no BIN is made.
