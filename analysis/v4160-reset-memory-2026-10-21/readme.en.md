# Reset memory reconstruction evidence

Target: ID2966 V4.1.60, SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. The original memory-initialization slice is `[0x186BA,0x186F8)`, 62 bytes / 17 instructions, within the 138-byte reset sequence. Its source initializer is `[0x1AB60,0x1ABE0)`, 128 bytes. No original firmware is executed or emulated.

The readable source and own host tests are in `experiments/tsl9-v4160-reset-memory/`. Separate reviews contain:

- [Source proof](source-review/readme.en.md): exact bytes, decoded operands, initializer and raw negative controls.
- [Caller boundary](caller-review/readme.en.md): reset, clock and unresolved ROM continuation; normal A0/A1 remain live.
- [Independent C/C++ review](code-review/readme.en.md): ordered synthetic memory/GP/output oracle and actually compiled mutants.
- [Compiler review](compiler-review/readme.en.md): actual freestanding RV32 objects, linked components, structural coverage and rejected placement/provider cases.

The ordinary fixed-GP path copies 32 words and clears 8,758 words. Tests also distinguish the three GP observations, live forward aliasing, skipped domains, unsigned comparisons and final A0/A1/A2. Unaligned numeric callbacks are synthetic; hardware alignment behavior is unknown. Inputs that would make the original copy wrap without termination are not executed by host tests.

The native leaf is 78 bytes, and its optional continuation fragment is 80 bytes. Neither fits the original 62-byte extent. The original falls through; a C-generated return is a different interface. A numeric relocation witness does not implement the missing entry/continuation adapter or prove the resident ROM. Register/loop structural checks do not establish original IRQ or asynchronous intermediate-state behavior. The existing full-image carrier and original BINs remain unchanged; no new BIN is produced.

Published/delivered evidence includes selected review source, text and receipt metadata. Historical generated objects, executables and probes remain in workspace build archives. Destination and publication verification produce fresh local ignored outputs. See `destination-verification.json` in the delivery directory for those local receipts. Exact original artifacts and published files are covered by the repository manifest. Local Windows checks do not establish Linux/macOS or shell launch success.
