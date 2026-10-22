# SPI native reconstruction milestone

[繁體中文](README.md)

C11 and C++17 now generate and link the complete SPI leaf `[0x16896,0x168DE)` to **72 bytes / 25 instructions identical to the official image**. See the [experiment](../../experiments/tsl9-spi-transfer-leaf/README.md) for the selected source, explicit assembly ports and commands, and [contract.json](contract.json) for register/access contracts.

- Standalone: 2 actual ELFs and 36 negative controls per language. Read-only replay passes; the strict firmware-ready gate deliberately rejects.
- Receive pipeline: expanded from 280B to **352B / 16 genuine FUNCs**. Six SPI calls now bind the new definition. Of 17 relocations, 15 target definitions; two packet-provider calls remain UND. All 32 structural controls per language reject without the whole-file hash gate.
- The partial link retains zero-displacement JAL/RVC placeholders. The old 280B and native SPI 72B projections are unchanged; 294 bytes outside control fields match the original image. This is not a resolved executable or device Flash layout.

[summary.json](summary.json) and the [four public receipts](receipts/) bind the precise hashes and scope. Receipts were created with path variables and are byte-identical to local originals. ELF/IR/MD/log artifacts and historical receipts remain local. The prior provider receipt is a pinned historical input: its artifacts were reread, but its complete checker dependency closure was not replayed.

[packet-next.json](packet-next.json) captures the next implementation constraints. Packet GPIO selection uses `channel==1`, unlike the two independent bit tests in register read/write. Its 48B frame, 13-byte receive loop, cleanup-before-validation and fresh-slot restores must remain. That provider has not been rebuilt yet.

A possible diagnostic can distinguish valid zero data from timeout using the existing exit residues: success A4=1/A5>0 versus timeout A4=A5=0. It is not implemented. Diagnostic RAM ownership and complete IRQ context must be established first; A0=0 alone is insufficient.

The existing curated `src/` inventory is unchanged this milestone; provenance/object checks precede promoting the selected SPI source. No target/ISA execution, hardware access or BIN generation occurred. Packet/resident/startup/IRQ/memory/OTA compatibility remains incomplete. **This evidence does not authorize a flashable-firmware claim.**
