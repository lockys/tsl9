# Flags to receive path: offline static analysis

[繁體中文](README.md) · [Source spans and hashes](source-spans.json) · [C/C++ verification](../../experiments/tsl9-irq-flag-consumer/readme.en.md)

**Confirmed within the recorded spans:** `17002` clears flags before calling `16B0A` with channel 1/2. The latter reads register `0x2C`, uses returned A0 bit0 to choose `0x61`, then tests then-live S0 bit1 to choose `0x71`, and writes `0x2C=0`. S0 initially stores status, but its preservation across the first downstream call remains unproved at the provider boundary. Channel and receive-buffer selection are different layers.

`16994`/`16A30` send `03`/`02` plus an address for reads/writes. Downstream `16896` performs 16-bit MMIO at `0x40013008`/`0x4001300C`. Each polling stage permits at most 255 attempts; timeout returns 0, which is not evidence of a successful zero-valued read.

`16A7C` receives 13 bytes and calls `12BC8` after format checks. The latter uses 32 slots of 12 bytes starting at `0x2000C038` and loads an indirect provider from `0x4004C`. Its installed implementation is unknown; an ordinary `memcpy` cannot be assumed equivalent.

**Reconstruction limits:** all 54 non-call bytes of the flag consumer match; two JALs remain unresolved. The SPI candidate compiles to 74B/26 instructions against the original 72B/25, fails full-code equality and is excluded from `src/`. The complete receive chain, physical chip, IRQ/ROM ABI and flash readiness remain unproved.

`source-spans.json` pins seven spans totaling 586 bytes/210 instruction-width rows, with raw bytes and file offsets. This bounded analysis proves neither complete function extents nor all indirect entries. No RV32/MMIO execution or hardware operation occurred.
