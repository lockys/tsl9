# AB68 strict leaf-only binding control

The local saved-caller experiment also builds a separate leaf-only executable using a strict link (no `--unresolved-symbols=ignore-all`). For both C and C++ candidate objects, omitting the data binding fails with `undefined hidden symbol: tsl9_ab68_data`; defining `tsl9_ab68_data=0x2000bee8` links successfully and yields the original leaf bytes `17150020034505388280`. The normal and Python `-O` controller runs both passed.

This strict check includes only the leaf, not the two larger saved caller sections. The caller-section comparison still ignores other unresolved references; the scripts and saved object dependencies remain local. A numeric binding is an assumption, not proof of the live device's RAM, a full graph, or runtime behavior.
