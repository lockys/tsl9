# Adjacent address-pair scan for sequence state

Assuming numeric GP `0x20004000`, the four sequence-state bytes occupy `[0x2000414C,0x20004150)`. In the hash-pinned 69,412-byte selected code layout and 3,124-byte linearly decoded `[0x14056,0x14C8A)` window, this scan checks adjacent standard `LUI`/`AUIPC` and standard load, store or `ADDI` instructions using the same destination register as base: 1,280 pairs match that encoding, none of whose resulting numeric ranges overlaps the four state bytes.

The scan excludes nonadjacent instructions, subsequent address arithmetic, compressed memory instructions, pointers, other code, resident and asynchronous effects. It does not prove there are no other state writes or establish a global 0/1 bound. Linear decoding does not prove any instruction is reachable.

Run `python experiments/tsl9-sequence-address-pairs/verify.py --firmware <CANDIDATE_BIN> --layout <ORIGINAL_LAYOUT_ELF> --reader <ELF_READER>`. Inputs are hash-pinned and five synthetic decoder controls run locally; there is no target execution or hardware access.
