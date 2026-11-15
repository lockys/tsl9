# v4.1.60 0x10408: bounded placement evidence

This note records an offline experiment, not aggregate acceptance. The original image SHA-256 is `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`. No device was contacted and the original image was not modified.

On 2026-11-15, C and C++ candidate-aliases ET_REL objects from two fresh experimental build runs were audited against the existing seven-leaf baseline and linked in a temporary directory. The two runs produced the same respective object hashes:

- C: `b141de29dccd8af198d4cbe38af122130926e6cf5c2d1539af34177c9e79fee8`
- C++: `ac8428cb0fec3108a8953bb383ac4de58d9025b184a6de782a0a6d56d9ed505f`

The input audit checks, among other things, the 10408 leaf's HI20/LO12 and RELAX relocations, the caller's JAL relocation and alias, and nonleaf section and relocation deltas. The diagnostic link retains only four sections, at 0x10402, 0x10408, 0x1040e and 0x139a6; all other input sections are discarded. With `--relax --relax-gp`, assumed GP `0x20004000`, assumed leaf witness `0x20004052`, and a numeric 0x828c call target, their complete output bytes match the corresponding original image bytes. The retained call at 0x139aa targets 0x10408, and the call at 0x10416 targets 0x828c. Without relaxation, the linker rejects overlap between the leaf and its following section. All four C/C++-and-run combinations passed with normal and Python `-O` controllers.

A separate real-link negative control pre-encoded the original caller JAL and disabled its input relocation. Its final retained sections still matched the original bytes, but the input ET_REL audit rejected the fake object. This demonstrates why comparing linked bytes alone is insufficient to establish input relocation provenance.

The diagnostic scripts, baseline and experimental object files used for this observation remain local untracked artifacts and are **not included in this checkpoint**. This note alone is therefore not a self-contained reproducibility package. Their local SHA-256 values include `audit_saved.py` `6c4476cd463b17884d61c499e661a1b9ed309d2c464469d412a286b7f1dfaf22`, `test_adjacent_placement.py` `871d44eb70200c0fc729092ce7a15c6a42a87bb969aa2cdc7c1631a065f395c5`, and `test_preencoded_call_control.py` `f581260fcfbd128d3e1ac798a588a587daac3d69c91f3de9185fe32545ce26b5`.

Limitations: the ET_REL parser and tools were local dependencies, the fixed addresses are assumptions, and discarded sections, complete relocation semantics, actual GP, runtime behavior, firmware flashability and OTA readiness are not established. A full placement and independently reproducible acceptance chain remain necessary.
