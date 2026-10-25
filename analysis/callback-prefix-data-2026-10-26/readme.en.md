# Fixed-length callback-path DATA (experiment)

[繁體中文](README.md)

Add [readonly C/C++ DATA](../../experiments/tsl9-callback-prefix-data/src/callback_prefix_data.v1.c): **14 actual allocations, 109 bytes**. Windows follow original A0 pointers and A2 length arguments. No implicit NUL or neighboring-address declaration guess.

- All 104 fresh instructions in 16 windows match the original BIN; the whole selected CODE scope is 64,544 bytes / 21,938 instructions.
- C11/C++17 DATA and experimental ET_REL objects match; two independent ELF readers agree.
- Preserve every prior CODE/DATA byte, all six real DATA labels, and 4,861 typed relocations. Experimental undefined providers fall **22 to 8**.
- Not yet curated into `src/`, the complete source proof, or original-coordinate placement. Accepted status stays **88.89% / 22 undefined providers**.

## Contracts and limits

Nominal slot `0x4003C` matches the archived SDK's `tmos_memcmp` candidate. Its declared result is BOOL and its comment identifies TRUE as equal. Original calls and branches remain intact; standard C `memcmp` semantics are not substituted. Installed ROM/ABI and read contracts remain unproved. One selected window is not followed by NUL at its encoded length, so only the exact fixed-length bytes are supplied.

## Newly exposed callback gaps

The original `0x1236A..0x12384` call uses slot `0x401B0`, matching the archived SDK CentralStartDevice candidate formula. Data arguments `0x1A668` / `0x1A674` fit candidate RV32 three-pointer, 12-byte callback records. Installed SDK layout remains unproved.

Of five nonzero pointers, `0x10C34` has selected CODE backing; **`0x10C36`, `0x10D2E`, `0x10D30`, and `0x11544` do not**. Neither candidate table nor a handler stub is supplied here. These four indirect targets are outside the compiler-undefined count; eight undefined providers do not mean only eight runtime gaps remain.

No BIN, target/HOST-model/ISA execution, hardware access, or backend requests. Physical/OTA compatibility remains unproved.

[Summary](summary.json) · [Original evidence](evidence.json) · [Compiler evidence](native-proof.json) · [Contracts](provider-contracts.json) · [Next steps](next-providers.json) · [Feature proposal](feature-candidates.json)
