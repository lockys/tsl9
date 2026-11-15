# AB68 candidate with saved caller sections

A local `link_saved_callers.py` experiment compiled the renamed pure C candidate and linked it with two saved original caller sections for C and C++, using numeric `tsl9_ab68_data=0x2000bee8` and fixed section addresses. The resulting leaf bytes were `17150020034505388280`; linked calls at `0x10394` and `0x13ac6` matched the original firmware and targeted `0xab68`. Wrong address produced `17150020034515388280`; signed load produced `17150020030505388280`. Both ordinary and Python `-O` runs passed these checks.

The large saved caller sections contain other references and the experiment uses `--unresolved-symbols=ignore-all`; only the candidate symbol and two selected calls are explicitly checked. **The script, saved objects and parser are local and not included in this note checkpoint.** This is not a fresh build, full graph, proof that other dependencies are satisfied, live RAM binding, device execution or flashability.
