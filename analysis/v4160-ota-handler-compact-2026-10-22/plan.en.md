# OTA handler size and callee contract plan

[繁體中文](plan.zh-TW.md)

The full goal remains a rebuilt BIN usable on the original hardware through its BLE updater. This milestone addresses actual size and necessary callees of the previous 776-byte shared C/C++ component. Component tests do not prove hardware compatibility.

1. Reuse sealed sources, actual ET_REL/IR, the original 530-byte instruction body and complete-image baseline. Read real relocations and loops first; correct the prior three README static-callsite errors explicitly.
2. Bound source changes by a concrete compiler IR hypothesis. Retain the negative no-unroll result. Separating native reply and argument-object lifetimes must preserve all eight register inputs/outputs, memory clobbers, volatile effects, HOST behavior and W reply projections.
3. The three original shared terminal reply sites justify a second C control-flow hypothesis. Shared labels must retain each path's mask, source site, call order and stop behavior. Do not drop arguments that unknown callees may observe.
4. Independently inspect actual UID comparison, builder and slot `0x4004C` operands and call chains. Candidate ROM code establishes conditional contracts, not installed identity.
5. Freshly verify real C11/C++17 HOST behavior with own and independent fixtures. Independently read actual native ELF/IR/MD, all instruction fields and tool/source identities. Preserve old seals and admissions.
6. Deliver verified sources to `re-tsl9`, rerun in delivery and publication trees, preserve all existing files/images, then publish the authorized private milestone.

Physical S/SP/GP/RA, scratch/alias, asynchronous observers, installed ROM/BOOT, Flash, OTA format/acceptance/recovery remain separate requirements. Numeric fit proves none of them. No link, new BIN, RV32 execution/emulation, hardware access or vendor API is scheduled here.
