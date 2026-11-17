# V4.1.60 option: offline c7e8 countdown analysis

This report concerns the firmware image identified by SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. V4.1.60 is the server option label, not an independently verified internal build version. This report does not include the image.

## Findings

Under the tested synthetic conditions, countdown expiry enters the zero-input path at `0xc7aa`: the enable byte is cleared, and the routine then clears the byte at `gp+284`. Whether further calls occur depends on a reloaded configuration and record bytes. These are conditional observations, not evidence that the path is reachable on a device under normal operation.

An offline bounded instruction model covers selected expiry paths. A separate static `rasm2` comparison checks the selected disassembly. Controlled next-PC checks exercise both directions of ten conditional branches and six direct calls or jumps, and check the corresponding JAL link value. Synthetic faults and instruction mutations are included.

## Validation and limits

The bounded scenario suite reports 16 ordered scenarios, 8 fault cases and 7 instruction mutations in both normal Python and `python -O`. Static-disassembly tests report 5 tests in each mode; next-PC tests report 2 in each mode. The experiment relies on a hand-written instruction model, synthetic RAM and synthetic returning hooks. Its event trace is selective, and the check does not validate all instruction side effects, actual provider behavior, the complete ABI, runtime reachability, or hardware. The reference image's SHA-256 identifies bytes only, not provenance or permission to redistribute them.

The implementation and its dependencies remain under local review and are not included in this report. In particular, these results do not establish a complete C reconstruction, a flashable image, or firmware equivalence.
