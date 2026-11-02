# Expanded direct-write scan for sequence state

The earlier sequence audit scanned 69,412 bytes of selected code for standard byte, halfword or word stores based directly on GP that overlap `GP+[332,336)`. This check adds the formerly omitted 3,124-byte linear decode window `[0x14056,0x14C8A)`; across 24,610 instructions in both, no such direct store is found.

The sequence code updates state through other registers and indexing, so this does not mean there are no writes. It also does not exclude indirect pointers, other encodings, unselected code, resident, IRQ/DMA or reentrancy. The global 0/1 invariant remains conditional on those unresolved factors.

Replay with `experiments/tsl9-state167-writers/verify.py` and the hash-pinned candidate BIN, layout, ELF reader and radare2. The checker includes eight synthetic store-boundary cases. No target execution or hardware operation occurs.
