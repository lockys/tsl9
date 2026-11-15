# AB68 linked symbol and duplicate-owner control

The local saved-caller link experiment now also checks that the linked ELF defines exactly one `__tsl9v4160_call_ab68` symbol at `0xab68`, size 10. A real second copy of the C or C++ candidate object is rejected by `ld.lld` with `duplicate symbol: __tsl9v4160_call_ab68`. Normal and Python `-O` runs passed the positive and negative controls.

As in `SAVED-CALLERS-LINK-NOTE.md`, other undefined caller references are ignored and the script and object dependencies remain local, outside this checkpoint. These checks are not a complete graph or execution proof.
