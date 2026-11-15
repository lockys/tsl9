# 0x9f74: retained diagnostic ELF reference scope

Offline comparison against `ID-2966-V4.1.60-decoded.bin`, SHA-256
`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`.
The existing mixed C/assembly owner is not a newly recovered function.

On the local retained C and C++ artifacts in each of the following directories,
the current experimental audit found one executable six-byte owner at `0x9f74`,
bytes `a387010a8280`, and original address-materialization sequences at `0xa0b8`,
`0xa1b8`, and `0xa356`:

- `experiments/tsl9-original-layout/build/safe-gap-v2/`
- `experiments/tsl9-original-layout/build/input-state-decoders-v1/`

All four artifacts have zero `PT_LOAD` segments. In safe-gap-v2 the three
reference sites are in `.original_code_span_00008520`, so their presence does
not establish reconstruction of those sites from C source. The checks compare
retained bytes to the original and independently decode their address target;
they do not establish runtime reachability, callback execution, live GP, build
provenance, hardware behavior or an OTA-ready image.

The local extension to `audit_original_layout.py` accepts `--all-references`;
its updated tests cover both safe-gap-v2 languages and mutations at all three
sites. Both normal and Python `-O` runs passed five tests. **That audit extension
and the saved ELF artifacts are not included in this checkpoint**, so this note
alone is not a self-contained reproduction. The earlier committed audit targets
only the narrower rom-dependencies-v1 scope and fails closed on the other scope.
